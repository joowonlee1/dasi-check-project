"""독립 소개 화면: 깡지 도우미 이미지·보라색 카드 안내. 게임과 인증은 유지합니다."""
import base64
from html import escape
from pathlib import Path
import streamlit as st
import dotori_data as dd

SEEN = "welcome_intro_seen_v1"
HELP = "welcome_intro_help_pending_v1"


def _enter(mode):
    if mode in ("new", "back"):
        st.session_state["welcome_form_mode"] = mode
        st.session_state["login_mode_welcome"] = mode
        st.session_state["welcome_auth_pending"] = True
    else:
        st.session_state[SEEN] = True
        if mode == "help":
            st.session_state[HELP] = True
            st.session_state["welcome_help_access"] = True
        elif mode == "guest":
            st.session_state["guest"] = True
            st.session_state["guest_go_home"] = True
            from login_resume import PREFIX
            st.session_state[PREFIX + "ready"] = True
    st.rerun()


CSS = """
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarNav"],
[data-testid="stHeader"], #dotori-helper {display:none!important;}
.stApp {background:#FCFAFF!important;}
[data-testid="stMain"] {padding-top:0!important;}
.block-container, [data-testid="stMainBlockContainer"] {
 max-width:1060px!important;width:100%!important;min-width:0!important;
 padding:32px 24px 36px!important;box-sizing:border-box!important;}
.pi-hero {display:flex;align-items:center;gap:24px;padding:22px;
 background:linear-gradient(135deg,#F2EBFF,#FAF7FF);border:1px solid #DDD0F5;
 border-radius:24px;margin:8px 0 14px;box-sizing:border-box;}
.pi-avatar {flex:0 0 140px;text-align:center;}
.pi-orbit {display:flex;align-items:center;justify-content:center;width:124px;height:124px;
 margin:0 auto 8px;box-sizing:border-box;padding:10px;border:3px solid #8B5CF6;
 border-radius:50%;background:#F5F3FF;box-shadow:0 5px 16px #7C3AED20;}
.pi-orbit img {width:100%;height:100%;object-fit:contain;}
.pi-avatar small {font-weight:800;color:#6D28D9;white-space:nowrap;}
.pi-speech {position:relative;flex:1;min-width:0;padding:20px 22px;background:#fff;
 border:2px solid #D8C6F4;border-radius:20px;box-sizing:border-box;}
.pi-speech::before {content:"";position:absolute;left:-10px;top:calc(50% - 9px);
 width:16px;height:16px;background:#fff;border-left:2px solid #D8C6F4;
 border-bottom:2px solid #D8C6F4;transform:rotate(45deg);}
.pi-speech .pi-eyebrow {font-size:.85rem;font-weight:800;color:#7C3AED;margin-bottom:5px;}
.pi-speech h1 {font-size:clamp(1.35rem,3vw,1.85rem)!important;line-height:1.45!important;
 margin:0 0 9px!important;padding:0!important;color:#4C1D95;word-break:keep-all;overflow-wrap:anywhere;}
.pi-speech p {margin:0!important;line-height:1.7!important;color:#514364;word-break:keep-all;overflow-wrap:anywhere;}
.pi-steps {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0;}
.pi-step {background:#fff;border:1px solid #E5DAF7;border-radius:14px;padding:12px;text-align:center;color:#5B21B6;}
.pi-step .pi-icon {display:block;font-size:1.55rem;margin-bottom:3px;}
.pi-step strong {display:block;font-size:1rem;}
.pi-step span:last-child {display:block;font-size:.88rem;color:#71617F;margin-top:3px;line-height:1.5;}
.pi-tip {padding:10px 14px;border-radius:12px;background:#F1EAFE;color:#5B21B6;font-size:.95rem;line-height:1.7;margin:10px 0;}
.pi-guide {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:12px 0;}
.pi-guide article {min-width:0;background:#fff;border:1px solid #E4D7F6;border-radius:16px;padding:14px 16px;box-sizing:border-box;}
.pi-guide h3 {font-size:1rem!important;color:#5B21B6;margin:0 0 7px!important;padding:0!important;line-height:1.5!important;}
.pi-guide p {font-size:.94rem!important;color:#5F536B;line-height:1.65!important;margin:0!important;word-break:keep-all;overflow-wrap:anywhere;}
.pi-guide b {color:#5B21B6;}
.pi-note {background:#F6F1FC;border-radius:12px;padding:10px 14px;color:#71617F;font-size:.85rem;line-height:1.65;margin:8px 0;}
[data-testid="stTabs"] [role="tab"] {color:#6D28D9;min-height:44px;height:auto;white-space:normal;}
[data-testid="stTabs"] [aria-selected="true"] {color:#6D28D9!important;font-weight:800;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:#8B5CF6!important;}
.st-key-intro_help button {min-height:50px!important;height:auto!important;width:100%!important;
 padding:10px 14px!important;background:#FFF5F7!important;border:1.5px solid #E8A3B3!important;
 color:#9F2847!important;border-radius:14px!important;box-sizing:border-box;}
.st-key-intro_help button p {white-space:normal!important;line-height:1.5!important;margin:0!important;}
.st-key-intro_actions [data-testid="stHorizontalBlock"] {gap:12px!important;align-items:stretch!important;}
.st-key-intro_actions [data-testid="stColumn"] {flex:1 1 0!important;min-width:0!important;width:0!important;}
.st-key-intro_actions button {width:100%!important;height:64px!important;min-height:64px!important;
 padding:8px 12px!important;background:#7C3AED!important;color:#fff!important;border:2px solid #7C3AED!important;
 border-radius:14px!important;box-sizing:border-box!important;font-weight:800!important;}
.st-key-intro_actions button p {color:#fff!important;font-size:1rem!important;font-weight:800!important;
 line-height:1.4!important;margin:0!important;white-space:normal!important;}
.st-key-intro_actions button:hover {background:#6D28D9!important;border-color:#6D28D9!important;}
.st-key-intro_actions button:focus-visible {outline:3px solid #C4B5FD!important;outline-offset:3px;}
@media(max-width:640px){
 .block-container,[data-testid="stMainBlockContainer"] {padding:22px 16px 28px!important;}
 .pi-hero {gap:16px;padding:16px;flex-direction:column;}
 .pi-avatar {flex:auto;}.pi-orbit {width:100px;height:100px;margin-bottom:4px;padding:8px;}
 .pi-speech {width:100%;padding:16px;}
 .pi-speech::before {left:calc(50% - 9px);top:-10px;transform:rotate(135deg);}
 .pi-step {padding:10px 5px;}.pi-step strong {font-size:.9rem;}
 .pi-step span:last-child {font-size:.8rem;}
 .pi-guide {grid-template-columns:1fr;gap:8px;}
 .st-key-intro_actions [data-testid="stHorizontalBlock"] {flex-direction:column!important;}
 .st-key-intro_actions [data-testid="stColumn"] {flex:1 1 auto!important;width:100%!important;}
}
"""


def _avatar():
    # 실제 깡지 도우미와 같은 헬멧 쓴 이미지. 시민증 사진의 자르기 함수를 사용하지 않습니다.
    try:
        data = base64.b64encode((Path(__file__).parent / "assets" / "btn_ai.png").read_bytes()).decode("ascii")
        return f'<img src="data:image/png;base64,{data}" alt="안테나 달린 헬멧을 쓴 깡지 도우미">'
    except OSError:
        return '<span role="img" aria-label="깡지 도우미" style="font-size:56px">🤖</span>'


def _cards(items):
    return '<div class="pi-guide">' + ''.join(
        f'<article><h3>{escape(title)}</h3><p>{body}</p></article>'
        for title, body in items
    ) + '</div>'


def show_intro_if_needed():
    if dd.citizen() or st.session_state.get("admin_open"):
        if st.session_state.pop("welcome_auth_pending", False):
            st.session_state[SEEN] = True
            st.session_state["guest_go_home"] = True
        return
    if st.session_state.get("guest") or st.session_state.get("welcome_help_access"):
        return
    st.markdown('<style>' + CSS + '</style>', unsafe_allow_html=True)
    st.markdown("""<style>
    .pi-avatar {flex:0 0 180px;}.pi-avatar .pi-large {width:176px;height:196px;object-fit:contain;display:block;margin:auto;}
    .pi-find {display:flex;align-items:center;gap:20px;background:linear-gradient(120deg,#EDE2FF,#F7F2FF);
      border:2px solid #A78BFA;border-radius:20px;padding:18px 22px;margin:14px 0 18px;
      color:#4C1D95;line-height:1.6;box-shadow:0 6px 20px #7C3AED14;box-sizing:border-box;}
    .pi-find .pi-orbit {width:92px;height:92px;flex:0 0 92px;padding:7px;margin:0;background:#fff;}
    .pi-find-copy {min-width:0;}
    .pi-find h2 {font-size:1.35rem!important;font-weight:800!important;color:#4C1D95!important;
      line-height:1.4!important;margin:0 0 8px!important;padding:0!important;word-break:keep-all;}
    .pi-find-location {display:inline-flex;align-items:center;gap:10px;background:#6D28D9;color:#fff!important;
      border-radius:10px;padding:7px 14px;font-size:1.15rem;font-weight:800;line-height:1.4;flex-wrap:wrap;}
    .pi-find-arrow {font-size:1.5rem;line-height:1;}
    .pi-find p {margin:8px 0 0!important;color:#5B4675!important;font-size:1rem!important;}
    .st-key-login_choices_welcome {display:none!important;}
    [data-testid="stForm"] {border:1px solid #DDD0F5;border-radius:16px;background:#fff;padding:16px;}
    @media(max-width:640px){.pi-avatar{flex:auto;}.pi-avatar .pi-large{width:144px;height:158px;}}
    </style>""", unsafe_allow_html=True)
    if st.button("🚨 실제 피해가 의심되나요? 대처 안내 바로 보기", key="intro_help", width="stretch"):
        _enter("help")
    avatar = _avatar()
    large = avatar.replace('<img ', '<img class="pi-large" ', 1)
    st.markdown(
        '<section class="pi-hero" aria-label="깡지의 짧은 앱 소개">'
        f'<div class="pi-avatar">{large}</div><div class="pi-speech">'
        '<h1>안녕! 나는 깡지야!</h1><p><b>잠깐!</b>은 수상한 전화와 문자에<br>'
        '<b>멈추고 · 확인하고 · 판단하는 방법</b>을 연습하는 앱이야.</p></div></section>'
        f'<aside class="pi-find" aria-label="깡지 도우미 위치 안내"><div class="pi-orbit">{avatar}</div>'
        '<div class="pi-find-copy"><h2>도움이 필요해? 깡지를 눌러봐!</h2>'
        '<div class="pi-find-location">화면 오른쪽 아래에 있어 <span class="pi-find-arrow" aria-hidden="true">↘</span></div>'
        '<p>앱에 들어간 뒤, 막히면 사용법과 힌트를 물어봐!</p></div></aside>',
        unsafe_allow_html=True,
    )
    with st.container(key="intro_actions"):
        guest, new, back = st.columns(3)
        if guest.button("👀 로그인 없이 둘러보기", key="intro_guest", width="stretch"):
            _enter("guest")
        if new.button("🪪 새 시민증 만들기", key="intro_new", width="stretch"):
            _enter("new")
        if back.button("🔑 다시 들어오기", key="intro_back", width="stretch"):
            _enter("back")
    if st.session_state.get("welcome_form_mode") in ("new", "back"):
        # 기존 폼을 재사용하여 비밀 숫자 검증·인증·도장 병합 처리를 보존합니다.
        st.caption("닉네임은 공개될 수 있어요. 실제 이름·학교와 다른 곳의 비밀번호는 쓰지 마세요.")
        dd.show_login_forms("welcome")
    else:
        st.caption("가입 없이 시작할 수 있어. 시민증은 기록을 저장하고 싶을 때 만들면 돼.")
    from admin_tools import show_admin_box
    show_admin_box()
    st.stop()

