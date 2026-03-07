"""Write processed feature matrices to Parquet for efficient ML training."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ParquetWriter:
    """Write a DataFrame to Parquet with gzip compression."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write(self, df: pd.DataFrame) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.path, compression="gzip", index=False)
