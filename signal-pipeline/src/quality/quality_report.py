"""Generate a data quality assessment report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .snr_calculator import SNRCalculator
from .repeatability import RepeatabilityChecker
from .outlier_detector import OutlierDetector


@dataclass
class QualityMetrics:
    total_points: int
    valid_points: int
    outlier_count: int
    mean_snr_db: float
    repeatability_cv: float
    pass_rate: float


class QualityReportGenerator:
    """Aggregate quality metrics across a dataset."""

    def __init__(
        self,
        snr_calc: SNRCalculator | None = None,
        outlier_det: OutlierDetector | None = None,
    ) -> None:
        self.snr_calc = snr_calc or SNRCalculator()
        self.outlier_det = outlier_det or OutlierDetector()

    def evaluate(
        self,
        waveforms: np.ndarray,
        force_values: np.ndarray | None = None,
    ) -> QualityMetrics:
        n = len(waveforms)
        snrs = np.array([self.snr_calc.compute(w) for w in waveforms])

        outlier_mask = self.outlier_det.detect(snrs)
        outlier_count = int(np.sum(outlier_mask))

        cv = 0.0
        if force_values is not None and len(force_values) > 1:
            cv = RepeatabilityChecker.coefficient_of_variation(force_values)

        return QualityMetrics(
            total_points=n,
            valid_points=n - outlier_count,
            outlier_count=outlier_count,
            mean_snr_db=float(np.mean(snrs)),
            repeatability_cv=cv,
            pass_rate=(n - outlier_count) / n if n > 0 else 0.0,
        )

    @staticmethod
    def save(metrics: QualityMetrics, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(metrics), indent=2, ensure_ascii=False), encoding="utf-8")
