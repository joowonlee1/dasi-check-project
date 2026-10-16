import streamlit as st
from mascot_ui import show_mascot


KEY = "grandma_verify_v2"

# 모든 연락과 확인 결과는 교육용으로 만든 가상 자료입니다.
EVENTS = [
    {
        "time": "10:02",
        "sender": "○○은행",
        "kind": "결제 알림",
        "text": "체크카드 승인 12,800원 · 한빛마트",
        "grandma": "아까 장 본 것 같은데, 금액도 한번 볼까?",
        "real": True,
        "route": (
            "문자에 답장하지 않고, 직접 실행한 은행 앱과 "
            "영수증을 비교해요."
        ),
        "evidence": (
            "가상 영수증과 은행 앱 내역에 "
            "한빛마트 12,800원 결제가 모두 있어요."
        ),
        "finding": (
            "이번 결제 알림은 할머니의 실제 구매 내역과 일치해요."
        ),
    },
    {
        "time": "10:05",
        "sender": "서울중앙지검이라고 표시된 번호",
        "kind": "전화",
        "text": (
            "수사관입니다. 할머님 통장이 범죄에 쓰였습니다. "
            "가족에게도 통화 내용을 알리지 마세요."
        ),
        "grandma": (
            "내가 무슨 일을 했다고… "
            "무서워서 어떻게 해야 할지 모르겠네."
        ),
        "real": False,
        "route": (
            "상대와 통화를 끝내고, 별도 기기로 공식 홈페이지의 "
            "대표번호를 찾아 확인해요."
        ),
        "evidence": (
            "게임 속 공식 확인 결과, 이 연락에서 주장한 담당자와 "
            "요청은 확인되지 않았어요. "
            "상대는 가족과의 확인도 막고 있어요."
        ),
        "finding": (
            "이 시나리오의 연락은 기관 사칭이에요. "
            "발신 표시만으로 신원을 믿으면 안 돼요."
        ),
    },
    {
        "time": "10:08",
        "sender": "햇살정형외과",
        "kind": "문자",
        "text": (
            "내일 오전 10시 진료 예약 안내드립니다. "
            "회신은 필요 없습니다."
        ),
        "grandma": (
            "무릎 진료 예약을 해 둔 건 맞아. "
            "시간이 언제였더라?"
        ),
        "real": True,
        "route": (
            "기존 예약증을 확인하고, "
            "예약증에 적힌 병원 번호로 확인해요."
        ),
        "evidence": (
            "기존 예약증과 게임 속 병원 확인 결과가 "
            "모두 내일 오전 10시로 일치해요."
        ),
        "finding": (
            "이번 문자는 기존 진료 예약과 일치하는 안내예요."
        ),
    },
    {
        "time": "10:11",
        "sender": "처음 보는 휴대전화 번호",
        "kind": "문자와 전화",
        "text": (
            "[사건 열람 안내] 가상 앱 설치 링크. "
            "상대는 설치하지 않으면 체포될 수 있다고 재촉합니다."
        ),
        "grandma": "빨리 설치해야 하는 거 아니니?",
        "real": False,
        "route": (
            "링크를 열지 않고, 별도로 찾은 공식 연락처에서 "
            "설치 요구를 확인해요."
        ),
        "evidence": (
            "게임 속 공식 확인 결과, 이 링크와 앱 설치 요청은 "
            "해당 기관의 안내가 아니에요."
        ),
        "finding": (
            "겁을 주면서 앱 설치를 유도하는 사칭 연락이에요."
        ),
    },
    {
        "time": "10:14",
        "sender": "우체국이라고 표시된 발신자",
        "kind": "문자",
        "text": (
            "등기우편이 오늘 14~16시에 배달될 예정입니다. "
            "회신 요청 없음."
        ),
        "grandma": (
            "올 서류가 있긴 한데, 이 안내가 맞는지 모르겠네."
        ),
        "real": True,
        "route": (
            "보낼 기관에서 미리 받은 접수번호를 이용해, "
            "직접 접속한 공식 배송 조회에서 확인해요."
        ),
        "evidence": (
            "기존 접수번호의 게임 속 배송 조회 결과가 "
            "오늘 14~16시 배달 예정으로 일치해요."
        ),
        "finding": (
            "별도 배송 기록으로 이번 안내를 확인했어요. "
            "링크가 없다는 이유만으로 진짜라고 판단한 것은 아니에요."
        ),
    },
    {
        "time": "10:17",
        "sender": "앞서 수사관이라고 말한 사람",
        "kind": "전화",
        "text": (
            "돈을 보호하려면 안전계좌로 옮겨야 합니다. "
            "은행 직원에게는 손주 등록금이라고 말하세요."
        ),
        "grandma": (
            "내 돈을 지키려는 건데… "
            "은행에 사실대로 말하면 안 되나?"
        ),
        "real": False,
        "route": (
            "이체를 보류하고, 직접 찾은 은행 공식 연락처에 "
            "상대의 요구를 그대로 설명해요."
        ),
        "evidence": (
            "게임 속 은행 확인 결과, 이 송금 요구는 "
            "사칭 수법으로 확인됐어요. "
            "은행 직원에게 거짓말하라는 요구도 위험 신호예요."
        ),
        "finding": (
            "요구를 따르지 않고 송금을 멈춰야 하는 상황이에요."
        ),
    },
    {
        "time": "10:21",
        "sender": "은행 앱의 이체 화면",
        "kind": "송금 직전",
        "text": (
            "받는 분: 금융보안관리 / 9,800,000원. "
            "전화 속 상대가 지금 바로 보내라고 재촉합니다."
        ),
        "grandma": "보내기 버튼만 누르면 된다는데…",
        "real": False,
        "route": (
            "보내기 버튼을 누르지 않고, 별도로 찾은 "
            "은행 공식 연락처에 송금 목적을 설명해요."
        ),
        "evidence": (
            "게임 속 은행은 상대가 요구한 송금을 "
            "진행하지 말라고 안내해요. "
            "은행 앱이 진짜여도 송금 요구까지 진짜인 것은 아니에요."
        ),
        "finding": (
            "정상 앱에서도 사기범의 요구에 따라 "
            "돈을 보낼 수 있어요. 송금을 멈추세요."
        ),
    },
]


# ─────────────────────────────────────
# 게임 상태
# ─────────────────────────────────────

def new_game():
    return {
        "step": 0,
        "checked": False,
        "held": False,
        "helper": False,
        "log": [],
        "ending": None,
    }


def reset():
    st.session_state[KEY] = new_game()
    st.session_state[KEY + "_started"] = True


def record_choice(game, action):
    game["log"].append(
        {
            "index": game["step"],
            "checked": game["checked"],
            "helper": game["helper"],
            "action": action,
        }
    )


def advance(game):
    game["step"] += 1
    game["checked"] = False
    game["held"] = False
    game["helper"] = False

    if game["step"] >= len(EVENTS):
        game["ending"] = "review"


# ─────────────────────────────────────
# 선택 처리
# ─────────────────────────────────────

def choose(game, action):
    event = EVENTS[game["step"]]

    # 확인은 장면을 넘기지 않고 근거만 공개합니다.
    if action in ("check", "help"):
        game["checked"] = True

        if action == "help":
            game["helper"] = True

        return

    if action == "pause":
        game["held"] = True

        # 확인 전 보류에는 정답 판정을 내리지 않습니다.
        if not game["checked"]:
            return

        record_choice(
            game,
            "확인 후 요구를 멈춤 / 연락을 보류함",
        )

        if not event["real"]:
            game["ending"] = "protected"
        else:
            advance(game)

        return

    if action == "continue":
        record_choice(
            game,
            "연락을 받아들이고 계속 진행함",
        )

        if game["step"] == len(EVENTS) - 1:
            game["ending"] = "sent"
        else:
            advance(game)


# ─────────────────────────────────────
# 결과 기록
# ─────────────────────────────────────

def make_report(game):
    lines = [
        "잠깐! · 할머니 폰 지키기",
        "교육용 가상 상황의 결과",
        "",
    ]

    for item in game["log"]:
        event = EVENTS[item["index"]]

        lines.extend(
            [
                f"{event['time']} · {event['sender']}",
                "게임 속 설정: "
                + ("진짜 연락" if event["real"] else "피싱"),
                "별도 경로 확인: "
                + ("했음" if item["checked"] else "하지 않음"),
                "내 선택: " + item["action"],
                "확인 근거: " + event["evidence"],
                "",
            ]
        )

    return "\n".join(lines)


def show_result(game):
    if game["ending"] == "protected":
        st.success(
            "🛡️ 별도 경로로 확인하고, 위험한 요구를 멈췄어요!"
        )
        st.write(
            "이번 사건은 여기서 마무리돼요. "
            "이후 연락은 진행하지 않아요."
        )

    elif game["ending"] == "sent":
        st.error(
            "게임 속에서 사기범이 요구한 송금이 진행됐어요."
        )
        st.write(
            "어떤 단계에서 보류하고 별도로 확인할 수 있었는지 "
            "기록을 살펴봐요."
        )

    else:
        st.info(
            "연습을 마쳤어요. 확인 과정과 선택을 돌아봐요."
        )

    checked = sum(
        item["checked"]
        for item in game["log"]
    )

    left, right = st.columns(2)
    left.metric("판단한 연락", len(game["log"]))
    right.metric("별도 경로로 확인한 연락", checked)

    st.caption(
        "학습 기록이며 실제 대응 능력이나 "
        "피해 확률을 나타내지 않아요."
    )

    st.subheader("📋 내 선택 돌아보기")

    for item in game["log"]:
        event = EVENTS[item["index"]]
        verdict = "진짜 연락" if event["real"] else "피싱"

        with st.expander(
            f"{event['time']} · {verdict} · 내 선택 돌아보기"
        ):
            st.write("**연락 내용:** " + event["text"])
            st.write("**내 선택:** " + item["action"])
            st.write("**판단 근거:** " + event["evidence"])

            if not item["checked"]:
                st.warning(
                    "선택 전 별도 경로로 확인하지 않았어요."
                )

            elif event["real"]:
                st.info(
                    "기존 내역과 대조했어요. "
                    "조심스럽게 확인하거나 보류한 것 자체는 "
                    "잘못이 아니에요."
                )

            elif "계속 진행" in item["action"]:
                st.warning(
                    "위험하다는 확인 결과가 있었지만 "
                    "계속 진행했어요. "
                    "확인 결과를 행동에도 반영해 봐요."
                )

            else:
                st.success(
                    "확인한 근거에 따라 위험한 요구를 멈췄어요."
                )

    st.markdown(
        "**기억해요**\n"
        "- 발신자 이름이나 저장된 번호만으로 "
        "신원을 확정하지 않아요.\n"
        "- 모르겠으면 먼저 보류하고 "
        "별도 경로로 확인해요.\n"
        "- 가족을 다그치기보다 안심시키고 "
        "함께 확인해요."
    )

    st.download_button(
        "기록 내려받기",
        data=make_report(game).encode("utf-8-sig"),
        file_name="jamkkan_grandma_report.txt",
        mime="text/plain",
    )

    show_mascot(
        "retry",
        "다른 선택도 연습해 볼까요?",
        width=100,
    )

    st.button(
        "다시 도전하기",
        on_click=reset,
    )


# ─────────────────────────────────────
# 화면
# ─────────────────────────────────────

st.title("✋ 잠깐! · 할머니 폰 지키기")

st.write(
    "정답을 찍기보다, 근거를 확인하고 "
    "할머니와 함께 대응해요."
)

st.caption(
    "연락·확인 결과는 모두 가상입니다. "
    "실제 전화·조회·설치·송금은 실행하지 않아요."
)

if KEY not in st.session_state:
    st.session_state[KEY] = new_game()

game = st.session_state[KEY]


# 시작 안내
if not st.session_state.get(KEY + "_started", False):
    show_mascot(
        "phone",
        "모르겠으면 잠깐 멈추고, 함께 확인해요.",
    )

    st.markdown(
        "### 어떻게 진행하나요?\n"
        "1. 새 연락과 할머니의 말을 읽어요.\n"
        "2. **함께 확인하기**로 별도 자료와 "
        "확인 결과를 살펴봐요.\n"
        "3. 확인한 내용을 바탕으로 계속 진행할지, "
        "멈출지 선택해요.\n\n"
        "모든 연락에 같은 버튼이 나와요. "
        "아직 모르겠다면 **일단 멈추기**를 눌러도 괜찮아요. "
        "가족에게 도움을 요청하면 "
        "함께 확인하는 가상 결과를 볼 수 있어요."
    )

    st.button(
        "👵 할머니 댁 들어가기",
        type="primary",
        on_click=reset,
    )


# 결과
elif game["ending"]:
    show_result(game)


# 게임 진행
else:
    event = EVENTS[game["step"]]

    st.caption(
        f"연락 {game['step'] + 1} / {len(EVENTS)}"
    )

    phone, grandma = st.columns([1.1, 1])

    with phone:
        with st.container(border=True):
            st.markdown("### 📱 할머니 휴대전화")

            st.caption(
                f"{event['time']} · {event['kind']}"
            )

            st.write(
                "**화면에 표시된 발신자:** "
                + event["sender"]
            )

            st.info(event["text"])

            st.caption(
                "발신자 표시는 확인 단서일 뿐, "
                "신원 확인 결과가 아니에요."
            )

    with grandma:
        show_mascot(
            "phone",
            "할머니의 이야기도 들어봐요.",
            width=100,
        )

        st.markdown("### 👵 할머니")
        st.write(event["grandma"])

    if game["held"]:
        st.info(
            "요구를 잠시 보류했어요. "
            "확인 전에는 진짜인지 피싱인지 단정하지 않아요."
        )

    if game["checked"]:
        with st.container(border=True):
            st.markdown("### 🔎 함께 확인한 근거")

            if game["helper"]:
                st.write(
                    "가족이 함께 내용을 살펴보고 "
                    "별도 경로로 확인했어요."
                )

            st.write(
                "**확인 방법:** " + event["route"]
            )

            st.write(
                "**가상 확인 결과:** " + event["evidence"]
            )

            st.write(
                "**판단:** " + event["finding"]
            )

    else:
        st.caption(
            "‘함께 확인하기’를 누르면 "
            "별도 경로로 확인한 가상 자료가 나타나요."
        )

    st.markdown("### 어떻게 대응할까요?")

    a, b = st.columns(2)

    with a:
        if st.button(
            "🔎 함께 확인하기",
            use_container_width=True,
        ):
            choose(game, "check")
            st.rerun()

        if st.button(
            "⏸️ 일단 멈추기 / 확인 후 보류하기",
            use_container_width=True,
        ):
            choose(game, "pause")
            st.rerun()

    with b:
        if st.button(
            "👪 가족에게 도움 요청하기",
            use_container_width=True,
        ):
            choose(game, "help")
            st.rerun()

        if st.button(
            "➡️ 연락을 받아들이고 계속 진행",
            use_container_width=True,
        ):
            choose(game, "continue")
            st.rerun()

    st.caption(
        "확인 전 멈추면 현재 장면에 머물러요. "
        "확인 후 멈추면 위험한 요구를 중단하거나 "
        "정상 연락을 보류해요."
    )
