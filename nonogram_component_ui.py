"""큐싱 노노그램 게임 화면 등록. 페이지 파일이 아닌 별도 모듈에서 등록해야 오류가 나지 않습니다."""
import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components


# 게임 HTML을 임시 폴더의 index.html로 저장해요(Streamlit 컴포넌트는 폴더 경로가 필요해요).
@st.cache_resource(show_spinner=False)
def _prepare_frontend(html_text):
    folder = Path(tempfile.mkdtemp(prefix="jamkkan_nono_"))
    (folder / "index.html").write_text(html_text, encoding="utf-8")
    return str(folder)


# 큐싱 노노그램 게임 화면을 Streamlit 사용자 정의 컴포넌트로 등록해요.
def create_nonogram_component(html_text):
    return components.declare_component("jamkkan_qr_nonogram", path=_prepare_frontend(html_text))
