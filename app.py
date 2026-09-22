import streamlit as st


st.set_page_config(
    page_title="잠깐!",
    page_icon="✋",
    layout="centered",
    initial_sidebar_state="expanded",
)


def apply_design():
    """모든 페이지에서 사용하는 공통 디자인입니다."""
    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&display=swap'
        );

        /* 한글 본문과 입력 요소에 공통 폰트를 적용합니다. */
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"],
        h1, h2, h3, h4, p, label,
        button, input, textarea, select {
            font-family: 'Noto Sans KR', sans-serif;
        }

        /* 은은한 빛과 격자로 디지털 공간의 분위기를 만듭니다. */
        .stApp {
            background-color: #0B1220;
            background-image:
                radial-gradient(
                    ellipse at 90% 5%,
                    rgba(94, 234, 212, 0.10),
                    transparent 45%
                ),
                linear-gradient(
                    rgba(148, 163, 184, 0.035) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(148, 163, 184, 0.035) 1px,
                    transparent 1px
                );
            background-size: auto, 40px 40px, 40px 40px;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 18, 32, 0.95);
        }

        [data-testid="stSidebar"] {
            background-color: #101B2D;
            border-right: 1px solid #28364B;
        }

        .block-container {
            max-width: 960px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            letter-spacing: -0.04em;
        }

        p {
            line-height: 1.8;
        }

        /* 첫 화면의 대표 영역 */
        .hero {
            padding: 42px 34px;
            margin-bottom: 24px;
            border: 1px solid #34445B;
            border-radius: 26px;
            background: linear-gradient(
                135deg,
                #192C43 0%,
                #111D30 65%,
                #173534 100%
            );
        }

        .eyebrow {
            color: #5EEAD4;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.12em;
        }

        .hero h1 {
            margin: 10px 0 16px;
            padding: 0;
            color: #FDE68A;
            font-size: clamp(3.5rem, 9vw, 5.5rem);
            font-weight: 900;
            line-height: 1.15;
        }

        .hero .lead {
            color: #F1F5F9;
            font-size: 1.25rem;
            font-weight: 700;
        }

        .hero .description {
            color: #C3CFDF;
            margin-bottom: 0;
        }

        /* 첫 화면에서만 사용하는 기능 카드 */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 28px;
        }

        .feature-card {
            padding: 24px;
            border: 1px solid #34445B;
            border-radius: 18px;
            background: #142136;
        }

        .feature-number {
            color: #5EEAD4;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .feature-card h3 {
            color: #F1F5F9;
            font-size: 1.12rem;
            margin: 10px 0;
            padding: 0;
        }

        .feature-card p {
            color: #C3CFDF;
            font-size: 0.95rem;
            margin: 0;
        }

        .brand {
            color: #FDE68A;
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.06em;
        }

        .footer-note {
            margin-top: 30px;
            padding-top: 18px;
            border-top: 1px solid #34445B;
            color: #B8C5D6;
            font-size: 0.82rem;
            line-height: 1.8;
        }

        /* 키보드로 조작할 때도 현재 위치가 보이게 합니다. */
        button:focus-visible,
        a:focus-visible {
            outline: 3px solid #FDE68A !important;
            outline-offset: 3px;
        }

        @media (max-width: 640px) {
            .hero {
                padding: 28px 22px;
            }

            .feature-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_home():
    """구현 상태를 매번 수정할 필요가 없는 첫 화면입니다."""
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">멈추고 · 확인하고 · 판단하기</div>
            <h1>잠깐!</h1>
            <p class="lead">
                익숙한 목소리에도, 낯선 링크에도 잠깐.
            </p>
            <p class="description">
                전화부터 문자까지 이어지는 상황 속에서<br>
                나의 선택으로 배우는 피싱 대응 체험.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/1_신종피싱_모의체험.py",
        label="가족 사칭 전화 체험 시작하기",
        icon="📞",
    )

    st.subheader("하나의 연락, 여러 갈래의 선택")
    st.write(
        "엄마로 표시된 전화가 왔습니다. "
        "곧이어 문자를 확인해 달라는 요구가 이어집니다. "
        "무엇을 믿고, 무엇을 확인할지 직접 선택해 보세요."
    )

    features = [
        (
            "01 · EXPERIENCE",
            "신종피싱 모의체험",
            "내 선택에 따라 달라지는 전화와 문자 상황.",
        ),
        (
            "02 · PRACTICE",
            "모의대화 연습",
            "의심스러운 요구에 대응하는 말을 연습하는 공간.",
        ),
        (
            "03 · QUIZ",
            "문자 대응 퀴즈",
            "문자 속 단서를 살펴보고 다음 행동을 선택하는 퀴즈.",
        ),
        (
            "04 · URL",
            "의심 URL 확인",
            "링크 주소에서 살펴봐야 할 특징을 알아보는 공간.",
        ),
        (
            "05 · LEARN",
            "개념과 통계",
            "피싱의 개념과 공식 자료를 바탕으로 배우는 공간.",
        ),
    ]

    # 아래 HTML에는 작성자가 정한 고정 문구만 넣습니다.
    cards = "".join(
        f"""
        <article class="feature-card">
            <div class="feature-number">{number}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </article>
        """
        for number, title, description in features
    )

    st.markdown(
        f'<div class="feature-grid">{cards}</div>',
        unsafe_allow_html=True,
    )

    st.caption("각 기능은 왼쪽 메뉴에서 열 수 있어요.")

    st.subheader("정답보다 중요한 것은 판단의 이유")
    st.write(
        "상대방을 믿게 만든 단서와 직접 확인한 사실은 다를 수 있어요. "
        "체험을 마친 뒤, 내가 어떤 근거로 행동했는지 돌아보세요."
    )


apply_design()

# app.py가 모든 페이지의 공통 화면 역할을 합니다.
# 기존 pages 폴더의 파일을 여기에서 명시적으로 연결합니다.
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
                "pages/1_신종피싱_모의체험.py",
                title="신종피싱 모의체험",
                icon="📞",
            ),
            st.Page(
                "pages/2_모의대화_연습.py",
                title="모의대화 연습",
                icon="💬",
            ),
            st.Page(
                "pages/3_문자_퀴즈.py",
                title="문자 대응 퀴즈",
                icon="📩",
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
    st.markdown('<div class="brand">잠깐!</div>', unsafe_allow_html=True)
    st.caption("익숙함을 믿기 전에,\n\n확인하는 습관부터.")

navigation.run()

st.markdown(
    """
    <div class="footer-note">
        잠깐! · 피싱 대응 교육 프로젝트<br>
        가상 체험과 학습을 위한 서비스입니다.
        실제 개인정보나 인증번호를 입력하지 마세요.
    </div>
    """,
    unsafe_allow_html=True,
)
