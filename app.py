import streamlit as st

st.set_page_config(
    page_title="잠깐! | 피싱 대응 체험",
    page_icon="✋",
    layout="centered",
    initial_sidebar_state="expanded",
)


def show_home():
    st.title("✋ 잠깐!")
    st.subheader("익숙한 목소리에도, 낯선 링크에도 잠깐.")
    st.write(
        "전화부터 문자까지 이어지는 가상 상황을 체험하며 "
        "스스로 판단하고 대응하는 방법을 연습하는 피싱 예방 플랫폼입니다."
    )

    st.divider()

    st.subheader("처음이라면 여기부터")
    st.write(
        "가족으로 표시된 전화가 왔습니다. "
        "상대방은 급한 일이라며 곧 보낼 문자를 확인해 달라고 합니다. "
        "여러분은 어떻게 행동하겠어요?"
    )

    # 완성된 체험 페이지로 이동하는 링크입니다.
    st.page_link(
        "pages/1_신종피싱_모의체험.py",
        label="가족 사칭 전화 체험 시작하기",
        icon="📞",
    )

    st.divider()

    st.subheader("잠깐!에서 할 수 있는 것")

    # 현재 실제 구현 상태를 표시합니다.
    features = [
        (
            "📞 신종피싱 모의체험",
            "전화와 후속 문자에 대응하고 결과 리포트를 확인합니다.",
            "체험 가능",
        ),
        (
            "💬 모의대화 연습",
            "힌트를 받으며 의심스러운 요구에 대응하는 말을 연습합니다.",
            "준비 중",
        ),
        (
            "📩 문자 퀴즈",
            "문자 속 단서를 살펴보고 적절한 대응을 선택합니다.",
            "준비 중",
        ),
        (
            "🔗 URL 확인",
            "입력한 링크의 주소에서 의심할 특징을 살펴봅니다.",
            "입력 화면 구현 · 분석 준비 중",
        ),
        (
            "📊 개념과 통계",
            "피싱 관련 개념과 출처가 있는 공식 통계를 살펴봅니다.",
            "준비 중",
        ),
    ]

    for title, description, status in features:
        st.markdown(f"**{title}**")
        st.write(description)
        st.caption(f"현재 상태: {status}")

    st.divider()

    st.subheader("우리 프로젝트의 차별점")
    st.write(
        "전화와 문자를 하나의 연속된 상황으로 체험하고, "
        "내가 선택한 행동을 바탕으로 해설을 확인합니다."
    )
    st.write(
        "상대방을 믿게 된 단서와 "
        "내가 직접 확인한 사실을 구분하는 연습에 초점을 맞췄습니다."
    )

    st.info(
        "이 앱은 교육용 가상 체험입니다. "
        "체험 점수는 실제 피싱 확률을 뜻하지 않으며, "
        "실제 개인정보나 가족의 비밀 암호를 입력할 필요가 없습니다."
    )


show_home()
