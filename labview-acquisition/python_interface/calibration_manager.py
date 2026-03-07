"""Manage sensor calibration data."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass

import numpy as np


@dataclass
class CalibrationPoint:
    voltage_v: float
    force_n: float


class CalibrationManager:
    """Load and apply sensor calibration from JSON files."""

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    @property
    def force_sensor(self) -> dict:
        return self._data.get("force_sensor", {})

    @property
    def position_encoder(self) -> dict:
        return self._data.get("position_encoder", {})

    def voltage_to_force(self, voltage_v: float) -> float:
        """Convert raw voltage to force using calibration curve (linear interpolation)."""
        points = self.force_sensor.get("calibration_points", [])
        if not points:
            return voltage_v

        voltages = [p["voltage_v"] for p in points]
        forces = [p["force_n"] for p in points]
        return float(np.interp(voltage_v, voltages, forces))

    def pulses_to_mm(self, pulses: int) -> float:
        """Convert encoder pulses to displacement in mm."""
        mm_per_pulse = self.position_encoder.get("mm_per_pulse", 0.02)
        return pulses * mm_per_pulse

    def apply_zero_offset(self, voltage_v: float) -> float:
        """Remove zero offset from raw voltage reading."""
        offset_mv = self.force_sensor.get("zero_offset_mv", 0.0)
        return voltage_v - offset_mv / 1000.0
