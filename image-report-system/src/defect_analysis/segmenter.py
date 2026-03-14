"""Adaptive threshold segmentation for defect mask generation (no ML model required)."""

from __future__ import annotations

import cv2
import numpy as np


def segment_defects(
    image: np.ndarray,
    block_size: int = 51,
    c_offset: int = 15,
    morph_kernel: int = 5,
    min_area: int = 30,
) -> np.ndarray:
    """Produce a binary defect mask via adaptive thresholding + morphological cleanup.

    Works on BGR or grayscale input. Returns uint8 mask (0 or 255).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        blockSize=block_size, C=c_offset,
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morph_kernel, morph_kernel))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)

    if min_area > 0:
        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
        for i in range(1, n_labels):
            if stats[i, cv2.CC_STAT_AREA] < min_area:
                cleaned[labels == i] = 0

    return cleaned
