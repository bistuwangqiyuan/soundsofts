"""Abstract base class for all pipeline processing steps."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class PipelineStep(ABC):
    """Base class that every processing step must inherit."""

    def __init__(self, name: str | None = None, enabled: bool = True) -> None:
        self.name = name or self.__class__.__name__
        self.enabled = enabled

    @abstractmethod
    def process(self, signal: np.ndarray, ctx: dict[str, Any] | None = None) -> np.ndarray:
        """Transform *signal* in-place or return a new array.

        Args:
            signal: 1-D float array representing one A-scan waveform.
            ctx: Mutable context dict (sampling_rate, features, metadata, etc.).

        Returns:
            Processed signal array.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(enabled={self.enabled})"
