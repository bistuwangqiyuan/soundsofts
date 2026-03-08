"""U-Net training loop with AdamW, OneCycleLR, and early stopping."""

from __future__ import annotations

import logging
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import OneCycleLR
from torch.utils.data import DataLoader

from ..models.loss import BCEDiceLoss
from ..models.metrics import iou_score, dice_score

logger = logging.getLogger(__name__)


class UNetTrainer:
    """Manages the full training lifecycle."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        lr: float = 3e-4,
        weight_decay: float = 1e-4,
        epochs: int = 100,
        patience: int = 15,
        bce_weight: float = 0.5,
        dice_weight: float = 0.5,
        checkpoint_dir: str | Path = "checkpoints",
        device: str | None = None,
    ) -> None:
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.epochs = epochs
        self.patience = patience
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.criterion = BCEDiceLoss(bce_weight=bce_weight, dice_weight=dice_weight)
        self.optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.scheduler = OneCycleLR(
            self.optimizer, max_lr=lr, steps_per_epoch=len(train_loader), epochs=epochs
        )

    def train(self) -> dict[str, float]:
        best_iou = 0.0
        patience_counter = 0

        for epoch in range(self.epochs):
            train_loss = self._train_epoch()
            val_metrics = self._validate()

            logger.info(
                "Epoch %d/%d — loss=%.4f, val_IoU=%.4f, val_Dice=%.4f",
                epoch + 1, self.epochs, train_loss, val_metrics["iou"], val_metrics["dice"],
            )

            if val_metrics["iou"] > best_iou:
                best_iou = val_metrics["iou"]
                patience_counter = 0
                torch.save(self.model.state_dict(), self.checkpoint_dir / "best_model.pth")
            else:
                patience_counter += 1
                if patience_counter >= self.patience:
                    logger.info("Early stopping at epoch %d", epoch + 1)
                    break

        return {"best_iou": best_iou}

    def _train_epoch(self) -> float:
        self.model.train()
        total_loss = 0.0
        for batch in self.train_loader:
            images = batch["image"].to(self.device)
            masks = batch["mask"].to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(images)
            loss = self.criterion(logits, masks)
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()

            total_loss += loss.item()
        n_batches = len(self.train_loader)
        return total_loss / n_batches if n_batches else 0.0

    def _validate(self) -> dict[str, float]:
        self.model.eval()
        ious, dices = [], []
        with torch.no_grad():
            for batch in self.val_loader:
                images = batch["image"].to(self.device)
                masks = batch["mask"].to(self.device)
                logits = self.model(images)
                ious.append(iou_score(logits, masks))
                dices.append(dice_score(logits, masks))
        n = len(ious)
        if n == 0:
            return {"iou": 0.0, "dice": 0.0}
        return {"iou": sum(ious) / n, "dice": sum(dices) / n}
