"""관리자 인증 상태를 보여 주는 전용 카드와 홈·시민증 관리 도구."""
import streamlit as st
from pathlib import Path
import base64

def manager_photo():
    return base64.b64encode((Path(__file__).resolve().parent/'assets'/'ggangji_manager.png').read_bytes()).decode('ascii')

def card(compact=False):
    if not st.session_state.get("admin_open"):
        return
    if compact:
        st.markdown("<style>[data-testid=stSidebarNav]{margin-top:200px!important;}</style>",unsafe_allow_html=True)
    try:
        photo=f'<img src="data:image/png;base64,{manager_photo()}" alt="관리자 깡지" style="width:{52 if compact else 116}px;height:{52 if compact else 116}px;object-fit:contain;flex-shrink:0;border:3px solid #efd68b;border-radius:8px;">'
    except Exception:
        photo='<span style="font-size:40px">🐿️</span>'
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:#173f35;color:#fff7db;border:2px solid #d8b85d;border-radius:16px;padding:12px;box-sizing:border-box;">'
        +photo+'<div style="min-width:0;line-height:1.4;word-break:keep-all;overflow-wrap:normal;font-size:.85rem"><div style="color:#f4d784;font-weight:800">★ 도토리시<br>관리자증</div>'
        '<strong style="font-size:1.2rem;color:#fff">관리자</strong><div style="font-size:.8rem;color:#fff7db">🔑 인증 완료</div></div></div>',unsafe_allow_html=True)

def tools_button(prefix):
    if not st.session_state.get("admin_open"):
        return
    key="admin_tools_"+prefix
    if st.button("🔑 관리자 정답·관리",key=key,width="stretch"):
        st.session_state[key+"_open"]=not st.session_state.get(key+"_open",False)
    if st.session_state.get(key+"_open"):
        from admin_tools import show_admin_box
        show_admin_box()
