"""Brightness projection analysis for ROI detection."""

from __future__ import annotations

import cv2
import numpy as np


def brightness_projection(image: np.ndarray, axis: int = 0) -> np.ndarray:
    """Compute mean brightness projection along an axis.

    axis=0 → project along rows (column profile).
    axis=1 → project along columns (row profile).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    return np.mean(gray, axis=axis)
