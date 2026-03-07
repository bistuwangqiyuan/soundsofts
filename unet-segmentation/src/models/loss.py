"""Combined BCE + Dice loss for binary segmentation."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class BCEDiceLoss(nn.Module):
    """Weighted combination of Binary Cross-Entropy and Dice Loss.

    Args:
        bce_weight: Weight for BCE component.
        dice_weight: Weight for Dice component.
    """

    def __init__(self, bce_weight: float = 0.5, dice_weight: float = 0.5, smooth: float = 1.0) -> None:
        super().__init__()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, targets)

        probs = torch.sigmoid(logits)
        intersection = (probs * targets).sum()
        dice = 1 - (2.0 * intersection + self.smooth) / (probs.sum() + targets.sum() + self.smooth)

        return self.bce_weight * bce + self.dice_weight * dice
