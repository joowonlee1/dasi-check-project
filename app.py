import streamlit as st


st.set_page_config(
    page_title="잠깐!",
    page_icon="✋",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

    html, body, h1, h2, h3, h4, p, label,
    button, input, textarea, select {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: #FFFEF8;
    }

    [data-testid="stHeader"] {
        background: #FFFEF8;
    }

    [data-testid="stSidebar"] {
        background: #F0F5F4;
        border-right: 1px solid #CDDAD6;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        color: #172B3A;
        letter-spacing: -0.035em;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p {
        font-size: 1.03rem;
        line-height: 1.85;
    }

    [data-testid="stCaptionContainer"] p {
        color: #52636B;
        font-size: 0.92rem;
    }

    .hero {
        padding: 38px 30px;
        margin-bottom: 24px;
        background: #FFF4C7;
        border: 1px solid #E7D89E;
        border-radius: 24px;
    }

    .hero h1 {
        padding: 0;
        margin: 12px 0;
        font-size: clamp(3.5rem, 9vw, 5.5rem);
        font-weight: 900;
        color: #172B3A;
    }

    .hero .tag {
        color: #375C52;
        font-weight: 700;
    }

    .hero .lead {
        color: #172B3A;
        font-size: 1.25rem;
        font-weight: 700;
    }

    .hero .description {
        color: #40545E;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
        margin: 24px 0;
    }

    .feature-card {
        padding: 24px;
        background: #FFFFFF;
        border: 1px solid #CDDAD6;
        border-top: 4px solid #0F766E;
        border-radius: 16px;
    }

    .feature-card h3 {
        font-size: 1.2rem;
        padding: 0;
        margin: 10px 0;
    }

    .feature-card p {
        color: #40545E;
        margin: 0;
    }

    .feature-number {
        color: #0F766E;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .brand {
        color: #0F766E;
        font-size: 2rem;
        font-weight: 900;
    }

    .footer-note {
        border-top: 1px solid #CDDAD6;
        margin-top: 30px;
        padding-top: 18px;
        color: #52636B;
        font-size: 0.9rem;
        line-height: 1.8;
    }

    [data-testid="stButton"] button,
    [data-testid="stFormSubmitButton"] button {
        min-height: 48px;
        border-radius: 12px;
    }

    button:focus-visible, a:focus-visible {
        outline: 3px solid #0F766E !important;
        outline-offset: 3px;
    }

    @media (max-width: 640px) {
        .feature-grid {
            grid-template-columns: 1fr;
        }

        .hero {
            padding: 26px 20px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_home():
    st.markdown(
        """
        <section class="hero">
            <div class="tag">멈추고 · 확인하고 · 판단하기</div>
            <h1>잠깐!</h1>
            <p class="lead">익숙한 목소리에도, 낯선 링크에도 잠깐.</p>
            <p class="description">
                상황을 체험하고, 대화를 연습하고,<br>
                증거를 찾아 사건을 해결하는 피싱 예방 플랫폼.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    first, second = st.columns(2)

    with first:
        st.page_link(
            "pages/1_할머니_폰_지키기.py",
            label="할머니 폰 지키기 시작",
            icon="👵",
        )

    with second:
        st.page_link(
            "pages/3_피싱_방탈출.py",
            label="피싱 방탈출 입장",
            icon="🗝️",
        )

    st.subheader("어떤 방식으로 연습할까요?")

    features = [
        (
            "01 · 행동하기",
            "👵 할머니 폰 지키기",
            "속고 있는 가족을 어떻게 도울지, 언제 끼어들고 어떻게 말할지 연습해요.",
        ),
        (
            "02 · 대화하기",
            "💬 AI 모의대화",
            "직접 답변을 작성하며 의심스러운 요구에 대응하는 말을 연습해요.",
        ),
        (
            "03 · 추리하기",
            "🗝️ 피싱 방탈출",
            "증거를 모아 사건을 해결하고, 원하는 경우 닉네임으로 랭킹에 참여해요.",
        ),
        (
            "04 · 확인하기",
            "🔗 의심 URL 확인",
            "주소에 접속하지 않고 호스트명과 살펴볼 특징을 확인해요.",
        ),
        (
            "05 · 알아보기",
            "📊 개념과 통계",
            "피싱 관련 개념과 출처가 표시된 공식 자료를 살펴봐요.",
        ),
    ]

    cards = "".join(
        (
            '<article class="feature-card">'
            f'<div class="feature-number">{number}</div>'
            f"<h3>{title}</h3>"
            f"<p>{description}</p>"
            "</article>"
        )
        for number, title, description in features
    )

    st.markdown(
        f'<div class="feature-grid">{cards}</div>',
        unsafe_allow_html=True,
    )

    st.subheader("정답보다 중요한 판단의 근거")

    st.write(
        "상대방을 믿게 만든 단서와 직접 확인한 사실은 다를 수 있어요. "
        "왜 믿었는지, 무엇을 확인했는지 돌아보는 것이 ‘잠깐!’의 목표예요."
    )


navigation = st.navigation(
    {
        "잠깐!": [
            st.Page(
                show_home,
                title="홈",
                icon="✋",
                default=True,
            ),
        ],
        "체험과 연습": [
            st.Page(
                "pages/1_할머니_폰_지키기.py",
                title="할머니 폰 지키기",
                icon="👵",
            ),
            st.Page(
                "pages/2_모의대화_연습.py",
                title="AI 모의대화",
                icon="💬",
            ),
            st.Page(
                "pages/3_피싱_방탈출.py",
                title="피싱 방탈출",
                icon="🗝️",
            ),
        ],
        "확인과 학습": [
            st.Page(
                "pages/4_URL_확인.py",
                title="의심 URL 확인",
                icon="🔗",
            ),
            st.Page(
                "pages/5_개념과_통계.py",
                title="개념과 통계",
                icon="📊",
            ),
        ],
    }
)

with st.sidebar:
    st.divider()

    st.markdown(
        '<div class="brand">잠깐!</div>',
        unsafe_allow_html=True,
    )

    st.caption("익숙함을 믿기 전에,\n\n확인하는 습관부터.")

navigation.run()

st.markdown(
    """
    <div class="footer-note">
        잠깐! · 피싱 대응 교육 프로젝트<br>
        모든 체험은 가상 상황입니다.
        실제 개인정보나 인증번호를 입력하지 마세요.
    </div>
    """,
    unsafe_allow_html=True,
)
