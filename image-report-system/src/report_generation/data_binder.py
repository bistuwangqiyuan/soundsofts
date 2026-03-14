"""Bind analysis data to report template -- 8-section professional report."""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from ..multimodal_fusion.fusion import FusionResult
from .template_engine import ReportTemplate

if TYPE_CHECKING:
    from ..pipeline import AnalysisResult, DetectedDefect


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
    defects: list[DetectedDefect] = field(default_factory=list)
    analysis_result: AnalysisResult | None = None
    organization: str = "超声检测实验室"
    standard_ref: str = "GB/T 23257-2017"


def _generate_report_id(specimen_id: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M")
    return f"IRS-{specimen_id}-{ts}"


def bind_data_to_report(template: ReportTemplate, data: ReportData) -> ReportTemplate:
    """Populate a report template with 8 professional sections."""
    report_id = _generate_report_id(data.specimen_id)

    # Header / footer
    template.add_header_footer(report_id, data.organization)

    # Section 0: Cover page
    template.add_cover_page(
        title="聚乙烯补口粘接质量超声检测报告",
        subtitle="C扫图像分析 · 多模态融合决策 · 自动报告生成",
        org=data.organization,
        date=data.inspection_date,
        report_id=report_id,
    )

    # Section 1: Inspection metadata
    template.add_section("一、检测基本信息")
    template.add_table(
        ["项目", "内容"],
        [
            ["报告编号", report_id],
            ["试样编号", data.specimen_id],
            ["检测日期", data.inspection_date],
            ["操作人员", data.operator],
            ["检测设备", data.equipment],
            ["执行标准", data.standard_ref],
            ["报告生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ],
    )

    # Section 2: Results overview
    template.add_section("二、检测结果总览")
    quality = data.fusion_result.overall_quality
    verdict_text = {"合格": "PASS ✓", "不合格": "FAIL ✗", "待复核": "REVIEW ◎"}.get(quality, quality)
    template.add_table(
        ["指标", "结果"],
        [
            ["综合质量判定", f"{quality}  ({verdict_text})"],
            ["融合置信度", f"{data.fusion_result.confidence:.2%}"],
            ["缺陷数量", str(data.defect_count)],
            ["缺陷面积占比", f"{data.defect_area_ratio:.2%}"],
            ["预测粘接力", f"{data.fusion_result.predicted_force:.1f} N/cm"],
        ],
    )

    # Branch scores
    if data.fusion_result.branch_scores:
        template.add_section("融合分支评分", level=2)
        template.add_table(
            ["分支", "原始得分", "权重", "加权得分"],
            [
                [b.name, f"{b.score:.3f}", f"{b.weight:.0%}", f"{b.weighted:.3f}"]
                for b in data.fusion_result.branch_scores
            ],
        )

    # Section 3: Defect detail table
    template.add_section("三、缺陷明细")
    if data.defects:
        template.add_paragraph(f"共检出 {len(data.defects)} 处缺陷，详见下表：", indent=True)
        template.add_defect_detail_table(data.defects)
    else:
        template.add_paragraph("本次检测未检出缺陷。", indent=True)

    # Section 4: Analysis images
    template.add_section("四、缺陷分割与可视化")
    _embed_analysis_images(template, data)

    # Section 5: Rule check results
    template.add_section("五、工艺规则校核")
    for check in data.fusion_result.rule_checks:
        status = "✓ 通过" if check.passed else "✗ 未通过"
        template.add_paragraph(f"[{status}] {check.rule_name}：{check.message}", indent=True)

    passed = sum(1 for c in data.fusion_result.rule_checks if c.passed)
    total = len(data.fusion_result.rule_checks)
    template.add_paragraph(f"\n规则校核汇总：{passed}/{total} 项达标。", bold=True)

    # Section 6: Statistical charts
    template.add_section("六、统计分析")
    _embed_charts(template, data)

    # Section 7: Conclusion
    template.add_page_break()
    template.add_section("七、结论与建议")
    if quality == "合格":
        template.add_paragraph(
            "本次检测结果表明，试样聚乙烯补口粘接质量满足 GB/T 23257 标准要求。"
            f"共检出 {data.defect_count} 处缺陷，缺陷面积占比 {data.defect_area_ratio:.2%}，"
            f"预测粘接力 {data.fusion_result.predicted_force:.1f} N/cm，"
            "各项指标均达标。建议予以验收通过。",
            indent=True,
        )
    elif quality == "不合格":
        template.add_paragraph(
            "本次检测结果表明，试样粘接质量未达到标准要求。"
            f"共检出 {data.defect_count} 处缺陷，缺陷面积占比 {data.defect_area_ratio:.2%}。"
            "建议进行返工处理后重新检测。",
            indent=True,
        )
    else:
        template.add_paragraph(
            "本次检测结果需人工复核确认。部分指标处于临界状态，"
            "建议安排现场复检或由高级检测人员审核。",
            indent=True,
        )

    # Section 8: Standard reference
    template.add_section("八、引用标准")
    standards = [
        "GB/T 23257-2017 埋地钢质管道聚乙烯防腐层",
        "SY/T 0413-2002 埋地钢质管道聚乙烯防腐层技术标准",
        "GB/T 11344-2008 无损检测 接触式超声脉冲回波法测厚方法",
    ]
    for s in standards:
        template.add_paragraph(f"• {s}", indent=True)

    return template


def _embed_analysis_images(template: ReportTemplate, data: ReportData) -> None:
    """Embed original image + defect overlay + heatmap into the report."""
    if data.analysis_result is None:
        if data.image_path:
            template.add_image(data.image_path, caption="原始C扫图像")
        return

    try:
        from ..image_processing.visualizer import save_analysis_figure
        overlay_path, heatmap_path, composite_path = save_analysis_figure(
            data.analysis_result.preprocessed_image
            if data.analysis_result.preprocessed_image.ndim == 3
            else data.analysis_result.original_image,
            data.defects,
            data.analysis_result.defect_mask,
        )
        template.add_image(composite_path, width_inches=6.0, caption="图 1  原始图像 | 缺陷标注 | 热力图")
    except Exception:
        if data.image_path:
            template.add_image(data.image_path, caption="原始C扫图像")


def _embed_charts(template: ReportTemplate, data: ReportData) -> None:
    """Generate and embed statistical charts."""
    try:
        from .chart_generator import defect_type_pie_chart, defect_area_histogram, severity_bar_chart
        tmp = Path(tempfile.mkdtemp(prefix="irs_charts_"))

        pie_path = defect_type_pie_chart(data.defects, tmp / "type_pie.png")
        template.add_image(pie_path, width_inches=4.0, caption="图 2  缺陷类型分布")

        hist_path = defect_area_histogram(data.defects, tmp / "area_hist.png")
        template.add_image(hist_path, width_inches=4.0, caption="图 3  缺陷面积分布")

        sev_path = severity_bar_chart(data.defects, tmp / "severity_bar.png")
        template.add_image(sev_path, width_inches=3.5, caption="图 4  缺陷严重度分布")
    except Exception:
        template.add_paragraph("（图表生成失败，请检查 matplotlib 是否安装）", indent=True)
