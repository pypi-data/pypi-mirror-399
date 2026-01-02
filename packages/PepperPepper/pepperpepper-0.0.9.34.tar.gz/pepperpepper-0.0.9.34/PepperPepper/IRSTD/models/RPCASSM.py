# KAN-State Space Model- PCA
import math
from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from einops import rearrange, repeat
import einops
from mamba_ssm.ops.selective_scan_interface import selective_scan_fn
from functools import partial

try:
    from causal_conv1d import causal_conv1d_fn, causal_conv1d_update
except ImportError:
    causal_conv1d_fn, causal_conv1d_update = None, None

try:
    from mamba_ssm.ops.triton.selective_state_update import selective_state_update
except ImportError:
    selective_state_update = None



try:
    from mamba_ssm.ops.triton.layernorm import RMSNorm, layer_norm_fn, rms_norm_fn
except ImportError:
    RMSNorm, layer_norm_fn, rms_norm_fn = None, None, None
from PepperPepper.layers.KAN import KANLinear





class mamba_init:
    @staticmethod
    def dt_init(dt_rank, d_inner, dt_scale=1.0, dt_init="random", dt_min=0.001, dt_max=0.1, dt_init_floor=1e-4):
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

    @staticmethod
    def A_log_init(d_state, d_inner, copies=-1, device=None, merge=True):
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

    @staticmethod
    def D_init(d_inner, copies=-1, device=None, merge=True):
        # D "skip" parameter
        D = torch.ones(d_inner, device=device)
        if copies > 0:
            D = D[None].repeat(copies, 1).contiguous()
            if merge:
                D = D.flatten(0, 1)
        D = nn.Parameter(D)  # Keep in fp32
        D._no_weight_decay = True
        return D

    @classmethod
    def init_dt_A_D(cls, d_state, dt_rank, d_inner, dt_scale, dt_init, dt_min, dt_max, dt_init_floor, k_group=4):
        # dt proj ============================
        dt_projs = [
            cls.dt_init(dt_rank, d_inner, dt_scale, dt_init, dt_min, dt_max, dt_init_floor)
            for _ in range(k_group)
        ]
        dt_projs_weight = nn.Parameter(torch.stack([t.weight for t in dt_projs], dim=0))  # (K, inner, rank)
        dt_projs_bias = nn.Parameter(torch.stack([t.bias for t in dt_projs], dim=0))  # (K, inner)
        del dt_projs

        # A, D =======================================
        A_logs = cls.A_log_init(d_state, d_inner, copies=k_group, merge=True)  # (K * D, N)
        Ds = cls.D_init(d_inner, copies=0, merge=True)  # (K * D)
        return A_logs, Ds, dt_projs_weight, dt_projs_bias








class mask_ssm(nn.Module):
    def __init__(
        self, 
        d_model=32, 
        d_state=16, 
        ssm_ratio=1.0, 
        dt_rank="auto", 
        force_fp32=True,
        act_layer=nn.SiLU
    ):
        super().__init__()
        k_group = 4
        self.d_model = int(d_model)
        d_state = int(d_state)
        d_inner = int(ssm_ratio * d_model)
        dt_rank = int(math.ceil(self.d_model / 16) if dt_rank=="auto" else dt_rank)
        d_conv = 3
        dt_scale = 1.0
        dt_init = "constant"
        dt_min = 0.001
        dt_max = 0.1
        dt_init_floor = 1e-4

        self.d_inner = d_inner
        self.k_group = k_group
        self.topk = 0.15


        
        # x proj ============================
        self.x_proj = [
            nn.Linear(d_inner, (dt_rank + d_state * 2), bias=False)
            for _ in range(k_group)
        ]
        self.x_proj_weight = nn.Parameter(torch.stack([t.weight for t in self.x_proj], dim=0))  # (K, N, inner)
        del self.x_proj


        self.in_proj = nn.Conv2d(d_model, d_inner * 2, kernel_size=3, padding=1, stride=1)
        self.act: nn.Module = act_layer()



        # dt proj, A, D ============================
        self.A_logs, self.Ds, self.dt_projs_weight, self.dt_projs_bias = mamba_init.init_dt_A_D(
            d_state, dt_rank, d_inner, dt_scale, dt_init, dt_min, dt_max, dt_init_floor, k_group=4,
        )



        self.proj_d = nn.Sequential(
            nn.Linear(d_inner, (k_group + 1)*d_inner, bias=False),
            nn.SiLU()
        )

        self.out_norm = nn.LayerNorm(d_inner)
        self.out_proj = nn.Conv2d(d_inner, d_model, kernel_size=3, padding=1, stride=1, bias=False)

        


    def forward(self, x):
        x = self.act(self.in_proj(x))
        x, z = x.chunk(2, dim=1)
        B, D, H, W = x.shape
        max_n = int(H * W * self.topk)

        # mask generate
        mask = self.adjust_target(x)
        heartmap = F.interpolate(mask, size=(H, W), mode='nearest')

        # Dt generate
        Ds = self.proj_d(self.Ds.float())
        Ds_t, Ds_b = torch.split(Ds, [self.d_inner * self.k_group, self.d_inner], dim=0)

        out_Blist = []


        for i in range(B):
            S_heartmap = heartmap[i:i+1]    # [1, 1, H, W]
            flat = S_heartmap.view(-1)    # [H*W]
            mask_bool = flat > 0
            sel = mask_bool.nonzero(as_tuple=False).view(-1)
            
            
            # 选择topk点
            if sel.numel() > max_n:
                _, top_idx = torch.topk(flat[sel], k=max_n)
                sel = sel[top_idx]
            elif sel.numel() == 0:
                _, top_idx = torch.topk(flat, k=16)
                sel = top_idx

            # 创建输出mask
            out_mask = torch.zeros_like(flat, dtype=torch.bool, device=x.device)
            out_mask[sel] = True
            out_mask_2d = out_mask.view(H, W)  # [H, W]
            indices = out_mask_2d.nonzero(as_tuple=False)  # [N, 2]
            h_indices, w_indices = indices[:, 0], indices[:, 1]


            # 未选中的negmask
            # 3. 未选中索引
            neg_mask = torch.ones_like(flat, dtype=torch.bool, device=x.device)
            neg_mask[sel] = False
            neg_mask_2d = neg_mask.view(H, W) # [H, W]
            neg_indices = neg_mask_2d.nonzero(as_tuple=False)  # [N, 2]
            neg_h_indices, neg_w_indices = neg_indices[:, 0], neg_indices[:, 1]


            # 获取当前样本的特征
            xs = x[i]  # [C, H, W]

            # 提取行特征和列特征
            xs_row = xs[:, h_indices, w_indices]  # [C, N]

            neg_xs_row = xs[:, neg_h_indices, neg_w_indices] # [C, N]
            
            # 对于列特征，我们需要转置
            xs_t = xs.transpose(1, 2)  # [C, W, H]
            xs_col = xs_t[:, w_indices, h_indices]  # [C, N]

            # 准备输入特征 [batch, 2(行/列), N, C]
            xs_rc = torch.stack([xs_row, xs_col], dim=0)  # [2, C, N]
            xs_rc = xs_rc.unsqueeze(0)  # [1, 2, N, C]
            xs_rc = xs_rc.contiguous()

            # 通过ssm模块处理
            y_ssm = self.ssm_forward(xs_rc, Ds_t).squeeze(0) # [1, 2, C, N]
            y_D = (Ds_b.unsqueeze(1) * neg_xs_row) # [1, C, N]


            # 分离处理后的特征

            y_row_ssm = y_ssm[0, :, :]  # [C, N]
            y_col_ssm = y_ssm[1, :, :]  # [C, N]


            # 创建更新后的特征图 - 使用全零张量
            xs_t_updated = torch.zeros_like(xs)  # [C, W, H]
            
            # 将处理后的特征填入对应位置
            xs_t_updated[:, w_indices, h_indices] += y_col_ssm

            
            # 对于列特征，我们同样需要转置操作来填入
            xs_updated = xs_t_updated.transpose(1, 2)  # [C, H, W]
            xs_updated[:, h_indices, w_indices] += y_row_ssm
            xs_updated = xs_updated/2
            xs_updated[:, neg_h_indices, neg_w_indices] = y_D

            result = xs_updated.unsqueeze(0)
            out_Blist.append(result)



        out_y = torch.cat(out_Blist, dim=0)
        out_y = rearrange(out_y,'b c h w -> b h w c')
        y = self.out_norm(out_y)
        y = rearrange(y, 'b h w c -> b c h w')
        y = y * z
        out = self.out_proj(y)
        return out
    


    def adjust_target(self, x, init_thresh=0.3, step=0.05, size=16, max_num=10):
        B, C, H, W = x.shape
        density = torch.mean(x, dim=1, keepdim=True).sigmoid()
        density = F.adaptive_avg_pool2d(density, (H//size, W//size))
        device = density.device
        final_mask = torch.zeros_like(density, device=device, dtype=torch.float)
        for b in range(B):
            single_feat = density[b:b+1]
            current_thresh = init_thresh
            found = False

            while current_thresh >=0:
                mask = (single_feat > current_thresh).float()
                if mask.any():
                    # 控制mask的数量不超过10个
                    if mask.sum() > max_num:
                        values, _ = single_feat.view(-1).topk(max_num)
                        min_val = values[-1] if len(values) > 0 else current_thresh
                        mask = (single_feat >= min_val).float()

                    final_mask[b:b+1] = mask
                    found = True
                    break
                current_thresh = round(current_thresh-step, 2)

            # not find efficient region
            if not found:
                mask = (single_feat >= single_feat.max()).float()
                final_mask[b:b+1] = mask

        # print(final_mask.sum())
        return final_mask
    



    def ssm_forward(self, x, Ds_t, force_fp32=True):
        B, K2, D, L = x.shape
        K, D, R = self.dt_projs_weight.shape
        D, N = self.A_logs.shape
        selective_scan = selective_scan_fn


        xs = torch.cat([x, torch.flip(x, dims=[-1])], dim=1) # b k d n
        x_dbl = torch.einsum("b k d l, k c d -> b k c l", xs, self.x_proj_weight)

        dts, Bs, Cs = torch.split(x_dbl, [R, N, N], dim=2)
        dts = torch.einsum("b k r l, k d r -> b k d l", dts, self.dt_projs_weight)
        xs = xs.view(B, -1, L)  # (b, k * d, l)
        dts = dts.contiguous().view(B, -1, L)  # (b, k * d, l)
        Bs = Bs.contiguous()  # (b, k, d_state, l)
        Cs = Cs.contiguous()  # (b, k, d_state, l)

        As = -self.A_logs.float().exp()  # (k * d, d_state)

        dt_projs_bias = self.dt_projs_bias.float().view(-1)  # (k * d)

        to_fp32 = lambda *args: (_a.to(torch.float32) for _a in args)

        if force_fp32:
            xs, dts, Bs, Cs = to_fp32(xs, dts, Bs, Cs)


        out_y = selective_scan(
                xs, dts,
                As, Bs, Cs, Ds_t,
                delta_bias=dt_projs_bias,
                delta_softplus=True,
        ).view(B, K, -1, L)

        inv_y = torch.flip(out_y[:, 2:4], dims=[-1]).view(B, 2, -1, L)
        y = out_y[:, 0:2].view(B, 2, -1, L)
        # print(y.shape)
        # print(inv_y.shape)
        # print(out_y.shape)
        out = (y + inv_y)/2

        return out

    










class KANSSSMBlock(nn.Module):
    def __init__(
        self,
        d_model,
        d_state=16,
        d_conv=4,
        expand=1,
        dt_rank="auto",
        dt_min=0.001,
        dt_max=0.1,
        dt_init="random",
        dt_scale=1.0,
        dt_init_floor=1e-4,
        conv_bias=True,
        bias=False,
        layer_idx=None,
        device=None,
        dtype=None,
    ):  
        k_group=4
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        self.d_inner = int(self.expand * self.d_model)
        self.dt_rank = math.ceil(self.d_model / 16) if dt_rank == "auto" else dt_rank
        self.layer_idx = layer_idx

        # self.in_proj = nn.Linear(self.d_model, self.d_inner * 2, bias=bias, **factory_kwargs)

        self.in_proj = KANLinear(self.d_model, self.d_inner * 2)

        self.conv1d = nn.Conv1d(
            in_channels=self.d_inner,
            out_channels=self.d_inner,
            bias=conv_bias,
            kernel_size=d_conv,
            groups=self.d_inner,
            padding=d_conv - 1,
            **factory_kwargs,
        )

        self.activation = "silu"
        self.act = nn.SiLU()


        self.x_proj = KANLinear(self.d_inner, self.dt_rank + self.d_state * 2)

        
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=False, **factory_kwargs)


        self.dt_projs_bias = nn.Parameter(torch.ones(k_group, self.d_inner,dtype=torch.float32))  # (K, inner)




        # Initialize special dt projection to preserve variance at initialization
        dt_init_std = self.dt_rank**-0.5 * dt_scale
        if dt_init == "constant":
            nn.init.constant_(self.dt_proj.weight, dt_init_std)
        elif dt_init == "random":
            nn.init.uniform_(self.dt_proj.weight, -dt_init_std, dt_init_std)
        else:
            raise NotImplementedError
        



        # Initialize dt bias so that F.softplus(dt_bias) is between dt_min and dt_max
        dt = torch.exp(
            torch.rand(self.d_inner, **factory_kwargs) * (math.log(dt_max) - math.log(dt_min))
            + math.log(dt_min)
        ).clamp(min=dt_init_floor)
        # Inverse of softplus: https://github.com/pytorch/pytorch/issues/72759
        inv_dt = dt + torch.log(-torch.expm1(-dt))
        with torch.no_grad():
            self.dt_projs_bias.copy_(inv_dt)
        # Our initialization would set all Linear.bias to zero, need to mark this one as _no_reinit
        self.dt_projs_bias._no_reinit = True

        # S4D real initialization
        A = repeat(
            torch.arange(1, self.d_state + 1, dtype=torch.float32, device=device),
            "n -> d n",
            d=self.d_inner,
        ).contiguous()


        self.A_logs = self.A_log_init(self.d_state, self.d_inner, copies=k_group, merge=True) # (K * D, N)


        # D "skip" parameter
        self.Ds = self.D_init(self.d_inner, copies=k_group, merge=True)  # (K * D)

        # self.out_proj = nn.Linear(self.d_inner * 2, self.d_model, bias=bias, **factory_kwargs)
        # self.d_model, self.d_inner * 2
        self.out_proj = KANLinear(self.d_inner * 2, self.d_model)

    def forward(self, hidden_states, inference_params=None, force_fp32=True):
        """
        hidden_states: (B, N, L, D)
        Returns: same shape as hidden_states
        """
        batch, Num, seqlen, dim = hidden_states.shape

        conv_state, ssm_state = None, None
        if inference_params is not None:
            conv_state, ssm_state = self._get_states_from_cache(inference_params, batch)
            if inference_params.seqlen_offset > 0:
                # The states are updated inplace
                out, _, _ = self.step(hidden_states, conv_state, ssm_state)
                return out

        # We do matmul and transpose BLH -> HBL at the same time
        xz = self.in_proj(hidden_states)

        As = -torch.exp(self.A_logs.float())  # (d_inner, d_state)
        # In the backward pass we write dx and dz next to each other to avoid torch.cat

        x, z = xz.chunk(2, dim=-1)


        x = rearrange(x, 'b n l d -> (b n) d l')
        x = self.act(self.conv1d(x)[..., :seqlen])
        x = rearrange(x, '(b n) d l -> b n l d', n=Num)


        # B, N, L, D = x.shape
        # D, K = self.A_logs.shape


        xs = torch.cat([x, torch.flip(x, dims=[-2])], dim=1).contiguous()


        B, N, L, D = xs.shape
        D, K = self.A_logs.shape
        x_dbl = self.x_proj(xs)  # (B N L dt_rank+2*d_state)
        dt, Bs, Cs = torch.split(x_dbl, [self.dt_rank, self.d_state, self.d_state], dim=-1)

        # We're careful here about the layout, to avoid extra transposes.
        # We want dt to have d as the slowest moving dimension
        # and L axss the fastest moving dimension, since those are what the ssm_scan kernel expects.
        dts = self.dt_proj(dt)  # (B N L d_inner)


        xs = rearrange(xs, "b k l d -> b (k d) l").contiguous()
        dts = rearrange(dts, 'b k l d -> b (k d) l').contiguous()
        Bs = rearrange(Bs, 'b k l d -> b k d l').contiguous()
        Cs = rearrange(Cs, 'b k l d -> b k d l').contiguous()


        Ds = self.Ds.float()  # (k * d)

        dt_projs_bias = self.dt_projs_bias.float().view(-1) # (K*d_inner)

        to_fp32 = lambda *args: (_a.to(torch.float32) for _a in args)

        if force_fp32:
            xs, dts, Bs, Cs = to_fp32(xs, dts, Bs, Cs)

        # dt = self.dt_proj.weight @ dt.t()
        # dt = rearrange(dt, "b n k l-> b (n k) l", l=seqlen)
        # B = rearrange(B, "(b l) dstate -> b dstate l", l=seqlen).contiguous()
        # C = rearrange(C, "(b l) dstate -> b dstate l", l=seqlen).contiguous()
        # print(f'xs shape: {xs.shape}')
        # print(f'dts shape: {dts.shape}')
        # print(f'Bs shape: {Bs.shape}')
        # print(f'Cs shape: {Cs.shape}')
        # print(f'As shape: {As.shape}')
        # print(f'Ds shape: {Ds.shape}')


        assert self.activation in ["silu", "swish"]
        out_y = selective_scan_fn(
            xs,
            dts,
            As, Bs, Cs, Ds,
            delta_bias=dt_projs_bias.float(),
            delta_softplus=True,
        ).view(B, N, -1, L)

        # print("out_y shape:", out_y.shape)

        assert out_y.dtype == torch.float
        inv_y = torch.flip(out_y[:, 2:4], dims=[-1]).view(B, 2, -1, L)
        y = out_y[:, :2].view(B, 2, -1, L) + inv_y
        # print("y shape:", y.shape)
        # print("z shape:", z.shape)
        y = rearrange(y, "b n d l -> b n l d").contiguous()
        out = torch.cat([y, z], dim=-1)
        out = self.out_proj(out)
        # print("out shape:", out.shape)
        return out



    def step(self, hidden_states, conv_state, ssm_state):
        dtype = hidden_states.dtype
        assert hidden_states.shape[1] == 1, "Only support decoding with 1 token at a time for now"
        xz = self.in_proj(hidden_states.squeeze(1))  # (B 2D)
        x, z = xz.chunk(2, dim=-1)  # (B D)

        # Conv step
        if causal_conv1d_update is None:
            conv_state.copy_(torch.roll(conv_state, shifts=-1, dims=-1))  # Update state (B D W)
            conv_state[:, :, -1] = x
            x = torch.sum(conv_state * rearrange(self.conv1d.weight, "d 1 w -> d w"), dim=-1)  # (B D)
            if self.conv1d.bias is not None:
                x = x + self.conv1d.bias
            x = self.act(x).to(dtype=dtype)
        else:
            x = causal_conv1d_update(
                x,
                conv_state,
                rearrange(self.conv1d.weight, "d 1 w -> d w"),
                self.conv1d.bias,
                self.activation,
            )

        x_db = self.x_proj(x)  # (B dt_rank+2*d_state)
        dt, B, C = torch.split(x_db, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        # Don't add dt_bias here
        dt = F.linear(dt, self.dt_proj.weight)  # (B d_inner)
        A = -torch.exp(self.A_log.float())  # (d_inner, d_state)

        # SSM step
        if selective_state_update is None:
            # Discretize A and B
            dt = F.softplus(dt + self.dt_proj.bias.to(dtype=dt.dtype))
            dA = torch.exp(torch.einsum("bd,dn->bdn", dt, A))
            dB = torch.einsum("bd,bn->bdn", dt, B)
            ssm_state.copy_(ssm_state * dA + rearrange(x, "b d -> b d 1") * dB)
            y = torch.einsum("bdn,bn->bd", ssm_state.to(dtype), C)
            y = y + self.D.to(dtype) * x
            y = y * self.act(z)  # (B D)
        else:
            y = selective_state_update(
                ssm_state, x, dt, A, B, C, self.D, z=z, dt_bias=self.dt_proj.bias, dt_softplus=True
            )

        out = self.out_proj(y)

        print("out shape:", out.shape)
        return out.unsqueeze(1), conv_state, ssm_state

    def allocate_inference_cache(self, batch_size, max_seqlen, dtype=None, **kwargs):
        device = self.out_proj.weight.device
        conv_dtype = self.conv1d.weight.dtype if dtype is None else dtype
        conv_state = torch.zeros(
            batch_size, self.d_model * self.expand, self.d_conv, device=device, dtype=conv_dtype
        )
        ssm_dtype = self.dt_proj.weight.dtype if dtype is None else dtype
        # ssm_dtype = torch.float32
        ssm_state = torch.zeros(
            batch_size, self.d_model * self.expand, self.d_state, device=device, dtype=ssm_dtype
        )
        return conv_state, ssm_state
    
    
    def _get_states_from_cache(self, inference_params, batch_size, initialize_states=False):
        assert self.layer_idx is not None
        if self.layer_idx not in inference_params.key_value_memory_dict:
            batch_shape = (batch_size,)
            conv_state = torch.zeros(
                batch_size,
                self.d_model * self.expand,
                self.d_conv,
                device=self.conv1d.weight.device,
                dtype=self.conv1d.weight.dtype,
            )
            ssm_state = torch.zeros(
                batch_size,
                self.d_model * self.expand,
                self.d_state,
                device=self.dt_proj.weight.device,
                dtype=self.dt_proj.weight.dtype,
                # dtype=torch.float32,
            )
            inference_params.key_value_memory_dict[self.layer_idx] = (conv_state, ssm_state)
        else:
            conv_state, ssm_state = inference_params.key_value_memory_dict[self.layer_idx]
            # TODO: What if batch size changes between generation, and we reuse the same states?
            if initialize_states:
                conv_state.zero_()
                ssm_state.zero_()
        return conv_state, ssm_state



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






class KSB_low(nn.Module):
    def __init__(self, channel):
        super().__init__()
        self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgw = nn.AdaptiveAvgPool2d((1, None))
        self.conv1 = nn.Conv1d(channel, channel, kernel_size=3, padding=1, stride=1)
        self.bn1 = nn.BatchNorm1d(channel)
        self.act = nn.SELU()
        self.ksb = KANSSSMBlock(d_model=channel, d_state=channel//4)

    def forward(self, x):
        identity = x
        b, c, h, w = x.size()

        h_avg = self.avgh(x).squeeze(-1)
        w_avg = self.avgw(x).squeeze(-2)

        # print("h_avg shape:", h_avg.shape)
        # print("w_avg shape:", w_avg.shape)

        outh = self.act(self.bn1(self.conv1(h_avg)))
        outw = self.act(self.bn1(self.conv1(w_avg)))

        outhw = torch.stack([outh, outw], dim=1).contiguous()
        outhw = rearrange(outhw, 'b n d l -> b n l d').contiguous()
        outhw = rearrange(self.ksb(outhw), 'b n l d -> b n d l').contiguous()
        outh, outw = outhw[:,0], outhw[:,1]
        outh = outh.unsqueeze(-1).sigmoid()
        outw = outw.unsqueeze(-2).sigmoid()
        # print("outhw shape:", outhw.shape)
        outs = outw * outh
        return identity * outs








class Deformable_Sample(nn.Module):
    def __init__(
        self, 
        in_channels=32, 
        out_channels=32, 
        kernel_size=3, 
        stride=1,
        offset_range_factor=1.0,
        dilation=1
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.offset_range_factor=offset_range_factor
        self.dilation = dilation

        pad_size=kernel_size//2 if kernel_size!=stride else 0


        self.proj_x = nn.Conv2d(
            in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1
        )

        self.conv_offset = nn.Sequential(
            nn.Conv2d(out_channels, out_channels, kernel_size, stride, padding=pad_size, groups=out_channels),
            nn.LazyBatchNorm2d(),
            nn.GELU(),
            nn.Conv2d(out_channels, 2, 1, 1, 0, bias=False)
        )
        

    

    def forward(self, x):
        B, C, H, W = x.shape
        dtype, device = x.dtype, x.device

        out = self.proj_x(x)

        offset = self.conv_offset(out).contiguous() # B 2 Hg Wg

        Hk, Wk = offset.size(2), offset.size(3)

        if self.offset_range_factor >= 0:
            offset_range = torch.tensor(
                [1.0 / (Hk - 1.0), 1.0 / (Wk - 1.0)], device=device).reshape(1, 2, 1, 1)
            offset = offset.tanh().mul(offset_range).mul(self.offset_range_factor)


        offset = einops.rearrange(offset, 'b p h w -> b h w p')
        reference = self._get_ref_points(Hk, Wk, B, dtype, device)

        if self.offset_range_factor >= 0:
            pos = offset + reference
        else:
            pos = (offset + reference).clamp(-1., +1.)

        x_sampled = F.grid_sample(
            input=x, grid=pos[..., (1, 0)], mode='bilinear', align_corners=True
        )

        return x_sampled

    
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
        ref = ref[None, ...].expand( B, -1, -1, -1)  # B H W 2

        return ref
    




    







class Sparse_SSM(nn.Module):
    def __init__(
        self, 
        in_channels=32, 
        out_channels=32, 
        kernel_size=3, 
        stride=1,
        offset_range_factor=1.0,
        dilation=1,
        topk=0.1
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.offset_range_factor=offset_range_factor
        self.dilation = dilation
        self.topk = topk

        
        self.DFSample = Deformable_Sample(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            offset_range_factor=offset_range_factor,
            dilation=dilation
        )


        # self.kanssm = KANSSSMBlock(d_model=out_channels, d_state=out_channels//4)
        self.sparsessm = mask_ssm(d_model=out_channels, d_state=out_channels//2)


    def forward(self, x):
        identity = x
        B, C, H, W = x.shape
        x_sampled = self.DFSample(x)  # 假设返回 [B, C, H, W]
        out = self.sparsessm(x_sampled).sigmoid() * identity
        return out








class BasicBlock(nn.Module):
    def __init__(self, in_channel, out_channel, stride=1, if_KSB_low=False, if_sparse_ssm=False, **kwargs):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False, dilation=1)
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.LeakyReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)

        self.if_KSB_low = if_KSB_low
        self.if_sparse_ssm = if_sparse_ssm
        if self.if_KSB_low:
            self.ksb_low = KSB_low(out_channel)
        if self.if_sparse_ssm:
            self.sparse_ssm = Sparse_SSM(out_channel, out_channel)


    def forward(self, x):
        b, c, h, w = x.size()
        identity = x
        # if self.downsample is not None:
        #     identity = self.downsample(x)
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        # if self.if_sparse_ssm:
        #     mask = adjust_target(out)

        out = self.bn2(out)
        if self.if_KSB_low:
            out = self.ksb_low(out)
        if self.if_sparse_ssm:
            out = self.sparse_ssm(out)
        out += identity
        out = self.relu(out)
        return out
    




# from torch.nn import 
class TOPKSSMBlockSC(nn.Module):
    def __init__(self, channel=32, topk=0.15):
        super().__init__()
        self.topk = topk


    def forward(self, x):
        B, C, H, W = x.shape
        max_n = int(H * W * self.topk)
        out_Blist = []
        heartmap = torch.mean(x,  dim=1, keepdim=True)

        for i in range(B):
            S_heartmap = heartmap[i].unsqueeze(0) # 1(B) 1(C) H W
            # print(S_heartmap.shape)

            flat = S_heartmap.view(-1)
            # print(flat.shape)
            mask = flat > 0
            # sel = S_heartmap[mask]
            # 1. 先在原始空间拿到所有 True 的索引
            sel = mask.nonzero(as_tuple=False).view(-1)

            # 2. 如果太多，再 top-k
            if sel.numel() > max_n:
                _, top_idx = torch.topk(flat[sel], k=max_n)
                sel = sel[top_idx]
            elif sel.numel() == 0:
                _, top_idx = torch.topk(flat, k=16)
                sel = top_idx


            # 3. 一次性写回原始空间
            out_mask = torch.zeros_like(flat, dtype=torch.bool).to(x.device)
            out_mask[sel] = True
            out_mask = out_mask.view(H, W)

            # print(out_mask.shape)

            # 获取选中位置的二维坐标
            indices = out_mask.nonzero(as_tuple=False)
            h_indices, w_indices = indices[:, 0], indices[:, 1]
            xs = x[i]  # C H W
            xs_row = xs[:, h_indices, w_indices]  # C N
            
            # 对于列特征，我们需要转置图像
            xs_t = xs.transpose(1, 2)  # C W H
            xs_col = xs_t[:, w_indices, h_indices]  # C N

            xs_rc = torch.stack([xs_row, xs_col], dim=0).unsqueeze(0).contiguous()
            xs_rc = rearrange(xs_rc, 'b n d l -> b n l d').contiguous()
            xs_rc = self.ssm(xs_rc)
            xs_c = xs_rc[:, 1]  # 获取处理后的列特征
            
            # 将处理后的列特征重塑为 [C, N]
            # xs_c_processed = xs_c.squeeze(0).permute(1, 0)  # 从 [1, N, C] -> [N, C] -> [C, N]
            xs_c_processed = rearrange(xs_c, 'b n d -> b d n')
            
            # 将处理后的列特征写回转置后的特征图
            xs_t_updated = xs_t.clone()
            xs_t_updated[:, w_indices, h_indices] = xs_c_processed[0]
            
            # 将转置后的特征图转回原始形状
            xs_updated = xs_t_updated.transpose(1, 2)  # C H W
            
            # 从更新后的特征图中提取行特征
            xs_col_updated = xs_updated[:, h_indices, w_indices].unsqueeze(0)  # B C N

            xs_row_updated = rearrange(xs_rc[:, 0], 'b n d -> b d n')
            # print(xs_row_updated.shape)
            # print('xs_col_updated shape', xs_col_updated.shape)
            
            # 融合行特征和处理后的列特征
            xs_post = xs_row_updated + xs_col_updated
            # print(xs_post.shape)
            # print(xs)
            # print(xs_row.shape)
            # print('Q shape', Q.shape)
            # print('K shape', K.shape)
            # print('V shape', V.shape)
            # q, k, v
            # out = self.sca(Q, K, V)
            out_Blist.append(out)

        out = torch.cat(out_Blist, dim=0)
        return out
    





class SparsePromptSSM(nn.Module):
    def __init__(self, channel=32):
        super().__init__()
        self.topkssm = TOPKSSMBlockSC(channel=channel)


    def forward(self, T):
        out = self.topkssm(T)
        return out










class KASSMPCA(nn.Module):
    def __init__(self, stage_num=3, slayers=1, llayers=1, mlayers=2, channel=32, mode='train'):
        super(KASSMPCA, self).__init__()
        self.stage_num = stage_num
        self.decos = nn.ModuleList()
        self.mode = mode
        for _ in range(stage_num):
            self.decos.append(DecompositionModule(slayers=slayers, llayers=llayers,
                                                  mlayers=mlayers, channel=channel))
        # 迭代循环初始化参数
        for m in self.modules():
            # 也可以判断是否为cooutnv2d，使用相应的初始化方式
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_normal_(m.weight)
                # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, D):
        T_list = []

        B = D
        T = torch.zeros(D.shape).to(D.device)
        
        for i in range(self.stage_num):
            B, T = self.decos[i](B, T)
            T_list.append(T)

        if self.training:
            return B, T, T_list
        else:
            return T














class DecompositionModule(nn.Module):
    def __init__(self, slayers=1, llayers=1, mlayers=1, channel=32):
        super(DecompositionModule, self).__init__()
        self.lowrank = LowrankModule(channel=channel, layers=llayers)
        self.sparse = SparseModule(channel=channel, layers=slayers)
        # self.merge = MergeModule(channel=channel, layers=mlayers)

    def forward(self, B, T):
        B = self.lowrank(B, T)
        T = self.sparse(B, T)
        # D = self.merge(D, B, T)
        return B, T
    












class LowrankModule(nn.Module):
    def __init__(self, channel=32, layers=1):
        super(LowrankModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.LeakyReLU(True))
                                
        # self.p2 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p3 = BasicBlock_new_low_sparse(channel, channel, if_VMamba=True)
        # self.p4 = BasicBlock_new_low_sparse(channel, channel, if_att=False)
        self.p2 = BasicBlock(channel, channel, stride=1, if_KSB_low=False)
        self.p3 = BasicBlock(channel, channel, stride=1, if_KSB_low=True)
        self.p4 = BasicBlock(channel, channel, stride=1, if_KSB_low=False)

        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.a = nn.Parameter(torch.Tensor([0.08]), requires_grad=True)


    def forward(self, B, T):
        # print(D.shape)
        # print(T.shape)
        # print(B.shape)
        x = (- T + B) / 2
        out = self.p1(x)
        out = self.p2(out)
        out = self.p3(out)
        out = self.p4(out)
        out = self.p5(out) * self.a + x
        return out








from PepperPepper.IRSTD.layers.SDifferenceConv import SD_Resblock, SDifferenceConv2D
from PepperPepper.IRSTD.layers.SProb import SProbBlock, SProb



class DFSQEProb(nn.Module):
    def __init__(self, in_channels=32, out_channels=32, stride=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, stride=stride, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU()
        )

        self.dfconv = nn.Sequential(
            SDifferenceConv2D(in_channels=out_channels, out_channels=out_channels,  kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm2d(out_channels)
        )

        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=True),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.shortcut = nn.Identity()

        self.relu = nn.LeakyReLU(True)



    def forward(self, x):
        identity = self.shortcut(x)
        out = self.conv(x)
        out = self.dfconv(out)
        out = self.relu(out + identity)
        return out











class SparseModule(nn.Module):
    def __init__(self, channel=32, layers=1) -> object:
        super(SparseModule, self).__init__()
        self.p1 = nn.Sequential(
            nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1), 
            nn.BatchNorm2d(channel), 
            nn.LeakyReLU(True)
        )

        for i in range(layers):
            self.p1.append(nn.Conv2d(channel, channel, kernel_size=3, padding=1, stride=1))
            # self.p1.append(nn.BatchNorm2d(channel))
            self.p1.append(nn.LeakyReLU(True))

        
        self.p2 = DFSQEProb(in_channels=channel, out_channels=channel, stride=1)
        self.p3 = BasicBlock(in_channel=channel, out_channel=channel, stride=1, if_KSB_low=False, if_sparse_ssm=True)
        self.p4 = BasicBlock(in_channel=channel, out_channel=channel, stride=1, if_KSB_low=False, if_sparse_ssm=False)
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.epsilon = nn.Parameter(torch.Tensor([0.08]), requires_grad=True)
        # self.la = LA()
        




    def forward(self, B, T):
        x = (T - B)/2
        out = self.p1(x)
        out = self.p2(out)
        out = self.p3(out)
        out = self.p4(out)
        # out = self.PR(out)
        # out = self.SMSSM(out)
        out = self.p5(out)
        out = x + out * self.epsilon
        return out
    













    
class MergeModule(nn.Module):
    def __init__(self, channel=32, layers=1):
        super(MergeModule, self).__init__()
        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.LeakyReLU(True))
        for i in range(layers):
            self.p1.append(nn.Conv2d(channel, channel, kernel_size=3, padding=1, stride=1))
            self.p1.append(nn.BatchNorm2d(channel))
            self.p1.append(nn.LeakyReLU(True))


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







class AxisMean(nn.Module):
    def __init__(self, ):
        super().__init__()
        self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgw = nn.AdaptiveAvgPool2d((1, None))

    def forward(self, x):
        b, c, h, w = x.size()
        x_max = x.max()
        x_min = x.min()
        x = (x - x_min) / (x_max - x_min + 1e-8)
        h_avg = self.avgh(x).squeeze(-1)
        w_avg = self.avgw(x).squeeze(-2)
        return h_avg, w_avg
    


    

class AxisMax(nn.Module):
    def __init__(self, ):
        super().__init__()
        # self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        # self.avgw = nn.AdaptiveAvgPool2d((1, None))

        self.maxh = nn.AdaptiveMaxPool2d((None, 1))
        self.maxw = nn.AdaptiveMaxPool2d((1, None))

    def forward(self, x):
        b, c, h, w = x.size()
        x_max = x.max()
        x_min = x.min()
        x = (x - x_min) / (x_max - x_min + 1e-8)
        h_max = self.maxh(x).squeeze(-1)
        w_max = self.maxw(x).squeeze(-2)
        return h_max, w_max




class AxisMin(nn.Module):
    def __init__(self, ):
        super().__init__()
        # self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        # self.avgw = nn.AdaptiveAvgPool2d((1, None))

        self.maxh = nn.AdaptiveMaxPool2d((None, 1))
        self.maxw = nn.AdaptiveMaxPool2d((1, None))

        # self.minh = nn.AdaptiveMinPool2d((None, 1))
        # self.minw = nn.AdaptiveMinPool2d((1, None))

    def forward(self, x):
        b, c, h, w = x.size()
        x_max = x.max()
        x_min = x.min()
        x = (x - x_min) / (x_max - x_min + 1e-8)
        # h_min = self.minh(x).squeeze(-1)
        # w_min = self.minw(x).squeeze(-2)


        h_min = self.maxh(-x).squeeze(-1) * -1
        w_min = self.maxw(-x).squeeze(-2) * -1

        return h_min, w_min











if __name__ == '__main__':
    # 创建模型实例
    import thop
    model = KASSMPCA(stage_num=3, channel=32, mode='train')
    # model = mask_ssm()
    model = model.cuda()
    T = torch.rand(1, 1, 256, 256).cuda()

    flops, params = thop.profile(model, (T, ))
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')





