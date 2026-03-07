"""Visual analysis branch using U-Net + ResNet34."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn


class VisualBranch:
    """U-Net inference for visual defect feature extraction."""

    def __init__(self, model: nn.Module, device: str = "cpu") -> None:
        self.model = model.to(device)
        self.model.eval()
        self.device = device

    def predict_mask(self, image_tensor: torch.Tensor) -> np.ndarray:
        with torch.no_grad():
            logits = self.model(image_tensor.to(self.device))
            prob = torch.sigmoid(logits).squeeze().cpu().numpy()
        return prob

    def extract_features(self, image_tensor: torch.Tensor) -> np.ndarray:
        """Extract intermediate encoder features for multi-modal fusion."""
        with torch.no_grad():
            if hasattr(self.model, "encoder"):
                features = self.model.encoder(image_tensor.to(self.device))
                last_feature = features[-1]
                return torch.nn.functional.adaptive_avg_pool2d(last_feature, 1).flatten().cpu().numpy()
        return np.array([])
