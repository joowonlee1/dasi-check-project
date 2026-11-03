"""독립 소개 화면: 깡지 도우미 이미지·보라색 카드 안내. 게임과 인증은 유지합니다."""
import base64
from html import escape
from pathlib import Path
import streamlit as st
import dotori_data as dd

SEEN = "welcome_intro_seen_v1"
HELP = "welcome_intro_help_pending_v1"


def _enter(mode):
    st.session_state[SEEN] = True
    if mode == "help":
        st.session_state[HELP] = True
    elif mode == "guest":
        st.session_state["guest"] = True
        st.session_state["guest_go_home"] = True
        # 비회원 선택 시 이전 로그인 정보를 자동 복원하지 않습니다.
        # 저장된 토큰이나 기존 계정은 삭제하지 않습니다.
        from login_resume import PREFIX
        st.session_state[PREFIX + "ready"] = True
    else:
        st.session_state["login_mode_gate"] = mode
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
    if (st.session_state.get(SEEN) or dd.citizen()
            or st.session_state.get("guest") or st.session_state.get("admin_open")):
        return
    st.markdown('<style>' + CSS + '</style>', unsafe_allow_html=True)
    if st.button("🚨 실제 피해가 의심되나요? 대처 안내 바로 보기", key="intro_help", width="stretch"):
        _enter("help")
    st.markdown(
        '<section class="pi-hero" aria-label="깡지 도우미의 앱 소개">'
        f'<div class="pi-avatar"><div class="pi-orbit">{_avatar()}</div><small>너의 안내 도우미 · 깡지</small></div>'
        '<div class="pi-speech"><div class="pi-eyebrow">🌰 도토리시에 온 걸 환영해!</div>'
        '<h1>안녕! 나는 깡지야.</h1><p>수상한 연락이 와도 당황하지 않도록,<br>'
        '<b>멈추고 · 확인하고 · 판단하는 연습</b>을 함께 해보자!</p></div></section>'
        '<div class="pi-steps"><div class="pi-step"><span class="pi-icon">📱</span><strong>상황 체험</strong><span>수상한 연락에 대응하기</span></div>'
        '<div class="pi-step"><span class="pi-icon">🔍</span><strong>단서 찾기</strong><span>문자와 URL 살펴보기</span></div>'
        '<div class="pi-step"><span class="pi-icon">💬</span><strong>대화 연습</strong><span>거절하고 따로 확인하기</span></div></div>'
        '<div class="pi-tip">🤖 들어간 뒤 도움이 필요하면 <b>오른쪽 아래 보라색 깡지 얼굴</b>을 눌러줘!</div>',
        unsafe_allow_html=True,
    )
    activity, helper, settings = st.tabs(["🎮 시작·기록", "🤖 깡지 사용법", "🔊 소리·화면"])
    with activity:
        st.markdown(_cards([
            ("🗺️ 어디부터 시작할까?", "지도나 <b>왼쪽 메뉴</b>에서 장소를 골라줘.<br>처음에는 <b>할머니 폰 지키기</b>를 추천해!"),
            ("🎮 어떤 활동이 있을까?", "대화·추리·퍼즐로 대응을 연습해.<br>문자 필터, URL 확인, 개념·통계도 있어."),
            ("🪪 시민증은 선택이야", "<b>닉네임 + 비밀 숫자 6자리</b>로 만들어.<br>다음에도 같은 정보로 로그인할 수 있어."),
            ("🏅 기록과 도장을 모아봐", "시민증으로 게임 기록과 도장을 저장해.<br>통계·명예의 전당은 <b>도토리시 통계청</b>에서!"),
        ]) + '<div class="pi-note">가입 없이도 체험할 수 있어. 비회원 도장·진행은 새로고침하거나 창을 닫으면 사라질 수 있어. '
            '시민증도 게임 중간 화면을 모두 저장하는 건 아니야. 공개될 수 있는 닉네임에는 실제 이름·학교를 쓰지 마.</div>', unsafe_allow_html=True)
    with helper:
        st.markdown(_cards([
            ("👆 얼굴을 누르면 열려", "<b>오른쪽 아래 보라색 원 안의 깡지</b>를 찾아줘.<br>휴대폰 모양 버튼과는 다른 버튼이야."),
            ("💡 막히면 버튼으로 물어봐", "<b>사용법 · 이 화면 설명 · 힌트 줘</b><br>정답 대신 조작 방법과 살펴볼 단서를 안내해."),
            ("💬 직접 질문해도 좋아", "“이 게임은 어떻게 시작해?”처럼 적고<br><b>물어보기</b>를 눌러줘."),
            ("↔ 크기 조절·닫기", "<b>가− / 가+</b>로 대화창 크기를 조절해.<br><b>닫기 ✕ · 🎒 넣기</b>로 접고, 얼굴로 다시 열어."),
        ]) + '<div class="pi-note">일부 활동은 전용 도우미를 사용해. AI 답변은 틀릴 수 있어. AI 질문을 보내면 질문과 현재 보이는 게임 글이 '
            '외부 AI 서비스로 전송돼. 실제 개인정보·비밀번호·인증번호는 입력하지 마.</div>', unsafe_allow_html=True)
    with settings:
        st.markdown(_cards([
            ("☰ 설정은 왼쪽 메뉴에!", "입장 후 <b>왼쪽 사이드바</b>에서 설정해.<br>안 보이면 <b>왼쪽 위 펼치기 화살표</b>를 눌러줘."),
            ("🔊 효과음 켜기·끄기", "<b>🔊 효과음</b> 스위치로 켜거나 꺼.<br><b>🔔 소리 들어보기</b>로 소리를 확인해."),
            ("🎚️ 음량은 슬라이더로", "<b>🎚️ 음량</b>을 왼쪽으로 밀면 작아지고<br>오른쪽으로 밀면 커져. <b>0은 무음</b>이야."),
            ("🔠 글씨를 더 크게", "<b>🔠 큰 글씨로 보기</b>를 켜줘.<br>깡지 대화창 크기는 안쪽의 <b>가− / 가+</b>로!"),
        ]) + '<div class="pi-note">설정이 안 보이면 사이드바 안을 아래로 스크롤해봐. 다른 활동은 왼쪽 메뉴에서 골라줘. '
            '소리가 안 나면 기기 음소거·미디어 음량도 확인해. 통화·음성 재생은 효과음과 다를 수 있으니 해당 활동의 재생 안내를 확인해줘.</div>', unsafe_allow_html=True)
    st.markdown('<div class="pi-tip">🌰 <b>처음이라면 비회원으로 가볍게 시작해봐!</b> 시민증은 기록을 남기고 싶을 때 만들면 돼.</div>', unsafe_allow_html=True)
    with st.container(key="intro_actions"):
        guest, new, back = st.columns(3)
        if guest.button("👀 로그인 없이 둘러보기", key="intro_guest", width="stretch"):
            _enter("guest")
        if new.button("🪪 새 시민증 만들기", key="intro_new", width="stretch"):
            _enter("new")
        if back.button("🔑 다시 들어오기", key="intro_back", width="stretch"):
            _enter("back")
    st.caption("교육용 가상 상황이야. 실제 개인정보·인증번호는 입력하지 마. 실제 피해가 의심되면 맨 위 대처 안내를 먼저 확인해줘.")
    st.stop()
