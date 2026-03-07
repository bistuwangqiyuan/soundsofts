"""Word report template engine using python-docx."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


class ReportTemplate:
    """Generate structured Word reports from template."""

    def __init__(self) -> None:
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self) -> None:
        style = self.doc.styles["Normal"]
        font = style.font
        font.name = "宋体"
        font.size = Pt(12)

    def add_title(self, title: str) -> None:
        p = self.doc.add_heading(title, level=0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_section(self, heading: str, level: int = 1) -> None:
        self.doc.add_heading(heading, level=level)

    def add_paragraph(self, text: str) -> None:
        self.doc.add_paragraph(text)

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = "Light Grid Accent 1"
        for i, header in enumerate(headers):
            table.rows[0].cells[i].text = header
        for r_idx, row in enumerate(rows):
            for c_idx, cell in enumerate(row):
                table.rows[r_idx + 1].cells[c_idx].text = cell

    def add_image(self, image_path: str | Path, width_inches: float = 5.0) -> None:
        self.doc.add_picture(str(image_path), width=Inches(width_inches))

    def save(self, output_path: str | Path) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output_path))
