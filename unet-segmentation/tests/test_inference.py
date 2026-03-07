"""Tests for inference modules."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import torch
import pytest

from src.models.unet import build_unet
from src.inference.predictor import UNetPredictor
from src.inference.postprocessor import PostProcessor, DefectRegion
from src.inference.overlay import overlay_mask


class TestUNetPredictor:
    def test_predict_shape(self, sample_image):
        model = build_unet(encoder="resnet34", encoder_weights=None, in_channels=3, classes=1)
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "model.pth"
            torch.save(model.state_dict(), ckpt)
            predictor = UNetPredictor(model, ckpt, image_size=(384, 768))
            mask = predictor.predict(sample_image)
            assert mask.shape == (384, 768)
            assert mask.dtype == np.uint8
            assert set(np.unique(mask)).issubset({0, 1})

    def test_predict_batch(self, sample_image):
        model = build_unet(encoder="resnet34", encoder_weights=None, in_channels=3, classes=1)
        with tempfile.TemporaryDirectory() as tmp:
            ckpt = Path(tmp) / "model.pth"
            torch.save(model.state_dict(), ckpt)
            predictor = UNetPredictor(model, ckpt, image_size=(384, 768))
            masks = predictor.predict_batch([sample_image, sample_image])
            assert len(masks) == 2
            assert all(m.shape == (384, 768) for m in masks)


class TestPostProcessor:
    def test_process_empty_mask(self):
        proc = PostProcessor(min_area=10)
        mask = np.zeros((64, 64), dtype=np.uint8)
        cleaned, regions = proc.process(mask)
        assert cleaned.shape == mask.shape
        assert len(regions) == 0

    def test_process_with_defect(self):
        proc = PostProcessor(min_area=10)
        mask = np.zeros((64, 64), dtype=np.uint8)
        mask[10:30, 10:30] = 1
        cleaned, regions = proc.process(mask)
        assert len(regions) >= 1
        assert isinstance(regions[0], DefectRegion)


class TestOverlay:
    def test_overlay_mask(self, sample_image, sample_mask):
        result = overlay_mask(sample_image, sample_mask)
        assert result.shape == sample_image.shape
        assert result.dtype == np.uint8
