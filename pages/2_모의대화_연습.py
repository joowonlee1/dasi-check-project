import streamlit as st


# 교육용 가상 대화입니다.
# 실제 AI가 생성하는 대화가 아니라 미리 작성한 시나리오입니다.
PRACTICE = {
    "가족 사칭": [
        {
            "message": "나 엄마야. 지금 급한 일이 있는데 도와줄 수 있어?",
            "hint": "상대가 가족이라고 말하는 것과 확인된 사실을 구분해 보세요.",
            "choices": [
                "무슨 일이든 바로 도와줄게.",
                "먼저 다른 연락 방법으로 확인할게.",
            ],
            "answer": 1,
            "feedback": [
                "요구를 알기 전에 따르겠다고 약속했어요. 먼저 확인할 시간을 확보해 보세요.",
                "별도로 확인하려는 대응이에요. 급하다는 말에도 확인 과정을 유지해 보세요.",
            ],
        },
        {
            "message": "다른 사람한테 말하지 마. 지금 나만 믿으면 돼.",
            "hint": "다른 사람에게 확인하지 못하게 하는 요구에 주목해 보세요.",
            "choices": [
                "혼자 결정하지 않고 다른 가족에게 확인할게.",
                "알겠어. 아무에게도 말하지 않을게.",
            ],
            "answer": 0,
            "feedback": [
                "혼자 판단하도록 만드는 요구에 따르지 않았어요.",
                "확인할 기회가 줄어들었어요. 비밀을 요구하는 이유도 의심해 보세요.",
            ],
        },
        {
            "message": "그럼 문자로 보낸 링크에서 확인 앱부터 설치해 줘.",
            "hint": "통화 중 동의했더라도 새로운 요구에서 멈출 수 있어요.",
            "choices": [
                "링크에 있는 앱을 바로 설치할게.",
                "설치하지 않고 따로 확인할게.",
            ],
            "answer": 1,
            "feedback": [
                "확인되지 않은 설치 요구를 따르는 선택이에요. 설치 전에 멈춰 보세요.",
                "새로운 요구에서 멈추고 확인하는 행동을 선택했어요.",
            ],
        },
    ],
    "기관 사칭": [
        {
            "message": "수사기관입니다. 본인 명의가 사건에 이용됐습니다.",
            "hint": "기관 이름을 말하는 것만으로 신원이 확인되지는 않아요.",
            "choices": [
                "통화를 끝내고 독립적으로 찾은 공식 연락처로 확인하겠습니다.",
                "수사기관이니 말씀하시는 대로 하겠습니다.",
            ],
            "answer": 0,
            "feedback": [
                "상대가 제시한 정보와 별개의 확인 경로를 선택했어요.",
                "기관이라는 주장만으로 따르기로 했어요. 확인 단계를 먼저 넣어 보세요.",
            ],
        },
        {
            "message": "조사에 필요하니 문자 인증번호를 알려주세요.",
            "hint": "인증번호를 전달하면 어떤 일이 가능해질지 생각해 보세요.",
            "choices": [
                "조사에 필요하다니 알려드리겠습니다.",
                "인증번호는 전달하지 않겠습니다.",
            ],
            "answer": 1,
            "feedback": [
                "민감한 인증 정보를 전달하는 선택이에요. 요구의 권위보다 정보의 성격을 살펴보세요.",
                "인증 정보를 전달하지 않는 대응을 선택했어요.",
            ],
        },
        {
            "message": "전화를 끊으면 불이익이 생깁니다. 계속 연결하세요.",
            "hint": "위협 때문에 확인할 기회를 포기하고 있지는 않나요?",
            "choices": [
                "불이익이 두려우니 계속 따르겠습니다.",
                "위협을 받아도 별도의 공식 경로로 확인하겠습니다.",
            ],
            "answer": 1,
            "feedback": [
                "위협이 판단에 영향을 주었어요. 확인할 시간을 확보하는 말을 연습해 보세요.",
                "압박 속에서도 확인하려는 원칙을 유지했어요.",
            ],
        },
    ],
    "택배 사칭": [
        {
            "message": "주소 오류로 배송이 중단됐습니다. 링크를 확인하세요.",
            "hint": "택배를 기다린다는 사실과 이 연락의 진위는 별개예요.",
            "choices": [
                "평소 이용하던 배송 앱에서 먼저 확인할게요.",
                "택배를 기다리고 있으니 링크를 열게요.",
            ],
            "answer": 0,
            "feedback": [
                "문자에 의존하지 않고 별도의 경로를 선택했어요.",
                "내 상황과 맞는다는 이유만으로 연락을 믿었어요.",
            ],
        },
        {
            "message": "배송 확인을 위해 별도의 앱을 설치해 주세요.",
            "hint": "배송 확인에 왜 새 앱 설치가 필요한지 생각해 보세요.",
            "choices": [
                "배송을 받아야 하니 설치하겠습니다.",
                "설치하지 않고 기존 배송 서비스에서 확인하겠습니다.",
            ],
            "answer": 1,
            "feedback": [
                "설치 요청을 검토하지 않고 따랐어요. 새로운 요구에서 멈춰 보세요.",
                "앱 설치를 멈추고 확인하는 대응을 선택했어요.",
            ],
        },
        {
            "message": "지금 처리하지 않으면 반송됩니다. 빨리 결정하세요.",
            "hint": "시간 압박이 판단을 대신하고 있지는 않나요?",
            "choices": [
                "급하더라도 배송 상태부터 따로 확인하겠습니다.",
                "반송되면 안 되니 요청을 모두 따르겠습니다.",
            ],
            "answer": 0,
            "feedback": [
                "시간 압박에도 확인 과정을 유지했어요.",
                "급하다는 요구 때문에 확인을 생략했어요.",
            ],
        },
    ],
}


def reset_practice():
    """대화 기록과 진행 상황을 초기화합니다."""
    st.session_state["practice_history"] = []
    st.session_state["practice_step"] = 0


st.title("💬 잠깐! · 모의대화 연습")
st.write("힌트를 보고 대응하는 말을 선택한 뒤, 바로 해설을 확인해요.")
st.caption("교육용 가상 대화 · AI 연결 없이 작동하는 시나리오형 연습")

scenario = st.selectbox(
    "연습할 상황",
    list(PRACTICE.keys()),
    key="practice_scenario",
    on_change=reset_practice,
)

if "practice_history" not in st.session_state:
    reset_practice()

st.button("이 상황 처음부터 연습", on_click=reset_practice)

scenes = PRACTICE[scenario]
history = st.session_state["practice_history"]

# 완료한 대화를 순서대로 보여줍니다.
for record in history:
    with st.chat_message("assistant"):
        st.write(record["message"])

    with st.chat_message("user"):
        st.write(record["reply"])

    with st.container(border=True):
        st.markdown("**연습 코치의 피드백**")
        st.write(record["feedback"])

step = st.session_state["practice_step"]
st.progress(step / len(scenes))

if step >= len(scenes):
    st.success("연습을 마쳤어요!")

    count = sum(record["correct"] for record in history)
    st.metric("권장 대응을 선택한 횟수", f"{count} / {len(scenes)}")

    st.write("처음 선택한 말을 더 나은 대응으로 바꾸어 다시 연습해 보세요.")
    st.caption("이 결과는 이번 연습 기록이며 실제 피해 가능성을 나타내지 않습니다.")

else:
    scene = scenes[step]
    st.caption(f"{len(scenes)}단계 중 {step + 1}단계")

    with st.chat_message("assistant"):
        st.write(scene["message"])

    with st.expander("💡 힌트 보기"):
        st.write(scene["hint"])

    for index, reply in enumerate(scene["choices"]):
        if st.button(
            reply,
            key=f"practice_reply_{scenario}_{step}_{index}",
            use_container_width=True,
        ):
            history.append(
                {
                    "message": scene["message"],
                    "reply": reply,
                    "feedback": scene["feedback"][index],
                    "correct": index == scene["answer"],
                }
            )

            st.session_state["practice_step"] += 1
            st.rerun()
