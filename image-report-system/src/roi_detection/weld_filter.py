"""Weld seam detection and exclusion from analysis regions."""

from __future__ import annotations

import cv2
import numpy as np

from .projector import brightness_projection


def detect_weld_region(image: np.ndarray, threshold_factor: float = 1.5) -> tuple[int, int] | None:
    """Detect weld seam as a high-brightness horizontal band.

    Returns (y_start, y_end) of the weld region, or None.
    """
    row_profile = brightness_projection(image, axis=1)
    mean_brightness = np.mean(row_profile)
    threshold = mean_brightness * threshold_factor

    weld_mask = row_profile > threshold
    if not np.any(weld_mask):
        return None

    indices = np.where(weld_mask)[0]
    return (int(indices[0]), int(indices[-1]))
