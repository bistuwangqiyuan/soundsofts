"""Segmentation evaluation metrics: IoU, Dice, Precision, Recall, F1."""

from __future__ import annotations

import torch
import numpy as np


def iou_score(pred: torch.Tensor, target: torch.Tensor, threshold: float = 0.5) -> float:
    pred_bin = (torch.sigmoid(pred) > threshold).float()
    intersection = (pred_bin * target).sum().item()
    union = pred_bin.sum().item() + target.sum().item() - intersection
    return intersection / (union + 1e-8)


def dice_score(pred: torch.Tensor, target: torch.Tensor, threshold: float = 0.5) -> float:
    pred_bin = (torch.sigmoid(pred) > threshold).float()
    intersection = (pred_bin * target).sum().item()
    return (2.0 * intersection) / (pred_bin.sum().item() + target.sum().item() + 1e-8)


def precision_recall_f1(
    pred: torch.Tensor,
    target: torch.Tensor,
    threshold: float = 0.5,
) -> dict[str, float]:
    pred_bin = (torch.sigmoid(pred) > threshold).float()
    tp = (pred_bin * target).sum().item()
    fp = (pred_bin * (1 - target)).sum().item()
    fn = ((1 - pred_bin) * target).sum().item()

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)

    return {"precision": precision, "recall": recall, "f1": f1}
