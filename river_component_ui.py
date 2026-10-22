"""게임 화면 등록은 별도의 import 가능한 모듈에서 수행합니다."""
import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

@st.cache_resource(show_spinner=False)
def _prepare_frontend(html_text):
    folder = Path(tempfile.mkdtemp(prefix="jamkkan_river_"))
    (folder / "index.html").write_text(html_text, encoding="utf-8")
    return str(folder)

def create_river_component(html_text):
    return components.declare_component(
        "jamkkan_river_adventure", path=_prepare_frontend(html_text)
    )
