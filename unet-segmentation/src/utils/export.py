"""Export U-Net to ONNX or TorchScript."""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn


def export_to_onnx(
    model: nn.Module,
    image_size: tuple[int, int] = (384, 768),
    output_path: str | Path = "model.onnx",
) -> None:
    model.eval()
    dummy = torch.randn(1, 3, image_size[0], image_size[1])
    torch.onnx.export(
        model, dummy, str(output_path),
        input_names=["image"], output_names=["mask"],
        dynamic_axes={"image": {0: "batch"}, "mask": {0: "batch"}},
        opset_version=17,
    )


def export_to_torchscript(
    model: nn.Module,
    image_size: tuple[int, int] = (384, 768),
    output_path: str | Path = "model.pt",
) -> None:
    model.eval()
    dummy = torch.randn(1, 3, image_size[0], image_size[1])
    scripted = torch.jit.trace(model, dummy)
    scripted.save(str(output_path))
