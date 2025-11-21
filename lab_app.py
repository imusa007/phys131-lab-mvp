import os
from io import BytesIO
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from pdf_generator import create_lab_pdf
from tex_tools import read_tex_file, render_latex_content


# ======================================================
# Streamlit UI Helpers
# ======================================================

def render_intro():
    st.set_page_config(page_title="Physics Lab Report v0.2", page_icon="🧪")
    st.title("🧪 Physics Lab Report Generator")
    st.write(
        "Fill out the fields below. When you are done, click **Generate PDF report** "
        "and upload the PDF to Blackboard."
    )
    st.info(f"Font file exists: **{os.path.exists('DejaVuSans.ttf')}**")


def render_student_info() -> Tuple[str, str]:
    st.subheader("Student Info (optional)")
    student_name = st.text_input("Student name (or initials)")
    section = st.text_input("Section / Period (e.g., 8th Grade – Period 3)")
    return student_name, section


def render_lab_info() -> Tuple[str, str]:
    st.subheader("Lab Information")
    default_title = "Constant Acceleration Motion Lab"
    lab_title = st.text_input("Lab title", value=default_title)
    objective = st.text_area(
        "Objective / Purpose",
        value=(
            "To investigate the relationship between position and time for an object moving "
            "with (approximately) constant acceleration."
        ),
        height=80,
    )
    return lab_title, objective


def render_data_table() -> pd.DataFrame:
    st.subheader("Data Table")
    if "data_df" not in st.session_state:
        st.session_state.data_df = pd.DataFrame(
            {
                "Time (s)": [0.0, 0.5, 1.0, 1.5],
                "Position (m)": [0.0, 1.2, 4.7, 10.5],
            }
        )

    return st.data_editor(
        st.session_state.data_df,
        num_rows="dynamic",
        use_container_width=True,
    )


def render_plot(data_df: pd.DataFrame) -> BytesIO | None:
    st.subheader("Quick Plot (Position vs Time)")
    if data_df.empty:
        st.info("Add data to see the quick plot preview.")
        return None

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
        st.pyplot(fig)
        return buf
    except Exception as exc:
        st.warning(f"Could not plot data: {exc}")
        return None


def render_analysis_sections() -> Tuple[str, str]:
    st.subheader("Analysis Questions")
    analysis = st.text_area(
        "Describe what your graph shows. How does position depend on time? Is the motion consistent with constant acceleration?",
        height=120,
    )
    conclusion = st.text_area(
        "Conclusion: Summarize what you learned from this experiment.",
        height=120,
    )
    return analysis, conclusion


def render_pdf_generation(
    student_name: str,
    section: str,
    lab_title: str,
    objective: str,
    data_df: pd.DataFrame,
    analysis: str,
    conclusion: str,
    fig_buf: BytesIO | None,
):
    st.markdown("---")
    if st.button("📄 Generate PDF report"):
        try:
            pdf_bytes = create_lab_pdf(
                student_name,
                section,
                lab_title,
                objective,
                data_df,
                analysis,
                conclusion,
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
        except Exception as exc:
            st.error(f"Error generating PDF: {exc}")


def render_tex_preview():
    st.markdown("---")
    st.subheader("LaTeX Preview")
    uploaded_tex = st.file_uploader("Upload LaTeX (.tex) file", type=["tex"])
    if uploaded_tex:
        latex_text = read_tex_file(uploaded_tex)
        render_latex_content(latex_text)
    else:
        st.info("Upload a .tex file to render it with MathJax.")


# ======================================================
# Streamlit App
# ======================================================


def main():
    render_intro()

    student_name, section = render_student_info()
    lab_title, objective = render_lab_info()
    data_df = render_data_table()
    fig_buf = render_plot(data_df)
    analysis, conclusion = render_analysis_sections()
    render_pdf_generation(
        student_name,
        section,
        lab_title,
        objective,
        data_df,
        analysis,
        conclusion,
        fig_buf,
    )
    render_tex_preview()


if __name__ == "__main__":
    main()
