"""Connected component analysis for defect region extraction."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ComponentInfo:
    label: int
    area: int
    centroid_x: float
    centroid_y: float
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int


def analyze_components(mask: np.ndarray, min_area: int = 30) -> list[ComponentInfo]:
    """Extract connected components from a binary mask."""
    mask_u8 = mask.astype(np.uint8)
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_u8, connectivity=8)

    components: list[ComponentInfo] = []
    for i in range(1, n_labels):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        components.append(ComponentInfo(
            label=i,
            area=area,
            centroid_x=float(centroids[i][0]),
            centroid_y=float(centroids[i][1]),
            bbox_x=int(stats[i, cv2.CC_STAT_LEFT]),
            bbox_y=int(stats[i, cv2.CC_STAT_TOP]),
            bbox_w=int(stats[i, cv2.CC_STAT_WIDTH]),
            bbox_h=int(stats[i, cv2.CC_STAT_HEIGHT]),
        ))
    return components
