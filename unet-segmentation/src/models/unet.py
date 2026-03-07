"""U-Net with ResNet34 encoder via segmentation-models-pytorch."""

from __future__ import annotations

import segmentation_models_pytorch as smp
import torch.nn as nn


def build_unet(
    encoder: str = "resnet34",
    encoder_weights: str = "imagenet",
    in_channels: int = 3,
    classes: int = 1,
) -> nn.Module:
    """Create a U-Net model with the specified encoder."""
    return smp.Unet(
        encoder_name=encoder,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=classes,
        activation=None,
    )
