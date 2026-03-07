"""Tests for U-Net model and metrics."""

import torch
import pytest

from src.models.unet import build_unet
from src.models.loss import BCEDiceLoss
from src.models.metrics import iou_score, dice_score


class TestUNet:
    def test_output_shape(self):
        model = build_unet(encoder="resnet34", encoder_weights=None, in_channels=3, classes=1)
        x = torch.randn(2, 3, 384, 768)
        out = model(x)
        assert out.shape == (2, 1, 384, 768)


class TestLoss:
    def test_perfect_prediction(self):
        logits = torch.ones(1, 1, 64, 64) * 10
        targets = torch.ones(1, 1, 64, 64)
        loss = BCEDiceLoss()(logits, targets)
        assert loss.item() < 0.1


class TestMetrics:
    def test_perfect_iou(self):
        pred = torch.ones(1, 1, 32, 32) * 10
        target = torch.ones(1, 1, 32, 32)
        assert iou_score(pred, target) > 0.99

    def test_perfect_dice(self):
        pred = torch.ones(1, 1, 32, 32) * 10
        target = torch.ones(1, 1, 32, 32)
        assert dice_score(pred, target) > 0.99
