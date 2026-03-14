"""Export final Word report."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .template_engine import ReportTemplate
from .data_binder import ReportData, bind_data_to_report
from .validator import validate_report_data


def export_report(data: ReportData, output_path: str | Path) -> list[str]:
    """Generate and save a Word report. Returns list of validation warnings."""
    issues = validate_report_data(data)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        raise ValueError(f"Report validation failed: {[e.message for e in errors]}")

    template = ReportTemplate()
    template = bind_data_to_report(template, data)
    template.save(output_path)

    return [i.message for i in issues if i.severity == "warning"]


def run_pipeline(
    input_path: str | Path,
    output_path: str | Path,
    specimen_id: str = "UNKNOWN",
    operator: str = "系统",
    equipment: str = "PAUT",
) -> list[str]:
    """Run full pipeline: image -> analysis -> report. Returns validation warnings."""
    from ..pipeline import AnalysisPipeline

    input_path = Path(input_path)
    output_path = Path(output_path)

    pipeline = AnalysisPipeline()
    result = pipeline.run(input_path)

    data = ReportData(
        specimen_id=specimen_id,
        inspection_date=datetime.now().strftime("%Y-%m-%d"),
        operator=operator,
        equipment=equipment,
        fusion_result=result.fusion_result,
        defect_count=result.defect_count,
        defect_area_ratio=result.defect_area_ratio,
        image_path=str(input_path),
        defects=result.defects,
        analysis_result=result,
    )

    return export_report(data, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="超声图像检测与报告生成")
    parser.add_argument("--input", "-i", required=True, help="Input C-scan image path")
    parser.add_argument("--output", "-o", required=True, help="Output Word report path (.docx)")
    parser.add_argument("--specimen", default="UNKNOWN", help="Specimen ID")
    parser.add_argument("--operator", default="系统", help="Operator name")
    parser.add_argument("--equipment", default="PAUT", help="Equipment name")
    args = parser.parse_args()

    warnings = run_pipeline(
        args.input,
        args.output,
        specimen_id=args.specimen,
        operator=args.operator,
        equipment=args.equipment,
    )
    if warnings:
        for w in warnings:
            print(f"Warning: {w}")
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
