"""Tests for report generation pipeline."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.multimodal_fusion.fusion import FusionResult
from src.multimodal_fusion.rule_engine import RuleCheckResult
from src.report_generation.data_binder import ReportData
from src.report_generation.exporter import export_report


@pytest.fixture
def sample_fusion_result():
    return FusionResult(
        defect_mask=np.zeros((100, 100), dtype=np.float32),
        predicted_force=85.0,
        rule_checks=[
            RuleCheckResult(passed=True, rule_name="剥离强度", message="85 N/cm 达标"),
        ],
        overall_quality="合格",
        confidence=0.92,
    )


def test_export_report(sample_fusion_result):
    data = ReportData(
        specimen_id="PIPE-1016-001",
        inspection_date="2026-03-01",
        operator="测试员",
        equipment="PAUT-500",
        fusion_result=sample_fusion_result,
        defect_count=3,
        defect_area_ratio=0.02,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test_report.docx"
        warnings = export_report(data, output)
        assert output.exists()
        assert output.stat().st_size > 0
