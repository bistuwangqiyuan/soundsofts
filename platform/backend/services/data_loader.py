"""Load HDF5 and CSV data for visualization."""

import asyncio
from pathlib import Path
from typing import Any, Optional

import numpy as np

from core.config import get_settings

settings = get_settings()


class DataLoaderService:
    """Load waveform and spectrum data from HDF5/CSV files."""

    def __init__(self) -> None:
        self._upload_dir = Path(settings.upload_dir)

    def _resolve_path(self, file_id: str) -> Optional[Path]:
        """Resolve file_id to actual path."""
        for ext in (".h5", ".hdf5", ".csv"):
            p = self._upload_dir / f"{file_id}{ext}"
            if p.exists():
                return p
        for p in self._upload_dir.glob(f"{file_id}*"):
            if p.suffix.lower() in (".h5", ".hdf5", ".csv"):
                return p
        return None

    async def get_file_info(self, path: str) -> dict[str, Any]:
        """Get file metadata (specimen count, point count, etc.)."""
        return await asyncio.to_thread(self._get_file_info_sync, path)

    def _get_file_info_sync(self, path: str) -> dict[str, Any]:
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix in (".h5", ".hdf5"):
            return self._get_hdf5_info(path)
        if suffix == ".csv":
            return self._get_csv_info(path)
        return {"file_type": "unknown", "specimen_count": 0, "point_count": 0}

    def _get_hdf5_info(self, path: str) -> dict[str, Any]:
        try:
            import h5py

            with h5py.File(path, "r") as f:
                specimens = list(f.keys())
                total_points = sum(
                    len([k for k in f[s].keys() if "waveform" in f[s][k]])
                    for s in specimens
                )
                return {
                    "file_type": "hdf5",
                    "specimen_count": len(specimens),
                    "point_count": total_points,
                }
        except Exception:
            return {"file_type": "hdf5", "specimen_count": 0, "point_count": 0}

    def _get_csv_info(self, path: str) -> dict[str, Any]:
        try:
            import pandas as pd

            df = pd.read_csv(path, nrows=1000)
            rows = len(df)
            cols = len(df.columns)
            return {
                "file_type": "csv",
                "specimen_count": 1,
                "point_count": max(rows, 1),
            }
        except Exception:
            return {"file_type": "csv", "specimen_count": 0, "point_count": 0}

    async def load_waveform(
        self,
        file_id: str,
        specimen: str = "",
        point: str = "",
        row: int = 0,
    ) -> Optional[dict[str, Any]]:
        """Load waveform data. Returns dict with x, y, sampling_rate."""
        path = self._resolve_path(file_id)
        if not path:
            return None
        return await asyncio.to_thread(
            self._load_waveform_sync, str(path), specimen, point, row
        )

    def _load_waveform_sync(
        self,
        path: str,
        specimen: str,
        point: str,
        row: int,
    ) -> Optional[dict[str, Any]]:
        p = Path(path)
        fs = 40e6  # default sampling rate
        if p.suffix.lower() in (".h5", ".hdf5"):
            try:
                import h5py

                with h5py.File(path, "r") as f:
                    if specimen and point:
                        wf = np.array(f[specimen][point]["waveform"], dtype=np.float64)
                    else:
                        specimens = list(f.keys())
                        pts = list(f[specimens[0]].keys()) if specimens else []
                        if not pts:
                            return None
                        wf = np.array(
                            f[specimens[0]][pts[0]]["waveform"], dtype=np.float64
                        )
                    n = len(wf)
                    x = np.linspace(0, (n - 1) / fs, n).tolist()
                    return {"x": x, "y": wf.tolist(), "sampling_rate": fs}
            except Exception:
                return None
        if p.suffix.lower() == ".csv":
            try:
                import pandas as pd

                df = pd.read_csv(path)
                if df.empty:
                    return None
                col = df.iloc[:, 0] if len(df.columns) > 0 else df.iloc[:, 0]
                y = col.values.astype(np.float64)
                n = len(y)
                x = np.linspace(0, (n - 1) / fs, n).tolist()
                return {"x": x, "y": y.tolist(), "sampling_rate": fs}
            except Exception:
                return None
        return None

    async def load_spectrum(
        self,
        file_id: str,
        specimen: str = "",
        point: str = "",
        row: int = 0,
    ) -> Optional[dict[str, Any]]:
        """Load FFT spectrum. Returns dict with freq, magnitude."""
        wf_data = await self.load_waveform(file_id, specimen, point, row)
        if wf_data is None:
            return None
        return await asyncio.to_thread(
            self._compute_spectrum,
            wf_data["y"],
            wf_data["sampling_rate"],
        )

    def _compute_spectrum(self, y: list, fs: float) -> dict[str, Any]:
        arr = np.array(y, dtype=np.float64)
        n = len(arr)
        fft_vals = np.fft.rfft(arr)
        magnitude = np.abs(fft_vals) / n
        freq = np.fft.rfftfreq(n, 1 / fs)
        return {
            "freq": freq.tolist(),
            "magnitude": magnitude.tolist(),
        }

    async def list_point_cards(
        self,
        file_id: Optional[str] = None,
        specimen: Optional[str] = None,
        defect_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List data point cards with optional filters. Returns list of DataPointCard dicts."""
        return await asyncio.to_thread(
            self._list_point_cards_sync,
            file_id,
            specimen,
            defect_type,
            limit,
            offset,
        )

    def _list_point_cards_sync(
        self,
        file_id: Optional[str],
        specimen: Optional[str],
        defect_type: Optional[str],
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        cards: list[dict[str, Any]] = []
        for p in self._upload_dir.glob("*"):
            if p.suffix.lower() not in (".h5", ".hdf5", ".csv"):
                continue
            if file_id and p.stem != file_id and file_id not in p.name:
                continue
            try:
                if p.suffix.lower() in (".h5", ".hdf5"):
                    import h5py

                    with h5py.File(p, "r") as f:
                        for spec in f.keys():
                            if specimen and spec != specimen:
                                continue
                            for pt in f[spec].keys():
                                if "waveform" not in f[spec][pt]:
                                    continue
                                wf = np.array(f[spec][pt]["waveform"], dtype=np.float64)
                                thumb = wf[:: max(1, len(wf) // 64)].tolist()
                                point_id = f"{p.stem}_{spec}_{pt}"
                                cards.append({
                                    "point_id": point_id,
                                    "file_id": p.stem,
                                    "specimen": spec,
                                    "x": 0.0,
                                    "y": 0.0,
                                    "waveform_thumbnail": thumb,
                                    "envelope": [],
                                    "defect_type": None,
                                    "defect_confidence": 0.0,
                                    "predicted_force_n_per_cm": None,
                                    "actual_force_n_per_cm": None,
                                    "prediction_error": None,
                                    "features": {},
                                })
                                if len(cards) >= offset + limit:
                                    return cards[offset : offset + limit]
            except Exception:
                pass
        return cards[offset : offset + limit]

    async def get_point_card(
        self,
        point_id: str,
        include_waveform: bool = True,
        include_features: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Get a single data point card by ID."""
        return await asyncio.to_thread(
            self._get_point_card_sync,
            point_id,
            include_waveform,
            include_features,
        )

    def _get_point_card_sync(
        self,
        point_id: str,
        include_waveform: bool,
        include_features: bool,
    ) -> Optional[dict[str, Any]]:
        parts = point_id.split("_", 2)
        if len(parts) < 3:
            return None
        file_stem, spec, pt = parts[0], parts[1], "_".join(parts[2:])
        path = self._resolve_path(file_stem)
        if not path or path.suffix.lower() not in (".h5", ".hdf5"):
            return None
        try:
            import h5py

            with h5py.File(path, "r") as f:
                if spec not in f or pt not in f[spec]:
                    return None
                wf = np.array(f[spec][pt]["waveform"], dtype=np.float64)
                thumb = wf[:: max(1, len(wf) // 64)].tolist() if include_waveform else []
                return {
                    "point_id": point_id,
                    "file_id": file_stem,
                    "specimen": spec,
                    "x": 0.0,
                    "y": 0.0,
                    "waveform_thumbnail": thumb,
                    "envelope": [],
                    "defect_type": None,
                    "defect_confidence": 0.0,
                    "predicted_force_n_per_cm": None,
                    "actual_force_n_per_cm": None,
                    "prediction_error": None,
                    "features": {} if include_features else {},
                }
        except Exception:
            return None

    async def get_batch_cards(
        self,
        point_ids: list[str],
        include_waveform: bool = True,
        include_features: bool = False,
    ) -> dict[str, Any]:
        """Get multiple data point cards. Returns BatchCardResponse dict."""
        cards: list[dict[str, Any]] = []
        missing_ids: list[str] = []
        for pid in point_ids:
            card = await self.get_point_card(
                point_id=pid,
                include_waveform=include_waveform,
                include_features=include_features,
            )
            if card:
                cards.append(card)
            else:
                missing_ids.append(pid)
        return {
            "cards": cards,
            "total": len(cards),
            "missing_ids": missing_ids,
        }
