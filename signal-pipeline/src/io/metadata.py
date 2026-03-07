"""Metadata management for specimens and scan points."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class SpecimenMeta:
    specimen_id: str
    specimen_type: str  # "pipe" or "plate"
    diameter_mm: float | None = None  # for pipe: 1016 or 1219
    dimensions_mm: str | None = None  # for plate: "300x300" or "600x600"
    defect_types: list[str] | None = None
    feature_point_count: int = 0


class MetadataManager:
    """CRUD operations for specimen metadata stored as JSON."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._data: dict[str, SpecimenMeta] = {}
        if self.db_path.exists():
            self._load()

    def _load(self) -> None:
        raw = json.loads(self.db_path.read_text(encoding="utf-8"))
        for sid, info in raw.items():
            self._data[sid] = SpecimenMeta(**info)

    def save(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {sid: asdict(m) for sid, m in self._data.items()}
        self.db_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, meta: SpecimenMeta) -> None:
        self._data[meta.specimen_id] = meta

    def get(self, specimen_id: str) -> SpecimenMeta | None:
        return self._data.get(specimen_id)

    def list_all(self) -> list[SpecimenMeta]:
        return list(self._data.values())
