"""Tests for augmentation pipeline."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("albumentations")
from src.data.augmentation import get_train_transforms, get_val_transforms


class TestAugmentation:
    def test_train_transforms(self):
        transform = get_train_transforms({})
        image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        mask = np.random.randint(0, 2, (100, 200), dtype=np.float32)
        out = transform(image=image, mask=mask)
        assert out["image"].shape == image.shape
        assert out["mask"].shape == mask.shape

    def test_val_transforms(self):
        transform = get_val_transforms()
        image = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        mask = np.random.randint(0, 2, (100, 200), dtype=np.float32)
        out = transform(image=image, mask=mask)
        assert out["image"].shape == image.shape
        assert out["mask"].shape == mask.shape
