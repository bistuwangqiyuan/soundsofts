"""Regional statistics for spatial zones (pipe grid / plate bands)."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..pipeline.step import PipelineStep


class RegionalStats(PipelineStep):
    """Compute per-region statistics from a collection of signals.

    This step works on *batched* data: ``ctx['region_signals']`` should be a
    dict mapping region id to a list of 1-D arrays.  Output is stored in
    ``ctx['region_stats']``.
    """

    def __init__(self) -> None:
        super().__init__(name="RegionalStats")

    def process(self, signal: np.ndarray, ctx: dict[str, Any] | None = None) -> np.ndarray:
        ctx = ctx if ctx is not None else {}
        region_signals: dict[str, list[np.ndarray]] | None = ctx.get("region_signals")
        if region_signals is None:
            return signal

        stats: dict[str, dict[str, float]] = {}
        for rid, sigs in region_signals.items():
            energies = [float(np.sum(s ** 2)) for s in sigs]
            stats[rid] = {
                "mean_energy": float(np.mean(energies)),
                "energy_variance": float(np.var(energies)),
                "count": float(len(sigs)),
                "max_amplitude": float(max(np.max(np.abs(s)) for s in sigs)),
            }
        ctx["region_stats"] = stats
        return signal
