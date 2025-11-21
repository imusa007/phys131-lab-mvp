# lab_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import tempfile

# --------- PDF helper --------- #

def create_lab_pdf(
    student_name: str,
    section: str,
    lab_title: str,
    objective: str,
    data_df: pd.DataFrame,
    analysis: str,
    conclusion: str,
    fig_buf: BytesIO | None,
) -> bytes:
    """
    Build a PDF in memory and return its bytes.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, lab_title, ln=True, align="C")
    pdf.ln(5)

    # Basic info
    pdf.set_font("Helvetica", "", 11)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.multi_cell(0, 6, f"Student Name: {student_name or 'N/A'}")
    pdf.multi_cell(0, 6, f"Section: {section or 'N/A'}")
    pdf.multi_cell(0, 6, f"Generated: {timestamp}")
    pdf.ln(5)

    # Objective
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Objective", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, objective or "N/A")
    pdf.ln(3)

    # Data Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Data", ln=True)
    pdf.set_font("Helvetica", "", 10)

    if not data_df.empty:
        # Simple text table
        col_widths = [pdf.get_string_width(str(c)) + 4 for c in data_df.columns]
        max_col_width = 40
        col_widths = [min(w, max_col_width) for w in col_widths]

        # Header row
        for i, col in enumerate(data_df.columns):
            pdf.cell(col_widths[i], 7, str(col), border=1)
        pdf.ln()

        # Data rows
        for _, row in data_df.iterrows():
            for i, col in enumerate(data_df.columns):
                text = str(row[col])
                pdf.cell(col_widths[i], 7, text, border=1)
            pdf.ln()
    else:
        pdf.multi_cell(0, 6, "No data entered.")
    pdf.ln(5)

    # Plot (if provided)
    if fig_buf is not None:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Graph", ln=True)
        pdf.ln(2)

        # Save buffer temporarily so FPDF can load it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(fig_buf.getvalue())
            tmp_path = tmp.name

        # Width 170 mm (roughly full page width minus margins)
        pdf.image(tmp_path, w=170)
        pdf.ln(5)

    # Analysis
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Analysis", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, analysis or "N/A")
    pdf.ln(3)

    # Conclusion
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Conclusion", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, conclusion or "N/A")

    # Export to bytes
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes


# --------- Streamlit app --------- #

def main():
    st.set_page_config(page_title="Physics Lab Report", page_icon="🧪")

    st.title("🧪 Physics Lab Report Generator")
    st.write(
        "Fill out the fields below. When you are done, click **Generate PDF report** "
        "and upload the PDF to Blackboard."
    )

    # --- Basic info --- #
    st.subheader("Student Info (optional)")
    student_name = st.text_input("Student name (or initials)")
    section = st.text_input("Section / Period (e.g., 8th Grade – Period 3)")

    # --- Lab info --- #
    st.subheader("Lab Information")
    default_title = "Constant Acceleration Motion Lab"
    lab_title = st.text_input("Lab title", value=default_title)
    objective = st.text_area(
        "Objective / Purpose",
        value="To investigate the relationship between position and time for an object moving with (approximately) constant acceleration.",
        height=80,
    )

    # --- Data entry --- #
    st.subheader("Data Table")

    # Initialize a default table in session_state so students can edit it
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

    st.markdown("You can edit any cell, add/remove rows. Include at least 3–4 data points.")

    # --- Plot --- #
    st.subheader("Quick Plot (Position vs Time)")
    fig_buf = None
    if not data_df.empty and "Time (s)" in data_df.columns and "Position (m)" in data_df.columns:
        # Simple scatter plot
        fig, ax = plt.subplots()
        try:
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
    else:
        st.info("Enter columns named 'Time (s)' and 'Position (m)' to see a plot.")

    # --- Analysis & Conclusion --- #
    st.subheader("Analysis Questions")
    analysis = st.text_area(
        "Describe what your graph shows. How does position depend on time? Is the motion consistent with constant acceleration?",
        height=120,
    )

    conclusion = st.text_area(
        "Conclusion: Summarize what you learned from this experiment.",
        height=120,
    )

    # --- Generate PDF --- #
    st.markdown("---")
    if st.button("📄 Generate PDF report"):
        pdf_bytes = create_lab_pdf(
            student_name=student_name,
            section=section,
            lab_title=lab_title,
            objective=objective,
            data_df=data_df,
            analysis=analysis,
            conclusion=conclusion,
            fig_buf=fig_buf,
        )

        file_name = f"lab_report_{lab_title.replace(' ', '_')}.pdf"

        st.success("PDF report generated! Click the button below to download.")
        st.download_button(
            "⬇️ Download your lab report (PDF)",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()
