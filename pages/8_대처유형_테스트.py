"""12문항, 4개 축, 16가지 교육용 대처 유형. 외부 전송·공개 저장 없음."""
import base64
from html import escape
from pathlib import Path
import streamlit as st
from mascot_ui import show_mascot

PREFIX = "coping_v1_"
NOTICE = "교육용 자기점검입니다. MBTI나 검증된 심리검사가 아니며, 실제 피해 가능성을 예측하지 않습니다."
AXES = [
    ("반응 속도", ("Q", "S"), ("먼저 반응", "잠시 숙고")),
    ("판단 단서", ("R", "E"), ("관계·말투 먼저", "내용·근거 먼저")),
    ("확인 방식", ("I", "T"), ("혼자 점검", "함께 점검")),
    ("요청 대응", ("H", "B"), ("도움 먼저", "경계 먼저")),
]
# 축 번호, 질문, 0에 해당하는 문장, 1에 해당하는 문장, 선택지 순서 반전 여부
QUESTIONS = [
    (0, "처음 보는 연락이 오면 나는 보통…", "짧게 답하고 내용을 알아본다", "잠시 읽고 생각한 뒤 답한다", False),
    (1, "아는 사람 같은 메시지에서 먼저 눈에 들어오는 것은?", "평소와 비슷한 말투와 관계", "메시지가 요구하는 내용과 이유", False),
    (2, "찜찜한 연락을 확인할 때 나는…", "내가 자료를 찾아 먼저 점검한다", "믿을 만한 사람과 내용을 먼저 나눈다", True),
    (3, "누군가 곤란하다며 부탁하면 먼저 드는 생각은?", "어떻게 도울 수 있을까", "내가 어디까지 할 수 있을까", False),
    (0, "답장을 고민하는 동안 나는…", "대화를 주고받으며 생각을 정리한다", "생각을 정리한 뒤 대화를 시작한다", True),
    (1, "설명이 낯설게 느껴질 때 먼저 살피는 것은?", "누가 어떤 어조로 설명하는지", "설명의 내용이 서로 맞는지", True),
    (2, "정보가 서로 다를 때 나는…", "직접 출처를 비교하는 편이다", "다른 사람의 의견도 함께 듣는 편이다", False),
    (3, "예상하지 못한 요청을 받으면 나는…", "상대의 사정을 먼저 묻는다", "요청의 범위와 조건을 먼저 묻는다", True),
    (0, "당장 답할 필요가 없는 메시지에도 나는…", "짧은 확인 답장을 먼저 보내는 편이다", "나중에 내용을 정리해 답하는 편이다", False),
    (1, "연락 내용을 돌아볼 때 더 기억에 남는 것은?", "상대와의 관계와 대화 분위기", "대화 속 구체적인 주장과 근거", False),
    (2, "새로운 확인 방법을 찾았다면 나는…", "직접 살펴본 뒤 필요하면 의견을 구한다", "함께 살펴볼 사람을 먼저 찾는다", True),
    (3, "부탁을 받아들일지 결정할 때 먼저 고려하는 것은?", "상대에게 도움이 되는 방법", "내가 지켜야 할 조건과 한계", False),
]
TYPE_NAMES = {
    "QRIH": "따뜻한 행동가", "QRIB": "빠른 경계지기",
    "QRTH": "다정한 연결자", "QRTB": "함께하는 문지기",
    "QEIH": "실행하는 탐구자", "QEIB": "민첩한 점검자",
    "QETH": "협력하는 해결사", "QETB": "빠른 확인대장",
    "SRIH": "신중한 공감가", "SRIB": "차분한 경계지기",
    "SRTH": "다정한 의논가", "SRTB": "든든한 동행자",
    "SEIH": "차근차근 탐구자", "SEIB": "꼼꼼한 점검자",
    "SETH": "함께 푸는 분석가", "SETB": "차분한 확인대장",
}
HABITS = {
    "Q": ("반응을 시작하는 쪽을 더 골랐어요.", "답장과 별개로 송금·설치·인증 요청은 잠시 멈추세요.", "계정 보안 사칭", "긴급 알림을 받아도 먼저 공식 앱에서 확인하는 연습"),
    "S": ("생각을 정리할 시간을 갖는 쪽을 더 골랐어요.", "이미 피해가 발생했다면 혼자 고민하며 신고를 미루지 마세요.", "택배 사칭", "생각한 뒤 실제 주문 내역과 대조하는 연습"),
    "R": ("관계와 말투를 먼저 살피는 쪽을 더 골랐어요.", "익숙한 말투와 발신자 이름은 신원 확인을 대신하지 못해요.", "가족 사칭", "원래 저장된 연락처로 따로 확인하는 연습"),
    "E": ("내용과 근거를 먼저 살피는 쪽을 더 골랐어요.", "자료가 그럴듯해 보여도 상대가 준 자료만으로 확인하지 마세요.", "기관 사칭", "기관이 보냈다는 문서를 별도 공식 경로에서 확인하는 연습"),
    "I": ("자료를 혼자 점검하는 쪽을 더 골랐어요.", "확신이 들지 않으면 믿을 만한 사람이나 공식 기관에 도움을 요청하세요.", "계정 보안 사칭", "직접 연 공식 서비스에서 기록을 확인하는 연습"),
    "T": ("다른 사람과 함께 점검하는 쪽을 더 골랐어요.", "지인의 추측도 정답은 아니에요. 함께 공식 근거를 확인하세요.", "모바일 초대장 사칭", "공유받은 메시지를 원래 알고 있던 사람에게 확인하는 연습"),
    "H": ("도울 방법을 먼저 생각하는 쪽을 더 골랐어요.", "도와주고 싶은 마음과 송금·정보 제공 여부는 따로 판단하세요.", "쇼핑몰 환불 사칭", "친절한 안내라도 요청 내용과 실제 내역을 따져보는 연습"),
    "B": ("조건과 한계를 먼저 확인하는 쪽을 더 골랐어요.", "차단 여부를 정하기 전에 필요한 연락인지 공식 경로에서 확인하세요.", "아르바이트 사칭", "업무 제안의 출처와 조건을 따로 확인하는 연습"),
}


STRENGTHS = {
    "Q": "필요한 질문이나 도움 요청을 시작하는 데 활용할 수 있어요.",
    "S": "급한 분위기에서 잠시 생각할 여유를 만드는 데 활용할 수 있어요.",
    "R": "평소와 다른 대화 분위기를 알아차리는 데 활용할 수 있어요.",
    "E": "주장 사이의 모순을 비교하는 데 활용할 수 있어요.",
    "I": "출처를 스스로 찾아 정리하는 데 활용할 수 있어요.",
    "T": "혼자 놓친 부분을 함께 점검하는 데 활용할 수 있어요.",
    "H": "상대의 사정을 듣고 차분하게 대화하는 데 활용할 수 있어요.",
    "B": "불확실한 요구에 한계를 설명하는 데 활용할 수 있어요.",
}


def options(q):
    return (1, 0) if q[4] else (0, 1)


def score(answers):
    if len(answers) != 12 or any(type(a) is not int or a not in (0, 1) for a in answers):
        raise ValueError("12문항에 모두 답해야 합니다.")
    counts = [[0, 0] for _ in AXES]
    for q, answer in zip(QUESTIONS, answers):
        counts[q[0]][answer] += 1
    winners = [0 if a > b else 1 for a, b in counts]
    code = "".join(axis[1][winner] for axis, winner in zip(AXES, winners))
    labels = [axis[2][winner] for axis, winner in zip(AXES, winners)]
    return code, labels, counts


def invalidate():
    st.session_state.pop(PREFIX + "result", None)


def reset():
    for key in list(st.session_state):
        if key.startswith(PREFIX):
            del st.session_state[key]


def result_card(code, labels):
    name = escape(TYPE_NAMES[code])
    mascot = ""
    path = Path(__file__).resolve().parents[1] / "assets" / "mascot_six.png"
    if path.is_file():
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        mascot = (
            '<svg x="750" y="58" width="230" height="230" viewBox="1024 0 512 512">'
            f'<image width="1536" height="1024" href="data:image/png;base64,{data}"/></svg>'
        )
    traits = "".join(
        f'<text x="90" y="{440 + i * 68}" font-size="32">{escape(label)}</text>'
        for i, label in enumerate(labels)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">'
        '<rect width="1080" height="1080" rx="48" fill="#f1f6ef"/>'
        '<rect x="38" y="38" width="1004" height="1004" rx="36" fill="#fffefa"/>'
        '<g font-family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif" fill="#20483f">'
        '<text x="90" y="140" font-size="42" font-weight="bold">잠깐! 대처유형 테스트</text>'
        f'<text x="90" y="230" font-size="32">{escape(code)} · 나의 응답 유형</text>'
        f'<text x="90" y="350" font-size="58" font-weight="bold">{name}</text>{traits}'
        '<text x="90" y="800" font-size="32" font-weight="bold">“지금은 멈추고, 제가 따로 확인할게요.”</text>'
        '<text x="90" y="930" font-size="23">교육용 자기점검 · 심리검사나 피해 가능성 진단이 아닙니다.</text>'
        '<text x="90" y="972" font-size="23">답변과 상황이 달라지면 결과도 달라질 수 있어요.</text>'
        f'</g>{mascot}</svg>'
    )


def show_result(answers):
    code, labels, counts = score(answers)
    st.subheader(f"나의 유형: {TYPE_NAMES[code]}")
    st.caption(f"{code} · 안전 점수나 우열을 나타내는 코드가 아니에요.")
    show_mascot("shield", "어떤 유형이든 멈추고, 따로 확인하는 연습이 중요해요.", width=110)
    for i, (axis, letter, label) in enumerate(zip(AXES, code, labels)):
        with st.container(border=True):
            st.markdown(f"**{axis[0]} · {label}**")
            st.write(HABITS[letter][0])
            st.write("**살릴 수 있는 강점:** " + STRENGTHS[letter])
            st.caption(f"{axis[2][0]} {counts[i][0]}개 / {axis[2][1]} {counts[i][1]}개 (각 3문항)")
            st.write("**연습할 습관:** " + HABITS[letter][1])
    st.subheader("추가로 연습할 수법")
    st.caption("이 유형이 아래 수법에 더 잘 당한다는 통계가 아닙니다. 응답을 돌아보기 위한 교육용 추천이에요.")
    seen = set()
    for letter in code:
        _, _, scenario, reason = HABITS[letter]
        if scenario not in seen:
            st.markdown(f"- **{scenario}**: {reason}")
            seen.add(scenario)
    st.info("바로 쓸 문장: 지금은 진행하지 않을게요. 제가 원래 알고 있던 연락처로 따로 확인하겠습니다.")
    st.subheader("결과 카드")
    svg = result_card(code, labels)
    st.image(svg, use_column_width=True)
    st.download_button("결과 카드 내려받기 (SVG)", svg.encode("utf-8"),
                       file_name=f"jamkkan_{code}.svg", mime="image/svg+xml")
    text = f"잠깐! 나의 대처유형: {TYPE_NAMES[code]} ({code})\n" + " / ".join(labels) + "\n" + NOTICE
    st.download_button("공유용 문구 내려받기", text.encode("utf-8-sig"),
                       file_name=f"jamkkan_{code}.txt", mime="text/plain")
    st.caption("카드에는 이름·연락처·문항별 답변이 들어가지 않아요. 다운로드 후 공유 여부는 직접 선택하세요.")
    st.page_link("pages/2_모의대화_연습.py", label="AI 모의대화로 연습하기", icon="💬")
    st.button("다시 테스트하기", on_click=reset)


def main():
    st.title("🧭 나의 피싱 대처유형")
    st.write("12개의 질문으로, 낯선 연락에 반응하는 나의 습관을 돌아봐요.")
    st.info(NOTICE)
    st.caption("정답은 없어요. 평소 모습에 더 가까운 쪽을 고르세요. 답변은 공개 저장하거나 AI 서비스로 전송하지 않습니다.")
    if PREFIX + "result" in st.session_state:
        show_result(st.session_state[PREFIX + "result"])
        return
    answers = [st.session_state.get(PREFIX + str(i)) for i in range(12)]
    done = sum(a is not None for a in answers)
    st.progress(done / 12)
    st.caption(f"{done} / 12문항 완료")
    for i, q in enumerate(QUESTIONS):
        with st.container(border=True):
            st.radio(f"{i + 1:02d}. {q[1]}", options(q), index=None,
                     format_func=lambda a, q=q: q[2 + a],
                     key=PREFIX + str(i), on_change=invalidate)
    answers = [st.session_state.get(PREFIX + str(i)) for i in range(12)]
    if st.button("나의 유형 보기", type="primary"):
        if any(a is None for a in answers):
            missing = ", ".join(str(i + 1) for i, a in enumerate(answers) if a is None)
            st.warning(f"아직 답하지 않은 문항: {missing}번")
        else:
            score(answers)
            st.session_state[PREFIX + "result"] = tuple(answers)
            st.rerun()
    with st.expander("유형은 어떻게 정해지나요?"):
        st.write("반응 속도·판단 단서·확인 방식·요청 대응의 4개 기준에 3문항씩 답해요. 기준마다 2개 이상 선택한 쪽을 조합해 16가지 유형을 만들어요.")
        st.caption("세 문항이라 동점은 없지만, 2대 1 결과가 뚜렷한 성격 차이를 뜻하는 것은 아니에요.")
    st.button("답변 초기화", on_click=reset)


if __name__ == "__main__":
    main()

