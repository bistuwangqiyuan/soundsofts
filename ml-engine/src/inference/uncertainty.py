"""Monte Carlo Dropout uncertainty estimation for 1D-CNN."""

from __future__ import annotations

import numpy as np
import torch

from ..models.cnn_1d import _CNN1DNet


def mc_dropout_predict(
    model: _CNN1DNet,
    X: np.ndarray,
    n_forward: int = 50,
    device: str = "cpu",
) -> tuple[np.ndarray, np.ndarray]:
    """Return (mean_predictions, std_predictions) over *n_forward* stochastic passes."""
    model.train()  # keep dropout active
    tensor = torch.tensor(X, dtype=torch.float32).to(device)

    preds = []
    with torch.no_grad():
        for _ in range(n_forward):
            preds.append(model(tensor).cpu().numpy())

    preds_arr = np.stack(preds, axis=0)
    return preds_arr.mean(axis=0), preds_arr.std(axis=0)
