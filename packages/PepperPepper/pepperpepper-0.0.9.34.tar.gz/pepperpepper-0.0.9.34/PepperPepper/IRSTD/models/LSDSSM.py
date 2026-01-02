import torch
import torch.nn as nn
from einops import rearrange, repeat
import math
import torch.nn.functional as F
from mamba_ssm.ops.selective_scan_interface import selective_scan_fn

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
        inpx, inpy = torch.split(inp, [c // 2, c // 2], dim=1)
        inpx = self.conv(inpx)
        oupx = self.norm(inpx)
        oupy = self.low(inpy.permute(0, 2, 1)).permute(0, 2, 1)
        oup = torch.cat([oupx, oupy], dim=1)
        ouph, oupw = torch.split(oup, [h, w], dim=-1)
        ouph = ouph.unsqueeze(-1).sigmoid()
        oupw = oupw.unsqueeze(-2).sigmoid()
        oup = oupw * ouph
        return identity * oup
    
    
class BasicBlock_new_low_sparse(nn.Module):
    expansion = 1

    def __init__(self, in_channel, out_channel, if_att=True, if_low=False, stride=1, downsample=None, **kwargs):
        super(BasicBlock_new_low_sparse, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False, dilation=1)
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.downsample = downsample
        self.sparse = att_sparse(out_channel)
        self.low = att_low(out_channel)
        self.if_att = if_att
        self.if_low = if_low
        # self.p2 = BasicBlock_new_low_sparse(channel, channel, if_att=False)

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
        if self.if_att == True:
            if self.if_low == True:
                out = self.low(out)
            else:
                out, _ = self.sparse(out)
        out += identity
        out = self.relu(out)
        return out


class LSDSSM(nn.Module):
    def __init__(self, stage_num=3, slayers=1, llayers=1, mlayers=1, channel=32, mode='train'):
        super(LSDSSM, self).__init__()
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
        # T = torch.zeros(D.shape).to(D.device)
        # B = D

        b, c, _, _ = D.size()
        k = 200
        low = []
        for i in range(b):
            img = D[i].squeeze(0)
            U, S, Vt = torch.linalg.svd(img)
            S_k = torch.zeros_like(S)
            S_k[:k] = S[:k]
            out_low = U @ torch.diag(S_k) @ Vt
            low.append(out_low.unsqueeze(0).unsqueeze(0))
        B = torch.cat(low, dim=0)
        T = D - B


        for i in range(self.stage_num):
            D, B, T = self.decos[i](D, B, T)
        # if self.mode == 'train':
        #     return D, B, T
        # else:
        #     return T
        
        if self.training:
            return D, B, T
        else:
            return T



class DecompositionModule(object):
    pass
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
    def __init__(self, channel=32, layers=1):
        super(LowrankModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
        self.p2 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p3 = BasicBlock_new_low_sparse(channel, channel, if_low=True)
        self.p4 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.a = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)


    def forward(self, D, B, T):
        x = (D - T + B) / 2
        out = self.p1(x)
        out = self.p2(out)
        out = self.p3(out)
        out = self.p4(out)
        out = self.p5(out) * self.a + x
        return out

class SparseModule(nn.Module):
    def __init__(self, channel=32, layers=1) -> object:
        super(SparseModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                 nn.ReLU(True))
        self.p2 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p3 = BasicBlock_new_low_sparse(channel, channel)
        self.p4 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.epsilon = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)
        self.la = LA()
    def forward(self, D, B, T):
        x = T + D - B
        out = self.p1(x)
        out = self.la(out)
        out = self.p2(out)
        out = self.p3(out)
        out = self.p4(out)
        out = self.p5(out)
        out = x - out * self.epsilon
        return out
    

    

class MergeModule(nn.Module):
    def __init__(self, channel=32, layers=1):
        super(MergeModule, self).__init__()
        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
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


import time
if __name__ == '__main__':
    # 创建模型实例

    import thop
    model = LSDSSM(stage_num=3, slayers=3, llayers=3, mlayers=2, channel=32, mode='train')
    model = model.cuda()
    inputs = torch.rand(1, 1, 256, 256).cuda()
    output = model(inputs)
    flops, params = thop.profile(model, (inputs,))
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')


    # 计算推理时间
    start_time = time.time()  # 记录开始时间
    with torch.no_grad():  # 不计算梯度
        for _ in range(100):  # 进行100次推理以获得更稳定的平均时间
            model(inputs)
    end_time = time.time()  # 记录结束时间
    inference_time = (end_time - start_time) / 100  # 计算平均推理时间

    print("Average Inference Time = {:.5f} seconds".format(inference_time))



