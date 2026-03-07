"""Process rule engine for cross-checking defect analysis results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleCheckResult:
    passed: bool
    rule_name: str
    message: str


class RuleEngine:
    """Apply engineering rules to validate and cross-check analysis results."""

    PEEL_STRENGTH_MIN = 70.0  # N/cm, GB/T 23257 requirement

    def check_peel_strength(self, force_n_per_cm: float) -> RuleCheckResult:
        passed = force_n_per_cm >= self.PEEL_STRENGTH_MIN
        return RuleCheckResult(
            passed=passed,
            rule_name="GB/T 23257 剥离强度",
            message=f"剥离强度 {force_n_per_cm:.1f} N/cm {'达标' if passed else '不达标'}（要求 >= {self.PEEL_STRENGTH_MIN} N/cm）",
        )

    def check_defect_area_ratio(self, defect_area: int, total_area: int, threshold: float = 0.05) -> RuleCheckResult:
        ratio = defect_area / (total_area + 1e-8)
        passed = ratio < threshold
        return RuleCheckResult(
            passed=passed,
            rule_name="缺陷面积比",
            message=f"缺陷面积占比 {ratio:.2%} {'达标' if passed else '超标'}（阈值 {threshold:.0%}）",
        )

    def run_all_checks(self, force: float, defect_area: int, total_area: int) -> list[RuleCheckResult]:
        return [
            self.check_peel_strength(force),
            self.check_defect_area_ratio(defect_area, total_area),
        ]
