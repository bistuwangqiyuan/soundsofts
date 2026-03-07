"""CSV data reader for structured acoustic-force coupling data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class CSVReader:
    """Read the cleaned coupling CSV dataset.

    Expected columns: ultra, X, y, db, number_bord, force
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> pd.DataFrame:
        return pd.read_csv(self.path, encoding="utf-8")

    def read_features_and_target(
        self,
        feature_cols: list[str] | None = None,
        target_col: str = "force",
    ) -> tuple[pd.DataFrame, pd.Series]:
        df = self.read()
        if feature_cols is None:
            feature_cols = [c for c in df.columns if c != target_col]
        return df[feature_cols], df[target_col]
