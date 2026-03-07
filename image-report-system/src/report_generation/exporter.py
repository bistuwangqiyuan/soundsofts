"""Export final Word report."""

from __future__ import annotations

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
