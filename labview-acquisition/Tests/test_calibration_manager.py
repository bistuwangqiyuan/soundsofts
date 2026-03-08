"""Tests for calibration_manager module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from python_interface.calibration_manager import CalibrationManager


@pytest.fixture
def calibration_json_path(tmp_path: Path) -> Path:
    """Minimal calibration JSON matching project format."""
    data = {
        "force_sensor": {
            "calibration_points": [
                {"voltage_v": 0.0, "force_n": 0.0},
                {"voltage_v": 1.0, "force_n": 100.0},
                {"voltage_v": 5.0, "force_n": 500.0},
            ],
            "zero_offset_mv": 10.0,
        },
        "position_encoder": {
            "mm_per_pulse": 0.02,
        },
    }
    path = tmp_path / "calibration_data.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def test_voltage_to_force(calibration_json_path: Path) -> None:
    cal = CalibrationManager(calibration_json_path)
    assert cal.voltage_to_force(0.0) == 0.0
    assert cal.voltage_to_force(1.0) == 100.0
    assert cal.voltage_to_force(5.0) == 500.0
    assert 49.0 <= cal.voltage_to_force(0.5) <= 51.0


def test_pulses_to_mm(calibration_json_path: Path) -> None:
    cal = CalibrationManager(calibration_json_path)
    assert cal.pulses_to_mm(0) == 0.0
    assert cal.pulses_to_mm(100) == 2.0
    assert cal.pulses_to_mm(500) == 10.0


def test_apply_zero_offset(calibration_json_path: Path) -> None:
    cal = CalibrationManager(calibration_json_path)
    # zero_offset_mv = 10 -> 0.01 V
    assert cal.apply_zero_offset(0.01) == pytest.approx(0.0, abs=1e-6)
    assert cal.apply_zero_offset(1.01) == pytest.approx(1.0, abs=1e-6)


def test_real_config() -> None:
    """Test against project Config/calibration_data.json if present."""
    root = Path(__file__).resolve().parent.parent
    path = root / "Config" / "calibration_data.json"
    if not path.is_file():
        pytest.skip("Config/calibration_data.json not found")
    cal = CalibrationManager(path)
    assert cal.voltage_to_force(0.0) == 0.0
    assert cal.voltage_to_force(5.0) == 500.0
    assert cal.position_encoder.get("mm_per_pulse") == 0.02
