"""큐싱 노노그램 게임 화면 등록. 페이지 파일이 아닌 별도 모듈에서 등록해야 오류가 나지 않습니다."""
import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components


@st.cache_resource(show_spinner=False)
def _prepare_frontend(html_text):
    folder = Path(tempfile.mkdtemp(prefix="jamkkan_nono_"))
    (folder / "index.html").write_text(html_text, encoding="utf-8")
    return str(folder)


def create_nonogram_component(html_text):
    return components.declare_component("jamkkan_qr_nonogram", path=_prepare_frontend(html_text))
