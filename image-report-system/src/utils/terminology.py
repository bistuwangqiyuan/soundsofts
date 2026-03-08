"""Unified terminology and metric standard management."""

from __future__ import annotations

UNIFIED_TERMS: dict[str, str] = {
    "PE": "聚乙烯",
    "补口": "聚乙烯补口",
    "剥离强度": "剥离强度（N/cm）",
    "气泡": "气泡缺陷",
    "弱粘": "弱粘接缺陷",
    "脱粘": "脱粘缺陷",
    "正常": "正常粘接",
    "MAPE": "平均绝对百分比误差",
    "IoU": "交并比",
    "Dice": "Dice系数",
}

TERMINOLOGY = UNIFIED_TERMS  # API compatibility

METRIC_STANDARDS: dict[str, dict[str, float]] = {
    "peel_strength_min": {"value": 70.0, "unit_factor": 1.0},
    "mape_threshold": {"value": 10.0, "unit_factor": 1.0},
    "analysis_time_max": {"value": 10.0, "unit_factor": 1.0},
}


def normalize_term(term: str) -> str:
    return UNIFIED_TERMS.get(term, term)
