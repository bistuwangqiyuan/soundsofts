"""Data quality validation before model training."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ValidationResult:
    is_valid: bool
    total_rows: int
    missing_count: int
    duplicate_count: int
    inf_count: int
    messages: list[str]


def validate_dataset(df: pd.DataFrame, target_col: str = "force") -> ValidationResult:
    messages: list[str] = []
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    inf_count = int(np.isinf(df.select_dtypes(include=[np.number])).sum().sum())

    if missing > 0:
        messages.append(f"{missing} missing values detected")
    if duplicates > 0:
        messages.append(f"{duplicates} duplicate rows detected")
    if inf_count > 0:
        messages.append(f"{inf_count} infinite values detected")
    if target_col not in df.columns:
        messages.append(f"Target column '{target_col}' not found")

    is_valid = len(messages) == 0

    return ValidationResult(
        is_valid=is_valid,
        total_rows=len(df),
        missing_count=missing,
        duplicate_count=duplicates,
        inf_count=inf_count,
        messages=messages,
    )
