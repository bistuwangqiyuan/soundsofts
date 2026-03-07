"""Full preprocessing pipeline: read → crop → standardize → tensor."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .reader import read_cscan
from .cropper import auto_crop
from .standardizer import standardize


def preprocess_cscan(
    path: str | Path,
    target_size: tuple[int, int] = (384, 768),
) -> np.ndarray:
    """Full preprocessing: read → auto-crop → resize → RGB normalization."""
    image = read_cscan(path)
    cropped = auto_crop(image)
    rgb = standardize(cropped, target_size=target_size, color_space="RGB")
    return rgb
