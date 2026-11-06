"""게임 화면 등록은 별도의 import 가능한 모듈에서 수행합니다."""
import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# 게임 HTML을 임시 폴더의 index.html로 저장해요(Streamlit 컴포넌트는 폴더 경로가 필요해요).
@st.cache_resource(show_spinner=False)
def _prepare_frontend(html_text):
    folder = Path(tempfile.mkdtemp(prefix="jamkkan_river_"))
    (folder / "index.html").write_text(html_text, encoding="utf-8")
    return str(folder)

# 가짜뉴스 확산 막기 게임 화면을 Streamlit 사용자 정의 컴포넌트로 등록해요(예전 '강 건너기' 시절 이름을 그대로 써요).
def create_river_component(html_text):
    return components.declare_component(
        "jamkkan_river_adventure", path=_prepare_frontend(html_text)
    )
