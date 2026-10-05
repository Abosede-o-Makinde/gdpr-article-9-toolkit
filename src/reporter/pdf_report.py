"""Article 9 assessment PDF via fpdf2."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from src import __version__
from src.article9.engine import Assessment, format_score
from src.reporter import DISCLAIMER, NO_GAPS, prepare_output

_BAND_FILL = {
    "PASS": (0, 128, 0),
    "PARTIAL": (200, 120, 0),
    "FAIL": (160, 0, 0),
}


class Article9PdfReport:
    """Writes a short A4 PDF from an assessment."""

    MARGIN = 20
    DARK_BLUE = (31, 56, 100)
    WHITE = (255, 255, 255)
    TEXT_DARK = (30, 30, 30)

    def generate(self, result: Assessment, output_path: Path) -> Path:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=self.MARGIN)
        pdf.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)
        self._add_summary(pdf, result)
        self._add_findings(pdf, result)
        target = prepare_output(output_path)
        pdf.output(str(target.resolve()))
        return target

    def _add_summary(self, pdf: FPDF, result: Assessment) -> None:
        activity = result.activity
        pdf.add_page()
        pdf.set_fill_color(*self.DARK_BLUE)
        pdf.rect(0, 0, 210, 45, style="F")
        pdf.set_text_color(*self.WHITE)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_y(12)
        pdf.cell(0, 10, "gdpr-article-9-toolkit", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=11)
        pdf.cell(
            0,
            8,
            f"UK GDPR Article 9 check v{__version__}",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_text_color(*self.TEXT_DARK)
        pdf.set_x(self.MARGIN)
        pdf.ln(18)
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 8, activity.name)
        pdf.set_font("Helvetica", size=11)
        for line in (
            f"Activity: {activity.activity_id}",
            f"Organisation: {activity.organisation or '-'}",
            f"Condition: {result.condition_label or 'none'}",
            f"Score: {format_score(result.score)}",
        ):
            pdf.set_x(self.MARGIN)
            pdf.multi_cell(0, 6, line)
        fill = _BAND_FILL[result.band]
        pdf.set_fill_color(*fill)
        pdf.set_text_color(*self.WHITE)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_x(self.MARGIN)
        pdf.cell(40, 8, result.band, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        pdf.set_text_color(*self.TEXT_DARK)
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(self.MARGIN)
        pdf.multi_cell(0, 5, result.dpia.message)

    def _add_findings(self, pdf: FPDF, result: Assessment) -> None:
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Findings", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        if not result.findings:
            pdf.set_x(self.MARGIN)
            pdf.multi_cell(0, 5, NO_GAPS)
        for item in result.findings:
            pdf.set_x(self.MARGIN)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, f"{item.rule_id} {item.severity}: {item.title}")
            pdf.set_x(self.MARGIN)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5, item.remediation)
            pdf.ln(1)
        pdf.ln(4)
        pdf.set_x(self.MARGIN)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, DISCLAIMER)
