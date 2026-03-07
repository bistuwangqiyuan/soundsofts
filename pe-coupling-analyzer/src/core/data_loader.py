"""Data loading for CSV and HDF5 files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd


def load_data(path: str | Path) -> dict[str, Any]:
    """Load data from CSV or HDF5 file."""
    p = Path(path)

    if p.suffix == ".csv":
        df = pd.read_csv(p)
        return {
            "dataframe": df,
            "features": df.drop(columns=["force"], errors="ignore").values.astype(np.float32),
            "force": df["force"].values.astype(np.float32) if "force" in df.columns else np.array([]),
            "source": str(p),
        }

    elif p.suffix in (".hdf5", ".h5"):
        with h5py.File(p, "r") as f:
            waveforms = []
            forces = []
            for specimen in f.keys():
                if specimen == "metadata":
                    continue
                for point in f[specimen].keys():
                    grp = f[specimen][point]
                    if "waveform" in grp:
                        waveforms.append(np.array(grp["waveform"], dtype=np.float32))
                    if "force" in grp:
                        forces.append(float(grp["force"][()]))
            return {
                "waveforms": waveforms,
                "force": np.array(forces, dtype=np.float32),
                "source": str(p),
            }

    raise ValueError(f"Unsupported file format: {p.suffix}")
