"""Tests for IO modules: CSV, HDF5, Parquet, Metadata."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.io import CSVReader, HDF5Reader, ParquetWriter, MetadataManager
from src.io.metadata import SpecimenMeta


class TestCSVReader:
    def test_read_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("ultra,X,y,db,number_bord,force\n")
            f.write("1.0,2.0,3.0,4.0,5,6.0\n")
            f.write("2.0,3.0,4.0,5.0,6,7.0\n")
            path = f.name
        try:
            reader = CSVReader(path)
            df = reader.read()
            assert len(df) == 2
            assert "force" in df.columns
        finally:
            Path(path).unlink()

    def test_read_features_and_target(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("ultra,X,y,force\n")
            f.write("1.0,2.0,3.0,10.0\n")
            f.write("2.0,3.0,4.0,20.0\n")
            path = f.name
        try:
            reader = CSVReader(path)
            X, y = reader.read_features_and_target(target_col="force")
            assert len(X) == 2
            assert len(y) == 2
            assert list(y) == [10.0, 20.0]
        finally:
            Path(path).unlink()


class TestHDF5Reader:
    def test_read_waveform(self):
        with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as f:
            path = f.name
        try:
            import h5py

            with h5py.File(path, "w") as hf:
                g = hf.create_group("spec1/point1")
                g.create_dataset("waveform", data=np.random.randn(100).astype(np.float32))

            reader = HDF5Reader(path)
            wf = reader.read_waveform("spec1", "point1")
            assert len(wf) == 100
            assert wf.dtype == np.float32

            assert reader.list_specimens() == ["spec1"]
            assert reader.list_points("spec1") == ["point1"]

            all_data = reader.read_all("spec1")
            assert "point1" in all_data
            assert len(all_data["point1"]) == 100
        finally:
            Path(path).unlink()


class TestParquetWriter:
    def test_write_parquet(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            path = f.name
        try:
            df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
            writer = ParquetWriter(path)
            writer.write(df)

            read_back = pd.read_parquet(path)
            pd.testing.assert_frame_equal(df, read_back)
        finally:
            Path(path).unlink()


class TestMetadataManager:
    def test_add_get_list(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            f.write("{}")
            path = f.name
        try:
            mgr = MetadataManager(path)
            meta = SpecimenMeta(
                specimen_id="S001",
                specimen_type="pipe",
                diameter_mm=1016.0,
                feature_point_count=100,
            )
            mgr.add(meta)
            mgr.save()

            mgr2 = MetadataManager(path)
            got = mgr2.get("S001")
            assert got is not None
            assert got.specimen_id == "S001"
            assert got.diameter_mm == 1016.0

            all_meta = mgr2.list_all()
            assert len(all_meta) == 1
        finally:
            Path(path).unlink()

    def test_empty_db(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b"{}")
            path = f.name
        try:
            mgr = MetadataManager(path)
            assert mgr.get("nonexistent") is None
            assert mgr.list_all() == []
        finally:
            Path(path).unlink()
