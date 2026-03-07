"""Split image dataset into train/val/test sets."""

from __future__ import annotations

import random
import shutil
from pathlib import Path


def split_dataset(
    image_dir: str | Path,
    output_dir: str | Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> dict[str, list[str]]:
    """Copy images into train/val/test subdirectories."""
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)
    files = sorted([f.name for f in image_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".bmp", ".tiff")])

    random.seed(seed)
    random.shuffle(files)

    n = len(files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    splits = {
        "train": files[:n_train],
        "val": files[n_train:n_train + n_val],
        "test": files[n_train + n_val:],
    }

    for split_name, split_files in splits.items():
        split_dir = output_dir / split_name
        split_dir.mkdir(parents=True, exist_ok=True)
        for f in split_files:
            shutil.copy2(image_dir / f, split_dir / f)

    return splits
