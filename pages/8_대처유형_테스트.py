"""12문항, 4개 축, 16가지 교육용 대처 유형. 외부 전송·공개 저장 없음."""
import base64
import time
from html import escape
from pathlib import Path
import streamlit as st

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
# 문항마다 장면을 떠올리기 쉽게 붙이는 그림 문자
QUESTION_ICONS = ["📩", "💬", "🕵️", "🙏", "⌨️", "🤔", "📰", "📨", "⏰", "🧠", "🛠️", "⚖️"]
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
# 유형별 엠블럼: 그림 문자, 배경색 2개, 한 줄 소개
TYPE_LOOK = {
    "QRIH": ("🔥", "#FF8A5B", "#FFC46B", "마음이 먼저 달려가는 다정한 불꽃"),
    "QRIB": ("🚨", "#FF6B6B", "#FFB36B", "낌새가 이상하면 바로 경보 울리기"),
    "QRTH": ("🤝", "#FF9F7A", "#FFD6A5", "고민은 나누고, 확인은 함께"),
    "QRTB": ("🛡️", "#F7797D", "#FBD786", "친구와 함께 문을 단단히 지켜요"),
    "QEIH": ("🧪", "#F9A03F", "#F6D365", "궁금하면 바로 직접 찾아보기"),
    "QEIB": ("🔍", "#F76B1C", "#FAD961", "빠르게 훑고, 수상하면 멈춤!"),
    "QETH": ("🧩", "#FF9966", "#FFD86F", "조각을 모아 함께 푸는 팀플레이어"),
    "QETB": ("⏱️", "#F857A6", "#FFB199", "확인 버튼은 누구보다 빠르게"),
    "SRIH": ("🌙", "#6A82FB", "#A8C0FF", "조용히 듣고 차분히 살피기"),
    "SRIB": ("🦉", "#5B7DB1", "#9CC5E8", "밤새 지켜보는 침착한 부엉이"),
    "SRTH": ("☕", "#7F7FD5", "#B8B5FF", "차 한 잔 하며 같이 생각해요"),
    "SRTB": ("🐘", "#6C8EBF", "#B6D0E2", "천천히, 하지만 든든하게 함께"),
    "SEIH": ("📚", "#2BA59A", "#8EE4C8", "한 장씩 넘기며 근거 찾기"),
    "SEIB": ("🧐", "#1F9E89", "#A3E4D7", "작은 글씨까지 놓치지 않기"),
    "SETH": ("📊", "#3AAFA9", "#B4EBCA", "자료는 같이 볼수록 정확해요"),
    "SETB": ("🧭", "#20807A", "#7FD1B9", "흔들려도 방향은 잃지 않아요"),
}
TRAIT_ICONS = {"Q": "⚡", "S": "🐢", "R": "💗", "E": "🔬", "I": "🔦", "T": "👥", "H": "🫶", "B": "🚧"}
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

# 유형별 그림을 직접 넣고 싶을 때: assets/types/유형코드.png (예: assets/types/SETH.png)
# 파일이 있으면 그 그림을, 없으면 위의 엠블럼을 보여 줍니다.
TYPE_IMAGE_DIR = Path(__file__).resolve().parents[1] / "assets" / "types"

CSS = """
<style>
@keyframes jk-pop {0%{transform:scale(.4);opacity:0} 60%{transform:scale(1.06);opacity:1} 100%{transform:scale(1)}}
@keyframes jk-slide {0%{transform:translateX(24px);opacity:0} 100%{transform:none;opacity:1}}
@keyframes jk-bounce {0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)}}
@keyframes jk-wiggle {0%,100%{transform:rotate(0)} 25%{transform:rotate(-10deg)} 75%{transform:rotate(10deg)}}
@keyframes jk-float {0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)}}
.jk-hero {border-radius:28px;padding:28px 22px;text-align:center;color:#1E3A34;
  box-shadow:0 10px 28px rgba(32,72,63,.15);animation:jk-pop .7s ease-out both;margin-bottom:14px;}
.jk-zzan {display:inline-block;background:#fff;border-radius:999px;padding:4px 16px;font-weight:800;
  font-size:1.05rem;letter-spacing:.05em;animation:jk-wiggle .6s .5s ease-in-out 2;}
.jk-emblem {width:150px;height:150px;margin:16px auto 8px;border-radius:50%;background:rgba(255,255,255,.88);
  display:flex;align-items:center;justify-content:center;font-size:82px;animation:jk-bounce 1.8s 1s ease-in-out infinite;}
.jk-emblem img {width:140px;height:140px;object-fit:contain;border-radius:50%;}
.jk-name {font-size:2.1rem;font-weight:900;margin:6px 0 2px;word-break:keep-all;}
.jk-code {font-weight:700;opacity:.75;letter-spacing:.2em;}
.jk-catch {font-size:1.1rem;font-weight:700;margin-top:8px;word-break:keep-all;}
.jk-chips {display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:14px;}
.jk-chip {background:rgba(255,255,255,.9);border-radius:999px;padding:5px 12px;font-weight:700;font-size:.95rem;}
.jk-q {background:#FFFEFA;border:2px solid #DCE8D6;border-radius:24px;padding:26px 20px;text-align:center;
  animation:jk-slide .35s ease-out both;margin:6px 0 14px;}
.jk-q-icon {font-size:64px;animation:jk-float 2.4s ease-in-out infinite;}
.jk-q-num {color:#3BA99C;font-weight:800;margin-top:4px;}
.jk-q-text {font-size:1.45rem;font-weight:800;color:#20483F;margin-top:6px;word-break:keep-all;line-height:1.5;}
.jk-intro {background:linear-gradient(135deg,#FFE3C2,#D6F2E6);border-radius:28px;padding:28px 20px;text-align:center;
  animation:jk-pop .6s ease-out both;}
.jk-intro-row {font-size:34px;letter-spacing:4px;line-height:1.6;}
.jk-intro-row span {display:inline-block;animation:jk-float 2.2s ease-in-out infinite;}
.jk-gift {font-size:96px;display:inline-block;animation:jk-wiggle .8s ease-in-out infinite;}
.jk-trait {background:#FFFEFA;border:1.5px solid #DCE8D6;border-radius:20px;padding:14px 16px;margin-bottom:12px;
  animation:jk-pop .5s ease-out both;}
.jk-trait-head {font-weight:800;font-size:1.1rem;color:#20483F;}
.jk-gauge {display:flex;align-items:center;gap:6px;margin:8px 0;font-size:.85rem;color:#4F6B63;}
.jk-dot {width:16px;height:16px;border-radius:50%;background:#E3EAE0;display:inline-block;}
.jk-dot.on {background:#3BA99C;}
.jk-drum {text-align:center;font-size:1.6rem;font-weight:800;color:#20483F;padding:48px 0;}
.jk-drum div {font-size:72px;animation:jk-bounce .5s ease-in-out infinite;}
</style>
"""


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


def get_answers():
    return [st.session_state.get(PREFIX + str(i)) for i in range(12)]


def reset():
    for key in list(st.session_state):
        if key.startswith(PREFIX):
            del st.session_state[key]


def start():
    st.session_state[PREFIX + "started"] = True
    st.session_state[PREFIX + "step"] = 0


def answer(i, value):
    st.session_state[PREFIX + str(i)] = value
    st.session_state.pop(PREFIX + "result", None)
    answers = get_answers()
    # 아직 답하지 않은 다음 문항으로, 모두 답했으면 결과 열기 화면으로 이동합니다.
    later = [n for n in range(i + 1, 12) if answers[n] is None]
    earlier = [n for n in range(12) if answers[n] is None]
    st.session_state[PREFIX + "step"] = (later or earlier or [12])[0]


def go_to(step):
    st.session_state[PREFIX + "step"] = step


def reveal():
    answers = get_answers()
    score(answers)
    st.session_state[PREFIX + "result"] = tuple(answers)
    st.session_state[PREFIX + "fresh"] = True


def type_image_uri(code):
    path = TYPE_IMAGE_DIR / f"{code}.png"
    if not path.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


# ───────── 화면 ─────────

def show_intro():
    emojis = "".join(
        f'<span style="animation-delay:{i * 0.12:.2f}s">{TYPE_LOOK[c][0]}</span>'
        for i, c in enumerate(TYPE_LOOK)
    )
    st.markdown(
        f'<div class="jk-intro"><div style="font-size:1.1rem;font-weight:800;color:#20483F;">'
        f'16가지 유형 중 나는 어떤 유형일까?</div>'
        f'<div class="jk-intro-row">{emojis}</div>'
        f'<div class="jk-chips"><span class="jk-chip">🃏 12문항</span>'
        f'<span class="jk-chip">⏱️ 약 2분</span><span class="jk-chip">🙆 정답 없음</span></div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.button("🚀 테스트 시작하기", type="primary", width="stretch", on_click=start)
    st.caption(NOTICE)
    st.caption("답변은 공개 저장하거나 AI 서비스로 전송하지 않습니다.")
    with st.expander("유형은 어떻게 정해지나요?"):
        st.write("반응 속도·판단 단서·확인 방식·요청 대응의 4개 기준에 3문항씩 답해요. 기준마다 2개 이상 선택한 쪽을 조합해 16가지 유형을 만들어요.")
        st.caption("세 문항이라 동점은 없지만, 2대 1 결과가 뚜렷한 성격 차이를 뜻하는 것은 아니에요.")


def show_question(i):
    q = QUESTIONS[i]
    answers = get_answers()
    done = sum(a is not None for a in answers)
    st.progress(done / 12, text=f"{done} / 12 완료")
    st.markdown(
        f'<div class="jk-q" id="q{i}"><div class="jk-q-icon">{QUESTION_ICONS[i]}</div>'
        f'<div class="jk-q-num">Q{i + 1}</div>'
        f'<div class="jk-q-text">{escape(q[1])}</div></div>',
        unsafe_allow_html=True,
    )
    for mark, value in zip(("🅰", "🅱"), options(q)):
        chosen = answers[i] == value
        st.button(
            f"{mark}  {q[2 + value]}" + ("  ✓" if chosen else ""),
            key=f"{PREFIX}btn_{i}_{value}",
            type="primary" if chosen else "secondary",
            width="stretch",
            on_click=answer,
            args=(i, value),
        )
    left, right = st.columns(2)
    if i > 0:
        left.button("◀ 이전 문항", on_click=go_to, args=(i - 1,), width="stretch")
    if answers[i] is not None and i < 11:
        right.button("다음 문항 ▶", on_click=go_to, args=(i + 1,), width="stretch")
    elif answers[i] is not None and i == 11 and None not in answers:
        right.button("결과 열기 ▶", on_click=go_to, args=(12,), width="stretch")


def show_ready():
    st.progress(1.0, text="12 / 12 완료")
    st.markdown(
        '<div class="jk-q"><div class="jk-gift">🎁</div>'
        '<div class="jk-q-text">12문항 완료!<br>나의 유형이 상자 안에 들어 있어요.</div></div>',
        unsafe_allow_html=True,
    )
    st.button("✨ 짠! 결과 열기", type="primary", width="stretch", on_click=reveal)
    st.button("◀ 답 고치기", on_click=go_to, args=(11,), width="stretch")


def drumroll():
    box = st.empty()
    for icon, text in (("🥁", "두구두구…"), ("🔍", "응답을 모으는 중…"), ("🎁", "상자를 여는 중…")):
        box.markdown(f'<div class="jk-drum"><div>{icon}</div>{text}</div>', unsafe_allow_html=True)
        time.sleep(0.6)
    box.empty()


def hero_html(code, labels):
    emoji, c1, c2, catch = TYPE_LOOK[code]
    image = type_image_uri(code)
    emblem = f'<img src="{image}" alt="{escape(TYPE_NAMES[code])} 그림">' if image else emoji
    chips = "".join(
        f'<span class="jk-chip">{TRAIT_ICONS[letter]} {escape(label)}</span>'
        for letter, label in zip(code, labels)
    )
    return (
        f'<div class="jk-hero" style="background:linear-gradient(135deg,{c1},{c2});">'
        f'<span class="jk-zzan">짠! 🎉 나의 대처유형</span>'
        f'<div class="jk-emblem">{emblem}</div>'
        f'<div class="jk-name">{escape(TYPE_NAMES[code])}</div>'
        f'<div class="jk-code">{code}</div>'
        f'<div class="jk-catch">“{escape(catch)}”</div>'
        f'<div class="jk-chips">{chips}</div></div>'
    )


def trait_html(index, letter, label, count):
    axis = AXES[index]
    side = axis[1].index(letter)
    dots = "".join(
        f'<span class="jk-dot{" on" if n < count[side] else ""}"></span>' for n in range(3)
    )
    return (
        f'<div class="jk-trait" style="animation-delay:{0.15 * index:.2f}s">'
        f'<div class="jk-trait-head">{TRAIT_ICONS[letter]} {axis[0]} · {escape(label)}</div>'
        f'<div class="jk-gauge">{escape(axis[2][side])} {dots} <span>({count[side]}/3)</span></div>'
        f'<div style="color:#33524A;word-break:keep-all;">💪 {escape(STRENGTHS[letter])}</div></div>'
    )


def result_card(code, labels):
    """내려받기용 결과 카드(SVG). 이름·연락처·문항별 답변은 넣지 않습니다."""
    emoji, c1, c2, catch = TYPE_LOOK[code]
    name = escape(TYPE_NAMES[code])
    image = type_image_uri(code)
    if image:
        emblem = f'<image x="700" y="150" width="280" height="280" href="{image}"/>'
    else:
        emblem = (
            '<text x="840" y="340" font-size="170" text-anchor="middle" '
            'font-family="Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif">'
            f'{emoji}</text>'
        )
    traits = "".join(
        f'<text x="90" y="{560 + i * 66}" font-size="34">{TRAIT_ICONS[letter]} {escape(label)}</text>'
        for i, (letter, label) in enumerate(zip(code, labels))
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/>'
        f'<stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
        '<rect width="1080" height="1080" rx="48" fill="url(#g)"/>'
        '<rect x="38" y="38" width="1004" height="1004" rx="36" fill="#fffefa" opacity="0.93"/>'
        '<circle cx="840" cy="290" r="165" fill="#ffffff" stroke="#e6ece3" stroke-width="4"/>'
        f'{emblem}'
        '<g font-family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif" fill="#20483f">'
        '<text x="90" y="140" font-size="40" font-weight="bold">잠깐! 대처유형 테스트</text>'
        f'<text x="90" y="220" font-size="30" letter-spacing="6">{escape(code)}</text>'
        f'<text x="90" y="330" font-size="64" font-weight="bold">{name}</text>'
        f'<text x="90" y="410" font-size="30">“{escape(catch)}”</text>{traits}'
        '<text x="90" y="880" font-size="31" font-weight="bold">“지금은 멈추고, 제가 따로 확인할게요.”</text>'
        '<text x="90" y="950" font-size="22">교육용 자기점검 · 심리검사나 피해 가능성 진단이 아닙니다.</text>'
        '<text x="90" y="988" font-size="22">답변과 상황이 달라지면 결과도 달라질 수 있어요.</text>'
        '</g></svg>'
    )


def show_result(answers):
    code, labels, counts = score(answers)
    if st.session_state.pop(PREFIX + "fresh", False):
        drumroll()
        st.balloons()
    st.markdown(hero_html(code, labels), unsafe_allow_html=True)
    st.caption("유형 코드는 안전 점수나 우열을 나타내지 않아요.")

    st.subheader("🎮 나의 대처 능력치")
    for row in (0, 2):  # 두 개씩 한 줄에 놓아 휴대폰에서도 순서가 유지되게 합니다.
        cols = st.columns(2)
        for i in (row, row + 1):
            cols[i - row].markdown(trait_html(i, code[i], labels[i], counts[i]), unsafe_allow_html=True)

    st.subheader("🎯 오늘의 연습 미션")
    st.caption("해 볼 미션에 체크해 보세요. 체크한 내용은 저장되지 않아요.")
    for letter in code:
        st.checkbox(HABITS[letter][1], key=f"{PREFIX}mission_{letter}")

    st.subheader("🕹️ 추가로 연습할 수법")
    st.caption("이 유형이 아래 수법에 더 잘 당한다는 통계가 아닙니다. 응답을 돌아보기 위한 교육용 추천이에요.")
    seen = []
    for letter in code:
        if HABITS[letter][2] not in [s[0] for s in seen]:
            seen.append(HABITS[letter][2:])
    for scenario, reason in seen:
        st.markdown(f"- **{scenario}** · {reason}")
    st.page_link("pages/2_모의대화_연습.py", label="AI 모의대화로 바로 연습하기", icon="💬")
    st.info("🗣️ 바로 쓸 문장: 지금은 진행하지 않을게요. 제가 원래 알고 있던 연락처로 따로 확인하겠습니다.")

    with st.expander("📝 응답 풀이 자세히 보기"):
        for i, (axis, letter, label) in enumerate(zip(AXES, code, labels)):
            st.markdown(f"**{axis[0]} · {label}** — {HABITS[letter][0]}")
            st.caption(f"{axis[2][0]} {counts[i][0]}개 / {axis[2][1]} {counts[i][1]}개 (각 3문항)")

    st.subheader("🖼️ 결과 카드")
    svg = result_card(code, labels)
    st.image(svg)
    c1, c2 = st.columns(2)
    c1.download_button("결과 카드 내려받기 (SVG)", svg.encode("utf-8"),
                       file_name=f"jamkkan_{code}.svg", mime="image/svg+xml", width="stretch")
    text = f"잠깐! 나의 대처유형: {TYPE_NAMES[code]} ({code})\n" + " / ".join(labels) + "\n" + NOTICE
    c2.download_button("공유용 문구 내려받기", text.encode("utf-8-sig"),
                       file_name=f"jamkkan_{code}.txt", mime="text/plain", width="stretch")
    st.caption("카드에는 이름·연락처·문항별 답변이 들어가지 않아요. 다운로드 후 공유 여부는 직접 선택하세요.")
    st.caption(NOTICE)
    st.button("🔄 다시 테스트하기", on_click=reset, width="stretch")


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.title("🧭 나의 피싱 대처유형")
    if PREFIX + "result" in st.session_state:
        show_result(st.session_state[PREFIX + "result"])
        return
    if not st.session_state.get(PREFIX + "started"):
        show_intro()
        return
    step = st.session_state.get(PREFIX + "step", 0)
    if step >= 12 and None not in get_answers():
        show_ready()
    else:
        show_question(min(step, 11))
    st.button("처음부터 다시", on_click=reset)


if __name__ == "__main__":
    main()
