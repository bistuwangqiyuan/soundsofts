"""Tests for report generation pipeline."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image

from src.multimodal_fusion.fusion import FusionResult
from src.multimodal_fusion.rule_engine import RuleCheckResult
from src.report_generation.data_binder import ReportData
from src.report_generation.exporter import export_report, run_pipeline


def _mock_preprocess(path):
    """Return dummy preprocessed array (avoids cv2 dependency in tests)."""
    return np.ones((200, 300, 3), dtype=np.uint8) * 128


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


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a minimal valid C-scan image for pipeline tests."""
    img = Image.fromarray(np.ones((200, 300, 3), dtype=np.uint8) * 128, mode="RGB")
    path = tmp_path / "test_cscan.png"
    img.save(path)
    return path


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


def test_run_pipeline(sample_image_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "pipeline_report.docx"
        with patch("src.image_processing.preprocessor.preprocess_cscan", side_effect=_mock_preprocess):
            warnings = run_pipeline(sample_image_path, output)
        assert output.exists()
        assert output.stat().st_size > 0
