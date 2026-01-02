# PoincareBall PCANet
import geoopt
import torch
from torch import nn 
from einops import rearrange, repeat
import math
import torch.nn.functional as F

class PBPCA(nn.Module):
    def __init__(self, stage_num=3, slayers=3, llayers=3, mlayers=3, channel=32, mode='train'):
        super(PBPCA, self).__init__()
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
    def __init__(self, channel=32, layers=1):
        super(LowrankModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                                nn.BatchNorm2d(channel),
                                nn.ReLU(True))
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.a = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)


    def forward(self, D, B, T):
        x = (D - T + B) / 2
        out = self.p1(x)
        out = self.p5(out) * self.a + x
        return out

class SparseModule(nn.Module):
    def __init__(self, channel=32, layers=1) -> object:
        super(SparseModule, self).__init__()

        self.p1 = nn.Sequential(nn.Conv2d(1, channel, kernel_size=3, padding=1, stride=1),
                 nn.ReLU(True))
        self.p5 = nn.Conv2d(channel, 1, kernel_size=3, padding=1, stride=1)
        self.epsilon = nn.Parameter(torch.Tensor([0.01]), requires_grad=True)
        # self.la = LA()
    def forward(self, D, B, T):
        x = T + D - B
        out = self.p1(x)
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


if __name__ == '__main__':
    # 创建模型实例

    import thop
    model = PBPCA(stage_num=3, slayers=1, llayers=1, mlayers=1, channel=32, mode='train')
    model = model.cuda()
    inputs = torch.rand(1, 1, 256, 256).cuda()
    output = model(inputs)
    flops, params = thop.profile(model, (inputs,))
    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')



