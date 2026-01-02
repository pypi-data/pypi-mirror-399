import torch
import torch.nn as nn
from einops import rearrange, repeat
import math
import torch.nn.functional as F
from mamba_ssm.ops.selective_scan_interface import selective_scan_fn
import einops

class MambaLow(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=1, dt_rank="auto", dt_min=0.001, dt_max=0.1,
                 dt_init="random", dt_scale=1.0, dt_init_floor=1e-4, conv_bias=True, bias=False,
                 use_fast_path=True, layer_idx=None, device=None, dtype=None):
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.d_model = d_model
        self.d_state = d_model // 4 * expand
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(self.expand * self.d_model)
        self.dt_rank = math.ceil(self.d_model / 16) if dt_rank == "auto" else dt_rank
        self.use_fast_path = use_fast_path
        self.layer_idx = layer_idx
        self.get_A = nn.Linear(self.d_model // 2, self.d_inner // 4)
        self.in_proj = nn.Linear(self.d_model, self.d_inner, bias=bias, **factory_kwargs)
        self.x_proj = nn.Linear(self.d_inner // 2, self.dt_rank + self.d_state * 2, bias=False, **factory_kwargs)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner // 2, bias=True, **factory_kwargs)

        # Initialize dt_proj weights
        dt_init_std = self.dt_rank ** -0.5 * dt_scale
        if dt_init == "constant":
            nn.init.constant_(self.dt_proj.weight, dt_init_std)
        elif dt_init == "random":
            nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)
        else:
            raise NotImplementedError

        # Initialize dt bias
        dt = torch.exp(
            torch.rand(self.d_inner // 2, **factory_kwargs) * (math.log(dt_max) - math.log(dt_min))
            + math.log(dt_min)
        ).clamp(min=dt_init_floor)
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_proj.bias.copy_(inv_dt)

        # Initialize A matrix
        A = repeat(
            torch.arange(1, self.d_state + 1, dtype=torch.float32, device=device),
            "n -> d n",
            d=self.d_inner // 2,
        ).contiguous()
        A_log = torch.log(A)
        self.A_log = nn.Parameter(A_log)
        self.A_log._no_weight_decay = True
        self.D = nn.Parameter(torch.ones(self.d_inner // 2, device=device))
        self.D._no_weight_decay = True
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=bias, **factory_kwargs)

        # Convolution layers
        self.conv1d_x = nn.Conv1d(
            in_channels=self.d_inner // 2,
            out_channels=self.d_inner // 2,
            bias=conv_bias // 2,
            kernel_size=d_conv,
            groups=self.d_inner // 2,
            **factory_kwargs,
        )
        self.conv1d_z = nn.Conv1d(
            in_channels=self.d_inner // 2,
            out_channels=self.d_inner // 2,
            bias=conv_bias // 2,
            kernel_size=d_conv,
            groups=self.d_inner // 2,
            **factory_kwargs,
        )

        self.epsilon = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)

    def low_rank_approximation(self, matrix, rank):
        U, S, V = torch.svd(matrix)
        return U[:, :rank] @ torch.diag(S[:rank]) @ V[:, :rank].T

    def robust_control(self, A, disturbance):
        """
        Implement a simple robust control strategy.
        Here we can use a simple feedback mechanism to adjust A based on disturbance.
        """
        adjusted_A = A + disturbance
        return adjusted_A

    def forward(self, hidden_states):
        """
        hidden_states: (B, L, D)
        Returns: same shape as hidden_states
        """
        _, seqlen, _ = hidden_states.shape
        xz = self.in_proj(hidden_states)
        xz = rearrange(xz, "b l d -> b d l")
        x, z = xz.chunk(2, dim=1)
        getA = self.get_A(x.permute(0, 2, 1))
        b, l, d = getA.size()
        rank = d // 4 + 1
        getA = rearrange(getA, "b d l -> (b d) l")
        getx = rearrange(x, "b d l -> d (b l)")
        A = (getx @ getA)

        min_val = A.min()
        max_val = A.max()
        normalized_A = (A - min_val) / (max_val - min_val)

        disturbance = torch.randn_like(normalized_A) * self.epsilon
        adjusted_A = self.robust_control(normalized_A, disturbance)

        x = F.silu(F.conv1d(input=x, weight=self.conv1d_x.weight, bias=self.conv1d_x.bias, padding='same',
                            groups=self.d_inner // 2))

        z = F.conv1d(input=z, weight=self.conv1d_z.weight, bias=self.conv1d_z.bias, padding='same',
                     groups=self.d_inner // 2)
        z = F.silu(z)

        x_dbl = self.x_proj(rearrange(x, "b d l -> (b l) d"))
        dt, B, C = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        A = self.low_rank_approximation(adjusted_A, rank=rank)
        B = self.low_rank_approximation(B, rank=rank)
        C = self.low_rank_approximation(C, rank=rank)
        D = self.D.float()

        dt = rearrange(self.dt_proj(dt), "(b l) d -> b d l", l=seqlen)
        B = rearrange(B, "(b l) dstate -> b dstate l", l=seqlen).contiguous()
        C = rearrange(C, "(b l) dstate -> b dstate l", l=seqlen).contiguous()

        y = selective_scan_fn(x,
                              dt,
                              A,
                              B,
                              C,
                              D,
                              z=None,
                              delta_bias=self.dt_proj.bias.float(),
                              delta_softplus=True,
                              return_last_state=None)

        y = torch.cat([y, z], dim=1)
        y = rearrange(y, "b d l -> b l d")
        out = self.out_proj(y)
        return out

class MambaSparse(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=1, dt_rank="auto", dt_min=0.001, dt_max=0.1,
                 dt_init="random", dt_scale=1.0, dt_init_floor=1e-4, conv_bias=True, bias=False,
                 use_fast_path=True, layer_idx=None, device=None, dtype=None):
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.d_model = d_model
        self.d_state = d_model // 4 * expand
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(self.expand * self.d_model)
        self.dt_rank = math.ceil(self.d_model / 16) if dt_rank == "auto" else dt_rank
        self.use_fast_path = use_fast_path
        self.layer_idx = layer_idx

        # Linear layers for input projection and sparse representation
        self.in_proj = nn.Linear(self.d_model, self.d_inner, bias=bias, **factory_kwargs)
        self.sparse_proj = nn.Linear(self.d_inner//2, self.d_inner//2, bias=False,
                                     **factory_kwargs)  # For sparse representation
        self.x_proj = nn.Linear(self.d_inner // 2, self.dt_rank + self.d_state * 2, bias=False, **factory_kwargs)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner // 2, bias=True, **factory_kwargs)

        # Initialize dt_proj weights
        dt_init_std = self.dt_rank ** -0.5 * dt_scale
        if dt_init == "constant":
            nn.init.constant_(self.dt_proj.weight, dt_init_std)
        elif dt_init == "random":
            nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)
        else:
            raise NotImplementedError

        # Initialize dt bias
        dt = torch.exp(
            torch.rand(self.d_inner // 2, **factory_kwargs) * (math.log(dt_max) - math.log(dt_min))
            + math.log(dt_min)
        ).clamp(min=dt_init_floor)
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_proj.bias.copy_(inv_dt)

        # Initialize A matrix
        A = repeat(
            torch.arange(1, self.d_state + 1, dtype=torch.float32, device=device),
            "n -> d n",
            d=self.d_inner // 2,
        ).contiguous()
        A_log = torch.log(A)
        self.A_log = nn.Parameter(A_log)
        self.A_log._no_weight_decay = True
        self.D = nn.Parameter(torch.ones(self.d_inner // 2, device=device))
        self.D._no_weight_decay = True
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=bias, **factory_kwargs)

        # Convolution layers
        self.conv1d_x = nn.Conv1d(
            in_channels=self.d_inner // 2,
            out_channels=self.d_inner // 2,
            bias=conv_bias // 2,
            kernel_size=d_conv,
            groups=self.d_inner // 2,
            **factory_kwargs,
        )
        self.conv1d_z = nn.Conv1d(
            in_channels=self.d_inner // 2,
            out_channels=self.d_inner // 2,
            bias=conv_bias // 2,
            kernel_size=d_conv,
            groups=self.d_inner // 2,
            **factory_kwargs,
        )

        self.epsilon = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)

    def sparse_approximation(self, matrix):
        threshold = torch.max(matrix) * 0.1
        return torch.sign(matrix) * F.relu(torch.abs(matrix) - threshold)
    def sparse_regularization(self, x):
        """ Apply L1 regularization to encourage sparsity. """
        return F.l1_loss(x, torch.zeros_like(x), reduction='mean')

    def robust_control(self, A, disturbance):
        """
        Implement a simple robust control strategy.
        Here we can use a simple feedback mechanism to adjust A based on disturbance.
        """
        adjusted_A = A + disturbance
        return adjusted_A

    def forward(self, hidden_states):
        """
        hidden_states: (B, L, D)
        Returns: same shape as hidden_states
        """
        _, seqlen, _ = hidden_states.shape
        xz = self.in_proj(hidden_states)
        xz = rearrange(xz, "b l d -> b d l")
        x, z = xz.chunk(2, dim=1)

        sparse_representation = self.sparse_proj(x.permute(0, 2, 1))
        sparse_loss = self.sparse_regularization(sparse_representation)
        A = -torch.exp(self.A_log.float())
        disturbance = torch.randn_like(A) * self.epsilon
        A = self.robust_control(A, disturbance)

        x = F.silu(F.conv1d(input=x, weight=self.conv1d_x.weight, bias=self.conv1d_x.bias, padding='same',
                            groups=self.d_inner // 2))

        z = F.conv1d(input=z, weight=self.conv1d_z.weight, bias=self.conv1d_z.bias, padding='same',
                     groups=self.d_inner // 2)
        z = F.silu(z)

        x_dbl = self.x_proj(rearrange(x, "b d l -> (b l) d"))
        dt, B, C = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        A = self.sparse_approximation(A)
        B = self.sparse_approximation(B)
        C = self.sparse_approximation(C)
        D = self.D.float()

        dt = rearrange(self.dt_proj(dt), "(b l) d -> b d l", l=seqlen)
        B = rearrange(B, "(b l) dstate -> b dstate l", l=seqlen).contiguous()
        C = rearrange(C, "(b l) dstate -> b dstate l", l=seqlen).contiguous()

        y = selective_scan_fn(x,
                              dt,
                              A,
                              B,
                              C,
                              D,
                              z=None,
                              delta_bias=self.dt_proj.bias.float(),
                              delta_softplus=True,
                              return_last_state=None)

        y = torch.cat([y, z], dim=1)
        y = rearrange(y, "b d l -> b l d")
        out = self.out_proj(y)

        return out, sparse_loss




class LA(nn.Module):
    def __init__(self):
        super(LA, self).__init__()
        self.avgpoolh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgpoolw = nn.AdaptiveAvgPool2d((1, None))
        self.avgpool = nn.AdaptiveAvgPool2d(1)
    def weightch(self, alpha, beta):
        param = 2
        alpha = alpha.squeeze(-1).squeeze(-1)
        beta = beta.squeeze(-1).squeeze(-1)
        b, ch = alpha.size()
        t = int(ch * torch.mean(torch.exp(beta - alpha)))
        if t <= param:
            t = param + 1
        distance = torch.norm(alpha.unsqueeze(-1) + beta.unsqueeze(1), dim=0)
        dist_n_top = torch.kthvalue(distance, t, dim=1, keepdim=True)[0]
        dist_sigma = torch.kthvalue(distance, param, dim=1, keepdim=True)[0]
        distance_truncated = distance.where(distance < dist_n_top, torch.tensor(float("inf")))
        weight = torch.exp(-(distance_truncated / dist_sigma).pow(2))
        # Symmetrically normalize the weight matrix
        sym_norm_factor = torch.sqrt(torch.sum(weight ** 2, dim=0) + torch.sum(weight ** 2, dim=1))
        sym_weight = torch.divide(weight, sym_norm_factor)
        sym_weight = (sym_weight + sym_weight.t()) / 2
        sym_weight = sym_weight.detach()
        sym_weight = torch.where(torch.isnan(sym_weight), torch.full_like(sym_weight, 0), sym_weight)
        return sym_weight

    def weightch_batch(self, alpha, beta):
        param = 2
        alpha = alpha.squeeze(-1).squeeze(-1)
        beta = beta.squeeze(-1).squeeze(-1)
        b, ch = alpha.size()
        # t = ch // 4
        t = int(ch * torch.mean(torch.exp(beta - alpha)))
        if t <= param:
            t = param + 1
        all = []
        for i in range(b):
            distance = torch.norm(alpha.unsqueeze(-1) + beta.unsqueeze(1), dim=0)
            dist_n_top = torch.kthvalue(distance, t, dim=1, keepdim=True)[0]
            dist_sigma = torch.kthvalue(distance, param, dim=1, keepdim=True)[0]
            distance_truncated = distance.where(distance < dist_n_top, torch.tensor(float("inf")).cuda())
            weight = torch.exp(-(distance_truncated / dist_sigma).pow(2))
            # Symmetrically normalize the weight matrix
            sym_norm_factor = torch.sqrt(torch.sum(weight ** 2, dim=0) + torch.sum(weight ** 2, dim=1))
            sym_weight = torch.divide(weight, sym_norm_factor)
            sym_weight = (sym_weight + sym_weight.t()) / 2
            sym_weight = sym_weight.detach()
            sym_weight = torch.where(torch.isnan(sym_weight), torch.full_like(sym_weight, 0), sym_weight)
            sym_weight = torch.diag(sym_weight)
            all.append(sym_weight.unsqueeze(0))
        sym_weights = torch.cat(all, dim=0)
        return sym_weights


    def forward(self, x):
        identity = x
        b, c, h, w = x.size()
        ch_max = torch.max(torch.max(identity, dim=-1)[0], dim=-1)[0].unsqueeze(-1).unsqueeze(-1).sigmoid()
        alpha = ch_max
        beta = 1 - alpha
        out0 = self.weightch(alpha, beta)
        eps = torch.diag(out0).unsqueeze(0).unsqueeze(-1).unsqueeze(-1)
        out_c = alpha * (1 + eps)
        out = out_c * identity
        return out


class att_sparse(nn.Module):
    def __init__(self, channel):
        super(att_sparse, self).__init__()
        self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgw = nn.AdaptiveAvgPool2d((1, None))
        self.sparse = MambaSparse(d_model=channel//2, d_state=8, d_conv=3, expand=1)
        self.conv = nn.Conv1d(channel//2, channel//2, 3, 1, 1)
        self.norm = nn.BatchNorm1d(channel//2)

    def forward(self, x):
        identity = x
        b, c, h, w = x.size()
        inp = torch.cat([self.avgh(x).squeeze(-1), self.avgw(x).squeeze(-2)], dim=-1)
        inpx, inpy = torch.split(inp, [c // 2, c // 2], dim=1)
        inpx = self.conv(inpx)
        oupx = self.norm(inpx)
        q = self.sparse(inpy.permute(0, 2, 1))
        oupy = q[0].permute(0, 2, 1)
        s_loss = q[1]
        oup = torch.cat([oupx, oupy], dim=1)
        ouph, oupw = torch.split(oup, [h, w], dim=-1)
        ouph = ouph.unsqueeze(-1).sigmoid()
        oupw = oupw.unsqueeze(-2).sigmoid()
        oup = oupw * ouph
        return identity * oup, s_loss

class att_low(nn.Module):
    def __init__(self, channel):
        super(att_low, self).__init__()
        self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgw = nn.AdaptiveAvgPool2d((1, None))
        self.conv = nn.Conv1d(channel // 2, channel // 2, 3, 1, 1)
        self.norm = nn.BatchNorm1d(channel // 2)
        self.low = MambaLow(d_model=channel // 2, d_state=8, d_conv=3, expand=1)

    def forward(self, x):
        identity = x
        b, c, h, w = x.size()
        inp = torch.cat([self.avgh(x).squeeze(-1), self.avgw(x).squeeze(-2)], dim=-1)
        # print(inp.shape)
        inpx, inpy = torch.split(inp, [c // 2, c // 2], dim=1)
        # print(inpx.shape)
        inpx = self.conv(inpx)
        oupx = self.norm(inpx)
        oupy = self.low(inpy.permute(0, 2, 1)).permute(0, 2, 1)
        oup = torch.cat([oupx, oupy], dim=1)
        ouph, oupw = torch.split(oup, [h, w], dim=-1)
        ouph = ouph.unsqueeze(-1).sigmoid()
        oupw = oupw.unsqueeze(-2).sigmoid()
        oup = oupw * ouph
        return identity * oup
    
    




# class BasicBlock_new_low_sparse(nn.Module):
#     expansion = 1

#     def __init__(self, in_channel, out_channel, if_att=True, if_low=False, stride=1, downsample=None, **kwargs):
#         super(BasicBlock_new_low_sparse, self).__init__()
#         self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
#                                kernel_size=3, stride=stride, padding=1, bias=False, dilation=1)
#         self.bn1 = nn.BatchNorm2d(out_channel)
#         self.relu = nn.ReLU()
#         self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
#                                kernel_size=3, stride=1, padding=1, bias=False)
#         self.bn2 = nn.BatchNorm2d(out_channel)
#         self.downsample = downsample
#         self.sparse = att_sparse(out_channel)
#         self.low = att_low(out_channel)
#         self.if_att = if_att
#         self.if_low = if_low

#     def forward(self, x):
#         b, c, h, w = x.size()
#         identity = x
#         if self.downsample is not None:
#             identity = self.downsample(x)
#         out = self.conv1(x)
#         out = self.bn1(out)
#         out = self.relu(out)
#         out = self.conv2(out)
#         out = self.bn2(out)
#         if self.if_att == True:
#             if self.if_low == True:
#                 out = self.low(out)
#             else:
#                 out, _ = self.sparse(out)
#         out += identity
#         out = self.relu(out)
#         return out














class VSSM(nn.Module):
    def __init__(
            self, 
            # basic dims =============
            d_model=32, 
            d_state=16, 
            ssm_ratio=1.0, 
            offset_range_factor=1.0,
            dt_rank="auto", 
            # ==================
            dropout=0.0,
            # ==================
            force_fp32=True,
            **kwargs):
        # d_conv=3, bias=False, dt_init="random", dt_scale=1.0, dt_init_floor=1e-4, dt_min=0.001, dt_max=0.1, k_group=4, device=None, dtype=None,
        act_layer = nn.SiLU
        dt_min = 0.001
        dt_max = 0.1
        dt_init = "random"
        dt_scale = 1.0
        dt_init_floor = 1e-4
        bias = False
        conv_bias = True
        d_conv = 3
        k_group = 4
        factory_kwargs = {"device": None, "dtype": None}
        super().__init__()
        d_inner = int(ssm_ratio * d_model)
        dt_rank = math.ceil(d_model / 16) if dt_rank == "auto" else dt_rank

        self.kernel = 16
        self.offset_range_factor=1.0


        # in proj ============================
        self.in_proj = nn.Linear(d_model, d_inner * 2, bias=bias, **factory_kwargs)
        self.act: nn.Module = act_layer()
        self.conv2d = nn.Conv2d(
            in_channels=d_inner,
            out_channels=d_inner,
            groups=d_inner,
            bias=True,
            kernel_size=d_conv,
            padding=(d_conv - 1) // 2,
            **factory_kwargs,
        )



        # x proj ========================
        self.x_proj = [
            nn.Linear(d_inner, (dt_rank + d_state * 2), bias=False)
            for _ in range(k_group)
        ]

        self.x_proj_weight = nn.Parameter(torch.stack([t.weight for t in self.x_proj], dim=0))  # (K, N, inner)
        del self.x_proj


        # dt proj, A, D ============================

        dt_projs = [
            self.dt_init(dt_rank, d_inner, dt_scale, dt_init, dt_min, dt_max, dt_init_floor)
            for _ in range(k_group)
        ]
        self.dt_projs_weight = nn.Parameter(torch.stack([t.weight for t in dt_projs], dim=0))  # (K, inner, rank)
        self.dt_projs_bias = nn.Parameter(torch.stack([t.bias for t in dt_projs], dim=0))  # (K, inner)
        del dt_projs


        # print(self.dt_projs_bias.shape)


        self.A_logs = self.A_log_init(d_state, d_inner, copies=k_group, merge=True) # (K * D, N)

        self.Ds = self.D_init(d_inner, copies=k_group, merge=True)  # (K * D)

        # out proj =======================================
        self.out_norm = nn.LayerNorm(d_inner)
        self.out_proj = nn.Linear(d_inner, d_model, bias=bias)
        self.dropout = nn.Dropout(dropout) if dropout > 0. else nn.Identity()



        self.conv_offset = nn.Sequential(
            nn.Conv2d(d_inner, d_inner, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(d_inner),
            nn.GELU(),
            nn.Conv2d(d_inner, 2, 1, 1, 0, bias=False)
        )
        self.no_off = False
        self.n_groups=1
        self.n_group_channels=d_inner



    def forward(self, x: torch.Tensor, seq=False, force_fp32=True, **kwargs):
        # x.shape=(B, C, H, W)
        # offset = self.conv_offset()
        x = rearrange(x, "b c h w -> b h w c")


        x = self.in_proj(x)
        x, z = x.chunk(2, dim=-1)  # (b, h, w, d)
        z = self.act(z)
        x = rearrange(x, "b h w d -> b d h w")
        # x = self.conv2d(x) # (b, d, h, w)
        # x = self.act(x)

        B, C, H, W = x.size()
        dtype, device = x.dtype, x.device

        offset = self.conv_offset(x).contiguous()  # B * g 2 Hg Wg
        Hk, Wk = offset.size(2), offset.size(3)



        if self.offset_range_factor >= 0 and not self.no_off:
            offset_range = torch.tensor(
                [1.0 / (Hk - 1.0), 1.0 / (Wk - 1.0)], device=device).reshape(1, 2, 1, 1)
            offset = offset.tanh().mul(offset_range).mul(self.offset_range_factor)

        offset = einops.rearrange(offset, 'b p h w -> b h w p')
        reference = self._get_ref_points(Hk, Wk, B, dtype, device)

        if self.no_off:
            offset = offset.fill_(0.0)

        if self.offset_range_factor >= 0:
            pos = offset + reference
        else:
            pos = (offset + reference).clamp(-1., +1.)

        if self.no_off:
            x_sampled = F.avg_pool2d(
                x, kernel_size=self.stride, stride=self.stride)
            assert x_sampled.size(2) == Hk and x_sampled.size(
                3) == Wk, f"Size is {x_sampled.size()}"
        else:
            x_sampled = F.grid_sample(
                input=x.reshape(B * self.n_groups,
                                self.n_group_channels, H, W),
                grid=pos[..., (1, 0)],  # y, x -> x, y
                mode='bilinear', align_corners=True)  # B * g, Cg, Hg, Wg

        x = x_sampled.reshape(B, C, H, W).contiguous()
        # print(x.shape)


        x = rearrange(x, "b c (k1 h) (k2 w) -> (b k1 k2) c h w", k1=self.kernel, k2=self.kernel)





        B, D, H, W = x.shape
        D, N = self.A_logs.shape
        K, D, R = self.dt_projs_weight.shape
        L = H * W


        x_hwwh = torch.stack([x.view(B, -1, L), torch.transpose(x, dim0=2, dim1=3).contiguous().view(B, -1, L)], dim=1).view(B, 2, -1, L)

        xs = torch.cat([x_hwwh, torch.flip(x_hwwh, dims=[-1])], dim=1)  # (b, k, d, l)


        # print(xs.shape)
        # print(self.x_proj_weight.shape)
        x_dbl = torch.einsum("b k d l, k c d -> b k c l", xs, self.x_proj_weight)
        if hasattr(self, 'x_proj_bias'):
            x_dbl = x_dbl + self.x_proj_bias.view(1, K, -1, 1)
        dts, Bs, Cs = torch.split(x_dbl, [R, N, N], dim=2)
        dts = torch.einsum("b k r l, k d r -> b k d l", dts, self.dt_projs_weight)


        xs = xs.view(B, -1, L)  # (b, k * d, l)
        dts = dts.contiguous().view(B, -1, L)  # (b, k * d, l)
        Bs = Bs.contiguous()  # (b, k, d_state, l)
        Cs = Cs.contiguous()  # (b, k, d_state, l)

        As = -self.A_logs.float().exp()  # (k * d, d_state)
        Ds = self.Ds.float()  # (k * d)
        dt_projs_bias = self.dt_projs_bias.float().view(-1)  # (k * d)

        to_fp32 = lambda *args: (_a.to(torch.float32) for _a in args)

        if force_fp32:
            xs, dts, Bs, Cs = to_fp32(xs, dts, Bs, Cs)


        # print(As.shape, Bs.shape, Cs.shape, Ds.shape)

        if seq:
            out_y = []
            for i in range(4):
                yi = selective_scan_fn(
                    xs.view(B, K, -1, L)[:, i], dts.view(B, K, -1, L)[:, i],
                    As.view(K, -1, N)[i], Bs[:, i].unsqueeze(1), Cs[:, i].unsqueeze(1), Ds.view(K, -1)[i],
                    delta_bias=dt_projs_bias.view(K, -1)[i],
                    delta_softplus=True,
                ).view(B, -1, L)
                out_y.append(yi)
            out_y = torch.stack(out_y, dim=1)
        else:
            out_y = selective_scan_fn(
                xs, dts,
                As, Bs, Cs, Ds,
                delta_bias=dt_projs_bias,
                delta_softplus=True,
            ).view(B, K, -1, L)
        assert out_y.dtype == torch.float

        inv_y = torch.flip(out_y[:, 2:4], dims=[-1]).view(B, 2, -1, L)
        wh_y = torch.transpose(out_y[:, 1].view(B, -1, W, H), dim0=2, dim1=3).contiguous().view(B, -1, L)
        invwh_y = torch.transpose(inv_y[:, 1].view(B, -1, W, H), dim0=2, dim1=3).contiguous().view(B, -1, L)
        y = out_y[:, 0] + inv_y[:, 0] + wh_y + invwh_y

        y = y.transpose(dim0=1, dim1=2).contiguous()  # (B, L, C)
        y = self.out_norm(y).view(B, H, W, -1)

        y = rearrange(y, "(b k1 k2) h w c-> b (k1 h) (k2 w) c", k1=self.kernel, k2=self.kernel)

        y = y * z
        out = self.dropout(self.out_proj(y))
        out = rearrange(out, "b h w c -> b c h w")
        # print(out.shape)

        # out = rearrange(out, "(b k1 k2) c h w-> b c (k1 h) (k2 w)", k1=self.kernel, k2=self.kernel)

        # print(out.shape)
        return out
    
    @torch.no_grad()
    def _get_ref_points(self, H_key, W_key, B, dtype, device):

        ref_y, ref_x = torch.meshgrid(
            torch.linspace(0.5, H_key - 0.5, H_key,
                           dtype=dtype, device=device),
            torch.linspace(0.5, W_key - 0.5, W_key,
                           dtype=dtype, device=device),
            indexing='ij'
        )
        ref = torch.stack((ref_y, ref_x), -1)
        ref[..., 1].div_(W_key - 1.0).mul_(2.0).sub_(1.0)
        ref[..., 0].div_(H_key - 1.0).mul_(2.0).sub_(1.0)
        ref = ref[None, ...].expand(
            B * self.n_groups, -1, -1, -1)  # B * g H W 2

        return ref
    
    def A_log_init(self, d_state, d_inner, copies=-1, device=None, merge=True):
        # S4D real initialization
        A = torch.arange(1, d_state + 1, dtype=torch.float32, device=device).view(1, -1).repeat(d_inner, 1).contiguous()
        A_log = torch.log(A)  # Keep A_log in fp32
        if copies > 0:
            A_log = A_log[None].repeat(copies, 1, 1).contiguous()
            if merge:
                A_log = A_log.flatten(0, 1)
        A_log = nn.Parameter(A_log)
        A_log._no_weight_decay = True
        return A_log
    
    def D_init(self, d_inner, copies=-1, device=None, merge=True):
        # D "skip" parameter
        D = torch.ones(d_inner, device=device)
        if copies > 0:
            D = D[None].repeat(copies, 1).contiguous()
            if merge:
                D = D.flatten(0, 1)
        D = nn.Parameter(D)  # Keep in fp32
        D._no_weight_decay = True
        return D
    





    def dt_init(self, dt_rank, d_inner, dt_scale=1.0, dt_init="random", dt_min=0.001, dt_max=0.1, dt_init_floor=1e-4):
        dt_proj = nn.Linear(dt_rank, d_inner, bias=True)

         # Initialize special dt projection to preserve variance at initialization
        dt_init_std = dt_rank ** -0.5 * dt_scale
        if dt_init == "constant":
            nn.init.constant_(dt_proj.weight, dt_init_std)
        elif dt_init == "random":
            nn.init.uniform_(dt_proj.weight, -dt_init_std, dt_init_std)
        else:
            raise NotImplementedError

        # Initialize dt bias so that F.softplus(dt_bias) is between dt_min and dt_max
        dt = torch.exp(
            torch.rand(d_inner) * (math.log(dt_max) - math.log(dt_min))
            + math.log(dt_min)
        ).clamp(min=dt_init_floor)
        # Inverse of softplus: https://github.com/pytorch/pytorch/issues/72759
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            dt_proj.bias.copy_(inv_dt)
        # Our initialization would set all Linear.bias to zero, need to mark this one as _no_reinit
        # dt_proj.bias._no_reinit = True

        return dt_proj
    







class Prompt_VSSM(nn.Module):
    def __init__(self, in_channel, out_channel, stride=1, prompt_size=16, ratio=0.2):
        super().__init__()
        self.prompt_size = prompt_size
        self.r = ratio
        self.vssm = VSSM(d_model=out_channel, d_state=out_channel//2, ssm_ratio=1.0, dt_rank="auto", dropout=0.0)
        self.prompt = nn.Identity()





    def forward(x):
        return x










class BasicBlock_new_low_sparse(nn.Module):
    def __init__(self, in_channel, out_channel, stride=1, downsample=None, if_VMamba=False, **kwargs):
        super(BasicBlock_new_low_sparse, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False, dilation=1)
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.downsample = downsample
        # self.sparse = att_sparse(out_channel)
        # self.low = att_low(out_channel)
        # self.if_att = if_att
        # self.if_low = if_low
        # self.spatial_mamba = nn.Identity()
        self.if_VMamba = if_VMamba
        if if_VMamba:
            self.Vmamba = VSSM(d_model=out_channel, d_state=out_channel//2, ssm_ratio=1.0, dt_rank="auto", dropout=0.0)


    def forward(self, x):
        b, c, h, w = x.size()
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        # if self.if_att == True:
        #     if self.if_low == True:
        #         out = self.low(out)
        #     else:
        #         out, _ = self.sparse(out)
        if self.if_VMamba:
            out = self.Vmamba(out)
        out += identity
        out = self.relu(out)
        return out










class PCAMamba(nn.Module):
    def __init__(self, stage_num=3, slayers=1, llayers=1, mlayers=1, channel=32, mode='train'):
        super(PCAMamba, self).__init__()
        self.stage_num = stage_num
        self.decos = nn.ModuleList()
        self.mode = mode
        for _ in range(stage_num):
            self.decos.append(DecompositionModule(slayers=slayers, llayers=llayers,
                                                  mlayers=mlayers, channel=channel))
        # 迭代循环初始化参数
        for m in self.modules():
            # 也可以判断是否为conv2d，使用相应的初始化方式
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_normal_(m.weight)
                # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, D):
        B = D
        T = torch.zeros(D.shape).to(D.device)
        
        for i in range(self.stage_num):
            D, B, T = self.decos[i](D, B, T)
        if self.mode == 'train':
            return D, B, T
        else:
            return T








class DecompositionModule(nn.Module):
    def __init__(self, slayers=1, llayers=1, mlayers=1, channel=32):
        super(DecompositionModule, self).__init__()
        self.lowrank = LowrankModule(channel=channel, layers=llayers)
        self.sparse = SparseModule(channel=channel, layers=slayers)
        self.merge = MergeModule(channel=channel, layers=mlayers)

    def forward(self, D, B, T):
        B = self.lowrank(D, B, T)
        T = self.sparse(D, B, T)
        D = self.merge(D, B, T)
        return D, B, T


class LowrankModule(nn.Module):
    def __init__(self, channel=32, layers=3):
        super(LowrankModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
        # self.p2 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p3 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p4 = BasicBlock_new_low_sparse(channel, channel, if_att=False)

        for i in range(layers):
            self.p1.append(nn.Conv2d(channel, channel, kernel_size=3, padding=1, stride=1))
            self.p1.append(nn.BatchNorm2d(channel))
            self.p1.append(nn.ReLU(True))

        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.a = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)


    def forward(self, D, B, T):
        x = (D - T + B) / 2
        out = self.p1(x)
        # out = self.p2(out)
        # out = self.p3(out)
        # out = self.p4(out)
        out = self.p5(out) * self.a + x
        return out
    






class SparseModule(nn.Module):
    def __init__(self, channel=32, layers=2) -> object:
        super(SparseModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
        
        for i in range(layers):
            self.p1.append(nn.Conv2d(channel, channel, kernel_size=3, padding=1, stride=1))
            self.p1.append(nn.BatchNorm2d(channel))
            self.p1.append(nn.ReLU(True))

        
        self.p2 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p3 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p4 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.epsilon = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)
        # self.la = LA()
    def forward(self, D, B, T):
        x = T + D - B
        out = self.p1(x)
        # out = self.la(out)
        out = self.p2(out)
        # out = self.p3(out)
        # out = self.p4(out)
        out = self.p5(out)
        out = x - out * self.epsilon
        return out
    



class MergeModule(nn.Module):
    def __init__(self, channel=32, layers=3):
        super(MergeModule, self).__init__()
        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
        # for i in range(layers):
        #     self.p1.append(nn.Conv2d(channel, channel, kernel_size=3, padding=1, stride=1))
        #     self.p1.append(nn.BatchNorm2d(channel))
        #     self.p1.append(nn.ReLU(True))
        self.p2 = nn.Conv2d(channel, channel, 3, 1, 1)
        self.p3 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.d = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)

    def forward(self, D, B, T):
        x = B + T
        out = self.p1(x)
        out = self.p2(out)
        out = self.p3(out)
        out = D + out * self.d

        return out


if __name__ == '__main__':
    # 创建模型实例
    import thop
    # model = LSDSSM(stage_num=3, slayers=1, llayers=1, mlayers=1, channel=32, mode='train')
    # model = VSSM()
    # model = PCAMamba(stage_num=3, slayers=1, llayers=1, mlayers=1, channel=32, mode='train')
    model = PCAMamba(stage_num=3, channel=32, mode='train')
    model = model.cuda()
    inputs = torch.rand(1, 1, 256, 256).cuda()
    output = model(inputs)
    flops, params = thop.profile(model, (inputs,))
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')




