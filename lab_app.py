from fpdf import FPDF
import tempfile
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import os

# ======================================================
# PDF Generator (fpdf2, supports Unicode)
# ======================================================
def safe_multicell(pdf, text, h=6):
    """Safe multi-cell that never throws width errors."""
    line_width = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.multi_cell(line_width, h, text)

def create_lab_pdf(
    student_name,
    section,
    lab_title,
    objective,
    data_df,
    analysis,
    conclusion,
    fig_buf,
):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    # Load Unicode font
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 16)

    # Title
    safe_multicell(pdf, lab_title)
    pdf.ln(3)

    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, f"Student Name: {student_name or 'N/A'}")
    safe_multicell(pdf, f"Section: {section or 'N/A'}")
    safe_multicell(pdf, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    pdf.ln(3)
    safe_multicell(pdf, f"Objective:\n{objective}")
    pdf.ln(5)

    # Data Table
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Data Table")
    pdf.ln(1)

    pdf.set_font("DejaVu", "", 10)

    if not data_df.empty:
        col_count = len(data_df.columns)
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / col_count

        # Header
        for col in data_df.columns:
            pdf.cell(col_width, 8, str(col), border=1)
        pdf.ln()

        # Rows
        for _, row in data_df.iterrows():
            for col in data_df.columns:
                pdf.cell(col_width, 8, str(row[col]), border=1)
            pdf.ln()
    else:
        safe_multicell(pdf, "No data entered.")

    pdf.ln(5)

    # Plot
    if fig_buf is not None:
        pdf.set_font("DejaVu", "", 12)
        safe_multicell(pdf, "Plot")
        pdf.ln(1)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(fig_buf.getvalue())
            img_path = tmp.name

        pdf.image(img_path, w=170)
        pdf.ln(5)

    # Analysis
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Analysis")
    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, analysis or "N/A")
    pdf.ln(5)

    # Conclusion
    pdf.set_font("DejaVu", "", 12)
    safe_multicell(pdf, "Conclusion")
    pdf.set_font("DejaVu", "", 11)
    safe_multicell(pdf, conclusion or "N/A")

    return pdf.output(dest="S").encode("latin1")

# ======================================================
# Streamlit App
# ======================================================

def main():
    st.set_page_config(page_title="Physics Lab Report v0.1 beta", page_icon="🧪")
    
    st.title("🧪 Physics Lab Report Generator v0.1 beta")
    st.write(
        "Fill out the fields below. When you are done, click **Generate PDF report** "
        "and upload the PDF to Blackboard."
    )

    st.info(f"Font file exists: **{os.path.exists('DejaVuSans.ttf')}**")

    # --- Student Info ---
    st.subheader("Student Info (optional)")
    student_name = st.text_input("Student name (or initials)")
    section = st.text_input("Section / Period (e.g., 8th Grade – Period 3)")

    # --- Lab Information ---
    st.subheader("Lab Information")
    default_title = "Constant Acceleration Motion Lab"
    lab_title = st.text_input("Lab title", value=default_title)
    objective = st.text_area(
        "Objective / Purpose",
        value="To investigate the relationship between position and time for an object moving with (approximately) constant acceleration.",
        height=80,
    )

    # --- Data Table ---
    st.subheader("Data Table")

    if "data_df" not in st.session_state:
        st.session_state.data_df = pd.DataFrame(
            {
                "Time (s)": [0.0, 0.5, 1.0, 1.5],
                "Position (m)": [0.0, 1.2, 4.7, 10.5],
            }
        )

    data_df = st.data_editor(
        st.session_state.data_df,
        num_rows="dynamic",
        use_container_width=True,
    )

    # --- Plot ---
    st.subheader("Quick Plot (Position vs Time)")
    fig_buf = None

    if not data_df.empty:
        try:
            fig, ax = plt.subplots()
            ax.scatter(data_df["Time (s)"], data_df["Position (m)"])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Position (m)")
            ax.set_title("Position vs Time")
            ax.grid(True)

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            fig_buf = buf
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Could not plot data: {e}")

    # --- Analysis ---
    st.subheader("Analysis Questions")
    analysis = st.text_area(
        "Describe what your graph shows. How does position depend on time? Is the motion consistent with constant acceleration?",
        height=120,
    )

    conclusion = st.text_area(
        "Conclusion: Summarize what you learned from this experiment.",
        height=120,
    )

    # --- PDF Generation ---
    st.markdown("---")
    if st.button("📄 Generate PDF report"):
        try:
            pdf_bytes = create_lab_pdf(
                student_name, section, lab_title,
                objective, data_df, analysis, conclusion,
                fig_buf,
            )

            file_name = f"lab_report_{lab_title.replace(' ', '_')}.pdf"

            st.success("PDF report generated! Click below to download.")
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")


if __name__ == "__main__":
    main()
