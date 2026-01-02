import torch
import torch.nn.functional as F
import torch.nn as nn
from einops import rearrange
from einops.layers.torch import Rearrange
from PepperPepper.layers import ResBlock




class TPro(nn.Module):
    def __init__(self, d_model=8, num_head=2, seqlen=8):
        super(TPro, self).__init__()
        self.d_model = d_model
        self.num_head = num_head
        self.seqlen = seqlen
        self.k = nn.Linear(d_model, d_model * num_head)
        self.v = nn.Linear(d_model, d_model * num_head)
        self.q = nn.Linear(d_model, d_model * num_head)




    def forward(self, x):
        B, C, T, H, W = x.shape
        e = rearrange(x, 'b c t h w -> (b h w) t c')
        q = self.q(e)
        k = self.k(e)
        v = self.v(e)

        # 多头分割: C -> num_head x head_dim
        q = rearrange(q, 'b t (h d) -> b h t d', h=self.num_head)
        k = rearrange(k, 'b t (h d) -> b h t d', h=self.num_head)
        v = rearrange(v, 'b t (h d) -> b h t d', h=self.num_head)

        # 计算注意力分数 QK^T
        attn_scores = torch.einsum('bhid,bhjd->bhij', q, k)  # [(B H W), H, T, T]

        # 缩放
        attn_scores = attn_scores / (self.d_model ** 0.5)

        # 转换为注意力权重
        attn_weights = F.softmax(attn_scores, dim=-1)

        # 注意力加权求和
        attn_out = torch.einsum('bhij,bhjd->bhid', attn_weights, v)



        # 修改点：在头的维度上求和合并多头
        attn_out = attn_out.sum(dim=1)  # [(B H W), T, D]  D=head_dim



        # 恢复原始形状: [(B H W), T, C] -> [B, C, T, H, W]
        attn_out = rearrange(attn_out, '(b h w) t c -> b c t h w',
                             b=B, h=H, w=W, c=C)

        out = attn_out + x

        return out







class TSUNet(nn.Module):
    def __init__(self, in_channel=1, out_channel=1, dims=16 ,sqlen=8):
        super(TSUNet, self).__init__()
        self.pool = nn.MaxPool3d(kernel_size=(1,2,2), stride=(1,2,2))
        self.in_channel = in_channel
        self.out_channel = out_channel
        self.sqlen = sqlen
        self.dims = dims
        self.layer1 = ResBlock(in_channel, dims)
        self.layer1_prob = TPro(dims)

        self.layer1 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(in_channel, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )


        self.layer2 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(dims, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )


        self.layer3 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(dims, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )

        self.decode3 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(dims, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )

        self.decode2 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(dims, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )

        self.decode1 = nn.Sequential(
            Rearrange('b c t h w -> (b t) c h w'),
            ResBlock(dims, dims),
            Rearrange('(b t) c h w -> b c t h w', t=sqlen),
            TPro(dims)
        )



        self.fuse2 = nn.Conv3d(dims * 2, dims, kernel_size=(1,1,1), stride=(1,1,1))
        self.fuse1 = nn.Conv3d(dims * 2, dims, kernel_size=(1,1,1), stride=(1,1,1))
        self.cout = nn.Conv3d(dims, out_channel, kernel_size=(1,1,1), stride=(1,1,1))








    def forward(self, x):
        # B,C,T,H,W
        # B, C, T,H, W = x.shape
        e1 = self.layer1(x)
        e2 = self.layer2(self.pool(e1))
        e3 = self.layer3(self.pool(e2))

        d3 = self.decode3(e3)
        d3 = F.interpolate(d3, scale_factor=(1, 2, 2), mode='trilinear', align_corners=True)

        d2 = torch.cat((e2, d3), dim=1)
        d2 = self.fuse2(d2)
        d2 = self.decode2(d2)

        d2 = F.interpolate(d2, scale_factor=(1, 2, 2), mode='trilinear', align_corners=True)
        d1 = torch.cat((e1, d2), dim=1)
        d1 = self.fuse1(d1)
        d1 = self.decode1(d1)
        out = self.cout(d1)
        return out


from thop import profile


if __name__ == '__main__':
    model = TSUNet().cuda()
    x = torch.randn(1, 1, 8, 256, 256).cuda()
    # print(output.shape)
    flops, params = profile(model, (x,))

    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')
