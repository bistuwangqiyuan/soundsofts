"""Full preprocessing pipeline: read -> denoise -> CLAHE -> crop -> standardize."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .reader import read_cscan
from .cropper import auto_crop
from .standardizer import standardize


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, grid_size: int = 8) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(grid_size, grid_size))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def denoise(image: np.ndarray, method: str = "bilateral") -> np.ndarray:
    """Apply denoising: 'bilateral', 'gaussian', or 'nlm' (non-local means)."""
    if method == "bilateral":
        return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)
    elif method == "gaussian":
        return cv2.GaussianBlur(image, (5, 5), 0)
    elif method == "nlm":
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    return image


def preprocess_cscan(
    path: str | Path,
    target_size: tuple[int, int] = (384, 768),
    enable_clahe: bool = True,
    enable_denoise: bool = True,
    denoise_method: str = "bilateral",
) -> np.ndarray:
    """Full preprocessing: read -> denoise -> CLAHE -> auto-crop -> resize -> RGB."""
    image = read_cscan(path)

    if enable_denoise:
        image = denoise(image, method=denoise_method)

    if enable_clahe:
        image = apply_clahe(image)

    cropped = auto_crop(image)
    rgb = standardize(cropped, target_size=target_size, color_space="RGB")
    return rgb
