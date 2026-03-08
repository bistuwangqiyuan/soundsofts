"""Service for computing correlation metrics between ultrasonic features and peel force."""

import asyncio
from typing import Any, List, Optional, Tuple


class CorrelationCalculatorService:
    """Compute Pearson, Spearman, and mutual information between ultrasonic features and peel force."""

    def __init__(self) -> None:
        pass

    async def compute_correlations(
        self,
        ultrasonic_values: List[float],
        force_values: List[float],
        segment_size: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Compute Pearson, Spearman, and mutual information between ultrasonic features and peel force.

        Args:
            ultrasonic_values: Ultrasonic feature values (e.g., amplitude, energy).
            force_values: Corresponding peel force values (N/cm).
            segment_size: If set, compute segment-wise correlations; otherwise global only.

        Returns:
            Dict with pearson, spearman, mutual_info, and optionally segment_correlations.
        """
        return await asyncio.to_thread(
            self._compute_correlations_sync,
            ultrasonic_values,
            force_values,
            segment_size,
        )

    def _compute_correlations_sync(
        self,
        ultrasonic_values: List[float],
        force_values: List[float],
        segment_size: Optional[int],
    ) -> dict[str, Any]:
        import numpy as np
        from scipy import stats
        x = np.asarray(ultrasonic_values, dtype=np.float64)
        y = np.asarray(force_values, dtype=np.float64)
        n = min(len(x), len(y))
        if n < 2:
            return {
                "pearson": 0.0,
                "spearman": 0.0,
                "mutual_info": 0.0,
                "segment_correlations": [],
            }
        x, y = x[:n], y[:n]

        pearson_r, pearson_p = stats.pearsonr(x, y)
        spearman_r, spearman_p = stats.spearmanr(x, y)
        mi = self._mutual_info(x, y)

        result: dict[str, Any] = {
            "pearson": float(pearson_r),
            "spearman": float(spearman_r),
            "mutual_info": float(mi),
        }

        if segment_size and segment_size > 0 and n > segment_size:
            segments = self._segment_correlations(x, y, segment_size)
            result["segment_correlations"] = segments
        else:
            result["segment_correlations"] = [
                {"start": 0, "end": n, "pearson": float(pearson_r), "spearman": float(spearman_r)}
            ]

        return result

    def _mutual_info(self, x: Any, y: Any) -> float:
        """Compute mutual information using scipy.stats."""
        import numpy as np
        try:
            from sklearn.feature_selection import mutual_info_regression

            x_2d = x.reshape(-1, 1)
            mi_scores = mutual_info_regression(x_2d, y, random_state=0)
            return float(mi_scores[0])
        except ImportError:
            # Fallback: use discrete binning with scipy
            n_bins = min(50, max(5, len(x) // 10))
            hist_2d, _, _ = np.histogram2d(x, y, bins=n_bins)
            pxy = hist_2d / hist_2d.sum()
            px = pxy.sum(axis=1, keepdims=True)
            py = pxy.sum(axis=0, keepdims=True)
            px_py = px * py
            nzs = pxy > 0
            mi = np.sum(pxy[nzs] * np.log(pxy[nzs] / px_py[nzs]))
            return float(mi)

    def _segment_correlations(
        self,
        x: Any,
        y: Any,
        segment_size: int,
    ) -> List[dict[str, Any]]:
        """Compute Pearson and Spearman for each segment."""
        from scipy import stats
        segments: List[dict[str, Any]] = []
        n = len(x)
        for start in range(0, n, segment_size):
            end = min(start + segment_size, n)
            if end - start < 2:
                continue
            xs, ys = x[start:end], y[start:end]
            try:
                pr, _ = stats.pearsonr(xs, ys)
                sr, _ = stats.spearmanr(xs, ys)
            except Exception:
                pr, sr = 0.0, 0.0
            segments.append({
                "start": int(start),
                "end": int(end),
                "pearson": float(pr),
                "spearman": float(sr),
            })
        return segments
