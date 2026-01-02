import torch
import torch.nn.functional as F
import torch.nn as nn
from PepperPepper.layers import ResBlock



class Encoder(nn.Module):
    def __init__(self, in_channels, out_channels, stride = 1):
        super(Encoder, self).__init__()
        self.en_layers1 = ResBlock(in_channels, out_channels, stride)
        self.en_layers2 = ResBlock(out_channels, out_channels, stride)
        self.en_layers3 = ResBlock(out_channels, out_channels, stride)
        self.pool = nn.MaxPool2d(2, 2)
        self.up = nn.UpsamplingBilinear2d(scale_factor=2)
        self.de_layers3 = ResBlock(out_channels, out_channels, stride)
        self.de_layers2 = ResBlock(out_channels, out_channels, stride)
        self.de_layers1 = ResBlock(out_channels, out_channels, stride)

        self.fuse1 = nn.Conv2d(out_channels * 2, out_channels, kernel_size=1, stride=1)
        self.fuse2 = nn.Conv2d(out_channels * 2, out_channels, kernel_size=1, stride=1)
        self.fuse3 = nn.Conv2d(out_channels * 2, out_channels, kernel_size=1, stride=1)

    def forward(self, x):
        e1 = self.en_layers1(x)
        e2 = self.en_layers2(self.pool(e1))
        e3 = self.en_layers3(self.pool(e2))

        d3 = self.de_layers3(e3)

        d2 = self.de_layers2(self.fuse2(torch.cat((e2, self.up(d3)), 1)))

        d1 = self.de_layers1(self.fuse1(torch.cat((e1, self.up(d2)), 1)))

        return d3, d2, d1









class IRMOTSNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=1, dims=32):
        super(IRMOTSNet, self).__init__()
        self.encoder = Encoder(in_channels, dims)

        self.out1 = nn.Conv2d(dims, 1, kernel_size=1, stride=1)
        self.conv2 = nn.Sequential(
            nn.Conv2d(dims, 1, kernel_size=1, stride=1),
            nn.UpsamplingBilinear2d(scale_factor=2)
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(dims, 1, kernel_size=1, stride=1),
            nn.UpsamplingBilinear2d(scale_factor=4)
        )

        self.conv = nn.Conv2d(3, 1, kernel_size=1, stride=1)






    def forward(self, x):
        if x.size(1) == 1:
            x = x.repeat(1, 3, 1, 1)
        p3, p2, p1 = self.encoder(x)
        out = self.out1(p1)

        if self.training:
            out2 = self.conv2(p2)
            out3 = self.conv3(p3)
            out_all = self.conv(torch.cat((out, out2, out3), 1))
            return out_all, out

        return out


from thop import profile


if __name__ == '__main__':
    model = IRMOTSNet().cuda()
    x = torch.randn(1, 3, 256, 256).cuda()
    # print(output.shape)
    flops, params = profile(model, (x,))

    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')



