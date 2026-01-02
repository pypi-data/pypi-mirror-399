import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange
from PepperPepper.layers.cf import SnycTwinSSM
import math


class PAGLattention(nn.Module):
    def __init__(self, dim, feature_size, Patchnum):
        super().__init__()
        # assert feature_size%Patchnum == 0
        self.feature_size = feature_size
        self.patch_num = Patchnum
        self.dim = dim
        # self.avg_h = nn.AdaptiveAvgPool2d((None, Patchnum))
        # self.avg_w = nn.AdaptiveAvgPool2d((Patchnum, None))
        self.max_pool = nn.AdaptiveAvgPool2d((Patchnum, Patchnum))

        # self.projQ1 = nn.Conv2d(dim, dim, 1, 1)
        # self.projK1 = nn.Conv2d(dim, dim, 1, 1)
        # self.projV1 = nn.Conv2d(dim, dim, 1, 1)
        #
        #
        # self.projQ2 = nn.Conv2d(dim, dim, 1, 1)
        # self.projK2 = nn.Conv2d(dim, dim, 1, 1)
        # self.projV2 = nn.Conv2d(dim, dim, 1, 1)

        # self.scale = torch.sqrt(torch.tensor(Patchnum).float())
        # self.avg_last = nn.AdaptiveAvgPool2d((None, 1))
        #
        # self.stssm = SnycTwinSSM(d_model=dim // 2, d_state=8, d_conv=3, expand=1)

        # self.outConv = nn.Sequential(
        #     nn.Conv2d(dim, 1, 3, 1, 1),
        #     nn.Sigmoid()
        # )

        self.q = nn.Conv2d(dim, dim, kernel_size=3, stride=1, padding=1, bias=False)
        self.k = nn.Conv2d(dim, dim, kernel_size=3, stride=1, padding=1, bias=False)
        self.v = nn.Conv2d(dim, dim, kernel_size=3, stride=1, padding=1, bias=False)
        self.project_out = nn.Conv2d(dim, dim, kernel_size=1, bias=False)
        self.KV_size = dim
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, e, PAM_out):
        identity = e
        b , c, h, w = e.shape
        max_e = self.max_pool(e)
        q = self.q(max_e)
        k = self.k(PAM_out)
        v = self.v(e)

        q = rearrange(q, 'b c h w -> b c (h w)')
        k = rearrange(k, 'b c h w -> b c (h w)')
        v = rearrange(v, 'b c h w -> b c (h w)')

        q = torch.nn.functional.normalize(q, dim=-1)
        k = torch.nn.functional.normalize(k, dim=-1)

        attn = (q @ k.transpose(-2, -1)) / math.sqrt(self.KV_size)

        attention_probs = self.softmax(attn)


        out = (attention_probs @ v)
        out = rearrange(out, 'b c (h w) -> b c h w', h=h, w=w)
        out = self.project_out(out) + e
        return out



from thop import profile

if __name__ == '__main__':
    model = PAGLattention(32, 256 ,16).cuda()
    feature = torch.ones(1, 32, 256, 256).cuda()
    PAM_out = torch.randn(1, 32, 16, 16).cuda()
    flops, params = profile(model, (feature, PAM_out))
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')




