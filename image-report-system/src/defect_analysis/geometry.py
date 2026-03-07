"""Geometric attribute computation for defect regions."""

from __future__ import annotations

from dataclasses import dataclass
import math

import cv2
import numpy as np


@dataclass
class GeometricAttributes:
    area_px: int
    perimeter_px: float
    centroid: tuple[float, float]
    bbox: tuple[int, int, int, int]
    aspect_ratio: float
    orientation_deg: float
    circularity: float
    equivalent_diameter: float


def compute_geometry(mask: np.ndarray, contour: np.ndarray) -> GeometricAttributes:
    """Compute geometric attributes from a single defect contour."""
    area = int(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))

    M = cv2.moments(contour)
    cx = M["m10"] / (M["m00"] + 1e-8)
    cy = M["m01"] / (M["m00"] + 1e-8)

    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = max(w, h) / (min(w, h) + 1e-8)

    orientation = 0.0
    if len(contour) >= 5:
        ellipse = cv2.fitEllipse(contour)
        orientation = float(ellipse[2])

    circularity = 4 * math.pi * area / (perimeter ** 2 + 1e-8)
    eq_diameter = math.sqrt(4 * area / math.pi)

    return GeometricAttributes(
        area_px=area,
        perimeter_px=perimeter,
        centroid=(cx, cy),
        bbox=(x, y, w, h),
        aspect_ratio=aspect_ratio,
        orientation_deg=orientation,
        circularity=circularity,
        equivalent_diameter=eq_diameter,
    )
