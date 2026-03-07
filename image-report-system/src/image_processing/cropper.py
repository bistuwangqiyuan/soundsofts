"""Adaptive cropping to remove axes, color bars, and UI elements."""

from __future__ import annotations

import cv2
import numpy as np


def auto_crop(image: np.ndarray, margin_ratio: float = 0.05) -> np.ndarray:
    """Detect and remove border elements (axes, color bars) from C-scan images.

    Uses edge detection to find the main content region.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    h, w = gray.shape

    # Project along rows/cols to find content boundaries
    col_sum = np.sum(gray, axis=0)
    row_sum = np.sum(gray, axis=1)

    col_threshold = np.mean(col_sum) * 0.3
    row_threshold = np.mean(row_sum) * 0.3

    col_mask = col_sum > col_threshold
    row_mask = row_sum > row_threshold

    if not np.any(col_mask) or not np.any(row_mask):
        return image

    x_start = max(0, int(np.argmax(col_mask) - w * margin_ratio))
    x_end = min(w, int(len(col_mask) - np.argmax(col_mask[::-1]) + w * margin_ratio))
    y_start = max(0, int(np.argmax(row_mask) - h * margin_ratio))
    y_end = min(h, int(len(row_mask) - np.argmax(row_mask[::-1]) + h * margin_ratio))

    return image[y_start:y_end, x_start:x_end]
