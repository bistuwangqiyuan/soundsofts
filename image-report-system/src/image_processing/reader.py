"""C-scan image reader supporting PNG, JPG, BMP, TIFF."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}


def read_cscan(path: str | Path) -> np.ndarray:
    """Read a C-scan image and return BGR numpy array."""
    p = Path(path)
    if p.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {p.suffix}")
    img = cv2.imread(str(p))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {p}")
    return img
