"""Tests for data_reader module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import h5py
import numpy as np
import pytest

from python_interface.data_reader import AcquisitionDataReader, AcquisitionRecord


@pytest.fixture
def sample_hdf5_path(tmp_path: Path) -> Path:
    """Create a minimal HDF5 file matching Data_Storage.vi structure."""
    path = tmp_path / "sample.h5"
    with h5py.File(path, "w") as f:
        meta = f.create_group("metadata")
        meta.attrs["specimen_id"] = "SPEC-001"
        meta.attrs["operator"] = "test"
        meta.attrs["date"] = "2026-03-08"
        meta.attrs["equipment"] = "NI USB-6363"
        acq = f.create_group("acquisition")
        for i in (1, 2):
            grp = acq.create_group(f"point_{i:04d}")
            grp.create_dataset("timestamp", data=np.float64(1.0 + i))
            grp.create_dataset("position", data=np.float32(10.0 * i))
            grp.create_dataset("force", data=np.float32(5.0 * i))
            wf = np.arange(100, dtype=np.float32) * 0.01
            grp.create_dataset("waveform", data=wf)
    return path


def test_read_all(sample_hdf5_path: Path) -> None:
    reader = AcquisitionDataReader(sample_hdf5_path)
    records = reader.read_all()
    assert len(records) == 2
    assert records[0].specimen_id == "SPEC-001"
    assert records[0].point_id == "point_0001"
    assert records[0].timestamp == 2.0
    assert records[0].position_mm == 10.0
    assert records[0].force_n == 5.0
    assert len(records[0].waveform) == 100
    assert records[1].point_id == "point_0002"
    assert records[1].position_mm == 20.0


def test_to_dataframe(sample_hdf5_path: Path) -> None:
    reader = AcquisitionDataReader(sample_hdf5_path)
    df = reader.to_dataframe()
    assert len(df) == 2
    assert list(df.columns) == [
        "specimen_id", "point_id", "timestamp", "position_mm", "force_n",
        "waveform_length", "peak_amplitude",
    ]
    assert df["waveform_length"].iloc[0] == 100
    assert df["peak_amplitude"].iloc[0] == pytest.approx(0.99, rel=1e-2)


def test_get_metadata(sample_hdf5_path: Path) -> None:
    reader = AcquisitionDataReader(sample_hdf5_path)
    meta = reader.get_metadata()
    assert meta["specimen_id"] == "SPEC-001"
    assert meta["operator"] == "test"
    assert meta["date"] == "2026-03-08"
