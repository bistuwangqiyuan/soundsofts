"""Application configuration management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AppConfig:
    model_path: str = "resources/models/random_forest.onnx"
    unet_model_path: str = "resources/models/unet.onnx"
    report_template: str = "resources/templates/report_template.docx"
    filter_low_mhz: float = 2.0
    filter_high_mhz: float = 8.0
    wavelet: str = "db8"
    wavelet_level: int = 5

    @classmethod
    def from_yaml(cls, path: str | Path) -> AppConfig:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return cls(**{k: v for k, v in raw.items() if k in cls.__dataclass_fields__})
