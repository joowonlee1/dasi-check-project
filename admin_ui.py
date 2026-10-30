"""관리자 인증 상태를 보여 주는 전용 카드와 홈·시민증 관리 도구."""
import streamlit as st
from pathlib import Path
import base64

def manager_photo():
    return base64.b64encode((Path(__file__).resolve().parent/'assets'/'ggangji_manager.png').read_bytes()).decode('ascii')

def _asset(name):
    return base64.b64encode((Path(__file__).resolve().parent/'assets'/name).read_bytes()).decode('ascii')

def card(compact=False):
    if not st.session_state.get("admin_open"):
        return
    if compact:
        st.markdown("<style>[data-testid=stSidebarNav]{margin-top:200px!important;}</style>",unsafe_allow_html=True)
    # 관리자증 증명사진(사이드바는 좁아서 조금 작게): 경례하는 깡지(금색 액자·별 포함) 사진. 사진이 없으면 예전 사진, 그것도 없으면 이모지로 대신해요.
    h = 84 if compact else 124
    try:
        photo = f'<img src="data:image/png;base64,{_asset("admin_photo.png")}" alt="경례하는 관리자 깡지" class="adm-ph" style="width:min({round(h*300/231)}px,{40 if compact else 38}%);height:auto;flex-shrink:0;display:block">'
    except Exception:
        try:
            photo = f'<img src="data:image/png;base64,{manager_photo()}" alt="관리자 깡지" style="width:{h}px;height:{h}px;object-fit:contain;flex-shrink:0;border:3px solid #efd68b;border-radius:8px;">'
        except Exception:
            photo = '<span style="font-size:40px">🐿️</span>'
    # 큰 카드 오른쪽 빈 곳은 종이비행기·별·방패 무늬로 채워요(왼쪽 끝은 흐리게 섞이고, 좁은 화면에서도 글씨를 덮지 않게 카드 너비의 42%까지만).
    deco = ""
    if True:  # 사이드바 카드도 오른쪽 빈 곳을 무늬로 채워요(사이드바는 좁아서 30%까지만)
        try:
            deco = (f'<img src="data:image/jpeg;base64,{_asset("admin_card_deco.jpg")}" alt="" aria-hidden="true" class="adm-deco" '
                    f'style="position:absolute;right:0;top:0;height:100%;width:auto;max-width:{30 if compact else 42}%;object-fit:cover;object-position:right center;pointer-events:none;'
                    '-webkit-mask-image:linear-gradient(to right,transparent,#000 22%);mask-image:linear-gradient(to right,transparent,#000 22%)">')
        except Exception:
            deco = ""
    gap, pad, t1, t2, t3 = (10, "8px 10px", ".82rem", "1.65rem", ".8rem") if compact else (20, "8px 14px", "1.2rem", "2.3rem", "1.02rem")
    # 아주 좁을 때(사이드바를 좁게 줄였을 때 등)는 사진을 위, 글을 아래로 쌓아서 글자가 잘리지 않게 해요.
    narrow = (
        "<style>.adm-wrap{container-type:inline-size}"
        "@container (max-width:250px){.adm-card{flex-direction:column!important;text-align:center;gap:6px!important;padding:8px!important}"
        ".adm-card .adm-ph{width:78%!important;max-width:150px}.adm-card .adm-tx{align-items:center!important;flex:none!important;width:100%}"
        ".adm-card .adm-tx strong{font-size:1.45rem!important}.adm-card .adm-t1{font-size:.8rem!important}.adm-card .adm-deco{display:none}}</style>"
    )
    head = narrow + (f'<div class="adm-wrap"><div class="adm-card" style="position:relative;overflow:hidden;display:flex;width:100%;align-items:center;gap:{gap}px;background:#164539;color:#fff7db;'
            f'border:{3 if compact else 4}px solid #f2cd5c;border-radius:{18 if compact else 26}px;padding:{pad};box-sizing:border-box;'
            'box-shadow:0 4px 0 #f8e7a6,0 6px 16px rgba(22,69,57,.18)">'
            + deco + photo +
            '<div class="adm-tx" style="position:relative;min-width:0;flex:1;display:flex;flex-direction:column;align-items:flex-start;gap:4px;line-height:1.25;white-space:nowrap">'
            f'<div class="adm-t1" style="color:#f6d55c;font-weight:900;font-size:{t1};white-space:normal;word-break:keep-all">★ 도토리시 관리자증</div>'
            f'<strong style="font-size:{t2};font-weight:900;color:#fff;text-shadow:0 2px 0 rgba(0,0,0,.18)">관리자</strong>'
            f'<span style="font-size:{t3};font-weight:900;background:linear-gradient(180deg,#fff3b0,#f6d55c);color:#173f35;border-radius:999px;padding:{"2px 10px" if compact else "4px 16px"};box-shadow:inset 0 -2px 0 rgba(0,0,0,.08)">🛡️ 인증 완료</span>'
            '</div></div></div>')
    note = ('' if compact else '<div style="margin:10px 0 6px;padding:10px 14px;background:#F0FDF4;border:2px solid #86EFAC;border-radius:12px;'
            'color:#14532D;font-size:1.02rem;font-weight:700;line-height:1.6;word-break:keep-all">'
            '🌱 관리자 모드에서는 게임을 <b>연습 모드로만</b> 할 수 있어요. 명예의 전당 기록은 <b>시민증 닉네임</b>으로만 남아요.</div>')
    st.markdown(head + note, unsafe_allow_html=True)

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
