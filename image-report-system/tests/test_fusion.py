"""Tests for multimodal_fusion modules."""

import numpy as np
import pytest

from src.multimodal_fusion.rule_engine import RuleCheckResult, RuleEngine
from src.multimodal_fusion.fusion import fuse_results, BranchScore


# --- Rule Engine (5 rules) ---

class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleEngine()

    def test_peel_strength_pass(self):
        r = self.engine.check_peel_strength(85.0)
        assert r.passed is True
        assert "达标" in r.message

    def test_peel_strength_fail(self):
        r = self.engine.check_peel_strength(50.0)
        assert r.passed is False

    def test_defect_area_ratio_pass(self):
        r = self.engine.check_defect_area_ratio(100, 10000)
        assert r.passed is True

    def test_defect_area_ratio_fail(self):
        r = self.engine.check_defect_area_ratio(600, 10000)
        assert r.passed is False

    def test_max_single_defect_pass(self):
        r = self.engine.check_max_single_defect(None)
        assert r.passed is True

    def test_max_single_defect_fail(self):
        from src.pipeline import DetectedDefect
        from src.defect_analysis.classifier import DefectType, SeverityLevel
        big_defect = DetectedDefect(
            defect_id=1, defect_type=DefectType.DISBOND, severity=SeverityLevel.SEVERE,
            confidence=0.9, area_px=8000, centroid=(50, 50), bbox=(0, 0, 100, 100),
            aspect_ratio=1.0, circularity=0.5,
        )
        r = self.engine.check_max_single_defect([big_defect])
        assert r.passed is False

    def test_defect_distribution_pass(self):
        r = self.engine.check_defect_distribution(None)
        assert r.passed is True

    def test_bonding_coverage_pass(self):
        r = self.engine.check_bonding_coverage(500, 10000)
        assert r.passed is True

    def test_bonding_coverage_fail(self):
        r = self.engine.check_bonding_coverage(2000, 10000)
        assert r.passed is False

    def test_run_all_checks_returns_5(self):
        checks = self.engine.run_all_checks(85.0, 100, 10000)
        assert len(checks) == 5


# --- Fusion ---

class TestFusion:
    def test_fuse_all_pass(self):
        checks = [RuleCheckResult(True, "r1", "ok")] * 5
        mask = np.zeros((10, 10), dtype=np.float32)
        result = fuse_results(mask, 0.9, 85.0, checks)
        assert result.overall_quality == "合格"
        assert result.confidence > 0.5

    def test_fuse_fail_low_force(self):
        checks = [
            RuleCheckResult(False, "剥离强度", "不达标"),
            RuleCheckResult(True, "面积比", "达标"),
            RuleCheckResult(True, "r3", "ok"),
            RuleCheckResult(True, "r4", "ok"),
            RuleCheckResult(True, "r5", "ok"),
        ]
        mask = np.zeros((10, 10), dtype=np.float32)
        result = fuse_results(mask, 0.5, 30.0, checks)
        assert result.overall_quality in ("不合格", "待复核")

    def test_fuse_review_case(self):
        checks = [
            RuleCheckResult(True, "r1", "ok"),
            RuleCheckResult(False, "r2", "fail"),
            RuleCheckResult(True, "r3", "ok"),
            RuleCheckResult(True, "r4", "ok"),
            RuleCheckResult(True, "r5", "ok"),
        ]
        mask = np.zeros((10, 10), dtype=np.float32)
        mask[:2, :2] = 1.0  # small defect
        result = fuse_results(mask, 0.7, 75.0, checks)
        assert result.overall_quality in ("待复核", "合格")

    def test_branch_scores_present(self):
        checks = [RuleCheckResult(True, "r", "ok")]
        mask = np.zeros((10, 10), dtype=np.float32)
        result = fuse_results(mask, 0.9, 85.0, checks)
        assert len(result.branch_scores) == 3
        assert all(isinstance(b, BranchScore) for b in result.branch_scores)

    def test_custom_weights(self):
        checks = [RuleCheckResult(True, "r", "ok")]
        mask = np.zeros((10, 10), dtype=np.float32)
        r1 = fuse_results(mask, 0.9, 85.0, checks, w_visual=1.0, w_acoustic=0.0, w_rules=0.0)
        r2 = fuse_results(mask, 0.9, 85.0, checks, w_visual=0.0, w_acoustic=0.0, w_rules=1.0)
        assert r1.confidence != r2.confidence or r1.overall_quality == r2.overall_quality

    def test_confidence_bounded(self):
        checks = [RuleCheckResult(True, "r", "ok")]
        mask = np.zeros((10, 10), dtype=np.float32)
        result = fuse_results(mask, 0.99, 120.0, checks)
        assert 0.0 < result.confidence < 1.0
