"""Single-image and batch inference for U-Net segmentation model."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn


class UNetPredictor:
    """Load a trained U-Net and predict defect masks."""

    def __init__(
        self,
        model: nn.Module,
        checkpoint_path: str | Path,
        image_size: tuple[int, int] = (384, 768),
        threshold: float = 0.5,
        device: str | None = None,
    ) -> None:
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = model.to(self.device)
        self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device, weights_only=True))
        self.model.eval()
        self.image_size = image_size
        self.threshold = threshold

    def predict(self, image: np.ndarray) -> np.ndarray:
        """Predict binary defect mask for a single C-scan image (H, W, 3)."""
        resized = cv2.resize(image, (self.image_size[1], self.image_size[0]))
        tensor = torch.from_numpy(resized.transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
        tensor = tensor.to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            prob = torch.sigmoid(logits).squeeze().cpu().numpy()

        return (prob > self.threshold).astype(np.uint8)

    def predict_batch(self, images: list[np.ndarray]) -> list[np.ndarray]:
        return [self.predict(img) for img in images]
