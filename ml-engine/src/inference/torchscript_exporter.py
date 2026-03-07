"""Export PyTorch models to TorchScript for TorchServe deployment."""

from __future__ import annotations

from pathlib import Path

import torch


def export_to_torchscript(
    model: torch.nn.Module,
    example_input: torch.Tensor,
    output_path: str | Path,
) -> None:
    model.eval()
    scripted = torch.jit.trace(model, example_input)
    scripted.save(str(output_path))
