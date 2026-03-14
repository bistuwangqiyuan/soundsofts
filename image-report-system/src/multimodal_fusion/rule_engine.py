"""Process rule engine for cross-checking defect analysis results (GB/T 23257)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..pipeline import DetectedDefect


@dataclass
class RuleCheckResult:
    passed: bool
    rule_name: str
    message: str


class RuleEngine:
    """Apply engineering rules to validate and cross-check analysis results."""

    PEEL_STRENGTH_MIN = 70.0      # N/cm
    DEFECT_AREA_THRESHOLD = 0.05  # 5%
    MAX_SINGLE_DEFECT_PX = 5000   # pixels
    UNIFORMITY_MAX_STD = 0.35     # normalized std of defect distribution
    MIN_BONDING_COVERAGE = 0.90   # 90%

    def check_peel_strength(self, force_n_per_cm: float) -> RuleCheckResult:
        passed = force_n_per_cm >= self.PEEL_STRENGTH_MIN
        return RuleCheckResult(
            passed=passed,
            rule_name="GB/T 23257 剥离强度",
            message=f"剥离强度 {force_n_per_cm:.1f} N/cm {'达标' if passed else '不达标'}（要求 >= {self.PEEL_STRENGTH_MIN} N/cm）",
        )

    def check_defect_area_ratio(self, defect_area: int, total_area: int, threshold: float | None = None) -> RuleCheckResult:
        threshold = threshold if threshold is not None else self.DEFECT_AREA_THRESHOLD
        ratio = defect_area / (total_area + 1e-8)
        passed = ratio < threshold
        return RuleCheckResult(
            passed=passed,
            rule_name="缺陷面积比",
            message=f"缺陷面积占比 {ratio:.2%} {'达标' if passed else '超标'}（阈值 {threshold:.0%}）",
        )

    def check_max_single_defect(self, defects: list[DetectedDefect] | None = None) -> RuleCheckResult:
        if not defects:
            return RuleCheckResult(passed=True, rule_name="最大单缺陷面积", message="无缺陷检出，达标")
        max_area = max(d.area_px for d in defects)
        passed = max_area <= self.MAX_SINGLE_DEFECT_PX
        return RuleCheckResult(
            passed=passed,
            rule_name="最大单缺陷面积",
            message=f"最大单缺陷 {max_area} px {'达标' if passed else '超标'}（阈值 {self.MAX_SINGLE_DEFECT_PX} px）",
        )

    def check_defect_distribution(self, defects: list[DetectedDefect] | None = None) -> RuleCheckResult:
        if not defects or len(defects) < 2:
            return RuleCheckResult(passed=True, rule_name="缺陷分布均匀性", message="缺陷不足 2 处，不评估分布")
        import numpy as np
        cx = np.array([d.centroid[0] for d in defects])
        cy = np.array([d.centroid[1] for d in defects])
        std_x = float(np.std(cx) / (np.ptp(cx) + 1e-8))
        std_y = float(np.std(cy) / (np.ptp(cy) + 1e-8))
        avg_std = (std_x + std_y) / 2
        passed = avg_std <= self.UNIFORMITY_MAX_STD
        return RuleCheckResult(
            passed=passed,
            rule_name="缺陷分布均匀性",
            message=f"分布离散度 {avg_std:.2f} {'均匀' if passed else '集中'}（阈值 {self.UNIFORMITY_MAX_STD}）",
        )

    def check_bonding_coverage(self, defect_area: int, total_area: int) -> RuleCheckResult:
        coverage = 1.0 - defect_area / (total_area + 1e-8)
        passed = coverage >= self.MIN_BONDING_COVERAGE
        return RuleCheckResult(
            passed=passed,
            rule_name="粘接覆盖率",
            message=f"粘接覆盖率 {coverage:.2%} {'达标' if passed else '不达标'}（要求 >= {self.MIN_BONDING_COVERAGE:.0%}）",
        )

    def run_all_checks(
        self,
        force: float,
        defect_area: int,
        total_area: int,
        defects: list[DetectedDefect] | None = None,
    ) -> list[RuleCheckResult]:
        return [
            self.check_peel_strength(force),
            self.check_defect_area_ratio(defect_area, total_area),
            self.check_max_single_defect(defects),
            self.check_defect_distribution(defects),
            self.check_bonding_coverage(defect_area, total_area),
        ]
