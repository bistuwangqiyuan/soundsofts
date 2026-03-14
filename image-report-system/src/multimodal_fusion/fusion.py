"""Three-branch weighted fusion: visual + acoustic + rules."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .rule_engine import RuleCheckResult


@dataclass
class BranchScore:
    name: str
    score: float
    weight: float
    weighted: float


@dataclass
class FusionResult:
    defect_mask: np.ndarray
    predicted_force: float
    rule_checks: list[RuleCheckResult]
    overall_quality: str   # "合格" / "不合格" / "待复核"
    confidence: float
    branch_scores: list[BranchScore] = field(default_factory=list)


def _platt_calibrate(raw: float, a: float = -1.5, b: float = 0.2) -> float:
    """Platt sigmoid calibration: P = 1/(1 + exp(a*raw + b))."""
    return 1.0 / (1.0 + math.exp(a * raw + b))


def fuse_results(
    visual_mask: np.ndarray,
    visual_confidence: float,
    predicted_force: float,
    rule_checks: list[RuleCheckResult],
    *,
    w_visual: float = 0.4,
    w_acoustic: float = 0.3,
    w_rules: float = 0.3,
) -> FusionResult:
    """Combine visual segmentation, force prediction, and rule checks via weighted scoring."""
    # Normalize weights
    total_w = w_visual + w_acoustic + w_rules
    w_visual /= total_w
    w_acoustic /= total_w
    w_rules /= total_w

    # Visual score: lower defect ratio -> higher score
    defect_ratio = float(np.sum(visual_mask > 0.5)) / (visual_mask.size + 1e-8)
    visual_score = max(0.0, 1.0 - defect_ratio * 10.0) * visual_confidence

    # Acoustic score: normalized force (70 N/cm = threshold, 120+ = perfect)
    acoustic_score = min(1.0, max(0.0, (predicted_force - 30.0) / 90.0))

    # Rules score: fraction of rules passed
    rules_passed = sum(1 for r in rule_checks if r.passed)
    rules_score = rules_passed / max(len(rule_checks), 1)

    # Weighted composite
    composite = w_visual * visual_score + w_acoustic * acoustic_score + w_rules * rules_score

    # Calibrated confidence
    confidence = _platt_calibrate(composite, a=-3.0, b=1.2)
    confidence = min(0.99, max(0.05, confidence))

    # Decision
    all_passed = all(r.passed for r in rule_checks)
    if composite >= 0.65 and all_passed:
        quality = "合格"
    elif composite < 0.40 or (not all_passed and rules_passed / max(len(rule_checks), 1) < 0.5):
        quality = "不合格"
    else:
        quality = "待复核"

    branches = [
        BranchScore("视觉分支", visual_score, w_visual, w_visual * visual_score),
        BranchScore("声力分支", acoustic_score, w_acoustic, w_acoustic * acoustic_score),
        BranchScore("规则引擎", rules_score, w_rules, w_rules * rules_score),
    ]

    return FusionResult(
        defect_mask=visual_mask,
        predicted_force=predicted_force,
        rule_checks=rule_checks,
        overall_quality=quality,
        confidence=confidence,
        branch_scores=branches,
    )
