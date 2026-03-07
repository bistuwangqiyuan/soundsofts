"""Three-branch fusion: visual + acoustic + rules."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .rule_engine import RuleCheckResult


@dataclass
class FusionResult:
    defect_mask: np.ndarray
    predicted_force: float
    rule_checks: list[RuleCheckResult]
    overall_quality: str  # "合格" / "不合格" / "待复核"
    confidence: float


def fuse_results(
    visual_mask: np.ndarray,
    visual_confidence: float,
    predicted_force: float,
    rule_checks: list[RuleCheckResult],
) -> FusionResult:
    """Combine visual segmentation, force prediction, and rule checks."""
    all_passed = all(r.passed for r in rule_checks)
    defect_ratio = float(np.sum(visual_mask > 0.5)) / (visual_mask.size + 1e-8)

    if all_passed and defect_ratio < 0.03:
        quality = "合格"
        conf = min(0.95, visual_confidence * 0.5 + 0.5)
    elif not all_passed or defect_ratio > 0.15:
        quality = "不合格"
        conf = min(0.95, visual_confidence * 0.4 + 0.4)
    else:
        quality = "待复核"
        conf = visual_confidence * 0.3 + 0.3

    return FusionResult(
        defect_mask=visual_mask,
        predicted_force=predicted_force,
        rule_checks=rule_checks,
        overall_quality=quality,
        confidence=conf,
    )
