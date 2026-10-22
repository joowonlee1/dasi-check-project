import html

import streamlit as st
from mascot_ui import show_mascot


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
        "진짜·가짜 강 건너기",
        "🌊",
        "pages/6_진짜가짜_강건너기.py",
        "운영자 미션 → 수법 공개 → 강 건너기",
        "가짜 계정 운영자가 되어 속이는 수법을 써 보고, 받는 사람이 되어 그 수법을 가려내요.",
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
]

# ─────────────────────────────────────
# 홈
# ─────────────────────────────────────

def show_home():
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

    st.subheader("어떤 활동을 해볼까요?")
    st.caption(
        "번호는 추천 순서예요. 원하는 활동부터 시작해도 괜찮아요."
    )

    for number, title, icon, path, steps, description in FEATURES:
        with st.container(border=True):
            st.markdown(f"### {number} · {icon} {title}")
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
            "- 공개 랭킹에 참여하려면 방탈출 시작 전에 "
            "닉네임으로 입장하세요."
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

navigation = st.navigation(
    {
        "잠깐!": [home],
        "피해 도움": [page_by_number["07"]],
        "체험과 연습": [page_by_number[n] for n in ("01", "02", "03", "06", "08")],
        "확인과 학습": [page_by_number[n] for n in ("04", "05")],
    }
)


# ─────────────────────────────────────
# 사이드바
# ─────────────────────────────────────

with st.sidebar:
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

    st.markdown(
        (
            '<div class="route">'
            f"<strong>{number} · "
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
