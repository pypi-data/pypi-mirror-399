import math
import torch
import torch.nn as nn
from typing import List
from torch.nn import init
import torch.nn.functional as F
from einops import rearrange
from PepperPepper.layers.KAN import KANLinear



class SProb(nn.Module):
    def __init__(self, d_model=32, num_head=2, seqlen=256):
        super().__init__()
        self.d_model = 32
        self.num_head = num_head
        self.hidden_dim = d_model // num_head
        self.seqlen = seqlen
        QK_heads: List[nn.Module] = []

        for i in range(num_head):
            # QK_heads.append(nn.Linear(seqlen, seqlen))
            QK_heads.append(nn.Conv1d(self.hidden_dim, self.hidden_dim, kernel_size=3, padding=1, stride=1))
            # QK_heads.append(KANLinear(seqlen, seqlen))
        
        self.QK_heads = nn.Sequential(*QK_heads)


    def forward(self, input):
        b, d, l = input.shape
        value = input.contiguous()
        value = value.view(b, self.num_head, self.hidden_dim, l)

        qkv = torch.zeros([b, self.num_head, self.hidden_dim, l]).to(input.device)
        for i in range(self.num_head):
            qkv[:, i, :, :] = self.QK_heads[i](value[:, i, :, :].contiguous())
        
        qkv = qkv.view(b, -1, l)
        out = qkv
        return out



class SProbBlock(nn.Module):
    def __init__(self, channels=32, shape=(256, 256)):
        super().__init__()
        self.channels = channels
        self.hseqlen = shape[0]
        self.wseqlen = shape[1]

        self.avgh = nn.AdaptiveAvgPool2d((None, 1))
        self.avgw = nn.AdaptiveAvgPool2d((1, None))
        self.hsprob = SProb(d_model=channels, num_head=2, seqlen=self.hseqlen)
        self.wsprob = SProb(d_model=channels, num_head=2, seqlen=self.wseqlen)


    def forward(self, x):
        identity = x
        b, c, h, w = x.size()
        x_avgh = self.avgh(x).squeeze(-1)
        x_avgw = self.avgw(x).squeeze(-2)
        x_avgh = self.hsprob(x_avgh)
        x_avgw = self.hsprob(x_avgw)
        x_avgh = x_avgh.unsqueeze(-1).sigmoid()
        x_avgw = x_avgw.unsqueeze(-2).sigmoid()
        outprob = x_avgw * x_avgw
        out = outprob * identity


        return out






if __name__ == '__main__':
    # 创建模型实例
    import thop
    # model = SProbBlock(32, 4, 256)
    model = SProbBlock()
    model = model.cuda()
    # inputs = torch.rand(1, 32, 256, 256).cuda()
    # output = model(inputs)
    x = torch.rand(1, 32, 256, 256).cuda()
    flops, params = thop.profile(model, (x, ))


    
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')






