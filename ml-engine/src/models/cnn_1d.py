"""1D Convolutional Neural Network for end-to-end waveform regression."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ..data.dataset import CouplingDataset
from .base_model import BaseModel


class _CNN1DNet(nn.Module):
    """1D-CNN architecture: Conv→BN→ReLU→Pool × 3 → FC."""

    def __init__(self, in_features: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool1d(1),
        )
        self.regressor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        return self.regressor(self.features(x)).squeeze(-1)


class CNN1DModel(BaseModel):
    name = "1D-CNN"

    def __init__(
        self,
        lr: float = 1e-3,
        epochs: int = 50,
        batch_size: int = 64,
        **kwargs: Any,
    ) -> None:
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net: _CNN1DNet | None = None

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs: Any) -> None:
        self.net = _CNN1DNet(X.shape[1]).to(self.device)
        dataset = CouplingDataset(X, y)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        optimizer = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        criterion = nn.MSELoss()

        self.net.train()
        for epoch in range(self.epochs):
            for xb, yb in loader:
                xb, yb = xb.to(self.device), yb.to(self.device)
                optimizer.zero_grad()
                loss = criterion(self.net(xb), yb)
                loss.backward()
                optimizer.step()

    def predict(self, X: np.ndarray) -> np.ndarray:
        assert self.net is not None
        self.net.eval()
        with torch.no_grad():
            t = torch.tensor(X, dtype=torch.float32).to(self.device)
            return self.net(t).cpu().numpy()

    def get_params(self) -> dict[str, Any]:
        return {"lr": self.lr, "epochs": self.epochs, "batch_size": self.batch_size}

    def save(self, path: str | Path) -> None:
        assert self.net is not None
        torch.save(self.net.state_dict(), path)

    def load(self, path: str | Path) -> None:
        state = torch.load(path, map_location=self.device, weights_only=True)
        in_features = state["features.0.weight"].shape[1]
        self.net = _CNN1DNet(in_features).to(self.device)
        self.net.load_state_dict(state)
