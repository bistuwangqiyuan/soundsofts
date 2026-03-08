"""Tests for model export (ONNX, TorchScript)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import torch
import pytest

from src.models.unet import build_unet
from src.utils.export import export_to_onnx, export_to_torchscript


class TestExport:
    def test_export_to_onnx(self):
        pytest.importorskip("onnxscript", reason="ONNX export requires onnxscript")
        model = build_unet(encoder="resnet34", encoder_weights=None, in_channels=3, classes=1)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "model.onnx"
            export_to_onnx(model, image_size=(64, 128), output_path=out)
            assert out.exists()

    def test_export_to_torchscript(self):
        model = build_unet(encoder="resnet34", encoder_weights=None, in_channels=3, classes=1)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "model.pt"
            export_to_torchscript(model, image_size=(64, 128), output_path=out)
            assert out.exists()
            loaded = torch.jit.load(str(out))
            x = torch.randn(1, 3, 64, 128)
            with torch.no_grad():
                y = loaded(x)
            assert y.shape == (1, 1, 64, 128)
