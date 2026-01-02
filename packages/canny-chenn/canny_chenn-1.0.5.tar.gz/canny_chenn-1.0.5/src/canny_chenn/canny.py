import math

import torch as t
from torch import Tensor, nn


class Canny(nn.Module):
    selection_ids: Tensor

    def __init__(
        self,
        thresh_lo: float = 0.1,
        thresh_hi: float = 0.2,
        sobel_k: int = 5,
        gauss_k: int = 5,
        gauss_sigma: float = 0.1,
    ) -> None:
        super().__init__()

        # self.thresh_lo: float, self.thresh_hi: float = thresh_lo, thresh_hi
        self.thresh_lo: float = thresh_lo
        self.thresh_hi: float = thresh_hi

        self.select_conv, select_ids = self.selection()
        self.register_buffer("selection_ids", select_ids)

        self.sobel_x, self.sobel_y = self.sobel(sobel_k)
        self.gauss = self.gaussian(gauss_k, gauss_sigma)
        self.hyst = self.hysteresis()

        self.requires_grad_(requires_grad=False)

    @staticmethod
    def selection() -> tuple[nn.Conv2d, Tensor]:
        lf = t.zeros([3, 3])
        lf[0, 1] = 1
        rt = t.zeros([3, 3])
        rt[2, 1] = 1
        up = t.zeros([3, 3])
        up[1, 0] = 1
        dn = t.zeros([3, 3])
        dn[1, 2] = 1
        tlf = t.zeros([3, 3])
        tlf[0, 0] = 1
        brt = t.zeros([3, 3])
        brt[2, 2] = 1
        blf = t.zeros([3, 3])
        blf[0, 2] = 1
        trt = t.zeros([3, 3])
        trt[2, 0] = 1

        select_conv = nn.Conv2d(in_channels=1, out_channels=8, kernel_size=3, padding=1, bias=False)
        select_conv.weight.data = t.stack([lf, rt, up, dn, tlf, brt, blf, trt], 0).unsqueeze(1)

        select_ids = t.tensor([[0, 1], [4, 5], [2, 3], [6, 7], [0, 1], [4, 5], [2, 3], [6, 7]], dtype=t.long)
        return select_conv, select_ids

    @staticmethod
    def sobel(sobel_k: int) -> tuple[nn.Conv2d, nn.Conv2d]:
        linrange = t.linspace(-(sobel_k // 2), sobel_k // 2, sobel_k)
        x, y = t.meshgrid(linrange, linrange, indexing="ij")
        sobel_numer = x
        sobel_denom = x.pow(2) + y.pow(2)
        sobel_denom[:, sobel_k // 2] = 1
        sobel = sobel_numer / sobel_denom
        sobel.div_(6)

        sobel_x = nn.Conv2d(1, 1, kernel_size=sobel_k, padding=sobel_k // 2, padding_mode="reflect", bias=False)
        sobel_x.weight.data = sobel.clone().t().view(1, 1, sobel_k, sobel_k)

        sobel_y = nn.Conv2d(1, 1, kernel_size=sobel_k, padding=sobel_k // 2, padding_mode="reflect", bias=False)
        sobel_y.weight.data = sobel.view(1, 1, sobel_k, sobel_k)
        return sobel_x, sobel_y

    @staticmethod
    def gaussian(gauss_k: int, sigma: float) -> nn.Conv2d:
        linrange = t.linspace(-1, 1, gauss_k)
        x, y = t.meshgrid(linrange, linrange, indexing="ij")
        sq_dist = x.pow(2) + y.pow(2)

        gaussian = (-sq_dist / (2 * sigma**2)).exp()
        gaussian = gaussian / (2 * math.pi * sigma**2)
        gaussian = gaussian / gaussian.sum()

        gauss = nn.Conv2d(1, 1, kernel_size=gauss_k, padding=gauss_k // 2, padding_mode="reflect", bias=False)
        gauss.weight.data = gaussian.view(1, 1, gauss_k, gauss_k)
        return gauss

    @staticmethod
    def hysteresis() -> nn.Conv2d:
        hyst = nn.Conv2d(1, 1, kernel_size=3, padding=1, padding_mode="reflect", bias=False)
        hyst.weight.data = t.ones((1, 1, 3, 3))
        return hyst

    def forward(self, batch: Tensor) -> Tensor:
        # flatten to greyscale
        greyscale_: Tensor = batch.norm(p=2, dim=1, keepdim=True)
        greyscale_.div_(greyscale_.max())

        # gauss blur
        greyscale = self.gauss(greyscale_)

        # take intensity-gradients
        sobel_x: Tensor = self.sobel_x(greyscale)
        sobel_y: Tensor = self.sobel_y(greyscale)

        grad_mag = (sobel_x.pow(2) + sobel_y.pow(2)).sqrt()
        grad_phase = t.atan2(sobel_x, sobel_y + 1e-5)
        zeros = t.zeros_like(grad_mag, dtype=t.float)

        # non-maximum suppression
        grad_phase = grad_phase.div(math.pi / 4).round().add(4).fmod(8)
        grad_phase = grad_phase.long()

        selections: Tensor = self.select_conv(grad_mag)
        neb_ids = self.selection_ids[grad_phase]
        nebs = selections.gather(1, neb_ids[:, 0, ...].permute(0, 3, 1, 2))

        mask1 = grad_mag < nebs[:, 0, None, ...]
        mask2 = grad_mag < nebs[:, 1, None, ...]
        mask_suppress = mask1 | mask2
        grad_mag = t.where(mask_suppress, zeros, grad_mag)

        # thresholds
        mask_lo = grad_mag < self.thresh_lo
        grad_mag = t.where(mask_lo, zeros, grad_mag)

        weak_mask = (grad_mag < self.thresh_hi) & (grad_mag > self.thresh_lo)
        high_mask = grad_mag > self.thresh_hi

        # hysteresis
        high_nebs: Tensor = self.hyst(high_mask.float())
        weak_keep = weak_mask & (high_nebs > 0)
        mask_not_edge = weak_keep.logical_not() & high_mask.logical_not()
        return t.where(mask_not_edge, zeros, grad_mag)
