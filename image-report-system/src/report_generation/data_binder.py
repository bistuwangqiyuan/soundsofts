"""Bind analysis data to report template."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..multimodal_fusion.fusion import FusionResult
from .template_engine import ReportTemplate


@dataclass
class ReportData:
    specimen_id: str
    inspection_date: str
    operator: str
    equipment: str
    fusion_result: FusionResult
    defect_count: int
    defect_area_ratio: float
    image_path: str | None = None


def bind_data_to_report(template: ReportTemplate, data: ReportData) -> ReportTemplate:
    """Populate a report template with analysis data."""
    template.add_title("聚乙烯补口粘接质量超声检测报告")

    template.add_section("一、检测基本信息")
    template.add_table(
        ["项目", "内容"],
        [
            ["试样编号", data.specimen_id],
            ["检测日期", data.inspection_date],
            ["操作人员", data.operator],
            ["检测设备", data.equipment],
            ["报告生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ],
    )

    template.add_section("二、检测结果总览")
    template.add_table(
        ["指标", "结果"],
        [
            ["缺陷数量", str(data.defect_count)],
            ["缺陷面积占比", f"{data.defect_area_ratio:.2%}"],
            ["预测粘接力", f"{data.fusion_result.predicted_force:.1f} N/cm"],
            ["综合质量判定", data.fusion_result.overall_quality],
            ["置信度", f"{data.fusion_result.confidence:.2%}"],
        ],
    )

    template.add_section("三、工艺规则校核")
    for check in data.fusion_result.rule_checks:
        status = "✓ 通过" if check.passed else "✗ 未通过"
        template.add_paragraph(f"[{status}] {check.rule_name}：{check.message}")

    if data.image_path:
        template.add_section("四、缺陷分割结果")
        template.add_image(data.image_path)

    template.add_section("五、结论与建议")
    if data.fusion_result.overall_quality == "合格":
        template.add_paragraph("本次检测结果表明，试样粘接质量满足标准要求，建议予以验收通过。")
    elif data.fusion_result.overall_quality == "不合格":
        template.add_paragraph("本次检测结果表明，试样粘接质量未达到标准要求，建议进行返工处理。")
    else:
        template.add_paragraph("本次检测结果需人工复核确认，建议安排现场复检。")

    return template
