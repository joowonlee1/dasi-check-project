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
    if not compact:
        st.caption("🌱 관리자 모드에서는 게임을 연습 모드로만 할 수 있어요. 명예의 전당 기록은 시민증 닉네임으로만 남아요.")

def tools_button(prefix):
    if not st.session_state.get("admin_open"):
        return
    key="admin_tools_"+prefix
    # 관리자증 카드와 같은 진초록·금색으로 크게 보여 줘요. 열려 있으면 '닫기'로 바뀌어요.
    st.markdown(
        f'<style>.st-key-{key}_box button{{background:linear-gradient(135deg,#173f35,#24604f)!important;color:#fff7db!important;'
        'border:3px solid #d8b85d!important;border-radius:16px!important;min-height:64px!important;'
        'box-shadow:0 4px 0 #b8953a,0 6px 14px rgba(23,63,53,.25)!important;}'
        f'.st-key-{key}_box button p{{font-size:1.2rem!important;font-weight:900!important;}}'
        f'.st-key-{key}_box button:hover{{filter:brightness(1.12);color:#fff!important;border-color:#f4d784!important;}}</style>',
        unsafe_allow_html=True)
    opened=st.session_state.get(key+"_open",False)
    with st.container(key=key+"_box"):
        clicked=st.button("🔑 관리자 정답·관리 닫기 ▲" if opened else "🔑 관리자 정답·관리 열기 ▼",key=key,width="stretch")
    if clicked:
        st.session_state[key+"_open"]=not opened
        st.rerun()
    if st.session_state.get(key+"_open"):
        from admin_tools import show_admin_box
        show_admin_box()
