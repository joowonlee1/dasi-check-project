import html

import streamlit as st
from mascot_ui import show_mascot
import dotori_data as dd


st.set_page_config(
    page_title="잠깐!",
    page_icon="✋",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────
# 전체 페이지 공통 디자인
# ─────────────────────────────────────

st.markdown(
    """
    <style>
    .stApp,
    [data-testid="stHeader"] {
        background: #FFFEFA;
    }

    [data-testid="stSidebar"] {
        background: #EDF4F1;
        border-right: 1px solid #CDDAD6;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        font-family:
            'Malgun Gothic',
            'Apple SD Gothic Neo',
            sans-serif;
        letter-spacing: -0.035em;
        line-height: 1.4;
    }

    h1 {
        font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
    }

    h2 {
        font-size: 1.55rem !important;
        margin-top: 1.2rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p {
        font-size: 1.05rem;
        line-height: 1.85;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }

    [data-testid="stCaptionContainer"] p {
        color: #52616B !important;
        font-size: 0.94rem !important;
        line-height: 1.7;
    }

    [data-testid="stWidgetLabel"] p {
        font-weight: 700;
    }

    /* 입력칸 */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
    }

    [data-testid="stTextInput"] input {
        min-height: 48px;
    }

    /* 버튼 */
    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stDownloadButton"] button {
        min-height: 48px;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 700;
    }

    [data-testid="stBaseButton-primary"] {
        background: #0F766E;
        border-color: #0F766E;
        color: white;
    }

    /* 중요한 버튼(시작·제출·다시 도전)은 크고 넓게 보여 줍니다 */
    [data-testid="stElementContainer"]:has([data-testid="stBaseButton-primary"]),
    [data-testid="stElementContainer"]:has([data-testid="stBaseButton-primaryFormSubmit"]),
    [data-testid="stButton"]:has([data-testid="stBaseButton-primary"]),
    [data-testid="stFormSubmitButton"]:has([data-testid="stBaseButton-primaryFormSubmit"]) {
        width: 100% !important;
    }

    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primaryFormSubmit"] {
        width: 100% !important;
        min-height: 58px !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.25);
    }

    [data-testid="stBaseButton-primary"] p,
    [data-testid="stBaseButton-primaryFormSubmit"] p {
        font-size: 1.15rem !important;
        font-weight: 800;
    }

    /* 페이지 링크: 글꼴에 따라 글씨 아래가 잘리지 않게 높이를 글씨에 맞춥니다 */
    [data-testid="stPageLink"] a {
        height: auto !important;
        min-height: 44px;
        padding: 8px 12px !important;
    }

    [data-testid="stPageLink"] a p,
    [data-testid="stPageLink"] a span {
        overflow: visible !important;
        line-height: 1.6 !important;
        white-space: normal !important;
    }

    /* 홈 맨 위 긴급 안내 링크는 눈에 띄게 */
    .st-key-emergency_link {
        margin-top: 18px;
    }

    .st-key-emergency_link [data-testid="stPageLink"] a {
        border: 2px solid #E5484D;
        background: #FFF1F1;
        border-radius: 12px;
    }

    .st-key-emergency_link [data-testid="stPageLink"] a p {
        color: #B42318 !important;
        font-weight: 800 !important;
    }

    /* 입력 영역 */
    [data-testid="stForm"] {
        border: 1px solid #BBCFC7;
        border-radius: 16px;
        padding: 1.3rem;
    }

    /* 안내와 경고 */
    [data-testid="stAlert"] {
        border-radius: 12px;
        line-height: 1.8;
    }

    /* 대화 말풍선 */
    [data-testid="stChatMessage"] {
        padding: 1.1rem;
        border: 1px solid #D7E2DD;
        border-radius: 16px;
        margin-bottom: 0.7rem;
    }

    /* 접을 수 있는 설명 */
    [data-testid="stExpander"] {
        border-radius: 12px;
        border-color: #BCCEC6;
    }

    [data-testid="stExpander"] summary {
        min-height: 48px;
        font-weight: 700;
    }

    /* 표 */
    [data-testid="stTable"] th {
        background: #E4F0EA;
        color: #173D35;
    }

    [data-testid="stTable"] td,
    [data-testid="stTable"] th {
        padding: 0.7rem !important;
        line-height: 1.7 !important;
    }

    /* 탭 모양과 선택 표시 (탭 이름에 번호가 이미 있어서 번호는 따로 붙이지 않아요) */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 8px;
        overflow-x: auto;
        padding: 6px 0 12px;
    }

    [data-testid="stTabs"] [role="tablist"] [role="tab"] {
        min-height: 50px;
        height: auto;
        flex-shrink: 0;
        padding: 10px 14px;
        background: #F1F5F2;
        border: 1px solid #CBDAD2;
        border-radius: 12px;
        gap: 8px;
    }

    [data-testid="stTabs"] [role="tablist"]
    [role="tab"][aria-selected="true"] {
        background: #E0F0E8;
        border: 2px solid #0F766E;
    }

    [data-testid="stTabs"] [role="tablist"] [role="tab"] p {
        font-size: 1rem !important;
        font-weight: 700;
        white-space: nowrap;
    }

    /* 키보드로 이동할 때 현재 위치 표시 */
    button:focus-visible,
    a:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 3px solid #0F766E !important;
        outline-offset: 3px;
    }

    /* 홈 화면 */
    .hero {
        padding: 30px;
        background: #FFF2C4;
        border: 1px solid #DFCE8D;
        border-radius: 22px;
        margin: 0 0 24px;
    }

    .hero h1 {
        font-size: 3.6rem !important;
        margin: 8px 0;
    }

    .hero p {
        color: #253F39;
    }

    /* 페이지별 이용 순서 */
    .route {
        padding: 16px 20px;
        border: 1px solid #CBDAD2;
        border-left: 5px solid #0F766E;
        border-radius: 12px;
        background: #F0F7F3;
        margin-bottom: 24px;
        color: #233D35;
    }

    .route strong {
        display: block;
        margin-bottom: 6px;
        color: #0B655B;
    }

    .route p {
        margin: 0;
        font-size: 1rem !important;
    }

    /* 도토리시 */
    .city-intro {
        background: linear-gradient(135deg, #FFF4D6, #E8F4EC);
        border: 2px solid #E2C98A;
        border-radius: 20px;
        padding: 18px 20px;
        margin: 4px 0 12px;
        color: #2F3B2A;
        font-weight: 700;
        line-height: 1.8;
        word-break: keep-all;
    }

    .city-intro b {
        display: block;
        font-size: 1.35rem;
        color: #6B4A1E;
        margin-bottom: 4px;
    }

    .st-key-dotori_map {
        background: #EAF4E4;
        border: 2px dashed #A7C79A;
        border-radius: 22px;
        padding: 12px;
    }

    .st-key-dotori_map [data-testid="stPageLink"] a {
        background: #FFFFFF;
        border: 1.5px solid #CFE0C6;
        border-radius: 14px;
    }

    .st-key-dotori_map [data-testid="stPageLink"] a:hover {
        background: #FFF7E3;
        border-color: #E2C98A;
    }

    .place-tag {
        display: inline-block;
        background: #FFF4D6;
        color: #6B4A1E;
        border: 1px solid #E2C98A;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .route .place {
        display: block;
        color: #6B4A1E;
        font-weight: 800;
        font-size: 1.05rem;
        margin-bottom: 2px;
    }

    .route .place-line {
        margin: 0 0 8px;
        color: #3E4A3A;
        font-weight: 600;
    }

    .footer-note {
        border-top: 1px solid #CBDAD2;
        margin-top: 32px;
        padding-top: 16px;
        color: #52616B;
        font-size: 0.94rem;
        line-height: 1.8;
    }

    /* 작은 화면 */
    @media (max-width: 640px) {
        .block-container {
            padding: 2rem 1rem 3rem;
        }

        .hero {
            padding: 22px;
        }

        [data-testid="stTabs"] [role="tablist"] [role="tab"] {
            padding: 8px 10px;
        }
    }

    /* 움직임 최소화 설정 존중 */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────
# 페이지 정보
# 기존 파일 경로를 유지합니다.
# ─────────────────────────────────────

FEATURES = [
    (
        "01",
        "할머니 폰 지키기",
        "📱",
        "pages/1_할머니_폰_지키기.py",
        "연락 확인 → 대응 선택 → 할머니와 함께 확인",
        "할머니 휴대전화에 들어오는 연락을 살펴보고, 피싱에 대응하는 방법을 연습해요.",
    ),
    (
        "02",
        "AI 모의대화",
        "💬",
        "pages/2_모의대화_연습.py",
        "상황 선택 → 직접 답변 → 대응 리포트",
        "의심스러운 요구에 어떻게 답할지 직접 연습해요.",
    ),
    (
        "03",
        "피싱 방탈출",
        "🗝️",
        "pages/3_피싱_방탈출.py",
        "규칙 확인 → 입장 → 증거 수집 → 잠금 해제",
        "증거를 비교해 사건을 해결하고 원하는 경우 랭킹에 참여해요.",
    ),
    (
        "04",
        "의심 URL 확인",
        "🔗",
        "pages/4_URL_확인.py",
        "주소 입력 → 특징 확인 → 공식 경로로 재확인",
        "주소에 접속하지 않고 문자열에 나타나는 특징을 살펴봐요.",
    ),
    (
        "05",
        "개념과 통계",
        "📊",
        "pages/5_개념과_통계.py",
        "개념 이해 → 통계 연도 확인 → 출처 살펴보기",
        "체험에서 만난 개념과 출처가 있는 통계 자료를 읽어요.",
    ),
    (
        "06",
        "가짜뉴스 확산 막기",
        "🌐",
        "pages/6_가짜뉴스_확산막기.py",
        "사전 알림 → 확산 막기 → 수법 공개",
        "주민 연결망에서 퍼지는 가짜 소식을 카드로 막아요. 누구를 먼저 지킬지가 전략이에요.",
    ),
    (
        "07", "피해가 의심될 때", "🚨", "pages/7_피해_대처_안내.py",
        "긴급 연락 → 상황 선택 → 필요한 조치 확인",
        "송금·정보 노출·앱 설치 등 상황별로 공식 대처 안내를 확인해요.",
    ),
    (
        "08", "대처유형 테스트", "🧭", "pages/8_대처유형_테스트.py",
        "12문항 응답 → 대처 습관 확인 → 결과 카드 저장",
        "16가지 교육용 유형으로 내 습관과 연습할 상황을 살펴봐요.",
    ),
    (
        "09", "단톡방 마피아", "🕵️", "pages/9_단톡방_마피아.py",
        "대화 읽기 → 조사 3번 → 마피아 투표",
        "친구 5명 중 숨은 사칭 계정(마피아)을 말투·질문·프로필로 찾아내요. 2~4명이 함께 할 수도 있어요.",
         ),
    (
        "10", "중고거래 사기단 추리", "🔐", "pages/10_중고거래_사기단_추리.py",
        "메모 해독 → 추리 표 → 진짜 지목",
        "사기단 메모의 암호를 풀어 단서를 얻고, 논리 표로 판매자 5명 중 진짜를 찾아내요.",
    ),
    (
        "11", "피싱 필터 만들기", "🤖", "pages/11_피싱_필터_만들기.py",
        "규칙 조립 → 필터 실행 → 오탐·미탐 고치기",
        "조건 블록을 ‘그리고·또는’으로 조립해 수상한 문자만 걸러 내는 필터를 만들어요.",
    ),
    (
        "12", "큐싱 노노그램", "🧩", "pages/12_큐싱_노노그램.py",
        "단서 읽기 → 칸 칠하기 → 그림 복원",
        "숫자 단서로 칸을 칠해 찢긴 QR 스티커를 복원하고, QR 코드 피싱(큐싱)을 알아봐요.",
    ),
    (
        "13", "도토리시 통계청", "📈", "pages/13_도토리시_통계청.py",
        "게임 고르기 → 통계 보기 → 명예의 전당",
        "시민들이 게임에서 남긴 진짜 기록으로 사람들이 어디서 많이 속는지 보고, 명예의 전당도 확인해요.",
    ),
]

# ─────────────────────────────────────
# 도토리시 세계관
# 모든 활동은 가상의 도시 '도토리시' 곳곳에서 일어나요. (실제 지역·기관과 관계없음)
# 번호: (장소 아이콘, 동네, 장소, 들어갈 때 보이는 한 줄 소개)
# ─────────────────────────────────────

CITY_INTRO = (
    "도토리시는 다람쥐처럼 부지런한 시민들이 사는 가상의 도시예요. "
    "그런데 요즘 도시 곳곳에 수상한 연락과 소문이 돌고 있어요. "
    "장소를 하나씩 돌며 시민들을 지켜 주세요!"
)

PLACES = {
    "01": ("🏡", "상수리동", "할머니 댁", "주말 오전, 할머니 댁에 놀러 왔어요. 그런데 할머니 휴대전화가 자꾸 울려요."),
    "02": ("🎙️", "시청로", "시민훈련센터 대화 연습실", "수상한 연락에 어떻게 답할지, 실제로 받기 전에 미리 연습하는 곳이에요."),
    "03": ("🗝️", "다람쥐동", "민서네 집", "도토리시 사건 파일 01. 같은 엄마 번호로 서로 다른 연락이 왔어요."),
    "04": ("🚧", "도토리역 앞", "사이버 검문소", "링크가 도시 안으로 들어오기 전에, 주소부터 꼼꼼히 검문해요."),
    "05": ("📚", "시청로", "도토리 시립도서관", "체험에서 만난 수법의 뜻과 공식 통계를 찾아 읽는 곳이에요."),
    "06": ("⛲", "중앙동", "도토리 광장", "광장에서 시작된 가짜 소식이 이웃을 타고 번지고 있어요."),
    "07": ("🚑", "중앙동", "시민안전센터", "실제 상황에서 쓰는 진짜 대처 안내예요."),
    "08": ("🪪", "시청로", "시민 등록소", "질문에 답하면 나의 피싱 대처유형이 적힌 결과 카드를 받아요."),
    "09": ("🏫", "떡갈나무동", "도토리고 2학년 3반 단톡방", "우리 반 단톡방에 친구를 사칭한 계정이 숨어들었어요."),
    "10": ("🛒", "개암골", "도토리 중고마켓", "인기 운동화를 둘러싼 거래 중 진짜 판매자는 단 한 명이에요."),
    "11": ("📮", "시청로", "도토리 우체국 문자 필터실", "도시로 들어오는 문자를 걸러 낼 필터 규칙을 직접 만들어요."),
    "12": ("🅿️", "중앙동", "도토리 공영주차장", "주차 정산기에 수상한 QR 스티커가 덧붙어 있었어요. 찢긴 조각으로 그림을 복원해요."),
    "13": ("🏛️", "시청로", "도토리시 통계청", "시민들이 게임에서 남긴 기록이 숫자로 모이는 곳이에요. 이름 없이 숫자만 모아요."),
}


# ─────────────────────────────────────
# 홈
# ─────────────────────────────────────

def show_home():
    with st.container(key="emergency_link"):
        st.page_link("pages/7_피해_대처_안내.py", label="실제 피해가 의심되나요? 대처 안내 바로 보기", icon="🚨")
    with st.container(border=True):
        st.title("✋ 잠깐!")
        st.caption("멈추고 · 확인하고 · 판단하기")

        show_mascot(
            "stop",
            "익숙한 연락도, 낯선 링크도 한 번 더 확인해요.",
            width=120,
        )

        st.write(
            "선택하고, 대화하고, 증거를 찾으며 배우는 "
            "피싱 예방 체험입니다."
        )

        st.page_link(
            FEATURES[0][3],
            label="처음이라면 · 할머니 폰 지키기 시작",
            icon="📱",
        )

    st.subheader("🌰 도토리시 지도")
    st.markdown(
        f'<div class="city-intro"><b>도토리시에 오신 걸 환영해요!</b>{html.escape(CITY_INTRO)}</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="dotori_map"):
        # 두 칸씩 한 줄로 만들어, 휴대폰에서도 같은 순서로 보이게 해요.
        for i, (number, title, icon, path, steps, description) in enumerate(FEATURES):
            if i % 2 == 0:
                map_cols = st.columns(2)
            place_icon, town, place, _ = PLACES[number]
            map_cols[i % 2].page_link(path, label=f"{town} · {place}", icon=place_icon, width="stretch")

    st.subheader("어떤 활동을 해볼까요?")
    st.caption(
        "원하는 활동부터 시작해도 괜찮아요."
    )

    for number, title, icon, path, steps, description in FEATURES:
        with st.container(border=True):
            place_icon, town, place, _ = PLACES[number]
            st.markdown(
                f'<span class="place-tag">{place_icon} {html.escape(town)} · {html.escape(place)}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"### {icon} {title}")
            st.write(description)
            st.caption(steps)

            st.page_link(
                path,
                label=f"{title} 시작하기",
                icon="➡️",
            )

    with st.expander("이용 전에 알아두세요"):
        show_mascot(
            "welcome",
            "반가워요! 아래 내용을 확인하고 함께 연습해요.",
            width=90,
        )

        st.markdown(
            "- 실제 개인정보나 인증번호는 입력하지 마세요.\n"
            "- 체험은 가상이며 실제 연락이나 송금을 실행하지 않습니다.\n"
            "- URL 확인 결과는 사이트의 안전을 보장하지 않습니다.\n"
            "- 방탈출 랭킹과 명예의 전당에 참여하려면 "
            "메뉴의 ‘도토리시 시민증’에서 닉네임을 만들어 주세요."
        )


# ─────────────────────────────────────
# 페이지 이동
# ─────────────────────────────────────


home = st.Page(
    show_home,
    title="홈",
    icon="✋",
    default=True,
)

feature_pages = [
    st.Page(
        row[3],
        title=row[1],
        icon=row[2],
    )
    for row in FEATURES
]

page_by_number = {row[0]: page for row, page in zip(FEATURES, feature_pages)}
citizen_page = st.Page("pages/0_도토리시_시민증.py", title="도토리시 시민증", icon="🪪")

navigation = st.navigation(
    {
        "잠깐!": [home, citizen_page],
        "피해 도움": [page_by_number["07"]],
        "체험과 연습": [page_by_number[n] for n in ("01", "02", "03", "06", "09", "10", "11", "12", "08")],
        "확인과 학습": [page_by_number[n] for n in ("04", "05", "13")],
    },
    expanded=True,  # 페이지가 많아져도 'View more'로 접히지 않고 메뉴가 모두 보이게
)


# ─────────────────────────────────────
# 사이드바
# ─────────────────────────────────────

with st.sidebar:
    # 큰 글씨 모드: 글씨가 작아 읽기 힘든 사람(어르신 등)도 쓸 수 있게 화면 전체를 키워요.
    big_text = st.toggle("🔠 큰 글씨로 보기", key="big_text", help="본문 글씨와 버튼을 크게 보여 줘요.")
    if big_text:
        st.markdown(
            """<style>
            [data-testid="stMainBlockContainer"] {zoom: 1.2;}
            /* 게임 화면(iframe)은 폭이 정해져 있어 키우면 휴대폰에서 옆으로 넘쳐요. 원래 크기로 둬요. */
            [data-testid="stMainBlockContainer"] iframe {zoom: calc(1 / 1.2);}
            [data-testid="stSidebarNav"] a span {font-size: 1.12rem !important;}
            </style>""",
            unsafe_allow_html=True,
        )

    # 로그인했을 때만 시민증 상태를 보여 줘요(시민증 만들기는 위 메뉴에 있어요).
    me = dd.citizen()
    if me:
        st.markdown(
            '<div style="background:#FFF4D6;border:2px solid #E2C98A;border-radius:14px;padding:8px 12px;'
            'font-weight:800;color:#6B4A1E;margin-bottom:6px;">🪪 시민 '
            f'<span style="color:#20483F">{html.escape(me["nickname"])}</span> 님</div>',
            unsafe_allow_html=True,
        )
    show_mascot(
        "stop",
        "멈추고, 확인하고, 판단하기",
        width=90,
    )

    st.caption(
        "캐릭터 원작 출처: "
        "[깡지 · @ggang.zi_](https://www.instagram.com/ggang.zi_/)"
    )

    st.caption(
        "웹앱에 사용한 일부 동작 이미지는 "
        "원작 캐릭터를 바탕으로 AI를 활용해 제작했습니다."
    )

    st.caption(
        "처음이라면 ‘할머니 폰 지키기’를 추천해요. "
        "원하는 활동부터 이용해도 괜찮아요."
    )




# ─────────────────────────────────────
# 현재 페이지의 이용 안내
# ─────────────────────────────────────

current = next(
    (
        row
        for row, page in zip(
            FEATURES,
            feature_pages,
        )
        if page.url_path == navigation.url_path
    ),
    None,
)

if current:
    (
        number,
        title,
        icon,
        path,
        steps,
        description,
    ) = current

    place_icon, town, place, place_line = PLACES[number]
    # 실제 피해 안내(07)는 급한 사람이 바로 읽도록 세계관 문구를 붙이지 않아요.
    place_html = (
        ""
        if number == "07"
        else f'<span class="place">{place_icon} 도토리시 {html.escape(town)} · {html.escape(place)}</span>'
        f'<p class="place-line">{html.escape(place_line)}</p>'
    )
    st.markdown(
        (
            '<div class="route">'
            f"{place_html}"
            # 번호는 보여 주지 않고, 긴급 안내(07)만 표시를 붙입니다.
            f"<strong>{'🚨 긴급 안내 · ' if number == '07' else ''}"
            f"{html.escape(title)} 이용 순서</strong>"
            f"<p>{html.escape(steps)}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if number == "03":
        st.info(
            "📌 시작 전 필독\n\n"
            "안내서의 04번 ‘꼭 알아야 할 7가지’를 확인하세요.\n\n"
            "증거는 읽은 뒤 직접 수집해야 해요. "
            "게임 중에는 새로고침을 피하세요.\n\n"
            "실제 제한 시간은 30분이며, 게임을 시작하면 "
            "타이머가 작동합니다."
        )

        # 방탈출의 6개 안내 탭 중 네 번째를 강조합니다.
        st.markdown(
            """
            <style>
            [data-testid="stTabs"] [role="tablist"]
            :is([role="tab"]) {
                scroll-margin-inline: 12px;
            }

            [data-testid="stTabs"] [role="tablist"]
            :is([role="tab"]):focus-visible {
                outline-offset: -3px;
            }

            [data-testid="stTabs"] [role="tablist"]
            :is([role="tab"]):nth-of-type(4) {
                scroll-margin-inline: 12px;
            }

            [data-testid="stTabs"] [role="tablist"]:has(
                > [role="tab"]:nth-of-type(6)
            ) > [role="tab"]:nth-of-type(4) {
                background: #FFF0C7;
                border: 2px solid #986500;
            }

            [data-testid="stTabs"] [role="tablist"]:has(
                > [role="tab"]:nth-of-type(6)
            ) > [role="tab"]:nth-of-type(4)::after {
                content: "필독";
                font-size: 0.8rem;
                font-weight: 800;
                background: #785000;
                color: white;
                padding: 2px 6px;
                border-radius: 5px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    elif number == "04":
        st.info(
            "**확인 범위** · 주소의 특징을 설명하는 도구입니다. "
            "‘특징 없음’이 ‘안전함’을 뜻하지는 않습니다."
        )

    elif number == "05":
        st.info(
            "**자료 읽기** · 통계의 기준 연도와 출처를 "
            "함께 확인하세요. 현재 자료는 "
            "실시간 자동 갱신 통계가 아닙니다."
        )


# ─────────────────────────────────────
# 선택한 기존 페이지 실행
# ─────────────────────────────────────

navigation.run()


# ─────────────────────────────────────
# 공통 하단 안내
# ─────────────────────────────────────

st.markdown(
    """
    <div class="footer-note">
        <b>잠깐! · 피싱 대응 교육 프로젝트</b><br>
        체험과 테스트는 교육용입니다. 실제 피해는 ‘피해가 의심될 때’ 안내를 확인하세요.<br>
        실제 개인정보나 인증번호를 이 웹앱에 입력하지 마세요.
    </div>
    """,
    unsafe_allow_html=True,
)
