import html

import streamlit as st


# 모든 인물·기관명·번호·링크는 교육용 가상 자료입니다.
STOP_LINE = 20      # 사기범을 믿는 정도가 이 값 이하로 내려가면 할머니가 멈추고 함께 확인합니다.
START_TRUST = 70    # 할머니가 처음에 나를 믿는 정도
COUNTER_PUSH = 10   # 다그치거나 몰래 막으면 사기범이 다음에 더 강하게 몰아붙입니다.

# 할머니 휴대전화에 시간 순서대로 들어오는 연락입니다.
# real=True는 진짜 연락, False는 피싱입니다. push는 할머니가 사기범을 더 믿게 되는 정도입니다.
EVENTS = [
    {
        "time": "10:02",
        "kind": "notice",
        "sender": "○○은행",
        "lines": ["[○○은행] 체크카드 승인 12,800원 · 한빛마트"],
        "real": True,
        "grandma": "아까 장 본 거네.",
        "options": "real",
    },
    {
        "time": "10:05",
        "kind": "call",
        "sender": "02-3480-○○○○ (발신 표시: 서울중앙지검)",
        "lines": [
            "서울중앙지방검찰청 김민준 수사관입니다.",
            "할머님 명의 통장이 범죄에 쓰여 사건에 연루되셨습니다.",
            "수사 보안상 지금 통화 내용은 가족에게도 알리시면 안 됩니다.",
        ],
        "real": False,
        "push": 70,
        "stage": "검찰 사칭 전화",
        "grandma": "아이고, 내가 무슨 일을… 경찰서 한 번 가 본 적 없는데.",
        "reason": "검찰은 전화로 사건을 알리면서 비밀로 하라고 하지 않아요.",
        "together": "놀라셨죠, 할머니 잘못 아니에요. 같이 검찰청 대표번호로 직접 걸어서 확인해 봐요.",
        "options": "scam",
    },
    {
        "time": "10:08",
        "kind": "sms",
        "sender": "햇살정형외과",
        "saved": True,
        "lines": ["[햇살정형외과] 내일(목) 오전 10시 진료 예약 안내드립니다. 회신은 필요 없습니다."],
        "real": True,
        "grandma": "아, 내일 무릎 보러 가는 날이지.",
        "options": "real",
    },
    {
        "time": "10:11",
        "kind": "sms",
        "sender": "010-6620-1184",
        "saved": False,
        "lines": [
            "[서울중앙지검] 사건번호 2026형제1234 열람",
            "🔗 가상의 앱 설치 링크 · 눌러도 실행되지 않음",
        ],
        "call_lines": ["(수사관) 링크 눌러서 보안 앱부터 설치하세요. 안 하시면 체포영장이 나갑니다."],
        "real": False,
        "push": 25,
        "stage": "앱 설치 요구",
        "grandma": "체포? 내가 감옥에 가는 거야? 빨리 깔아야 하나…",
        "reason": "검찰은 앱 설치를 시키지 않아요. 이 앱은 휴대폰을 원격으로 조종하는 앱일 수 있어요.",
        "together": "무서우시죠. 앱은 깔지 말고, 제가 옆에서 검찰청 대표번호로 같이 물어볼게요.",
        "options": "scam",
    },
    {
        "time": "10:14",
        "kind": "sms",
        "sender": "우체국",
        "saved": True,
        "lines": ["[우체국] 등기우편이 오늘 14~16시에 배달될 예정입니다. 링크·회신 요청 없음."],
        "real": True,
        "grandma": "무슨 등기가 오나? 연금 서류인가.",
        "options": "real",
    },
    {
        "time": "10:17",
        "kind": "call",
        "sender": "02-3480-○○○○ (발신 표시: 서울중앙지검)",
        "lines": [
            "할머님 예금이 범죄 자금과 섞여 있어요. 금융감독원 안전계좌로 옮겨야 보호됩니다.",
            "은행 직원이 물으면 ‘손주 등록금’이라고 하세요. 사실대로 말하면 수사에 방해돼요.",
        ],
        "real": False,
        "push": 25,
        "stage": "안전계좌 이체 요구",
        "grandma": "등록금이라고 하라고? …그래도 내 돈 지키려면 해야지.",
        "reason": "‘안전계좌’는 없어요. 어떤 기관도 돈을 옮기라고 하지 않고, 은행 직원에게 거짓말하라는 건 사기예요.",
        "together": "할머니 돈 지키려는 거 알아요. 이체하기 전에 저랑 같이 은행 창구에 가서 직원한테 먼저 물어봐요.",
        "options": "scam",
    },
    {
        "time": "10:21",
        "kind": "notice",
        "sender": "○○은행 앱",
        "lines": [
            "이체 화면 · 받는 분 ‘금융보안관리’ · 9,800,000원",
            "(수사관) 지금 바로 보내세요. 10분 안에 안 하시면 계좌가 동결됩니다.",
        ],
        "real": False,
        "push": 20,
        "stage": "송금 직전",
        "grandma": "손이 떨려서 비밀번호가 잘 안 눌리네…",
        "reason": "할머니, 진짜 기관은 ‘10분 안에’ 같은 말로 돈을 보내라고 하지 않아요.",
        "together": "할머니, 보내기 전에 딱 5분만요. 저랑 같이 은행에 전화해서 이 계좌가 뭔지 물어봐요.",
        "options": "final",
    },
]

# 끼어들 때 고를 수 있는 말과 행동입니다.
# base는 사기범을 믿는 정도를 낮추는 힘, trust는 나에 대한 신뢰 변화입니다.
APPROACHES = {
    "watch": {"label": "👀 일단 지켜본다", "base": 0, "trust": 0},
    "scold": {
        "label": "😠 “할머니, 그거 사기예요! 당장 끊어요!”",
        "base": 10,
        "trust": -15,
        "counter": True,
        "lesson": "다그치면 할머니는 창피하고 무서워져요. 사기범이 ‘가족에게 말하지 말라’고 한 말이 맞는 것처럼 느껴져 오히려 사기범 편에 서기 쉬워요.",
    },
    "reason": {
        "label": "근거를 하나 짚어 준다",
        "base": 25,
        "trust": 0,
        "lesson": "구체적인 근거 하나는 효과가 있어요. 다만 겁먹은 상태에서는 논리만으로 마음을 바꾸기 어려워요.",
    },
    "together": {
        "label": "공감하고, 함께 확인하자고 한다",
        "base": 45,
        "trust": 10,
        "lesson": "먼저 마음을 안심시키고, 상대가 준 번호가 아닌 공식 경로로 ‘같이’ 확인하자고 하면 할머니가 스스로 판단할 수 있어요.",
    },
    "snatch": {
        "label": "🤫 몰래 폰을 가져와 전화를 끊고 번호를 차단한다",
        "base": 30,
        "trust": -25,
        "counter": True,
        "lesson": "당장은 막을 수 있지만, 할머니는 무시당했다고 느껴요. 사기범은 다른 번호로 다시 연락하고, 할머니는 나 몰래 받을 수 있어요.",
    },
    "parent": {
        "label": "📱 엄마에게 바로 전화해 함께 설득한다",
        "base": 35,
        "trust": 0,
        "lesson": "혼자 어려울 때 다른 가족과 함께하면 힘이 실려요. 할머니가 평소 믿는 사람일수록 좋아요.",
    },
    "police": {
        "label": "🚨 112에 신고하고, 은행에 지급정지를 요청한다",
        "base": 100,
        "trust": -5,
        "lesson": "송금 직전·직후에는 망설이지 말고 112와 은행에 알려야 해요. 할머니가 놀라실 수 있으니 이유를 차분히 설명해 드려요.",
    },
    "real_check": {
        "label": "🔍 “이건 누가 보낸 건지 같이 볼까요?”",
        "base": 0,
        "trust": 0,
        "lesson": "진짜 연락은 함께 확인만 하고 넘어가면 돼요. 모든 연락을 의심하지 않는 것도 중요해요.",
    },
    "real_block": {
        "label": "🚫 “이것도 수상해요. 지우고 차단해요.”",
        "base": 0,
        "trust": -15,
        "lesson": "진짜 연락까지 막으면 할머니가 불편해지고, 정작 중요한 순간에 내 말을 덜 믿게 돼요.",
    },
}

OPTION_SETS = {
    "real": ["watch", "real_check", "real_block"],
    "scam": ["watch", "scold", "reason", "together", "snatch", "parent"],
    "final": ["watch", "scold", "together", "police"],
}

ENDINGS = {
    "best": ("⭐ 든든한 손주", "일찍 알아채고, 할머니가 놀라지 않게 공감하며 함께 확인했어요. 할머니는 손주 덕분에 스스로 사기라는 걸 깨달았어요.", "#DCFCE7"),
    "good": ("🟢 지켜 냈다", "중간에 사기범의 말이 먹히기도 했지만, 송금 전에 할머니가 멈추고 함께 확인했어요.", "#ECFDF5"),
    "close": ("🟠 아슬아슬", "송금 직전에야 막았어요. 실제라면 이미 앱이 깔리고 개인정보가 넘어갔을 수 있어요. 은행에 연락해 비밀번호를 바꾸고 설치된 앱을 지워야 해요.", "#FFEDD5"),
    "bad": ("🔴 송금 완료", "980만 원이 ‘안전계좌’로 넘어갔어요. 실제라면 즉시 112와 은행에 지급정지를 요청해야 해요. 다른 방법으로 다시 도전해 보세요.", "#FEE2E2"),
}


st.markdown(
    """
    <style>
    .gp-phone {max-width: 360px; margin: 0 auto 8px; background:#0B1220; border-radius:30px;
               padding:10px 12px 14px; border:3px solid #2B3645; box-shadow:0 10px 26px rgba(15,23,42,.28);
               color:#E5ECF4;}
    .gp-phone .notch {width:90px; height:6px; background:#2B3645; border-radius:6px; margin:0 auto 6px;}
    .gp-phone .status {display:flex; justify-content:space-between; font-size:.72rem; color:#AAB7C6; padding:2px 10px 8px;}
    .gp-title {font-size:.78rem; color:#9FB0C3; text-align:center; margin-bottom:6px;}
    .gp-item {background:#162033; border-radius:14px; padding:8px 10px; margin:6px 0; opacity:.55;}
    .gp-item.new {opacity:1; border:2px solid #FBBF24; animation: gp-pop .4s ease-out;}
    @keyframes gp-pop {from {transform:translateY(-8px); opacity:0;} to {transform:none; opacity:1;}}
    .gp-head {display:flex; justify-content:space-between; font-size:.74rem; color:#AAB7C6; margin-bottom:4px; gap:6px;}
    .gp-head b {color:#fff;}
    .gp-tag {font-size:.66rem; background:#7F1D1D; color:#FECACA; border-radius:6px; padding:1px 6px; white-space:nowrap;}
    .gp-tag.ok {background:#14532D; color:#BBF7D0;}
    .gp-tag.call {background:#1E3A8A; color:#BFDBFE;}
    .gp-line {font-size:.9rem; line-height:1.5; color:#F1F5F9;}
    .gp-line.voice {color:#FDE68A;}
    .gp-grandma {background:#FFF7ED; border:2px solid #FED7AA; border-radius:18px; padding:14px 16px; color:#172B3A;}
    .gp-grandma .face {font-size:2.6rem; line-height:1;}
    .gp-grandma .say {background:#fff; border-radius:14px 14px 14px 4px; padding:9px 12px; margin-top:8px;
                      border:1px solid #FED7AA; font-size:.98rem;}
    .gp-ending {border-radius:18px; padding:18px 20px; margin:6px 0 14px; color:#172B3A;}
    .gp-ending .t {font-size:1.6rem; font-weight:900; margin-bottom:6px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(text):
    return html.escape(str(text))


def reset_game():
    """게임 상태를 처음으로 되돌립니다."""
    for key in list(st.session_state):
        if key.startswith("gp_"):
            del st.session_state[key]
    st.session_state["gp_step"] = -1          # -1은 시작 전 안내 화면
    st.session_state["gp_belief"] = 0         # 할머니가 사기범을 믿는 정도
    st.session_state["gp_trust"] = START_TRUST
    st.session_state["gp_counter"] = False
    st.session_state["gp_log"] = []
    st.session_state["gp_result"] = None      # stopped / police / sent
    st.session_state["gp_pushed"] = -1        # 사기범의 push를 이미 반영한 연락 번호


def clamp(value):
    return max(0, min(100, value))


def enter_event(step):
    """피싱 연락이 들어오면 할머니가 사기범을 더 믿게 됩니다. 한 연락에 한 번만 반영합니다."""
    event = EVENTS[step]
    if event["real"] or st.session_state["gp_pushed"] == step:
        return
    push = event["push"]
    if st.session_state["gp_counter"]:
        push += COUNTER_PUSH
        st.session_state["gp_counter"] = False
    st.session_state["gp_belief"] = clamp(st.session_state["gp_belief"] + push)
    st.session_state["gp_pushed"] = step


def grandma_reaction(key, belief, stopped, real):
    if key == "watch":
        if real:
            return "(할머니가 문자를 한 번 보고 휴대전화를 내려놓는다.)"
        return "(할머니가 휴대전화를 귀에 댄 채 고개를 끄덕인다.)"
    if key == "real_check":
        return "그래, 같이 보자. …이건 맨날 오는 거야."
    if key == "real_block":
        return "이건 진짜야! 너 왜 이래, 할머니가 그것도 모를까 봐?"
    if key == "police":
        return "경찰까지? …그래, 네 말대로 해 보자. 손이 다 떨리네."
    if stopped:
        return "…듣고 보니 이상하네. 그래, 같이 확인해 보자. (할머니가 전화를 끊는다.)"
    if key == "scold":
        return "너까지 소리 지르니까 더 무섭다… 검사님이 아무한테도 말하지 말랬어."
    if key == "snatch":
        return "왜 남의 폰을 함부로 만져! 할머니가 알아서 해."
    if belief > 45:
        return "너는 몰라도 돼. 수사관이 진짜 같았어."
    return "그래도… 진짜 수사관 같던데. 조금만 더 생각해 볼게."


def act(key):
    step = st.session_state["gp_step"]
    event = EVENTS[step]
    approach = APPROACHES[key]
    trust_before = st.session_state["gp_trust"]

    # 나를 믿는 정도가 높을수록 같은 말도 더 잘 통합니다.
    effect = round(approach["base"] * trust_before / START_TRUST)
    if key == "police":
        effect = 100
    belief = clamp(st.session_state["gp_belief"] - effect)
    trust = clamp(trust_before + approach["trust"])
    st.session_state["gp_belief"] = belief
    st.session_state["gp_trust"] = trust
    if approach.get("counter"):
        st.session_state["gp_counter"] = True

    stopped = (not event["real"]) and key != "watch" and belief <= STOP_LINE
    if key == "police":
        result = "police"
    elif stopped:
        result = "stopped"
    elif event["options"] == "final":
        result = "sent"
    else:
        result = None

    if key == "reason":
        said = event["reason"]
    elif key == "together":
        said = event["together"]
    else:
        said = approach["label"]

    st.session_state["gp_log"].append(
        {
            "step": step,
            "key": key,
            "said": said,
            "reaction": grandma_reaction(key, belief, stopped, event["real"]),
            "lesson": approach.get("lesson", ""),
            "belief": belief,
            "trust": trust,
        }
    )

    if result:
        st.session_state["gp_result"] = result
        st.session_state["gp_step"] = len(EVENTS)  # 결말 화면
    else:
        st.session_state["gp_step"] = step + 1


def phone_html(step):
    items = []
    for index in range(step + 1):
        event = EVENTS[index]
        if event["kind"] == "call":
            tag = '<span class="gp-tag call">📞 통화</span>'
        elif event.get("saved"):
            tag = '<span class="gp-tag ok">저장된 연락처</span>'
        elif event["kind"] == "notice":
            tag = '<span class="gp-tag ok">앱 알림</span>'
        else:
            tag = '<span class="gp-tag">저장되지 않은 번호</span>'
        voice = " voice" if event["kind"] == "call" else ""
        lines = "".join(f'<div class="gp-line{voice}">{esc(t)}</div>' for t in event["lines"])
        lines += "".join(f'<div class="gp-line voice">{esc(t)}</div>' for t in event.get("call_lines", []))
        new = " new" if index == step else ""
        items.append(
            f'<div class="gp-item{new}"><div class="gp-head"><b>{esc(event["sender"])}</b>'
            f'<span>{tag} {esc(event["time"])}</span></div>{lines}</div>'
        )
    return (
        '<div class="gp-phone"><div class="notch"></div>'
        f'<div class="status"><span>{esc(EVENTS[step]["time"])}</span><span>📶 LTE 🔋 48%</span></div>'
        '<div class="gp-title">👵 할머니 휴대전화</div>'
        + "".join(reversed(items))
        + "</div>"
    )


def stage_count(step):
    return sum(1 for e in EVENTS[: step + 1] if not e["real"])


def show_gauges(step):
    belief = st.session_state["gp_belief"]
    trust = st.session_state["gp_trust"]
    total_stages = sum(1 for e in EVENTS if not e["real"])
    st.markdown(f"**😟 사기범을 믿는 정도 {belief}**")
    st.progress(belief / 100)
    st.markdown(f"**💛 할머니가 나를 믿는 정도 {trust}**")
    st.progress(trust / 100)
    st.markdown(f"**💸 송금까지 {stage_count(step)} / {total_stages}단계**")
    st.progress(stage_count(step) / total_stages)
    st.caption(
        f"사기범을 믿는 정도가 {STOP_LINE} 이하로 내려가면 할머니가 멈추고 함께 확인해요. "
        "수치는 게임 속 상태이며 실제 확률이 아니에요."
    )


def show_last_log():
    log = st.session_state["gp_log"]
    if not log:
        return
    last = log[-1]
    if last["key"] in ("watch", "real_check"):
        return
    if last["key"] in ("scold", "snatch", "real_block"):
        st.warning(f"💬 {last['lesson']}")
    else:
        st.info(f"💬 {last['lesson']}")


def show_intro():
    st.markdown("### 🎯 미션: 할머니의 돈을 지켜라")
    st.markdown(
        "주말 오전, 할머니 댁에 놀러 왔어요. 할머니 휴대전화에 연락이 하나씩 들어옵니다.\n\n"
        "- **진짜 연락**과 **피싱**이 섞여 있어요. 무엇이 피싱인지 직접 판단하세요.\n"
        "- 연락마다 **지켜볼지, 끼어들지, 어떻게 말할지** 골라요.\n"
        "- **다그치거나 몰래 막거나 진짜 연락까지 막으면** 할머니가 나를 덜 믿게 되고, 내 말이 잘 통하지 않아요.\n"
        "- 할머니가 스스로 멈추게 하거나, 송금 전에 막아야 해요."
    )
    st.markdown("#### 게이지 읽는 법")
    st.markdown(
        "- 😟 **사기범을 믿는 정도** — 피싱 연락이 올 때마다 올라가요. 설득하면 내려가요.\n"
        "- 💛 **할머니가 나를 믿는 정도** — 높을수록 같은 말도 더 잘 통해요.\n"
        "- 💸 **송금까지** — 마지막 단계까지 가기 전에 막아야 해요."
    )
    st.caption("교육용 가상 상황입니다. 실제 전화·문자·링크·송금은 일어나지 않아요.")
    if st.button("👵 할머니 댁 들어가기", type="primary"):
        st.session_state["gp_step"] = 0
        st.rerun()


def show_play():
    step = st.session_state["gp_step"]
    event = EVENTS[step]
    enter_event(step)

    show_last_log()
    phone_col, side_col = st.columns([1.1, 1])
    with phone_col:
        st.markdown(phone_html(step), unsafe_allow_html=True)
    with side_col:
        log = st.session_state["gp_log"]
        prev = log[-1]["reaction"] if log else None
        belief = st.session_state["gp_belief"]
        mood = "😰" if belief > 45 else "🤔" if belief > STOP_LINE else "👵"
        bubble = f'<div class="say">{esc(prev)}</div>' if prev else ""
        st.markdown(
            f'<div class="gp-grandma"><div class="face">{mood}</div>'
            f"{bubble}"
            f'<div class="say">{esc(event["grandma"])}</div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        show_gauges(step)

    st.markdown(f"#### {event['time']} · 새 연락이 왔어요. 어떻게 할까요?")
    for key in OPTION_SETS[event["options"]]:
        if key == "reason":
            label = f"💡 “{event['reason']}”"
        elif key == "together":
            label = f"🤝 “{event['together']}”"
        else:
            label = APPROACHES[key]["label"]
        st.button(
            label,
            key=f"gp_btn_{step}_{key}",
            on_click=act,
            args=(key,),
            use_container_width=True,
        )


def decide_ending():
    result = st.session_state["gp_result"]
    log = st.session_state["gp_log"]
    if result == "sent":
        return "bad"
    last_step = log[-1]["step"]
    if result == "police" or EVENTS[last_step]["options"] == "final":
        return "close"
    early = stage_count(last_step) <= 2
    return "best" if early and st.session_state["gp_trust"] >= START_TRUST else "good"


def show_ending():
    log = st.session_state["gp_log"]
    ending = decide_ending()
    title, story, color = ENDINGS[ending]
    trust = st.session_state["gp_trust"]

    st.markdown(
        f'<div class="gp-ending" style="background:{color};"><div class="t">{esc(title)}</div>{esc(story)}</div>',
        unsafe_allow_html=True,
    )
    if ending != "bad" and trust < 40:
        st.warning("💔 막기는 했지만 할머니 마음이 많이 상했어요. 다그치거나 몰래 막은 일이 있었는지 아래 기록에서 확인해 보세요.")

    blocked_real = sum(1 for r in log if r["key"] == "real_block")
    harsh = sum(1 for r in log if r["key"] in ("scold", "snatch"))
    first, second, third = st.columns(3)
    first.metric("💛 마지막 신뢰", trust)
    second.metric("진짜 연락을 막은 횟수", f"{blocked_real}번")
    third.metric("다그치거나 몰래 막은 횟수", f"{harsh}번")

    st.subheader("📋 그날 오전의 기록")
    st.caption("게임 중에는 알려 주지 않았던, 각 연락이 진짜였는지 피싱이었는지도 함께 공개해요.")
    for record in log:
        event = EVENTS[record["step"]]
        label = "✅ 진짜 연락" if event["real"] else f"🚨 피싱 · {event['stage']}"
        with st.expander(f"{event['time']} · {event['sender']} — {label}"):
            st.write("**연락 내용:**", " / ".join(event["lines"] + event.get("call_lines", [])))
            st.write("**내가 한 말·행동:**", record["said"])
            st.write("**할머니 반응:**", record["reaction"])
            if record["lesson"]:
                st.write("**돌아보기:**", record["lesson"])
            st.caption(f"이후 상태 · 사기범을 믿는 정도 {record['belief']} · 나를 믿는 정도 {record['trust']}")

    st.markdown("#### 주변 사람이 속고 있을 때, 이렇게 도와요")
    st.markdown(
        "1. **다그치지 말고 먼저 안심시키기** — “놀라셨죠, 잘못한 거 아니에요.” 겁먹은 사람은 꾸중을 들으면 더 숨어요.\n"
        "2. **근거는 짧고 분명하게** — “검찰은 전화로 돈을 옮기라고 하지 않아요.” 한 가지면 충분해요.\n"
        "3. **함께 확인하기** — 상대가 준 번호가 아니라 공식 대표번호·은행 창구로 ‘같이’ 확인해요. 판단은 본인이 하게 도와요.\n"
        "4. **진짜 연락은 막지 않기** — 모든 연락을 의심하면 정작 중요한 순간에 내 말을 믿지 않아요.\n"
        "5. **급하면 바로 신고** — 송금 직전·직후라면 112, 은행 지급정지, 금융감독원(1332)에 알리고 다른 가족과 함께해요."
    )

    report = (
        "잠깐! 할머니 폰 지키기 결과\n\n"
        f"결말: {title}\n마지막 신뢰: {trust}\n"
        f"진짜 연락을 막은 횟수: {blocked_real}번 · 다그치거나 몰래 막은 횟수: {harsh}번\n\n"
        + "\n".join(
            f"{EVENTS[r['step']]['time']} {EVENTS[r['step']]['sender']} "
            f"({'진짜' if EVENTS[r['step']]['real'] else '피싱'})\n"
            f"   내 행동: {r['said']}\n   할머니: {r['reaction']}"
            for r in log
        )
        + "\n\n교육용 가상 상황의 결과이며, 수치는 실제 확률이 아닙니다."
    )
    st.download_button(
        "기록 내려받기",
        data=report.encode("utf-8-sig"),
        file_name="jamkkan_grandma_report.txt",
        mime="text/plain",
    )
    st.button("🔄 다른 방법으로 다시 도전", type="primary", on_click=reset_game)


st.title("✋ 잠깐! · 할머니 폰 지키기")
st.write("내가 아니라 **옆에 있는 가족이 속고 있을 때**, 어떻게 말하고 언제 끼어들어야 할까요?")
st.caption("교육용 가상 사례입니다. 실제 전화, 문자, 링크 접속, 송금은 일어나지 않습니다.")

if "gp_step" not in st.session_state:
    reset_game()

step = st.session_state["gp_step"]
if step < 0:
    show_intro()
elif step >= len(EVENTS):
    show_ending()
else:
    show_play()
