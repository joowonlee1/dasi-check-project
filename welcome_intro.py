"""기존 앱 앞에 표시하는 소개 화면. 게임·인증·기록 저장 로직과 분리합니다."""
import streamlit as st
import dotori_data as dd
from mascot_ui import id_photo

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


def show_intro_if_needed():
    if (st.session_state.get(SEEN) or dd.citizen()
            or st.session_state.get("guest") or st.session_state.get("admin_open")):
        return

    # 이 분기에서는 아래의 로그인 복원·사이드바·게임·도우미를 실행하지 않습니다.
    st.markdown("""<style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"], [data-testid="stSidebarNav"],
    #dotori-helper {display:none!important;}
    .block-container {max-width:980px;padding-top:1.5rem;padding-bottom:2rem;}
    .wi-card {display:flex;align-items:center;gap:20px;background:#F7F8EC;
      border:1px solid #E3DFC1;border-radius:22px;padding:20px;margin:12px 0;}
    .wi-mascot {flex:0 0 100px;text-align:center;}
    .wi-mascot img {width:100px;height:auto;}
    .wi-mascot span {display:block;color:#36554A;font-weight:800;font-size:.9rem;}
    .wi-bubble {position:relative;flex:1;min-width:0;background:white;border:2px solid #C7DED1;
      border-radius:18px;padding:16px 20px;color:#293F38;word-break:keep-all;overflow-wrap:anywhere;}
    .wi-bubble::before {content:"";position:absolute;left:-10px;top:35px;width:16px;height:16px;
      background:white;border-left:2px solid #C7DED1;border-bottom:2px solid #C7DED1;transform:rotate(45deg);}
    .wi-bubble h1 {font-size:clamp(1.2rem,3vw,1.6rem);line-height:1.45;margin:0 0 10px;color:#20483F;}
    .wi-bubble p {margin:8px 0;line-height:1.75;}
    .wi-bubble strong {color:#20483F;}
    [data-testid="stButton"] button {min-height:48px;border-radius:12px;}
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {line-height:1.75;}
    .st-key-intro_help button {background:#FFF1F1!important;color:#B42318!important;
      border:2px solid #E5484D!important;font-weight:800!important;}
    @media(max-width:640px){
      .wi-card {flex-direction:column;gap:12px;padding:14px;}
      .wi-mascot {flex:auto;}.wi-mascot img {width:76px;}
      .wi-bubble {width:100%;box-sizing:border-box;padding:14px;}
      .wi-bubble::before {top:-10px;left:calc(50% - 9px);transform:rotate(135deg);}
      [data-testid="stTabs"] [role="tab"] {white-space:normal;height:auto;min-height:44px;}
    }
    </style>""", unsafe_allow_html=True)
    if st.button("🚨 실제 피해가 의심되나요? 대처 안내 바로 보기", key="intro_help", width="stretch"):
        _enter("help")
    try:
        photo = f'<img src="data:image/png;base64,{id_photo("ggangji_cream.png")}" alt="도토리시 안내 도우미 깡지">'
    except Exception:
        photo = '<span role="img" aria-label="깡지" style="font-size:64px">🐿️</span>'
    st.markdown(
        f'<section class="wi-card" aria-label="깡지의 앱 소개"><div class="wi-mascot">{photo}'
        '<span>도토리시 안내 도우미 · 깡지</span></div><div class="wi-bubble">'
        '<h1>안녕! 나는 도토리시 안내 도우미 깡지야! 🌰</h1>'
        '<p><strong>잠깐!</strong>은 수상한 전화와 문자에 '
        '<strong>멈추고, 확인하고, 판단하는 방법</strong>을 연습하는 피싱 예방 체험 앱이야.</p>'
        '<p>📱 수상한 연락에 대응하고 · 🔍 문자와 URL에서 단서를 찾고 · '
        '💬 사칭하는 상대에게 거절하는 말을 연습해봐!</p>'
        '<p>들어간 뒤 막히면 <strong>오른쪽 아래 보라색 원 안의 깡지 얼굴</strong>을 눌러줘. '
        '소리와 글씨 크기는 <strong>왼쪽 사이드바</strong>에서 바꿀 수 있어!</p>'
        '</div></section>', unsafe_allow_html=True,
    )
    st.caption("지금은 소개 화면이야. 아래 버튼으로 들어가면 사이드바와 깡지 도우미가 나타나. 자세한 내용은 안내 탭을 눌러봐!")
    activity, helper, settings = st.tabs(["🎮 체험·시민증", "🤖 깡지 도우미", "🔊 소리·화면·메뉴"])
    with activity:
        st.markdown("""
**처음이라면 ‘👀 로그인 없이 둘러보기’로 시작해!**

- **체험 시작:** 도토리시 지도나 왼쪽 메뉴에서 장소를 골라줘. 처음에는 **할머니 폰 지키기**를 추천해.
- **활동 종류:** 상황에서 대응 선택하기, AI 대화, 증거 추리와 퍼즐, 문자 필터 만들기, URL 확인, 개념·통계 학습을 할 수 있어. 활동별 이용 순서를 보고 시작하면 돼.
- **시민증은 선택:** **새 시민증 만들기**에서 닉네임과 비밀 숫자 6자리를 정해. 게임 기록과 도장을 저장할 수 있어. 닉네임은 명예의 전당에서 공개될 수 있으니 실제 이름·학교는 쓰지 마.
- **다시 들어오기:** 전에 만든 닉네임과 비밀 숫자로 로그인해. 게임을 하던 중간 화면이 모두 저장되는 것은 아니야.
- **비회원 이용:** 시민증 없이도 체험할 수 있어. 비회원의 도장과 진행 상태는 새로고침하거나 창을 닫으면 사라질 수 있어.
- **기록 보기:** 왼쪽 메뉴의 **도토리시 통계청**에서 활동 통계와 명예의 전당을 볼 수 있어.
""")
    with helper:
        st.markdown("""
**들어간 뒤 화면 오른쪽 아래에 떠 있는 ‘보라색 원 안의 깡지 얼굴’을 눌러줘!**

- **어떤 버튼이야?** 아래쪽의 휴대폰 모양 버튼과는 달라. **깡지 얼굴**을 누르면 도우미 대화창이 열려. 일부 활동은 전용 도우미를 사용해.
- **사용법:** 지금 화면에서 무엇을 해야 하는지 안내해.
- **이 화면 설명:** 현재 활동이 어떤 활동인지 설명해.
- **힌트 줘:** 비교하거나 살펴볼 단서를 안내해. 정답을 대신 풀어주는 기능은 아니야.
- **직접 질문:** 입력칸에 “이 게임은 어떻게 시작해?”처럼 적고 **물어보기**를 눌러줘.
- **대화창 크기:** 위쪽의 **가− / 가+**로 크기를 조절할 수 있어.
- **닫기·다시 열기:** **닫기 ✕**나 **🎒 넣기**를 누르면 얼굴 아이콘으로 돌아가. 다시 얼굴을 누르면 열려.

AI 답변은 틀릴 수 있으니 게임 안내와 함께 확인해줘. AI 질문을 보내면 질문과 현재 보이는 게임 글이 답변을 위해 외부 AI 서비스로 전송돼. **실제 개인정보·비밀번호·인증번호는 입력하지 마.**
""")
    with settings:
        st.markdown("""
**설정은 앱에 들어간 뒤 ‘왼쪽 사이드바’에서 할 수 있어!**

- **사이드바 열기:** 메뉴가 안 보이면 화면 **왼쪽 위의 화살표 모양 메뉴 펼치기 버튼**을 눌러줘. 휴대폰에서는 기본적으로 접혀 있을 수 있어.
- **효과음 켜기·끄기:** **🔊 효과음** 스위치로 게임 효과음을 켜거나 꺼.
- **음량 조절:** **🎚️ 음량** 슬라이더를 왼쪽으로 움직이면 작아지고, 오른쪽으로 움직이면 커져. 0으로 두면 소리가 나지 않아.
- **소리 확인:** **🔔 소리 들어보기**를 눌러 현재 음량을 확인해. 소리가 안 나면 효과음 스위치와 기기의 음소거·미디어 음량도 확인해줘.
- **통화 음성과 효과음:** 효과음 설정과 게임의 통화·음성 재생은 다를 수 있어. 음성은 해당 활동 화면의 재생 안내를 확인해줘.
- **글씨 크게 보기:** **🔠 큰 글씨로 보기** 스위치를 켜면 글씨와 버튼을 크게 볼 수 있어. 깡지 대화창 크기는 도우미 안의 **가− / 가+**로 조절해.
- **다른 활동으로 이동:** 왼쪽 메뉴에서 **홈**, **피해 도움**, **확인과 학습**, **체험과 연습**을 골라줘. 설정 항목이 안 보이면 사이드바 안을 아래로 스크롤해봐.
""")
    st.caption("교육용 가상 상황이야. 실제 개인정보·인증번호는 입력하지 마. 실제 피해가 의심되면 맨 위 빨간 대처 안내를 눌러줘.")
    # 좁은 화면에서도 버튼이 잘리지 않도록 세로로 배치합니다.
    if st.button("👀 로그인 없이 둘러보기", key="intro_guest", type="primary", width="stretch"):
        _enter("guest")
    first, second = st.columns(2)
    if first.button("🪪 새 시민증 만들기", key="intro_new", width="stretch"):
        _enter("new")
    if second.button("🔑 다시 들어오기", key="intro_back", width="stretch"):
        _enter("back")
    st.stop()
