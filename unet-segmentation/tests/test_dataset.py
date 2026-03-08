"""Tests for CScanDataset and data utilities."""

from __future__ import annotations

import pytest

pytest.importorskip("cv2")
from src.data.dataset import CScanDataset
from src.data.splitter import split_dataset


class TestCScanDataset:
    def test_dataset_length(self, temp_data_dir):
        ds = CScanDataset(
            temp_data_dir / "images",
            temp_data_dir / "masks",
            image_size=(64, 128),
        )
        assert len(ds) == 5

    def test_dataset_item_shape(self, temp_data_dir):
        ds = CScanDataset(
            temp_data_dir / "images",
            temp_data_dir / "masks",
            image_size=(64, 128),
        )
        item = ds[0]
        assert item["image"].shape == (3, 64, 128)
        assert item["mask"].shape == (1, 64, 128)
        assert "filename" in item

    def test_dataset_with_transform(self, temp_data_dir):
        pytest.importorskip("albumentations")
        from src.data.augmentation import get_train_transforms
        transform = get_train_transforms({})
        ds = CScanDataset(
            temp_data_dir / "images",
            temp_data_dir / "masks",
            image_size=(64, 128),
            transform=transform,
        )
        item = ds[0]
        assert item["image"].shape == (3, 64, 128)
        assert item["mask"].shape == (1, 64, 128)


class TestSplitter:
    def test_split_dataset(self, temp_data_dir):
        output_dir = temp_data_dir / "splits"
        splits = split_dataset(
            temp_data_dir / "images",
            output_dir,
            train_ratio=0.6,
            val_ratio=0.2,
            seed=42,
        )
        assert len(splits["train"]) == 3
        assert len(splits["val"]) == 1
        assert len(splits["test"]) == 1
        assert (output_dir / "train").exists()
        assert (output_dir / "val").exists()
        assert (output_dir / "test").exists()
