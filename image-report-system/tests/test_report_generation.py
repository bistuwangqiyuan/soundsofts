"""Tests for report generation pipeline."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

from src.multimodal_fusion.fusion import FusionResult, BranchScore
from src.multimodal_fusion.rule_engine import RuleCheckResult
from src.report_generation.data_binder import ReportData
from src.report_generation.exporter import export_report
from src.report_generation.validator import validate_report_data, ValidationIssue


def _make_fusion_result(**kwargs):
    defaults = dict(
        defect_mask=np.zeros((100, 100), dtype=np.float32),
        predicted_force=85.0,
        rule_checks=[RuleCheckResult(passed=True, rule_name="剥离强度", message="85 N/cm 达标")],
        overall_quality="合格",
        confidence=0.92,
        branch_scores=[
            BranchScore("视觉分支", 0.8, 0.4, 0.32),
            BranchScore("声力分支", 0.7, 0.3, 0.21),
            BranchScore("规则引擎", 1.0, 0.3, 0.30),
        ],
    )
    defaults.update(kwargs)
    return FusionResult(**defaults)


@pytest.fixture
def sample_fusion_result():
    return _make_fusion_result()


@pytest.fixture
def sample_image_path(tmp_path):
    img = Image.fromarray(np.ones((200, 300, 3), dtype=np.uint8) * 128, mode="RGB")
    path = tmp_path / "test_cscan.png"
    img.save(path)
    return path


# --- export_report ---

class TestExportReport:
    def test_basic_export(self, sample_fusion_result):
        data = ReportData(
            specimen_id="PIPE-1016-001", inspection_date="2026-03-01",
            operator="测试员", equipment="PAUT-500",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=0.02,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_report.docx"
            warnings = export_report(data, output)
            assert output.exists()
            assert output.stat().st_size > 0

    def test_export_with_defects(self, sample_fusion_result):
        from src.pipeline import DetectedDefect
        from src.defect_analysis.classifier import DefectType, SeverityLevel
        defects = [
            DetectedDefect(1, DefectType.BUBBLE, SeverityLevel.MINOR, 0.8, 200, (50, 50), (40, 40, 20, 20), 1.1, 0.85),
            DetectedDefect(2, DefectType.DISBOND, SeverityLevel.SEVERE, 0.9, 3000, (150, 80), (100, 60, 100, 40), 4.0, 0.3),
        ]
        data = ReportData(
            specimen_id="PIPE-002", inspection_date="2026-03-01",
            operator="测试员", equipment="PAUT-500",
            fusion_result=sample_fusion_result, defect_count=2, defect_area_ratio=0.05,
            defects=defects,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report_with_defects.docx"
            warnings = export_report(data, output)
            assert output.exists()
            assert output.stat().st_size > 1000

    def test_export_fail_quality(self):
        fusion = _make_fusion_result(overall_quality="不合格", confidence=0.6)
        data = ReportData(
            specimen_id="PIPE-FAIL", inspection_date="2026-03-01",
            operator="测试员", equipment="PAUT",
            fusion_result=fusion, defect_count=5, defect_area_ratio=0.12,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "fail_report.docx"
            warnings = export_report(data, output)
            assert output.exists()


# --- validator ---

class TestValidator:
    def test_valid_data(self, sample_fusion_result):
        data = ReportData(
            specimen_id="OK", inspection_date="2026-03-01", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=0.01,
        )
        issues = validate_report_data(data)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0

    def test_empty_specimen_id(self, sample_fusion_result):
        data = ReportData(
            specimen_id="", inspection_date="2026-03-01", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=0.01,
        )
        issues = validate_report_data(data)
        assert any(i.field == "specimen_id" and i.severity == "error" for i in issues)

    def test_negative_defect_count(self, sample_fusion_result):
        data = ReportData(
            specimen_id="X", inspection_date="2026-03-01", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=-1, defect_area_ratio=0.01,
        )
        issues = validate_report_data(data)
        assert any(i.field == "defect_count" for i in issues)

    def test_invalid_area_ratio(self, sample_fusion_result):
        data = ReportData(
            specimen_id="X", inspection_date="2026-03-01", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=1.5,
        )
        issues = validate_report_data(data)
        assert any(i.field == "defect_area_ratio" for i in issues)

    def test_bad_date_format(self, sample_fusion_result):
        data = ReportData(
            specimen_id="X", inspection_date="03/01/2026", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=0.01,
        )
        issues = validate_report_data(data)
        assert any(i.field == "inspection_date" for i in issues)

    def test_high_ratio_warning(self, sample_fusion_result):
        data = ReportData(
            specimen_id="X", inspection_date="2026-03-01", operator="A", equipment="B",
            fusion_result=sample_fusion_result, defect_count=0, defect_area_ratio=0.15,
        )
        issues = validate_report_data(data)
        assert any("偏高" in i.message for i in issues)
