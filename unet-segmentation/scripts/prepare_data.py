"""Prepare C-scan dataset: split images into train/val/test. Masks stay in one dir."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
from src.data.splitter import split_dataset


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cfg_path = root / "configs" / "train_config.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        data_cfg = cfg.get("data", {})
        train_ratio = data_cfg.get("train_ratio", 0.7)
        val_ratio = data_cfg.get("val_ratio", 0.15)
    else:
        train_ratio, val_ratio = 0.7, 0.15

    image_dir = root / "data" / "images"
    output_dir = root / "data" / "splits"
    if not image_dir.exists():
        print(f"Image directory not found: {image_dir}")
        print("Create it and put C-scan images there. Masks go in data/masks/ with same filenames.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    splits = split_dataset(image_dir, output_dir, train_ratio=train_ratio, val_ratio=val_ratio, seed=42)
    print(f"Split: train={len(splits['train'])}, val={len(splits['val'])}, test={len(splits['test'])}")
    print(f"Images copied to {output_dir}. Place masks in data/masks/ with matching filenames.")


if __name__ == "__main__":
    main()
