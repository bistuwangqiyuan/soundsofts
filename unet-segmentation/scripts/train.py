"""U-Net training entry point."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml
import torch
from torch.utils.data import DataLoader

from src.models.unet import build_unet
from src.data.dataset import CScanDataset
from src.data.augmentation import get_train_transforms, get_val_transforms
from src.training.trainer import UNetTrainer


def main() -> None:
    cfg_path = Path("configs/train_config.yaml")
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    model = build_unet(
        encoder=cfg["model"]["encoder"],
        encoder_weights=cfg["model"]["encoder_weights"],
        in_channels=cfg["model"]["in_channels"],
        classes=cfg["model"]["classes"],
    )

    aug_cfg = cfg.get("augmentation", {})
    train_transform = get_train_transforms(aug_cfg)
    val_transform = get_val_transforms()

    img_size = tuple(cfg["data"]["image_size"])

    train_ds = CScanDataset("data/splits/train", "data/masks", image_size=img_size, transform=train_transform)
    val_ds = CScanDataset("data/splits/val", "data/masks", image_size=img_size, transform=val_transform)

    train_loader = DataLoader(train_ds, batch_size=cfg["training"]["batch_size"], shuffle=True, num_workers=4)
    val_loader = DataLoader(val_ds, batch_size=cfg["training"]["batch_size"], shuffle=False, num_workers=4)

    trainer = UNetTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"],
        epochs=cfg["training"]["epochs"],
        patience=cfg["training"]["early_stopping_patience"],
        bce_weight=cfg["loss"]["bce_weight"],
        dice_weight=cfg["loss"]["dice_weight"],
    )

    result = trainer.train()
    print(f"Training complete. Best IoU: {result['best_iou']:.4f}")


if __name__ == "__main__":
    main()
