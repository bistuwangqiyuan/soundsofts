"""Defect type and severity classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geometry import GeometricAttributes


class DefectType(str, Enum):
    BUBBLE = "气泡"
    WEAK_BOND = "弱粘"
    DISBOND = "脱粘"
    NORMAL = "正常粘接"
    UNKNOWN = "未知"


class SeverityLevel(str, Enum):
    MINOR = "轻微"
    MODERATE = "中等"
    SEVERE = "严重"


@dataclass
class DefectClassification:
    defect_type: DefectType
    severity: SeverityLevel
    confidence: float


def classify_defect(
    attrs: GeometricAttributes,
    mean_intensity: float = 128.0,
) -> DefectClassification:
    """Rule-based defect classification using geometric and intensity features."""
    if attrs.circularity > 0.7 and attrs.area_px < 500:
        defect_type = DefectType.BUBBLE
    elif attrs.aspect_ratio > 3.0:
        defect_type = DefectType.DISBOND
    elif mean_intensity < 80:
        defect_type = DefectType.WEAK_BOND
    elif mean_intensity > 180:
        defect_type = DefectType.NORMAL
    else:
        defect_type = DefectType.UNKNOWN

    if attrs.area_px > 2000:
        severity = SeverityLevel.SEVERE
    elif attrs.area_px > 500:
        severity = SeverityLevel.MODERATE
    else:
        severity = SeverityLevel.MINOR

    confidence = min(0.95, 0.6 + 0.1 * attrs.circularity + 0.05 * (attrs.area_px / 1000))

    return DefectClassification(defect_type=defect_type, severity=severity, confidence=confidence)
