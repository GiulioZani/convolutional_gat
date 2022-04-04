import argparse
from .unet_parts import *
from .unet_parts_depthwise_separable import DoubleConvDS, UpDS, DownDS
from .layers import CBAM
import pytorch_lightning as pl
from .regression_lightning import Precip_regression_base
import torch as t
import ipdb


class CGAT(Precip_regression_base):
    def __init__(self, hparams):
        super(CGAT, self).__init__(hparams=hparams)
        pass

    def forward(self, x):
        pass


class UNet(Precip_regression_base):
    def __init__(self, hparams):
        super(UNet, self).__init__(hparams=hparams)
        self.n_channels = hparams.n_channels
        self.n_classes = hparams.n_classes
        self.bilinear = hparams.bilinear

        self.inc = DoubleConv(self.n_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        factor = 2 if self.bilinear else 1
        self.down4 = Down(512, 1024 // factor)
        self.up1 = Up(1024, 512 // factor, self.bilinear)
        self.up2 = Up(512, 256 // factor, self.bilinear)
        self.up3 = Up(256, 128 // factor, self.bilinear)
        self.up4 = Up(128, 64, self.bilinear)

        self.outc = OutConv(64, self.n_classes)

    def forward(self, x):
        print(f"heyyyy {x.shape=}")
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class UNet_Attention(Precip_regression_base):
    def __init__(self, hparams):
        super(UNet_Attention, self).__init__(hparams=hparams)
        self.n_channels = hparams.n_channels
        self.n_classes = hparams.n_classes
        self.bilinear = hparams.bilinear
        reduction_ratio = hparams.reduction_ratio

        self.inc = DoubleConv(self.n_channels, 64)
        self.cbam1 = CBAM(64, reduction_ratio=reduction_ratio)
        self.down1 = Down(64, 128)
        self.cbam2 = CBAM(128, reduction_ratio=reduction_ratio)
        self.down2 = Down(128, 256)
        self.cbam3 = CBAM(256, reduction_ratio=reduction_ratio)
        self.down3 = Down(256, 512)
        self.cbam4 = CBAM(512, reduction_ratio=reduction_ratio)
        factor = 2 if self.bilinear else 1
        self.down4 = Down(512, 1024 // factor)
        self.cbam5 = CBAM(1024 // factor, reduction_ratio=reduction_ratio)
        self.up1 = Up(1024, 512 // factor, self.bilinear)
        self.up2 = Up(512, 256 // factor, self.bilinear)
        self.up3 = Up(256, 128 // factor, self.bilinear)
        self.up4 = Up(128, 64, self.bilinear)

        self.outc = OutConv(64, self.n_classes)

    def forward(self, x):
        x1 = self.inc(x)
        x1Att = self.cbam1(x1)
        x2 = self.down1(x1)
        x2Att = self.cbam2(x2)
        x3 = self.down2(x2)
        x3Att = self.cbam3(x3)
        x4 = self.down3(x3)
        x4Att = self.cbam4(x4)
        x5 = self.down4(x4)
        x5Att = self.cbam5(x5)
        x = self.up1(x5Att, x4Att)
        x = self.up2(x, x3Att)
        x = self.up3(x, x2Att)
        x = self.up4(x, x1Att)
        logits = self.outc(x)
        return logits


class UNetDS(Precip_regression_base):
    def __init__(self, hparams):
        super(UNetDS, self).__init__(hparams=hparams)
        self.n_channels = hparams.n_channels
        self.n_classes = hparams.n_classes
        self.bilinear = hparams.bilinear
        kernels_per_layer = hparams.kernels_per_layer

        self.inc = DoubleConvDS(
            self.n_channels, 64, kernels_per_layer=kernels_per_layer
        )
        self.down1 = DownDS(64, 128, kernels_per_layer=kernels_per_layer)
        self.down2 = DownDS(128, 256, kernels_per_layer=kernels_per_layer)
        self.down3 = DownDS(256, 512, kernels_per_layer=kernels_per_layer)
        factor = 2 if self.bilinear else 1
        self.down4 = DownDS(512, 1024 // factor, kernels_per_layer=kernels_per_layer)
        self.up1 = UpDS(
            1024, 512 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up2 = UpDS(
            512, 256 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up3 = UpDS(
            256, 128 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up4 = UpDS(128, 64, self.bilinear, kernels_per_layer=kernels_per_layer)

        self.outc = OutConv(64, self.n_classes)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class UNetDS_Attention(Precip_regression_base):
    def __init__(self, hparams):
        super(UNetDS_Attention, self).__init__(hparams=hparams)
        self.n_channels = hparams.n_channels
        self.n_classes = hparams.n_classes
        self.bilinear = hparams.bilinear
        reduction_ratio = hparams.reduction_ratio
        kernels_per_layer = hparams.kernels_per_layer

        self.inc = DoubleConvDS(
            self.n_channels, 64, kernels_per_layer=kernels_per_layer
        )
        self.cbam1 = CBAM(64, reduction_ratio=reduction_ratio)
        self.down1 = DownDS(64, 128, kernels_per_layer=kernels_per_layer)
        self.cbam2 = CBAM(128, reduction_ratio=reduction_ratio)
        self.down2 = DownDS(128, 256, kernels_per_layer=kernels_per_layer)
        self.cbam3 = CBAM(256, reduction_ratio=reduction_ratio)
        self.down3 = DownDS(256, 512, kernels_per_layer=kernels_per_layer)
        self.cbam4 = CBAM(512, reduction_ratio=reduction_ratio)
        factor = 2 if self.bilinear else 1
        self.down4 = DownDS(512, 1024 // factor, kernels_per_layer=kernels_per_layer)
        self.cbam5 = CBAM(1024 // factor, reduction_ratio=reduction_ratio)
        self.up1 = UpDS(
            1024, 512 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up2 = UpDS(
            512, 256 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up3 = UpDS(
            256, 128 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up4 = UpDS(128, 64, self.bilinear, kernels_per_layer=kernels_per_layer)

        self.outc = OutConv(64, self.n_classes)

    def single_forward(self, x):
        x1 = self.inc(x)
        x1Att = self.cbam1(x1)
        x2 = self.down1(x1)
        x2Att = self.cbam2(x2)
        x3 = self.down2(x2)
        x3Att = self.cbam3(x3)
        x4 = self.down3(x3)
        x4Att = self.cbam4(x4)
        x5 = self.down4(x4)
        x5Att = self.cbam5(x5)
        x = self.up1(x5Att, x4Att)
        x = self.up2(x, x3Att)
        x = self.up3(x, x2Att)
        x = self.up4(x, x1Att)
        logits = self.outc(x)
        return logits

    def forward(self, xs):
        if len(xs.shape) > 4:
            """
            x = xs.permute(0, 4, 3, 1, 2)
            b, v, time, w, h = x.shape
            x = x.reshape(b*v, time, w, h)
            rand_indices = t.randperm(x.shape[0])
            x = x[rand_indices, :, :, :]
            logits = self.single_forward(x).view(b, v, time, w, h).permute(0, 3, 4, 2, 1) # permute(2, 3, 1, 0)
            """
            xp = xs.permute(4, 0, 3, 1, 2)
            x_slices = ((xp[0], xp[1]), (xp[2], xp[3]), (xp[4], xp[5]))
            x = t.cat(tuple(t.cat(slice, dim=2) for slice in x_slices), dim=-1)
            pred = self.single_forward(x)
            vslices = tuple(pred[:, :, :, i : i + 80] for i in range(3))
            pred_slices = tuple(
                (vslice[:, :, 0:80], vslice[:, :, 80:160]) for vslice in vslices
            )
            logits = t.stack(
                (
                    pred_slices[0][0],
                    pred_slices[0][1],
                    pred_slices[1][0],
                    pred_slices[1][1],
                    pred_slices[2][0],
                    pred_slices[2][1],
                )
            ).permute(1, 3, 4, 2, 0)

        else:
            logits = self.single_forward(xs.permute(0, 3, 1, 2))
        """
        preds = tuple(
            self.single_forward(xs[:, :, :, :, i].permute(0, 3, 1, 2)).permute(
                0, 2, 3, 1
            )
            for i in range(xs.shape[-1])
        )
        logits = t.stack(preds, dim=-1)
        """
        return logits


class UNetDS_Attention_4CBAMs(Precip_regression_base):
    def __init__(self, hparams):
        super(UNetDS_Attention_4CBAMs, self).__init__(hparams=hparams)
        self.n_channels = hparams.n_channels
        self.n_classes = hparams.n_classes
        self.bilinear = hparams.bilinear
        reduction_ratio = hparams.reduction_ratio
        kernels_per_layer = hparams.kernels_per_layer

        self.inc = DoubleConvDS(
            self.n_channels, 64, kernels_per_layer=kernels_per_layer
        )
        self.cbam1 = CBAM(64, reduction_ratio=reduction_ratio)
        self.down1 = DownDS(64, 128, kernels_per_layer=kernels_per_layer)
        self.cbam2 = CBAM(128, reduction_ratio=reduction_ratio)
        self.down2 = DownDS(128, 256, kernels_per_layer=kernels_per_layer)
        self.cbam3 = CBAM(256, reduction_ratio=reduction_ratio)
        self.down3 = DownDS(256, 512, kernels_per_layer=kernels_per_layer)
        self.cbam4 = CBAM(512, reduction_ratio=reduction_ratio)
        factor = 2 if self.bilinear else 1
        self.down4 = DownDS(512, 1024 // factor, kernels_per_layer=kernels_per_layer)
        self.up1 = UpDS(
            1024, 512 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up2 = UpDS(
            512, 256 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up3 = UpDS(
            256, 128 // factor, self.bilinear, kernels_per_layer=kernels_per_layer,
        )
        self.up4 = UpDS(128, 64, self.bilinear, kernels_per_layer=kernels_per_layer)

        self.outc = OutConv(64, self.n_classes)

    def forward(self, x):
        print(f"heyyyy {x.shape=}")
        x1 = self.inc(x)
        x1Att = self.cbam1(x1)
        x2 = self.down1(x1)
        x2Att = self.cbam2(x2)
        x3 = self.down2(x2)
        x3Att = self.cbam3(x3)
        x4 = self.down3(x3)
        x4Att = self.cbam4(x4)
        x5 = self.down4(x4)
        x = self.up1(x5, x4Att)
        x = self.up2(x, x3Att)
        x = self.up3(x, x2Att)
        x = self.up4(x, x1Att)
        logits = self.outc(x)
        return logits


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser = Precip_regression_base.add_model_specific_args(parser)
    parser = pl.Trainer.add_argparse_args(parser)

    parser.add_argument(
        "--dataset_folder",
        default="../data/precipitation/RAD_NL25_RAC_5min_train_test_2016-2019.h5",
        type=str,
    )
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=150)

    args = parser.parse_args()

    net = UNetDS_Attention(hparams=args)

    trainer = pl.Trainer(
        gpus=1,
        fast_dev_run=True,
        weights_summary=None,
        default_save_path="../lightning/precip",
        max_epochs=args.epochs,
    )
    trainer.fit(net)
