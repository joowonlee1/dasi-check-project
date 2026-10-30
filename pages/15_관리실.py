"""🛠️ 도토리시 관리실: 관리자만 들어오는 페이지. 정답 확인·시민 관리·기록 정리를 한곳에서 해요.

예전에는 페이지마다 맨 아래 '관리자 정답·관리 열기'를 펼쳐서 스크롤이 길어졌어요.
이제는 이 페이지 하나로 모았어요.
"""
import streamlit as st

st.title("🛠️ 도토리시 관리실")
if not st.session_state.get("admin_open"):
    st.info("🔒 관리자만 들어올 수 있는 곳이에요. 로그인 화면의 ‘🔑 관리자이신가요?’에서 관리자 코드를 입력해 주세요.")
    st.stop()

from admin_ui import card
from admin_tools import _admin_tools
from admin_progress import status

left, right = st.columns([1, 2.6], gap="medium")
with left:
    card()
    status("room")
with right:
    _admin_tools()
