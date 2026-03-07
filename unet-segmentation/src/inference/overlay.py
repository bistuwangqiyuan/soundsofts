"""Overlay segmentation results on original C-scan images."""

from __future__ import annotations

import cv2
import numpy as np


def overlay_mask(
    image: np.ndarray,
    mask: np.ndarray,
    color: tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.4,
) -> np.ndarray:
    """Blend a binary mask onto an image with transparency."""
    overlay = image.copy()
    overlay[mask > 0] = (
        np.array(color) * alpha + overlay[mask > 0] * (1 - alpha)
    ).astype(np.uint8)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, color, 2)

    return overlay
