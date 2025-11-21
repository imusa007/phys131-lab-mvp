"""Utilities for reading and rendering LaTeX content."""
from __future__ import annotations

from typing import IO

import streamlit as st

MATHJAX_SCRIPT = """
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
  svg: { fontCache: 'global' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
"""


def read_tex_file(file_obj: IO[bytes]) -> str:
    """Return the contents of a .tex file as text."""
    content = file_obj.read()
    try:
        file_obj.seek(0)
    except Exception:
        pass
    return content.decode("utf-8", errors="replace")


def render_latex_content(latex_text: str) -> None:
    """Render LaTeX text inside Streamlit using MathJax."""
    if not latex_text.strip():
        st.info("Upload a .tex file to see the rendered preview.")
        return

    html = (
        MATHJAX_SCRIPT
        + "<div class='latex-preview' style='padding: 1rem; background: #0e1117; color: white;'>"
        + latex_text
        + "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
    st.code(latex_text, language="latex")
