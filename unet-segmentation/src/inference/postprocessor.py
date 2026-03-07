"""Post-processing: thresholding, connected component analysis, fragment filtering."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class DefectRegion:
    label: int
    area: int
    centroid: tuple[float, float]
    bbox: tuple[int, int, int, int]  # x, y, w, h
    aspect_ratio: float


class PostProcessor:
    """Clean up raw segmentation masks and extract defect regions."""

    def __init__(self, min_area: int = 50, max_aspect_ratio: float = 20.0) -> None:
        self.min_area = min_area
        self.max_aspect_ratio = max_aspect_ratio

    def process(self, mask: np.ndarray) -> tuple[np.ndarray, list[DefectRegion]]:
        """Return cleaned mask and list of defect regions."""
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        cleaned = np.zeros_like(mask)
        regions: list[DefectRegion] = []

        for i in range(1, n_labels):
            area = int(stats[i, cv2.CC_STAT_AREA])
            if area < self.min_area:
                continue

            x, y, w, h = (
                int(stats[i, cv2.CC_STAT_LEFT]),
                int(stats[i, cv2.CC_STAT_TOP]),
                int(stats[i, cv2.CC_STAT_WIDTH]),
                int(stats[i, cv2.CC_STAT_HEIGHT]),
            )
            aspect = max(w, h) / (min(w, h) + 1e-6)
            if aspect > self.max_aspect_ratio:
                continue

            cleaned[labels == i] = 1
            regions.append(DefectRegion(
                label=i,
                area=area,
                centroid=(float(centroids[i][0]), float(centroids[i][1])),
                bbox=(x, y, w, h),
                aspect_ratio=aspect,
            ))

        return cleaned, regions
