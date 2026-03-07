"""Validate report data: number consistency, terminology checks."""

from __future__ import annotations

from dataclasses import dataclass

from .data_binder import ReportData


@dataclass
class ValidationIssue:
    field: str
    message: str
    severity: str  # "error" | "warning"


def validate_report_data(data: ReportData) -> list[ValidationIssue]:
    """Check for data consistency and terminology issues."""
    issues: list[ValidationIssue] = []

    if data.defect_count < 0:
        issues.append(ValidationIssue("defect_count", "缺陷数量不能为负", "error"))

    if not 0 <= data.defect_area_ratio <= 1:
        issues.append(ValidationIssue("defect_area_ratio", "缺陷面积占比应在 0-1 之间", "error"))

    if data.fusion_result.predicted_force < 0:
        issues.append(ValidationIssue("predicted_force", "预测粘接力不能为负", "error"))

    if not data.specimen_id:
        issues.append(ValidationIssue("specimen_id", "试样编号不能为空", "error"))

    return issues
