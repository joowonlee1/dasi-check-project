import streamlit as st

# 각 단계의 상황과 선택지입니다.
# 점수는 실제 사기 확률이 아닌 교육용 위험 행동 점수입니다.
SCENARIO = [
    {
        "title": "1단계 · 익숙한 이름의 전화",
        "message": (
            "📱 휴대전화에 저장된 '엄마'의 이름과 번호가 표시됩니다.\n\n"
            "상대방: “나 엄마야. 급한 일이 생겼어. "
            "지금 보낼 문자부터 확인해 줘.”"
        ),
        "choices": [
            {
                "text": "엄마로 표시되니 믿고, 시키는 대로 하겠다고 말한다.",
                "risk": 30,
                "feedback": (
                    "화면에 표시된 이름과 번호만으로 상대를 믿었어요. "
                    "표시 정보와 별도로 확인한 사실을 구분하는 연습이 필요해요."
                ),
            },
            {
                "text": "무슨 일인지 물어보되, 아직 상대의 신원을 확신하지 않는다.",
                "risk": 10,
                "feedback": (
                    "바로 따르지 않고 질문했어요. "
                    "다만 같은 통화에서 들은 설명만으로 확인을 마치지는 않았는지 살펴보세요."
                ),
            },
            {
                "text": "통화를 종료하고, 별도의 연락으로 가족에게 확인한다.",
                "risk": 0,
                "feedback": (
                    "상대방의 주장과 별개로 사실을 확인하려는 행동을 선택했어요."
                ),
            },
        ],
    },
    {
        "title": "2단계 · 통화 뒤에 도착한 문자",
        "message": (
            "📩 체험을 위해 후속 문자 상황도 살펴봅니다.\n\n"
            "“방금 전화한 엄마야. 아래 링크에서 확인 앱을 설치해 줘. "
            "급하니까 다른 사람에게는 말하지 마.”\n\n"
            "[가상의 앱 설치 링크]"
        ),
        "choices": [
            {
                "text": "급한 상황이라고 하니 링크를 눌러 앱을 설치한다.",
                "risk": 40,
                "feedback": (
                    "급하다는 말에 따라 확인되지 않은 앱을 설치하는 선택을 했어요. "
                    "앱 설치 요구가 나온 순간을 다시 살펴보세요."
                ),
            },
            {
                "text": "링크는 열지 않고, 같은 문자에 정말 엄마인지 묻는다.",
                "risk": 10,
                "feedback": (
                    "링크를 열지 않은 것은 좋은 판단이에요. "
                    "하지만 같은 상대에게 다시 묻는 것만으로 신원 확인이 끝나지는 않아요."
                ),
            },
            {
                "text": "링크를 열지 않고, 별도의 연락으로 문자 내용을 확인한다.",
                "risk": 0,
                "feedback": (
                    "설치를 멈추고 다른 연락 경로로 확인하는 선택을 했어요."
                ),
            },
        ],
    },
]


def reset_experience():
    """진행 단계와 응답 기록을 초기화합니다."""
    st.session_state["simulation_step"] = 0
    st.session_state["simulation_answers"] = []

    # 이전에 선택했던 라디오 버튼 값도 제거합니다.
    for index in range(len(SCENARIO)):
        st.session_state.pop(f"simulation_choice_{index}", None)


def calculate_score():
    """사용자가 선택한 행동의 점수를 합산합니다."""
    return sum(
        answer["risk"]
        for answer in st.session_state["simulation_answers"]
    )


def show_report():
    """전체 선택 기록과 피드백을 보여줍니다."""
    st.subheader("📋 나의 대응 리포트")

    score = calculate_score()
    st.metric("교육용 위험 행동 점수", f"{score} / 70")

    if score == 0:
        st.success("이번 체험에서는 별도로 확인하는 행동을 선택했어요.")
    elif score <= 20:
        st.warning("의심은 했지만, 확인하는 방법을 더 연습해 보세요.")
    else:
        st.error("익숙한 표시나 급하다는 요구에 따라 행동한 부분을 복습해 보세요.")

    for answer in st.session_state["simulation_answers"]:
        st.markdown(f"**{answer['title']}**")
        st.write("내 선택:", answer["text"])
        st.write("해설:", answer["feedback"])
        st.divider()

    st.caption(
        "점수는 이 체험의 선택지를 기준으로 만든 학습용 지표입니다. "
        "실제 피싱 확률이나 개인의 전반적인 대응 능력을 의미하지 않습니다."
    )

    st.button("처음부터 다시 체험", on_click=reset_experience)


def show_experience():
    """현재 단계의 상황과 선택지를 보여줍니다."""
    step = st.session_state["simulation_step"]
    scene = SCENARIO[step]

    st.progress(step / len(SCENARIO))
    st.caption(f"총 {len(SCENARIO)}단계 중 {step + 1}단계")

    st.subheader(scene["title"])
    st.info(scene["message"])

    choice = st.radio(
        "이 상황에서 어떻게 행동하겠어요?",
        options=range(len(scene["choices"])),
        format_func=lambda index: scene["choices"][index]["text"],
        index=None,
        key=f"simulation_choice_{step}",
    )

    if st.button("선택 확정", type="primary"):
        if choice is None:
            st.warning("행동을 하나 선택해 주세요.")
        else:
            selected = scene["choices"][choice]

            st.session_state["simulation_answers"].append(
                {
                    "title": scene["title"],
                    "text": selected["text"],
                    "risk": selected["risk"],
                    "feedback": selected["feedback"],
                }
            )

            st.session_state["simulation_step"] += 1
            st.rerun()


st.title("📞 가족 사칭 전화 모의체험")
st.write("전화에서 문자까지 이어지는 상황에서 나의 대응을 선택해 보세요.")
st.caption(
    "교육용 가상 시나리오입니다. 실제 전화·문자 전송이나 AI 음성 생성은 하지 않습니다."
)

# Streamlit은 버튼을 누를 때 코드를 다시 실행하므로
# session_state에 진행 상황을 보관합니다.
if "simulation_step" not in st.session_state:
    reset_experience()

if st.session_state["simulation_step"] < len(SCENARIO):
    show_experience()
else:
    show_report()
