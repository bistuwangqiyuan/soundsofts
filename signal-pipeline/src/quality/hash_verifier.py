"""Data integrity verification via SHA-256 hashing."""

from __future__ import annotations

import hashlib
from pathlib import Path


class HashVerifier:
    """Compute and verify SHA-256 checksums for raw data files."""

    @staticmethod
    def compute(filepath: str | Path) -> str:
        sha = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @staticmethod
    def verify(filepath: str | Path, expected_hash: str) -> bool:
        return HashVerifier.compute(filepath) == expected_hash
