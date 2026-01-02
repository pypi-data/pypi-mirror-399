import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.parameter import Parameter
from torch.nn import init
from torch.nn.modules.utils import _triple, _reverse_repeat_tuple, _pair
import math


class SDifferenceConv2D(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros'):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = _pair(kernel_size)
        self.stride = _pair(stride)
        self.padding = _pair(padding)
        self.dilation = _pair(dilation)
        self.groups = groups
        self.padding_mode = padding_mode


        if isinstance(self.padding, str):
            self._reversed_padding_repeated_twice = [0, 0] * len(kernel_size)
            if padding == 'same':
                for d, k, i in zip(dilation, kernel_size, range(len(kernel_size) -1, -1)):
                    total_padding = d * (k - 1)
                    left_pad = total_padding // 2
                    self._reversed_padding_repeated_twice[2 * i] = left_pad
                    self._reversed_padding_repeated_twice[2 * i + 1] = (total_padding - left_pad)
        else:
            self._reversed_padding_repeated_twice = _reverse_repeat_tuple(self.padding, 2)

        self.weight = Parameter(torch.empty(out_channels, in_channels // groups, *self.kernel_size)) # [out_channels, in_channels, 3, 3]
        
        if bias:
            self.bias = Parameter(torch.empty(out_channels))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()




    def reset_parameters(self):
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            init.uniform_(self.bias, -bound, bound)




    def forward(self, input):
        grad_weight = -self.weight.clone()
        hw = self.weight.size(-1)
        grad_weight[:, :, int((hw-1)/2), int((hw-1)/2)] = torch.sum(self.weight, dim=[2,3])

        if self.padding_mode != "zeros":
            return F.conv2d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
                            grad_weight, self.bias, self.stride, _pair(0), self.dilation, self.groups)
        return F.conv2d(input, grad_weight, self.bias, self.stride, self.padding, self.dilation, self.groups)


class SDifferenceConv3D(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros'):
        super(SDifferenceConv3D, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = _triple(kernel_size)       # kernel_size*kernel_size [3,3]
        self.stride = _triple(stride)
        self.padding = _triple(padding)
        self.dilation = _triple(dilation)
        self.groups = groups
        self.padding_mode = padding_mode
        if isinstance(self.padding, str):
            self._reversed_padding_repeated_twice = [0, 0] * len(kernel_size)
            if padding == 'same':
                for d, k, i in zip(dilation, kernel_size, range(len(kernel_size) - 1, -1, -1)):
                    total_padding = d * (k - 1)
                    left_pad = total_padding // 2
                    self._reversed_padding_repeated_twice[2 * i] = left_pad
                    self._reversed_padding_repeated_twice[2 * i + 1] = (total_padding - left_pad)
        else:
            self._reversed_padding_repeated_twice = _reverse_repeat_tuple(self.padding, 2)
        self.weight = Parameter(torch.empty(out_channels, in_channels // groups, *self.kernel_size))  # [out_channels, in_channels, 3, 3, 3]
        if bias:
            self.bias = Parameter(torch.empty(out_channels))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()


    def reset_parameters(self):
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            init.uniform_(self.bias, -bound, bound)


    def forward(self, input):
        grad_weight = -self.weight.clone()
        hw = self.weight.size(-1)
        grad_weight[:, :, :, int((hw-1)/2), int((hw-1)/2)] = torch.sum(self.weight, dim=[3,4])

        if self.padding_mode != "zeros":
            return F.conv3d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
                            grad_weight, self.bias, self.stride, _triple(0), self.dilation, self.groups)
        return F.conv3d(input, grad_weight, self.bias, self.stride, self.padding, self.dilation, self.groups)



class SD_Resblock(nn.Module):
    def __init__(self, in_channels, out_channels, stride):
        super().__init__()
        self.conv1 = SDifferenceConv2D(in_channels=in_channels, out_channels=out_channels,  kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)


        if stride !=1 or out_channels != in_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )
        else:
            self.shortcut = nn.Identity()

    def forward(self, x):
        residule = x
        # if self.shortcut is not None:
        residual = self.shortcut(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out += residual
        out = self.relu(out)

        return out












from thop import profile


if __name__ == '__main__':
    model = SDifferenceConv2D(in_channels=1, out_channels=32, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=True, padding_mode='zeros').cuda()
    inputs = torch.rand(1, 1, 256, 256).cuda()
    output = model(inputs)
    print(output.shape)
    if torch.isnan(output).any():
        print(f"NaN detected at layer output: {output}")
        # break

    flops, params = profile(model, (inputs,))

    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')