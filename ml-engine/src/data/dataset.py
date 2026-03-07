"""Data loading and PyTorch Dataset for 1D-CNN."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


class CouplingDataset(Dataset):
    """PyTorch Dataset wrapping the acoustic-force feature matrix.

    Each sample is a (features_tensor, target_scalar) pair.
    """

    def __init__(self, features: np.ndarray, targets: np.ndarray) -> None:
        self.features = torch.tensor(features, dtype=torch.float32)
        self.targets = torch.tensor(targets, dtype=torch.float32)

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]
