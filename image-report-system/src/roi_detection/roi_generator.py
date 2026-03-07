"""Automatic rectangular ROI generation from projection analysis."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .projector import brightness_projection


@dataclass
class ROI:
    x: int
    y: int
    width: int
    height: int


def detect_rois(
    image: np.ndarray,
    threshold_ratio: float = 0.5,
    min_width: int = 20,
    min_height: int = 20,
) -> list[ROI]:
    """Detect rectangular ROIs based on brightness thresholding."""
    col_profile = brightness_projection(image, axis=0)
    row_profile = brightness_projection(image, axis=1)

    col_thresh = np.mean(col_profile) * threshold_ratio
    row_thresh = np.mean(row_profile) * threshold_ratio

    col_mask = col_profile > col_thresh
    row_mask = row_profile > row_thresh

    rois: list[ROI] = []

    # Find contiguous bright regions
    col_changes = np.diff(col_mask.astype(int))
    col_starts = np.where(col_changes == 1)[0] + 1
    col_ends = np.where(col_changes == -1)[0] + 1

    row_changes = np.diff(row_mask.astype(int))
    row_starts = np.where(row_changes == 1)[0] + 1
    row_ends = np.where(row_changes == -1)[0] + 1

    if len(col_starts) == 0 or len(col_ends) == 0 or len(row_starts) == 0 or len(row_ends) == 0:
        h, w = image.shape[:2]
        return [ROI(0, 0, w, h)]

    for rs, re in zip(row_starts, row_ends):
        for cs, ce in zip(col_starts, col_ends):
            w = int(ce - cs)
            h = int(re - rs)
            if w >= min_width and h >= min_height:
                rois.append(ROI(x=int(cs), y=int(rs), width=w, height=h))

    return rois if rois else [ROI(0, 0, image.shape[1], image.shape[0])]
