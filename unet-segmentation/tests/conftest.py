"""Pytest fixtures for U-Net segmentation tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def temp_data_dir():
    """Create temporary directory with sample images and masks."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        img_dir = root / "images"
        mask_dir = root / "masks"
        img_dir.mkdir()
        mask_dir.mkdir()

        for i in range(5):
            img = np.random.randint(0, 255, (64, 128, 3), dtype=np.uint8)
            mask = np.random.randint(0, 2, (64, 128), dtype=np.uint8) * 255
            from PIL import Image
            Image.fromarray(img).save(img_dir / f"sample_{i}.png")
            Image.fromarray(mask).save(mask_dir / f"sample_{i}.png")

        yield root


@pytest.fixture
def sample_image():
    """Sample C-scan image (H, W, 3)."""
    return np.random.randint(0, 255, (384, 768, 3), dtype=np.uint8)


@pytest.fixture
def sample_mask():
    """Sample binary mask (H, W)."""
    mask = np.zeros((384, 768), dtype=np.uint8)
    mask[100:150, 200:250] = 1
    return mask
