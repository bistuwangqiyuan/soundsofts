"""HDF5 waveform data reader with gzip-compressed hierarchical storage."""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np


class HDF5Reader:
    """Read ultrasonic waveforms stored in HDF5 format.

    Expected hierarchy::

        /specimen_id/scan_point_id/waveform   -> 1-D float32
        /specimen_id/scan_point_id/metadata   -> JSON string attribute
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read_waveform(self, specimen: str, point: str) -> np.ndarray:
        with h5py.File(self.path, "r") as f:
            return np.array(f[specimen][point]["waveform"], dtype=np.float32)

    def list_specimens(self) -> list[str]:
        with h5py.File(self.path, "r") as f:
            return list(f.keys())

    def list_points(self, specimen: str) -> list[str]:
        with h5py.File(self.path, "r") as f:
            return list(f[specimen].keys())

    def read_all(self, specimen: str) -> dict[str, np.ndarray]:
        result: dict[str, np.ndarray] = {}
        with h5py.File(self.path, "r") as f:
            for pt in f[specimen]:
                if "waveform" in f[specimen][pt]:
                    result[pt] = np.array(f[specimen][pt]["waveform"], dtype=np.float32)
        return result
