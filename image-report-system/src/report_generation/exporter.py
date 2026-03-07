"""Export final Word report."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np

from ..multimodal_fusion.fusion import FusionResult
from ..multimodal_fusion.rule_engine import RuleCheckResult, RuleEngine
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
    """Run full pipeline: read image -> analyze -> generate report. Returns validation warnings."""
    from ..image_processing.preprocessor import preprocess_cscan

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    # Preprocess image
    preprocessed = preprocess_cscan(input_path)
    h, w = preprocessed.shape[:2]
    total_pixels = h * w

    # Rule engine (no ML models - use heuristics)
    engine = RuleEngine()
    defect_ratio = 0.02  # Placeholder when no segmentation model
    defect_area = int(defect_ratio * total_pixels)
    predicted_force = 85.0  # Placeholder when no RF model
    checks = engine.run_all_checks(predicted_force, defect_area, total_pixels)

    # Dummy defect mask (zeros for demo)
    defect_mask = np.zeros((h, w), dtype=np.float32)

    # Fusion result
    all_passed = all(c.passed for c in checks)
    if all_passed and defect_ratio < 0.03:
        quality, conf = "合格", 0.92
    elif not all_passed or defect_ratio > 0.15:
        quality, conf = "不合格", 0.75
    else:
        quality, conf = "待复核", 0.82

    fusion = FusionResult(
        defect_mask=defect_mask,
        predicted_force=predicted_force,
        rule_checks=checks,
        overall_quality=quality,
        confidence=conf,
    )

    data = ReportData(
        specimen_id=specimen_id,
        inspection_date=datetime.now().strftime("%Y-%m-%d"),
        operator=operator,
        equipment=equipment,
        fusion_result=fusion,
        defect_count=0,
        defect_area_ratio=defect_ratio,
        image_path=str(input_path),
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
