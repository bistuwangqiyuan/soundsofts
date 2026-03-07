"""Configurable signal processing pipeline."""

from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from .step import PipelineStep

logger = logging.getLogger(__name__)


class Pipeline:
    """Ordered chain of :class:`PipelineStep` instances.

    Example::

        pipe = Pipeline([DCRemoval(), BandpassFilter(2e6, 8e6, fs=40e6)])
        clean = pipe.run(raw_signal, sampling_rate=40e6)
    """

    def __init__(self, steps: list[PipelineStep] | None = None) -> None:
        self._steps: list[PipelineStep] = steps or []

    def add(self, step: PipelineStep) -> Pipeline:
        self._steps.append(step)
        return self

    def run(self, signal: np.ndarray, ctx: dict[str, Any] | None = None, **kwargs: Any) -> np.ndarray:
        """Execute every enabled step sequentially."""
        if ctx is None:
            ctx = dict(kwargs)
        result = signal.copy()
        for step in self._steps:
            if not step.enabled:
                continue
            t0 = time.perf_counter()
            result = step.process(result, ctx)
            elapsed = time.perf_counter() - t0
            logger.debug("%s finished in %.4f s", step.name, elapsed)
        return result

    def run_batch(self, signals: np.ndarray, ctx: dict[str, Any] | None = None, **kwargs: Any) -> np.ndarray:
        """Process a 2-D array where each row is an independent A-scan."""
        if ctx is None:
            ctx = dict(kwargs)
        return np.array([self.run(s, ctx=ctx) for s in signals])

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        names = [s.name for s in self._steps]
        return f"Pipeline({' → '.join(names)})"
