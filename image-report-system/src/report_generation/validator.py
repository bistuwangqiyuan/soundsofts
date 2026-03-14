"""Validate report data: number consistency, terminology checks, cross-validation."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .data_binder import ReportData


@dataclass
class ValidationIssue:
    field: str
    message: str
    severity: str  # "error" | "warning"


def validate_report_data(data: ReportData) -> list[ValidationIssue]:
    """Run 10+ validation rules for data consistency and terminology issues."""
    issues: list[ValidationIssue] = []

    # Required fields
    if not data.specimen_id:
        issues.append(ValidationIssue("specimen_id", "试样编号不能为空", "error"))

    if not data.operator:
        issues.append(ValidationIssue("operator", "操作人员不能为空", "error"))

    if not data.equipment:
        issues.append(ValidationIssue("equipment", "检测设备不能为空", "error"))

    # Numeric range checks
    if data.defect_count < 0:
        issues.append(ValidationIssue("defect_count", "缺陷数量不能为负", "error"))

    if not 0 <= data.defect_area_ratio <= 1:
        issues.append(ValidationIssue("defect_area_ratio", "缺陷面积占比应在 0-1 之间", "error"))

    if data.fusion_result.predicted_force < 0:
        issues.append(ValidationIssue("predicted_force", "预测粘接力不能为负", "error"))

    if not 0 <= data.fusion_result.confidence <= 1:
        issues.append(ValidationIssue("confidence", "置信度应在 0-1 之间", "error"))

    # Date format
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(data.inspection_date):
        issues.append(ValidationIssue("inspection_date", "日期格式应为 YYYY-MM-DD", "warning"))

    # Cross-consistency: defect count vs defect list
    if data.defects and len(data.defects) != data.defect_count:
        issues.append(ValidationIssue(
            "defect_count",
            f"缺陷数量 ({data.defect_count}) 与缺陷列表长度 ({len(data.defects)}) 不一致",
            "warning",
        ))

    # High defect ratio warning
    if data.defect_area_ratio > 0.10:
        issues.append(ValidationIssue(
            "defect_area_ratio",
            f"缺陷面积占比 {data.defect_area_ratio:.2%} 偏高，建议复核",
            "warning",
        ))

    # Low confidence warning
    if 0 < data.fusion_result.confidence < 0.5:
        issues.append(ValidationIssue(
            "confidence",
            f"融合置信度 {data.fusion_result.confidence:.2%} 偏低，建议人工复核",
            "warning",
        ))

    # Quality vs rules consistency
    all_rules_passed = all(c.passed for c in data.fusion_result.rule_checks)
    if data.fusion_result.overall_quality == "合格" and not all_rules_passed:
        issues.append(ValidationIssue(
            "overall_quality",
            "质量判定为 \"合格\" 但存在未通过的规则校核项",
            "warning",
        ))

    return issues
