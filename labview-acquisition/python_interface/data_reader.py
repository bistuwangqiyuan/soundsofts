"""Read acquisition data produced by the LabVIEW system."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


@dataclass
class AcquisitionRecord:
    """One synchronized acquisition record from the LabVIEW system."""
    timestamp: float
    position_mm: float
    waveform: np.ndarray
    force_n: float
    specimen_id: str
    point_id: str


class LabVIEWDataReader:
    """Read HDF5 files produced by the LabVIEW Data_Storage.vi.

    Expected HDF5 structure::

        /metadata              (attrs: specimen_id, operator, date, equipment)
        /acquisition/
            point_0001/
                waveform       (1-D float32 array)
                position       (scalar float, mm)
                force          (scalar float, N)
                timestamp      (scalar float, seconds since epoch)
            point_0002/
                ...
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read_all(self) -> list[AcquisitionRecord]:
        """Read all acquisition points from the HDF5 file."""
        records: list[AcquisitionRecord] = []
        with h5py.File(self.path, "r") as f:
            specimen_id = f["metadata"].attrs.get("specimen_id", "unknown")
            acq = f["acquisition"]
            for point_id in sorted(acq.keys()):
                grp = acq[point_id]
                records.append(AcquisitionRecord(
                    timestamp=float(grp["timestamp"][()]),
                    position_mm=float(grp["position"][()]),
                    waveform=np.array(grp["waveform"], dtype=np.float32),
                    force_n=float(grp["force"][()]),
                    specimen_id=str(specimen_id),
                    point_id=str(point_id),
                ))
        return records

    def to_dataframe(self) -> pd.DataFrame:
        """Convert acquisition data to a flat DataFrame (without full waveforms)."""
        records = self.read_all()
        return pd.DataFrame([{
            "specimen_id": r.specimen_id,
            "point_id": r.point_id,
            "timestamp": r.timestamp,
            "position_mm": r.position_mm,
            "force_n": r.force_n,
            "waveform_length": len(r.waveform),
            "peak_amplitude": float(np.max(np.abs(r.waveform))),
        } for r in records])

    def get_metadata(self) -> dict[str, str]:
        """Read file-level metadata."""
        with h5py.File(self.path, "r") as f:
            return dict(f["metadata"].attrs)
