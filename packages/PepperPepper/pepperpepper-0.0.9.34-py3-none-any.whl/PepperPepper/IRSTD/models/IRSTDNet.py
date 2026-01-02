from PepperPepper.environment import torch, nn, math, trunc_normal_, profile
from PepperPepper.IRSTD.models import SCTransNet, MiM, get_SCTrans_config, MLPNet
from PepperPepper.IRSTD.tools.loss import SoftLoULoss
from PepperPepper.layers.MultiWaveFusion import DWT_2D

from PepperPepper.IRSTD.models.ACM import ASKCResUNet
from PepperPepper.IRSTD.models.ALCNet import ASKCResNetFPN
from PepperPepper.IRSTD.models.DNANet import DNANet
from PepperPepper.IRSTD.models.AGPCNet import get_segmentation_model
from PepperPepper.IRSTD.models.UIUNet import UIUNET
from PepperPepper.IRSTD.models.MSHNet import MSHNet
from PepperPepper.IRSTD.models.LSDSSM import LSDSSM
from PepperPepper.IRSTD.models.DRPCANet import DRPCANet






class DWTModule(nn.Module):
    def __init__(self, wave = 'haar'):
        super(DWTModule, self).__init__()
        self.wave = wave
        self.dwt = DWT_2D(wave)


    def forward(self, x, filters):
        e1_dwt = self.dwt(x)
        e1_ll, e1_lh, e1_hl, e1_hh = e1_dwt.split(filters, 1)  # torch.Size([1, 32, 16, 16])
        # e1_highf = torch.cat((e1_lh, e1_hl, e1_hh), 1)
        e1_highf = [e1_lh, e1_hl, e1_hh]
        return e1_ll , e1_highf











class IRSTDNet(nn.Module):
    def __init__(self, model_name, model=None):
        super(IRSTDNet, self).__init__()
        self.model_name = model_name
        self.cal_loss = nn.BCEWithLogitsLoss()
        self.softiou = SoftLoULoss()
        self.model = None
        self.dwt = DWTModule()


        if model_name == 'MiM':
            self.model = MiM()
        elif model_name == 'ACM':
            self.model = ASKCResUNet()
        elif model_name == 'ALCNet':
            self.model = ASKCResNetFPN()
        elif model_name == 'DNANet':
            self.model = DNANet()
        elif model_name == 'AGPCNet':
            self.model = get_segmentation_model('AGPCNet')
        elif model_name == 'UIUNet':
            self.model = UIUNET()
        elif model_name == 'MSHNet':
            self.model = MSHNet()
        elif model_name == 'LSDSSMs':
            self.model = LSDSSM(stage_num=3, slayers=3, llayers=3, mlayers=2, channel=32, mode='train')
        elif model_name == 'DRPCA-Net':
            self.model = DRPCANet()
        elif model_name == 'SCTransNet':
            config = get_SCTrans_config()
            self.model = SCTransNet(config, mode='train', deepsuper=True)
        elif model_name == 'MLPNet':
            self.model = MLPNet()
        else:
            print('This model is not supported. Please you munually set the model for trainning!!')
            self.model = None
            # raise NotImplementedError

        if model is not None:
            self.model = model

        self.apply(self._init_weights)

    def forward(self, img):
        return self.model(img)

    def loss(self, preds, gt_masks):
        # preds = torch.sigmoid(preds)
        # gt_masks = torch.sigmoid(gt_masks)
        if isinstance(preds, list):
            loss_total = 0
            for i in range(len(preds)):
                pred = preds[i]
                # gt_mask = gt_masks[i]
                loss = self.cal_loss(pred, gt_masks) + self.softiou(pred, gt_masks)
                loss_total = loss_total + loss
            losss = loss_total / len(preds)
            loss_total = (losss + self.cal_loss(preds[-1], gt_masks) + self.softiou(preds[-1], gt_masks))/2
            return loss_total

        elif isinstance(preds, tuple):
            loss_total = 0
            for i in range(len(preds)):
                pred = preds[i]
                loss = self.cal_loss(pred, gt_masks) + self.softiou(pred, gt_masks)
                loss_total = loss_total + loss
            losss = loss_total / len(preds)
            loss_total = (losss + self.cal_loss(preds[-1], gt_masks) + self.softiou(preds[-1], gt_masks)) / 2
            return loss_total
        else:
            loss = self.cal_loss(preds, gt_masks) + self.softiou(preds, gt_masks)
            return loss





    def loss_wave(self, preds, gt_masks):
        mask = gt_masks
        if isinstance(preds, list) or isinstance(preds, tuple):
            loss_total = 0.
            for i in range(len(preds) - 1):
                mask, _ = self.dwt(mask, 1)
                mask = (mask > 0).to(preds[-1].dtype)

                pred = preds[i]
                loss = self.cal_loss(pred, mask) + self.softiou(pred, mask)
                loss_total = loss_total + loss
            losss = loss_total / len(preds)
            loss_total = (losss + self.cal_loss(preds[-1], gt_masks) + self.softiou(preds[-1], gt_masks)) / 2
            return loss_total


        else:
            loss = self.cal_loss(preds, gt_masks) + self.softiou(preds, gt_masks)
            return loss







    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        if isinstance(m, nn.Conv2d):
            fan_out = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
            fan_out //= m.groups
            m.weight.data.normal_(0, math.sqrt(2.0 / fan_out))
            if m.bias is not None:
                m.bias.data.zero_()
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)


if __name__ == '__main__':
    # config_vit = get_SCTrans_config()
    # # model = SCTransNet(config_vit, mode='train', deepsuper=True)
    # model = model

    net = IRSTDNet(model_name='MLPNet').cuda().eval()
    inputs = torch.rand(1, 1, 256, 256).cuda()
    output = net(inputs)
    flops, params = profile(net, (inputs,))


    print(output.shape)

    print("-" * 50)
    print('FLOPs = ' + str(flops / 1000 ** 3) + ' G')
    print('Params = ' + str(params / 1000 ** 2) + ' M')