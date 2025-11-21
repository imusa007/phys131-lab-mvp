"""PDF generation utilities for the Physics Lab app."""
from datetime import datetime
from io import BytesIO
import os
import tempfile
from typing import Optional

from fpdf import FPDF
import pandas as pd


def safe_multicell(pdf: FPDF, text: str, h: float = 6) -> None:
    """Safe multi-cell that never throws width errors."""
    line_width = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.multi_cell(line_width, h, text)


def _add_font(pdf: FPDF, font_path: str) -> None:
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
    else:
        pdf.set_font("Arial", "", 12)
        return
    pdf.set_font("DejaVu", "", 12)


def _render_header(pdf: FPDF, lab_title: str, student_name: str, section: str) -> None:
    pdf.set_font("DejaVu", "", 16)
    safe_multicell(pdf, lab_title)
    pdf.ln(3)

    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, f"Student Name: {student_name or 'N/A'}")
    safe_multicell(pdf, f"Section: {section or 'N/A'}")
    safe_multicell(pdf, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    pdf.ln(3)


def _render_data_table(pdf: FPDF, data_df: pd.DataFrame) -> None:
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Data Table")
    pdf.ln(1)

    pdf.set_font("DejaVu", "", 10)

    if not data_df.empty:
        col_count = len(data_df.columns)
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / col_count

        for col in data_df.columns:
            pdf.cell(col_width, 8, str(col), border=1)
        pdf.ln()

        for _, row in data_df.iterrows():
            for col in data_df.columns:
                pdf.cell(col_width, 8, str(row[col]), border=1)
            pdf.ln()
    else:
        safe_multicell(pdf, "No data entered.")

    pdf.ln(5)


def _render_plot(pdf: FPDF, fig_buf: Optional[BytesIO]) -> None:
    if fig_buf is None:
        return

    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Plot")
    pdf.ln(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(fig_buf.getvalue())
        img_path = tmp.name

    pdf.image(img_path, w=170)
    pdf.ln(5)



def _render_analysis(pdf: FPDF, analysis: str, conclusion: str) -> None:
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Analysis")
    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, analysis or "N/A")
    pdf.ln(5)

    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Conclusion")
    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, conclusion or "N/A")


def create_lab_pdf(
    student_name: str,
    section: str,
    lab_title: str,
    objective: str,
    data_df: pd.DataFrame,
    analysis: str,
    conclusion: str,
    fig_buf: Optional[BytesIO],
    font_path: str = "DejaVuSans.ttf",
) -> bytes:
    """Generate a PDF report for a lab using the provided data and text."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    _add_font(pdf, font_path)
    _render_header(pdf, lab_title, student_name, section)
    safe_multicell(pdf, f"Objective:\n{objective}")
    pdf.ln(5)
    _render_data_table(pdf, data_df)
    _render_plot(pdf, fig_buf)
    _render_analysis(pdf, analysis, conclusion)

    return bytes(pdf.output(dest="S"))
