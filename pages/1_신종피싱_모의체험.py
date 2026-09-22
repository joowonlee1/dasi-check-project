import streamlit as st


# 선택지마다 다음 상황(next)과 해설을 함께 저장합니다.
SCENES = {
    "call": {
        "title": "📞 엄마로 표시된 전화",
        "message": (
            "휴대전화에 저장된 '엄마'의 이름과 번호가 표시됩니다.\n\n"
            "“나 엄마야. 급한 일이 생겼어. "
            "곧 문자를 보낼 테니 확인해 줘.”"
        ),
        "choices": [
            {
                "text": "엄마로 표시되니 믿고 따르겠다고 한다.",
                "next": "install",
                "feedback": "표시된 이름과 번호를 신원 확인의 근거로 삼았어요.",
            },
            {
                "text": "아직 믿지 않고 무슨 일인지 물어본다.",
                "next": "pressure",
                "feedback": "바로 따르지 않았어요. 이후 어떤 근거로 판단하는지도 중요해요.",
            },
            {
                "text": "통화를 끝내고 다른 가족에게 따로 확인한다.",
                "next": "verify",
                "feedback": "의심스러운 연락과 별도의 경로에서 확인을 시도했어요.",
            },
        ],
    },
    "install": {
        "title": "📩 앱을 설치해 달라는 문자",
        "message": (
            "상대방은 통화에서 동의했다며 문자를 보냈습니다.\n\n"
            "“이 확인 앱부터 설치해 줘. 시간이 없어.”\n\n"
            "[가상의 앱 설치 링크]"
        ),
        "choices": [
            {
                "text": "약속했으니 앱을 설치한다.",
                "next": "end",
                "feedback": (
                    "앞서 동의했다는 이유로 설치까지 이어졌어요. "
                    "새로운 요구가 나오면 중간에도 멈추고 다시 판단할 수 있어요."
                ),
            },
            {
                "text": "설치는 멈추고 별도의 연락으로 확인한다.",
                "next": "end",
                "feedback": (
                    "처음에는 믿었지만 새로운 요구에서 멈췄어요. "
                    "판단을 바꾸고 확인한 것이 이번 선택의 핵심이에요."
                ),
            },
        ],
    },
    "pressure": {
        "title": "💬 나를 잘 아는 상대",
        "message": (
            "상대방은 가족의 이름과 여행 일정을 이야기합니다.\n\n"
            "“이것까지 아는데 왜 못 믿어? "
            "문자로 보낸 링크부터 확인해.”\n\n"
            "[가상의 확인 링크]"
        ),
        "choices": [
            {
                "text": "가족 정보를 알고 있으니 믿고 링크를 연다.",
                "next": "end",
                "feedback": (
                    "상대가 아는 정보를 신원의 증거로 받아들였어요. "
                    "정보가 맞다는 것과 상대가 가족이라는 판단을 구분해 보세요."
                ),
            },
            {
                "text": "정보를 알고 있어도 링크는 열지 않고 따로 확인한다.",
                "next": "end",
                "feedback": (
                    "상대가 제시한 정보만으로 판단을 끝내지 않았어요. "
                    "별도로 사실을 확인하려는 선택이에요."
                ),
            },
        ],
    },
    "verify": {
        "title": "👪 따로 확인한 가족의 답변",
        "message": (
            "다른 가족에게 연락하자 답변이 옵니다.\n\n"
            "“엄마 지금 나랑 같이 있어. 그런 전화 안 했대.”\n\n"
            "그때 앞서 전화했던 상대에게 문자가 도착합니다.\n\n"
            "“다른 사람 말 듣지 말고 이 링크로 확인해.”\n\n"
            "[가상의 확인 링크]"
        ),
        "choices": [
            {
                "text": "가족의 답변을 근거로 링크를 열지 않고 연락을 중단한다.",
                "next": "end",
                "feedback": (
                    "별도로 확인한 사실을 실제 행동에 반영했어요. "
                    "추가 요구에도 대응 원칙을 유지했어요."
                ),
            },
            {
                "text": "문자 내용도 확인해야 할 것 같아 링크를 연다.",
                "next": "end",
                "feedback": (
                    "별도로 확인했지만 후속 요구에 다시 반응했어요. "
                    "확인한 결과를 다음 행동에도 적용하는 연습이 필요해요."
                ),
            },
        ],
    },
}


def reset_experience():
    """현재 위치와 선택 기록을 초기화합니다."""
    st.session_state["branch_scene"] = "call"
    st.session_state["branch_history"] = []

    for scene_id in SCENES:
        st.session_state.pop(f"branch_choice_{scene_id}", None)


def show_scene():
    """현재 상황을 보여주고 선택에 맞는 상황으로 이동합니다."""
    scene_id = st.session_state["branch_scene"]
    scene = SCENES[scene_id]

    step = len(st.session_state["branch_history"]) + 1
    st.caption(f"2단계 중 {step}단계")
    st.subheader(scene["title"])
    st.info(scene["message"])

    choice = st.radio(
        "어떻게 행동하겠어요?",
        options=range(len(scene["choices"])),
        format_func=lambda index: scene["choices"][index]["text"],
        index=None,
        key=f"branch_choice_{scene_id}",
    )

    if st.button("선택 확정", type="primary"):
        if choice is None:
            st.warning("행동을 하나 선택해 주세요.")
            return

        selected = scene["choices"][choice]

        st.session_state["branch_history"].append(
            {
                "scene": scene["title"],
                "action": selected["text"],
                "feedback": selected["feedback"],
            }
        )

        # 선택지에 저장된 next 값이 다음 화면을 결정합니다.
        st.session_state["branch_scene"] = selected["next"]
        st.rerun()


def show_report():
    """사용자가 실제로 지나온 상황과 선택을 보여줍니다."""
    st.subheader("📋 나의 대응 리포트")

    history = st.session_state["branch_history"]
    route = " → ".join(record["scene"] for record in history)

    st.markdown("**내가 체험한 경로**")
    st.write(route)

    for number, record in enumerate(history, start=1):
        st.markdown(f"### {number}. {record['scene']}")
        st.write("내 선택:", record["action"])
        st.write("돌아보기:", record["feedback"])
        st.divider()

    st.markdown("**생각해 보기**")
    st.write(
        "상대방을 믿게 만든 단서는 무엇이었나요? "
        "그중 별도의 경로에서 직접 확인한 사실은 무엇이었나요?"
    )

    st.button("다른 선택으로 다시 체험", on_click=reset_experience)


st.title("✋ 잠깐! · 가족 사칭 모의체험")
st.write("내 선택에 따라 다음 상황이 달라집니다.")
st.caption(
    "교육용으로 만든 가상 사례입니다. "
    "실제 전화, 문자, 링크 접속이나 AI 음성 생성은 하지 않습니다."
)

if "branch_scene" not in st.session_state:
    reset_experience()

if st.session_state["branch_scene"] == "end":
    show_report()
else:
    show_scene()
