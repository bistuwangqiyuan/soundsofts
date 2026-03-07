"""Pipeline configuration loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PipelineConfig:
    """Holds the full pipeline configuration parsed from YAML."""

    steps: list[dict[str, Any]] = field(default_factory=list)
    sampling_rate: float = 40e6  # 40 MHz default
    filter_band: tuple[float, float] = (2e6, 8e6)
    wavelet: str = "db8"
    wavelet_level: int = 5
    grid_rows: int = 12
    grid_cols: int = 10

    @classmethod
    def from_yaml(cls, path: str | Path) -> PipelineConfig:
        with open(path, "r", encoding="utf-8") as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
        band = raw.get("filter_band", [2e6, 8e6])
        return cls(
            steps=raw.get("steps", []),
            sampling_rate=raw.get("sampling_rate", 40e6),
            filter_band=(band[0], band[1]),
            wavelet=raw.get("wavelet", "db8"),
            wavelet_level=raw.get("wavelet_level", 5),
            grid_rows=raw.get("grid_rows", 12),
            grid_cols=raw.get("grid_cols", 10),
        )
