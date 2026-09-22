import streamlit as st


# 실제 개인정보나 접속 가능한 링크를 사용하지 않는 가상 문항입니다.
QUESTIONS = [
    {
        "title": "엄마에게 온 문자?",
        "message": (
            "엄마야. 휴대전화가 고장 나서 다른 번호로 보낸다. "
            "급하게 결제해야 하니까 카드 사진이랑 인증번호 좀 보내줘."
        ),
        "options": [
            "급한 일이니 카드 사진과 인증번호를 보낸다.",
            "문자에 적힌 번호로 전화해서 목소리만 확인한다.",
            "정보를 보내지 않고 기존에 알고 있던 연락 경로로 가족에게 확인한다.",
        ],
        "answer": 2,
        "clue": "바뀐 번호라는 설명, 급하다는 요구, 금융정보 요청",
        "explanation": (
            "가족이라는 주장만으로 신원이 확인되지는 않아요. "
            "이 상황에서는 정보 전송을 멈추고 "
            "의심 문자와 별도의 연락 경로로 확인하는 행동이 적절해요."
        ),
    },
    {
        "title": "배송이 중단됐다고?",
        "message": (
            "[배송 안내] 주소가 정확하지 않아 배송이 중단되었습니다. "
            "아래 링크에서 주소 확인용 앱을 설치해 주세요.\n\n"
            "[가상의 앱 설치 링크]"
        ),
        "options": [
            "택배를 기다리고 있으니 바로 앱을 설치한다.",
            "문자 링크 대신 평소 이용하던 배송 앱에서 확인한다.",
            "택배라는 단어가 있으므로 정상 문자라고 판단한다.",
        ],
        "answer": 1,
        "clue": "배송 문제를 이유로 한 링크 접속과 앱 설치 요구",
        "explanation": (
            "택배를 기다린다는 사실만으로 발신자가 확인되지는 않아요. "
            "문자에 있는 링크 대신 별도로 이용하던 경로에서 "
            "배송 상태를 확인하는 선택이 적절해요."
        ),
    },
    {
        "title": "평범한 알림은 무조건 안전할까?",
        "message": (
            "[도서관] 대출한 도서의 반납 예정일은 내일입니다. "
            "대출 내역은 평소 이용하시는 도서관 앱에서 확인해 주세요."
        ),
        "options": [
            "링크가 없으므로 진짜 도서관에서 보냈다고 확신한다.",
            "문자로 온 알림은 모두 피싱이라고 판단한다.",
            "문자만으로 진위를 확정하지 않고 필요하면 도서관 앱에서 확인한다.",
        ],
        "answer": 2,
        "clue": "민감한 정보나 설치 요구는 없지만 발신자 확인 근거도 부족함",
        "explanation": (
            "앞선 문항과 같은 요구가 없다고 해서 발신자가 진짜라고 "
            "확정할 수는 없어요. 무조건 믿거나 모두 사기라고 판단하기보다 "
            "필요한 내용을 별도로 확인하는 연습이에요."
        ),
    },
]


def start_quiz(question_ids):
    """지정한 문항으로 퀴즈를 시작하고 이전 응답을 지웁니다."""
    st.session_state["quiz_active_ids"] = list(question_ids)
    st.session_state["quiz_submitted"] = None

    for question_id in range(len(QUESTIONS)):
        st.session_state.pop(f"quiz_answer_{question_id}", None)


def show_questions():
    """현재 풀 문항과 제출 버튼을 표시합니다."""
    question_ids = st.session_state["quiz_active_ids"]
    answers = {}

    st.caption(f"이번에 풀 문항: {len(question_ids)}개")

    with st.form("message_quiz_form"):
        for question_id in question_ids:
            question = QUESTIONS[question_id]

            st.subheader(
                f"문제 {question_id + 1}. {question['title']}"
            )
            st.info(question["message"])

            answers[question_id] = st.radio(
                "가장 적절한 행동은 무엇일까요?",
                options=range(len(question["options"])),
                format_func=lambda index, q=question: q["options"][index],
                index=None,
                key=f"quiz_answer_{question_id}",
            )

            st.divider()

        submitted = st.form_submit_button(
            "채점하고 해설 보기",
            type="primary",
        )

    if submitted:
        missing = [
            str(question_id + 1)
            for question_id, answer in answers.items()
            if answer is None
        ]

        if missing:
            st.warning(
                f"{', '.join(missing)}번 문제에 답하지 않았어요. "
                "선택을 마친 뒤 다시 제출해 주세요."
            )
            return

        st.session_state["quiz_submitted"] = answers
        st.rerun()


def show_results():
    """채점 결과와 해설, 다시 풀기 버튼을 표시합니다."""
    answers = st.session_state["quiz_submitted"]

    wrong_ids = [
        question_id
        for question_id, selected in answers.items()
        if selected != QUESTIONS[question_id]["answer"]
    ]

    total = len(answers)
    correct_count = total - len(wrong_ids)

    st.subheader("📋 나의 퀴즈 결과")
    st.metric("이번에 맞힌 문항", f"{correct_count} / {total}")
    st.progress(correct_count / total)

    if not wrong_ids:
        st.success("이번 문항에서 권장하는 대응을 모두 선택했어요!")
    else:
        st.info("해설을 확인하고 틀린 문제만 다시 연습할 수 있어요.")

    report_lines = [
        "잠깐! · 문자 대응 퀴즈 결과",
        f"이번에 맞힌 문항: {correct_count} / {total}",
        "",
    ]

    for question_id, selected in answers.items():
        question = QUESTIONS[question_id]
        correct = selected == question["answer"]

        with st.container(border=True):
            st.subheader(
                f"문제 {question_id + 1}. {question['title']}"
            )

            if correct:
                st.success("정답")
            else:
                st.warning("다시 살펴봐요")

            st.write("내 선택:", question["options"][selected])
            st.write(
                "권장 행동:",
                question["options"][question["answer"]],
            )
            st.write("살펴볼 단서:", question["clue"])
            st.write("해설:", question["explanation"])

        report_lines.extend(
            [
                f"문제 {question_id + 1}. {question['title']}",
                f"결과: {'정답' if correct else '오답'}",
                f"내 선택: {question['options'][selected]}",
                f"권장 행동: {question['options'][question['answer']]}",
                f"해설: {question['explanation']}",
                "",
            ]
        )

    st.caption(
        "이 결과는 이번에 푼 문항의 학습 결과입니다. "
        "실제 피해 가능성이나 전반적인 대응 능력을 나타내지는 않습니다."
    )

    st.download_button(
        "내 결과 내려받기",
        data="\n".join(report_lines).encode("utf-8-sig"),
        file_name="jamkkan_quiz_result.txt",
        mime="text/plain",
    )

    if wrong_ids:
        st.button(
            "틀린 문제만 다시 풀기",
            on_click=start_quiz,
            args=(wrong_ids,),
            type="primary",
        )

    st.button(
        "전체 3문항 다시 풀기",
        on_click=start_quiz,
        args=(list(range(len(QUESTIONS))),),
    )


st.title("📩 잠깐! · 문자 대응 퀴즈")
st.write("문자 속 단서를 읽고, 가장 적절한 다음 행동을 골라보세요.")
st.caption("모든 문자는 교육용 가상 사례입니다.")

if "quiz_active_ids" not in st.session_state:
    start_quiz(range(len(QUESTIONS)))

if st.session_state["quiz_submitted"] is None:
    show_questions()
else:
    show_results()
