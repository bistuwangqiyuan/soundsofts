"""Confidence filtering and fragment merging."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .classifier import DefectClassification


@dataclass
class FilteredDefect:
    classification: DefectClassification
    area: int
    centroid: tuple[float, float]


def filter_by_confidence(
    defects: list[tuple[DefectClassification, int, tuple[float, float]]],
    min_confidence: float = 0.5,
) -> list[FilteredDefect]:
    """Remove defects below the confidence threshold."""
    return [
        FilteredDefect(classification=d[0], area=d[1], centroid=d[2])
        for d in defects
        if d[0].confidence >= min_confidence
    ]


def merge_nearby_fragments(
    defects: list[FilteredDefect],
    distance_threshold: float = 20.0,
) -> list[FilteredDefect]:
    """Merge defects whose centroids are within distance_threshold pixels."""
    if len(defects) <= 1:
        return defects

    merged: list[FilteredDefect] = [defects[0]]
    for d in defects[1:]:
        should_merge = False
        for m in merged:
            dist = np.sqrt((d.centroid[0] - m.centroid[0]) ** 2 + (d.centroid[1] - m.centroid[1]) ** 2)
            if dist < distance_threshold:
                m.area += d.area
                m.centroid = ((m.centroid[0] + d.centroid[0]) / 2, (m.centroid[1] + d.centroid[1]) / 2)
                should_merge = True
                break
        if not should_merge:
            merged.append(d)
    return merged
