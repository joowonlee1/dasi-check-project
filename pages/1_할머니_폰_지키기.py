from play_ui import intro, bridge
import html
import copy
import random
import time

import streamlit as st
import streamlit.components.v1 as components
from mascot_ui import show_hero, show_key_question, show_mascot, show_tiles
from card_ui import show_result_card
import dotori_data as dd
from grandma_face import face_svg


# 모든 인물·기관명·번호·링크·확인 결과는 교육용 가상 자료입니다.
KEY = "grandma_v3"

STOP_LINE = 20      # 사기범을 믿는 정도가 이 값 이하가 되면 할머니가 스스로 멈춰요.
START_TRUST = 70    # 할머니가 처음에 나를 믿는 정도
COUNTER_PUSH = 10   # 다그치거나 몰래 막으면 사기범이 다음에 더 세게 몰아붙여요.

# 할머니 휴대전화에 시간 순서대로 들어오는 연락입니다.
# real=True는 진짜 연락, False는 피싱입니다. push는 할머니가 사기범을 더 믿게 되는 정도입니다.
# clues에는 판정 없이 '보이는 사실'만 적습니다. 판단은 플레이어가 합니다.
EVENTS = [
    {
        "time": "10:02",
        "kind": "notice",
        "sender": "○○은행",
        "lines": ["[○○은행] 체크카드 승인 12,800원 · 한빛마트"],
        "real": True,
        "grandma": "아까 장 본 거네.",
        "clues": [
            "할머니가 오늘 아침 한빛마트에서 장을 봤어요.",
            "금액과 가게 이름만 있고, 링크나 요구 사항은 없어요.",
        ],
        "route": "문자에 답하지 않고, 직접 실행한 은행 앱 내역이나 영수증과 비교해요.",
        "result": "영수증과 은행 앱에 한빛마트 12,800원 결제가 모두 있어요.",
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
        "grandma_alert": "아이고, 내가 무슨 일을… 경찰서 한 번 가 본 적 없는데.",
        "clues": [
            "화면에 ‘서울중앙지검’이라고 표시돼요.",
            "할머니 통장이 범죄에 쓰였다고 말해요.",
            "통화 내용을 가족에게도 알리지 말라고 해요.",
        ],
        "reason": "검찰은 전화로 사건을 알리면서 가족에게 비밀로 하라고 하지 않아요.",
        "together": "놀라셨죠, 할머니 잘못 아니에요. 같이 검찰청 대표번호로 직접 걸어서 확인해 봐요.",
        "route": "전화를 끊고, 검찰청 공식 홈페이지에서 직접 찾은 대표번호로 확인해요.",
        "result": "공식 대표번호로 확인하니 그런 담당자와 사건은 없었어요. 발신 표시는 조작될 수 있어요.",
    },
    {
        "time": "10:08",
        "kind": "sms",
        "sender": "햇살정형외과",
        "saved": True,
        "lines": ["[햇살정형외과] 내일(목) 오전 10시 진료 예약 안내드립니다. 회신은 필요 없습니다."],
        "real": True,
        "grandma": "아, 내일 무릎 보러 가는 날이지.",
        "clues": [
            "저장된 연락처 ‘햇살정형외과’에서 왔어요.",
            "할머니가 내일 무릎 진료를 예약해 두었어요.",
            "회신이나 링크를 요구하지 않아요.",
        ],
        "route": "기존 예약증에 적힌 병원 번호로 확인해요.",
        "result": "예약증과 병원 확인 결과 모두 내일 오전 10시예요.",
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
        "grandma_alert": "또 그 수사관이야? 이번엔 앱을 깔라네… 안 깔면 체포라는데.",
        "clues": [
            "저장되지 않은 010 번호에서 왔어요.",
            "‘사건 열람’을 하려면 앱을 설치하라는 링크가 있어요.",
            "설치하지 않으면 체포영장이 나온다고 재촉해요.",
        ],
        "reason": "검찰은 앱 설치를 시키지 않아요. 이 앱은 휴대폰을 원격으로 조종하는 앱일 수 있어요.",
        "together": "무서우시죠. 앱은 깔지 말고, 제가 옆에서 검찰청 대표번호로 같이 물어볼게요.",
        "route": "링크를 누르지 않고, 직접 찾은 공식 연락처로 앱 설치 요구가 맞는지 물어봐요.",
        "result": "공식 기관은 사건 열람을 위해 앱 설치를 요구하지 않아요. 원격 조종 앱일 수 있어요.",
    },
    {
        "time": "10:14",
        "kind": "sms",
        "sender": "우체국",
        "saved": True,
        "lines": ["[우체국] 등기우편이 오늘 14~16시에 배달될 예정입니다. 링크·회신 요청 없음."],
        "real": True,
        "grandma": "무슨 등기가 오나? 연금 서류인가.",
        "clues": [
            "저장된 ‘우체국’ 연락처에서 왔어요.",
            "할머니가 연금 서류를 기다리고 있어요.",
            "링크도 회신 요청도 없어요.",
        ],
        "route": "미리 받은 접수번호로, 직접 접속한 공식 배송 조회에서 확인해요.",
        "result": (
            "배송 조회 결과도 오늘 14~16시 배달 예정이에요. "
            "링크가 없다는 것만으로 진짜라고 단정하지 않고 따로 확인한 거예요."
        ),
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
        "grandma_alert": "아까 끊었는데 또 전화가 왔어. 돈을 옮기라는데… 진짜면 어쩌지?",
        "clues": [
            "아까 ‘수사관’이라던 사람이 다시 전화했어요.",
            "할머니 돈을 ‘안전계좌’로 옮기라고 해요.",
            "은행 직원에게는 ‘손주 등록금’이라고 말하라고 해요.",
        ],
        "reason": "‘안전계좌’는 없어요. 어떤 기관도 돈을 옮기라고 하지 않고, 은행 직원에게 거짓말하라는 건 사기예요.",
        "together": "할머니 돈 지키려는 거 알아요. 이체하기 전에 저랑 같이 은행 창구에 가서 직원한테 먼저 물어봐요.",
        "route": "이체하지 않고, 은행 창구나 직접 찾은 은행 대표번호에 상대의 요구를 그대로 말해요.",
        "result": "‘안전계좌’는 없어요. 은행 직원에게 거짓말하라는 요구도 사기의 신호예요.",
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
        "final": True,
        "push": 20,
        "stage": "송금 직전",
        "grandma": "손이 떨려서 비밀번호가 잘 안 눌리네…",
        "grandma_alert": "자꾸 재촉하니까 혹시나 싶어서 이체 화면을 열어 봤어…",
        "clues": [
            "은행 앱 이체 화면에 받는 분 ‘금융보안관리’, 980만 원이 입력돼 있어요.",
            "전화 속 상대가 10분 안에 안 보내면 계좌가 동결된다고 재촉해요.",
        ],
        "reason": "할머니, 진짜 기관은 ‘10분 안에’ 같은 말로 돈을 보내라고 하지 않아요.",
        "together": "할머니, 보내기 전에 딱 5분만요. 저랑 같이 은행에 전화해서 이 계좌가 뭔지 물어봐요.",
        "route": "보내기 버튼을 누르지 않고, 은행에 연락해 받는 계좌를 확인해요.",
        "result": "은행 앱이 진짜여도, 송금을 시키는 요구까지 진짜인 것은 아니에요.",
    },
]

# 모든 연락에 같은 선택지를 보여 줍니다. 버튼 모양으로 정답을 알 수 없게 하기 위해서예요.
# base: 사기범을 믿는 정도를 낮추는 힘 / trust: 피싱일 때 나에 대한 신뢰 변화
# real_trust: 진짜 연락에 이 행동을 했을 때 신뢰 변화
APPROACHES = {
    "watch": {"label": "👀 일단 지켜본다", "base": 0, "trust": 0, "real_trust": 0},
    "together": {
        "label": "🤝 공감하고, 원래 알던 번호로 함께 확인하자고 한다",
        "base": 45,
        "trust": 10,
        "real_trust": -10,
        "lesson": "먼저 마음을 안심시키고, 상대가 준 번호가 아닌 공식 경로로 ‘같이’ 확인하자고 하면 할머니가 스스로 판단할 수 있어요.",
    },
    "reason": {
        "label": "💡 수상한 점을 하나 짚어 준다",
        "base": 25,
        "trust": 0,
        "real_trust": -10,
        "lesson": "구체적인 근거 하나는 효과가 있어요. 다만 겁먹은 상태에서는 논리만으로 마음을 바꾸기 어려워요.",
    },
    "parent": {
        "label": "📱 엄마에게 전화해 함께 설득한다",
        "base": 35,
        "trust": 0,
        "real_trust": -10,
        "lesson": "혼자 어려울 때 다른 가족과 함께하면 힘이 실려요. 할머니가 평소 믿는 사람일수록 좋아요.",
    },
    "scold": {
        "label": "😠 “할머니, 그거 사기예요! 당장 끊어요!”",
        "base": 10,
        "trust": -15,
        "real_trust": -15,
        "counter": True,
        "lesson": "다그치면 할머니는 창피하고 무서워져요. ‘가족에게 말하지 말라’던 사기범의 말이 맞는 것처럼 느껴져 오히려 사기범 편에 서기 쉬워요.",
    },
    "snatch": {
        "label": "🤫 몰래 폰을 가져와 끊고 번호를 차단한다",
        "base": 30,
        "trust": -25,
        "real_trust": -25,
        "counter": True,
        "lesson": "당장은 막을 수 있지만, 할머니는 무시당했다고 느껴요. 사기범은 다른 번호로 다시 연락하고, 할머니는 나 몰래 받을 수 있어요.",
    },
    "police": {
        "label": "🚨 112에 신고하고, 은행에 지급정지를 요청한다",
        "base": 100,
        "trust": -5,
        "real_trust": -5,
        "lesson": "송금 직전·직후에는 망설이지 말고 112와 은행에 알려야 해요. 할머니가 놀라실 수 있으니 이유를 차분히 설명해 드려요.",
    },
}

NORMAL_OPTIONS = ["watch", "together", "reason", "parent", "scold", "snatch"]
FINAL_OPTIONS = NORMAL_OPTIONS + ["police"]

# 진짜 연락까지 의심하거나 막은 행동입니다.
DOUBT_KEYS = ("reason", "parent", "scold", "snatch", "police")

REAL_LESSON = {
    "together": "진짜 연락은 확인만 하고 넘어가면 충분해요. 모든 연락을 의심하면 할머니가 지칠 수 있어요.",
    "doubt": "진짜 연락까지 의심하거나 막으면 할머니가 불편해지고, 정작 중요한 순간에 내 말을 덜 믿게 돼요.",
    "over": "진짜 연락까지 매번 ‘같이 확인하자’고 하면 할머니가 지쳐서, 정작 피싱이 왔을 때 내 말을 덜 들어요. 진짜는 지켜보기만 해도 충분해요.",
}

ENDINGS = {
    "best": (
        "⭐ 든든한 손주",
        "일찍 알아채고, 할머니가 놀라지 않게 공감하며 함께 확인했어요. 진짜 연락은 괜히 막지 않았고, 사기범이 다시 연락해 와도 할머니는 흔들리지 않았어요.",
        "#DCFCE7",
    ),
    "good": (
        "🟢 지켜 냈다",
        "중간에 사기범의 말이 먹히기도 했지만, 송금 전에 할머니가 멈추고 함께 확인했어요.",
        "#ECFDF5",
    ),
    "close": (
        "🟠 아슬아슬",
        "송금 직전에야 막았어요. 실제라면 이미 앱이 깔리고 개인정보가 넘어갔을 수 있어요. 은행에 연락해 비밀번호를 바꾸고 설치된 앱을 지워야 해요.",
        "#FFEDD5",
    ),
    "bad": (
        "🔴 송금 완료",
        "980만 원이 ‘안전계좌’로 넘어갔어요. 실제라면 즉시 112와 은행에 지급정지를 요청해야 해요. 다른 방법으로 다시 도전해 보세요.",
        "#FEE2E2",
    ),
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
    .gp-grandma .say.prev {color:#6B7280; font-size:.9rem;}
    .gp-ending {border-radius:18px; padding:18px 20px; margin:6px 0 14px; color:#172B3A;}
    .gp-ending .t {font-size:1.6rem; font-weight:900; margin-bottom:6px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# '짠!' 효과: 결과가 나오는 순간에만 두구두구 → 도장 쾅 → 반짝이가 터져요.
st.markdown(
    """
<style>
@keyframes zz-pop {0%{transform:scale(.5);opacity:0} 65%{transform:scale(1.06);opacity:1} 100%{transform:scale(1)}}
@keyframes zz-bounce {0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)}}
@keyframes zz-stamp {0%{transform:scale(3) rotate(-18deg);opacity:0} 60%{transform:scale(.9) rotate(-12deg);opacity:1} 100%{transform:scale(1) rotate(-8deg);opacity:1}}
@keyframes zz-shake {0%,100%{transform:translateX(0)} 20%,60%{transform:translateX(-10px)} 40%,80%{transform:translateX(10px)}}
@keyframes zz-burst {0%{transform:translate(0,0) scale(.3);opacity:1} 100%{transform:translate(var(--x),var(--y)) scale(1.2);opacity:0}}
.zz-drum {text-align:center;font-size:1.5rem;font-weight:900;color:#20483F;padding:40px 0;}
.zz-drum div {font-size:70px;animation:zz-bounce .45s ease-in-out infinite;}
.zz-card {position:relative;overflow:hidden;}
.zz-card.go.win {animation:zz-pop .6s ease-out both;}
.zz-card.go.lose {animation:zz-shake .6s ease-in-out both;}
.zz-stamp {display:inline-block;margin-top:10px;border:5px solid #D7263D;color:#D7263D;border-radius:12px;padding:4px 18px;
  font-size:1.7rem;font-weight:900;letter-spacing:.08em;background:rgba(255,255,255,.65);transform:rotate(-8deg);max-width:92%;}
.zz-stamp.ok {border-color:#16815F;color:#16815F;}
.zz-stamp.miss {border-color:#5A7068;color:#5A7068;}
.go .zz-stamp {animation:zz-stamp .5s .45s ease-out both;}
.zz-spark {position:absolute;left:50%;top:45%;font-size:26px;opacity:0;pointer-events:none;}
.go .zz-spark {animation:zz-burst 1.1s ease-out both;}
@media (max-width:640px) {.zz-stamp {font-size:1.35rem;}}
@media (prefers-reduced-motion: reduce) {.zz-card *, .zz-card, .zz-drum div {animation:none !important;opacity:1;}}
</style>
""",
    unsafe_allow_html=True,
)


def drumroll(frames):
    """결과를 바로 보여 주지 않고 잠깐 뜸을 들여요."""
    box = st.empty()
    for icon, text in frames:
        box.markdown(f'<div class="zz-drum"><div>{icon}</div>{text}</div>', unsafe_allow_html=True)
        time.sleep(0.6)
    box.empty()


def sparks(icons):
    out = []
    for i, icon in enumerate(icons):
        x = [140, 120, 70, 0, -70, -120, -140, -120, -70, 0, 70, 120][i % 12]
        y = [0, -70, -120, -140, -120, -70, 0, 70, 120, 140, 120, 70][i % 12]
        out.append(f'<span class="zz-spark" style="--x:{x}px;--y:{y}px;animation-delay:{.45 + i * .02:.2f}s">{icon}</span>')
    return "".join(out)


def scroll_top():
    components.html(
        "<script>const m = window.parent.document.querySelector('[data-testid=stMain]');"
        "if (m) m.scrollTo(0, 0); window.parent.scrollTo(0, 0);</script>",
        height=0,
    )


def esc(text):
    return html.escape(str(text))


def clamp(value):
    return max(0, min(100, value))


# ─────────────────────────────────────
# 게임 상태
# ─────────────────────────────────────

def new_game(started=False):
    return {
        "started": started,
        "step": 0,
        "belief": 0,             # 할머니가 사기범을 믿는 정도
        "trust": START_TRUST,    # 할머니가 나를 믿는 정도
        "counter": False,        # 다그치거나 몰래 막아서 사기범이 더 세게 나오는지
        "alert": False,          # 할머니가 한 번이라도 스스로 멈췄는지
        "pushed": -1,            # 사기범의 push를 이미 반영한 연락 번호
        "clue_open": False,      # 현재 연락의 단서를 열어 봤는지
        "log": [],
        "result": None,          # protected / sent
    }


def start_game():
    st.session_state[KEY] = new_game(started=True)
    dd.scroll_top()  # 아래쪽 버튼을 눌러 들어와도 첫 연락을 맨 위부터 보여 줘요.
    
def back_to_intro():
    """다시 도전할 때는 게임 설명 화면부터 다시 보여 줍니다."""
    st.session_state[KEY] = new_game(started=False)
    dd.scroll_top()

def go_back():
    """바로 전 화면으로: 앞 연락을 고르기 전 상태로 되돌려요. 첫 연락이면 게임 설명 화면으로 가요."""
    game = st.session_state[KEY]
    history = game.get("history") or []
    if not history:
        back_to_intro()
        return
    previous = history.pop()
    previous["history"] = history
    previous.pop("show_reaction", None)
    st.session_state[KEY] = previous
    dd.scroll_top()

def open_clues():
    st.session_state[KEY]["clue_open"] = True


def scam_stage(step):
    return sum(1 for event in EVENTS[: step + 1] if not event["real"])


TOTAL_STAGES = sum(1 for event in EVENTS if not event["real"])


def enter_event(game):
    """피싱 연락이 오면 할머니가 사기범을 더 믿게 됩니다. 한 연락에 한 번만 반영합니다."""
    step = game["step"]
    event = EVENTS[step]
    if event["real"] or game["pushed"] == step:
        return
    push = event["push"]
    if game["alert"]:
        # 이미 한 번 속지 않은 할머니는 덜 흔들려요.
        push //= 2
    if game["counter"]:
        push += COUNTER_PUSH
        game["counter"] = False
    game["belief"] = clamp(game["belief"] + push)
    game["pushed"] = step


def grandma_reaction(key, game, stopped, real):
    if real:
        if key == "watch":
            return "(할머니가 문자를 한 번 보고 휴대전화를 내려놓는다.)"
        if key == "together":
            return "그래, 같이 보자. …이건 늘 오던 연락이야. 너무 걱정 말렴."
        if key == "reason":
            return "이게 뭐가 이상해? 평소에 오던 연락인데."
        if key == "parent":
            return "엄마까지 부를 일이니? 이건 진짜야."
        return "이건 진짜야! 너 왜 이래, 할머니가 그것도 모를까 봐?"

    if key == "police":
        return "경찰까지? …그래, 네 말대로 해 보자. 손이 다 떨리네."
    if stopped and key == "watch":
        return "(할머니가 고개를 갸웃한다) 아까부터 이상했어. 이번엔 안 따를래."
    if stopped:
        return "…듣고 보니 이상하네. 그래, 같이 확인해 보자. (할머니가 전화를 끊는다.)"
    if key == "scold":
        return "너까지 소리 지르니까 더 무섭다… 아무한테도 말하지 말랬는데."
    if key == "snatch":
        return "왜 남의 폰을 함부로 만져! 할머니가 알아서 해."
    if key == "watch":
        return "(할머니가 휴대전화를 귀에 댄 채 고개를 끄덕인다.)"
    if game["belief"] > 45:
        return "너는 몰라도 돼. 수사관이 진짜 같았어."
    return "그래도… 진짜 수사관 같던데. 조금만 더 생각해 볼게."


TYPED_KEYS = ("reason", "together")  # 직접 말을 써서 하는 선택지(나머지는 버튼만)
QUALITY_POWER = {2: 1.8, 1: 1.0, 0: 0.4}  # 쓴 말이 단서에 딱 맞을수록 더 잘 통해요
# AI 대답이 없거나 이상할 때 쓰는, 점수에 맞는 할머니 대답
SCORE_REPLY = {
    2: "듣고 보니 네 말이 맞는 것 같구나. 그렇게 해 보자.",
    1: "그런가… 그래도 혹시 진짜면 어쩌나 싶어.",
    0: "무슨 말인지 잘 모르겠다. 수사관이 급하다던데…",
}


def grade_words(event, key, text):
    """내가 쓴 말이 이 연락의 단서와 맞는지 AI(Gemini)가 0~2점으로 채점해요.
    AI에 연결할 수 없으면 단서 속 낱말이 얼마나 들어 있는지로 대신 채점해요.
    돌려주는 값: (점수, 할머니 반응 한 문장, 짧은 피드백)"""
    import json as _json
    import re as _re

    goal = "어디가 수상한지 짚어 주기" if key == "reason" else "공식 경로로 어떻게 함께 확인할지 말하기"
    facts = "\n".join(event["clues"]) + "\n안전한 확인 방법: " + event["route"]
    try:
        from google import genai
        from google.genai import types

        api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if not api_key:
            raise RuntimeError("no_key")
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=20000))
        prompt = (
            "피싱 예방 교육 게임이에요. 손주가 사기 연락을 받은 할머니를 설득하려고 말을 했어요.\n"
            f"[손주가 해야 할 일] {goal}\n[연락 내용] {' / '.join(event['lines'] + event.get('call_lines', []))}\n"
            f"[단서와 사실] {facts}\n[손주가 한 말] {text}\n\n"
            "손주의 말이 단서에 맞고 구체적이면 2, 맞지만 막연하면 1, 단서와 관계없거나 틀리면 0점이에요. "
            "다그치거나 무시하는 말투면 1점을 넘지 않아요.\n"
            "[할머니 반응 규칙] 할머니는 사기 연락을 받고 겁먹은 상태이고, 아직 아무것도 직접 확인하지 않았어요. "
            "손주가 한 말을 듣고 하는 대답 한 문장이에요. 점수가 2면 마음이 움직여 손주 말을 따라 보려 하고, "
            "1이면 반신반의하며 망설이고, 0이면 여전히 사기범 말이 더 걱정돼요. "
            "손주의 말을 되묻거나 반박하는 이상한 말, 확인했다는 말, 새로운 사실은 넣지 마요. "
            "할머니가 손주에게 하는 자연스러운 반말로, 25자 안팎으로 짧게 써요.\n"
            'JSON 한 줄로만 답해요: {"score":0~2,"reply":"할머니 대답 한 문장",'
            '"feedback":"손주에게 주는 한 문장 피드백(해요체)"}'
        )
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=300, response_mime_type="application/json"),
        )
        data = _json.loads(_re.search(r"\{.*\}", response.text or "", _re.S).group(0))
        score = max(0, min(2, int(data.get("score", 0))))
        reply = str(data.get("reply", "")).strip().strip('"“”')[:60]
        return score, reply or SCORE_REPLY[score], str(data.get("feedback", ""))[:160]
    except Exception:
        # 대신 채점: 단서·확인 방법에 나오는 2글자 이상 낱말이 내 말에 몇 개 들어 있는지
        words = {w for w in _re.findall(r"[가-힣A-Za-z0-9]{2,}", facts + " " + event.get(key, "")) if len(w) >= 2}
        hit = sum(1 for w in words if w in text)
        score = 2 if hit >= 3 else 1 if hit >= 1 else 0
        feedback = {2: "단서를 잘 짚어서 말했어요.", 1: "방향은 맞지만 조금 더 구체적으로 말하면 좋아요.",
                    0: "단서와 관계있는 내용을 넣어 말해 보세요."}[score]
        return score, SCORE_REPLY[score], feedback + " (AI 연결이 어려워 낱말로 채점했어요)"


DOUBT_WORDS = ("사기", "피싱", "수상", "의심", "이상", "가짜", "확인", "속", "조심", "차단", "신고")


def read_real_words(event, text):
    """진짜 연락에 내가 쓴 말이 '의심하는 말'인지 '괜찮다고 하는 말'인지 보고, 할머니 대답을 만들어요.
    돌려주는 값: (의심했는지, 할머니 대답 한 문장)"""
    import json as _json
    import re as _re

    try:
        from google import genai
        from google.genai import types

        api_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if not api_key:
            raise RuntimeError("no_key")
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=20000))
        prompt = (
            "피싱 예방 교육 게임이에요. 할머니가 받은 연락은 진짜(정상) 연락이에요.\n"
            f"[연락 내용] {' / '.join(event['lines'])}\n[할머니가 한 말] {event['grandma']}\n[손주가 한 말] {text}\n\n"
            "손주가 이 연락을 의심하거나 확인·차단하자고 하면 doubt=true, 정상이라고 하거나 맞장구치면 doubt=false예요. "
            "reply는 손주 말에 대한 할머니의 자연스러운 대답 한 문장(손주에게 하는 반말, 25자 안팎)이에요. "
            "손주 말을 그대로 받아서 대답하고, 걱정한 적 없는 일을 걱정했다고 하거나 새 사실을 지어내지 마요.\n"
            'JSON 한 줄로만 답해요: {"doubt":true/false,"reply":"할머니 대답"}'
        )
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=200, response_mime_type="application/json"),
        )
        data = _json.loads(_re.search(r"\{.*\}", response.text or "", _re.S).group(0))
        doubt = bool(data.get("doubt"))
        reply = str(data.get("reply", "")).strip().strip('"“”')[:60]
        return doubt, reply or (REAL_REPLY["doubt"] if doubt else REAL_REPLY["fine"])
    except Exception:
        doubt = any(w in text for w in DOUBT_WORDS)
        return doubt, REAL_REPLY["doubt"] if doubt else REAL_REPLY["fine"]


REAL_REPLY = {
    "fine": "그렇지? 할머니도 그렇게 생각했어.",
    "doubt": "이건 늘 오던 연락이야. 너무 걱정 말렴.",
}


def start_typing(key):
    st.session_state[KEY]["typing"] = key


def stop_typing():
    st.session_state[KEY].pop("typing", None)


def act(key, typed=None, quality=None, reply="", feedback="", real_fine=False):
    game = st.session_state[KEY]
    game.pop("typing", None)
    if game["result"]:
        return  # 결과 화면이 열리는 중에 남아 있던 버튼을 또 눌러도 기록이 늘지 않게 해요.
    # '이전 화면으로'를 누르면 되돌아갈 수 있게, 고르기 전 상태를 저장해 둬요.
    game.setdefault("history", []).append(copy.deepcopy({k: v for k, v in game.items() if k != "history"}))
    step = game["step"]
    event = EVENTS[step]
    approach = APPROACHES[key]
    real = event["real"]

    over = False
    if real and real_fine:
        # 진짜 연락에 '괜찮다'고 내 말로 말했어요: 의심한 게 아니니 할머니 마음이 상하지 않아요.
        stopped = False
        lesson = "진짜 연락을 알아보고 차분하게 말했어요. 진짜 연락은 이렇게 넘기면 충분해요."
    elif real:
        game["trust"] = clamp(game["trust"] + approach["real_trust"])
        stopped = False
        if key == "together":
            # 진짜 연락을 '함께 확인'하는 건 한 번까지 괜찮아요. 두 번째부터는 할머니가 지쳐요.
            over = any(EVENTS[r["step"]]["real"] and r["key"] == "together" for r in game["log"])
            if over:
                game["trust"] = clamp(game["trust"] - 10)
            lesson = REAL_LESSON["over" if over else "together"]
        elif key in DOUBT_KEYS:
            lesson = REAL_LESSON["doubt"]
        else:
            lesson = ""
    else:
        # 나를 믿는 정도가 높을수록 같은 말도 더 잘 통합니다.
        effect = approach["base"] * game["trust"] / START_TRUST
        # 단서를 보고 말하면 근거가 있어서 1.5배 더 잘 통하고, 안 보고 말하면 덜 통해요.
        persuade = key in ("together", "reason", "parent") and quality is None
        if quality is not None:
            effect *= QUALITY_POWER[quality]  # 직접 쓴 말은 AI 채점 점수로 효과가 정해져요
        elif persuade and game["clue_open"]:
            effect *= 1.5
        elif persuade:
            effect *= 0.7
        effect = round(effect)
        if key == "police":
            effect = 100
        game["belief"] = clamp(game["belief"] - effect)
        game["trust"] = clamp(game["trust"] + approach["trust"])
        if approach.get("counter"):
            game["counter"] = True
        stopped = game["belief"] <= STOP_LINE
        lesson = approach.get("lesson", "")
        if persuade and game["clue_open"]:
            lesson = "🔎 단서를 보고 근거를 들어 말해서 더 잘 통했어요. " + lesson
        elif persuade:
            lesson = "🔎 단서를 보지 않고 말해서 근거가 약했어요. 할머니가 덜 믿었어요. " + lesson
        if quality is not None:
            lesson = f"✍️ 내 말 점수 {quality}/2 · {feedback} " + approach.get("lesson", "")

    if typed:
        said = typed
    elif key == "reason" and not real:
        said = event["reason"]
    elif key == "together" and not real:
        said = event["together"]
    else:
        said = approach["label"]

    game["log"].append(
        {
            "step": step,
            "key": key,
            "said": said,
            "checked": game["clue_open"],
            "stopped": stopped,
            "over": over,
            "typed": bool(typed),          # 내가 직접 쓴 말인지
            "quality": quality,            # AI 채점 점수(0~2, 진짜 연락은 None)
            "feedback": feedback,          # AI 피드백 한 문장
            "fine": real_fine,             # 진짜 연락에 괜찮다고 말했는지
            "reaction": reply if (reply and not stopped) else grandma_reaction(key, game, stopped, real),
            "lesson": lesson,
            "belief": game["belief"],
            "trust": game["trust"],
        }
    )

    if stopped:
        game["alert"] = True
        game["fresh_stop"] = True

    if event.get("final"):
        game["result"] = "protected" if (stopped or key == "police") else "sent"
        game["fresh_end"] = True
    else:
        game["step"] = step + 1
        game["clue_open"] = False
        game["show_reaction"] = True  # 다음 화면에서 할머니 반응을 화면 가운데 큰 창으로 먼저 보여 줘요.
    dd.scroll_top()  # 다음 연락은 휴대전화 화면(위쪽)부터 보이게 해요.


# ─────────────────────────────────────
# 판단 기록
# ─────────────────────────────────────

def judged_right(record):
    """진짜 연락은 차분히 넘기고, 피싱에는 끼어들었는지 봅니다."""
    real = EVENTS[record["step"]]["real"]
    if real:
        return (record["key"] == "watch" or record.get("fine")
                or (record["key"] == "together" and not record.get("over")))
    return record["key"] != "watch"


def judgment_text(record):
    event = EVENTS[record["step"]]
    key = record["key"]
    if event["real"]:
        if key == "watch":
            return "✅ 진짜 연락을 차분히 넘겼어요."
        if record.get("fine"):
            return "✅ 진짜 연락임을 알아보고 차분하게 말했어요."
        if key == "together" and record.get("over"):
            return "⚠️ 진짜 연락까지 또 ‘같이 확인하자’고 했어요. 할머니가 지치기 시작했어요."
        if key == "together":
            return "🙂 진짜 연락을 함께 확인했어요. 이 정도는 괜찮아요."
        return "⚠️ 진짜 연락을 의심하거나 막았어요."
    if key == "watch":
        if record["stopped"]:
            return "🙂 지켜보기만 했지만, 할머니가 스스로 알아챘어요."
        return "⚠️ 피싱을 지켜보기만 했어요."
    if record["stopped"]:
        return "✅ 피싱에 끼어들어 할머니가 멈췄어요."
    return "🟡 끼어들었지만 할머니는 아직 흔들리고 있었어요."


def decide_ending(game):
    log = game["log"]
    if game["result"] == "sent":
        return "bad"
    stops = [record for record in log if record["stopped"]]
    first = stops[0] if stops else log[-1]
    if EVENTS[first["step"]].get("final"):
        return "close"
    doubted = sum(1 for r in log if EVENTS[r["step"]]["real"] and r["key"] in DOUBT_KEYS)
    # 진짜 연락까지 매번 '함께 확인'하면 할머니가 지쳐요. 한 번까지는 괜찮아요.
    over_checked = sum(1 for r in log if EVENTS[r["step"]]["real"] and r["key"] == "together")
    early = scam_stage(first["step"]) <= 2
    if early and game["trust"] >= START_TRUST and doubted == 0 and over_checked <= 1:
        return "best"
    return "good"


def make_report(game, title):
    log = game["log"]
    right = sum(judged_right(r) for r in log)
    lines = [
        "잠깐! · 할머니 폰 지키기 결과",
        "교육용 가상 상황의 결과이며, 수치는 실제 확률이 아닙니다.",
        "",
        f"결말: {title}",
        f"판단이 맞은 연락: {right} / {len(log)}",
        f"마지막 신뢰: {game['trust']}",
        "",
    ]
    for record in log:
        event = EVENTS[record["step"]]
        lines.extend(
            [
                f"{event['time']} · {event['sender']} ({'진짜 연락' if event['real'] else '피싱 · ' + event['stage']})",
                f"   단서 확인: {'했음' if record['checked'] else '하지 않음'}",
                f"   내 행동: {record['said']}",
                f"   할머니: {record['reaction']}",
                f"   판단: {judgment_text(record)}",
                f"   확인 방법: {event['route']}",
                f"   가상 확인 결과: {event['result']}",
                "",
            ]
        )
    return "\n".join(lines)


# ─────────────────────────────────────
# 화면 조각
# ─────────────────────────────────────

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


# 통화 목소리 연출: 수사관이 말하는 연락이면 '전화 받아서 듣기' 버튼이 생겨요(교육용 가상 대사).
# 이 말이 나오면 경고를 띄워요. 왜 수상한지는 플레이어가 직접 판단하도록 이유는 적지 않아요.
VOICE_WARN = ("가족에게도 알리시면 안", "체포영장", "안전계좌", "등록금’이라고 하세요", "10분 안에")


def show_voice_call(event, step):
    said = []
    if event["kind"] == "call":
        said += event["lines"]
    said += event.get("call_lines", [])
    said += [t for t in event["lines"] if event["kind"] != "call" and t.startswith("(수사관)")]
    if not said:
        return
    from voice_ui import call_button
    lines = []
    for text in said:
        text = text.replace("(수사관)", "").strip()
        warn = "⚠️ 방금 그 말, 수상하지 않나요?" if any(w in text for w in VOICE_WARN) else ""
        lines.append(["수사관", text, warn])
    number, _, shown = event["sender"].partition(" (")
    call_button({"name": shown.rstrip(")") or number, "number": number if shown else "", "avatar": "🕴️", "danger": True,
                 "lines": lines, "pitch": {"수사관": [0.9, 1.05]}, "gender": {"수사관": "m"}, "status": "통화 중",
                 "verdict": "📵 통화가 끝났어요. 할머니께 어떻게 말할지 골라 보세요."},
                "할머니 폰에 걸려 온 전화 받아서 듣기", key=f"gp_call_{step}")


def clue_block(game, event):
    """단서 버튼·단서 상자. 휴대폰 바로 아래에 두고, 상태 게이지는 두 영역 아래에 가로로 배치해요."""
    if game["clue_open"]:
        with st.container(border=True):
            st.markdown("**🔎 눈에 보이는 단서**")
            st.markdown("\n".join(f"- {clue}" for clue in event["clues"]))
            st.caption("단서는 사실만 보여 줘요. 진짜인지 피싱인지는 직접 판단하세요.")
    else:
        # 판단 전에 꼭 눌러 보면 좋은 버튼이라 크고 눈에 띄게 보여 줘요.
        st.markdown(
            """<style>.st-key-gp_clue button {background:#FFF4D6 !important;border:2px solid #E2A93B !important;
            min-height:56px !important;box-shadow:0 3px 10px rgba(226,169,59,.25);}
            .st-key-gp_clue button p {font-size:1.12rem !important;font-weight:900 !important;color:#7A4B00 !important;}</style>""",
            unsafe_allow_html=True,
        )
        st.button("🔎 단서 살펴보기 (판단 전에 눌러 보세요)", on_click=open_clues, key="gp_clue", width="stretch")
        st.caption("단서를 보고 말하면 설득이 1.5배 더 잘 통해요. ‘수상한 점을 하나 짚어 준다’는 단서를 봐야 고를 수 있어요.")


def show_gauges(game):
    stage = scam_stage(game["step"])
    gauges = st.columns(3)
    with gauges[0]:
        st.markdown(f"**😟 사기범을 믿는 정도 {game['belief']}**")
        st.progress(game["belief"] / 100)
    with gauges[1]:
        st.markdown(f"**💛 할머니가 나를 믿는 정도 {game['trust']}**")
        st.progress(game["trust"] / 100)
    with gauges[2]:
        st.markdown(f"**💸 송금까지 {stage} / {TOTAL_STAGES}단계**" + (" · ⚠️ 지금이 송금 직전이에요!" if stage == TOTAL_STAGES else ""))
        st.progress(stage / TOTAL_STAGES)
    st.caption(f"😟가 {STOP_LINE} 이하가 되면 할머니가 스스로 멈춰요.")


def show_last_feedback(game):
    if not game["log"]:
        return
    last = game["log"][-1]
    if last["stopped"]:
        fresh = game.pop("fresh_stop", False)
        go = " go" if fresh else ""
        if fresh:
            scroll_top()  # 선택 버튼은 아래에 있어서, 멈춘 순간을 보도록 위로 올려 줘요.
        st.markdown(
            f'<div class="zz-card win{go}" style="background:linear-gradient(135deg,#DCFCE7,#FEF3C7);'
            'border-radius:20px;padding:16px 18px;margin:4px 0 12px;text-align:center;">'
            '<div style="font-size:1.15rem;font-weight:800;color:#14532D;word-break:keep-all;line-height:1.7;">'
            "🛑 할머니가 방금 연락을 멈췄어요! "
            "하지만 사기범은 쉽게 포기하지 않아요. 다음 연락도 잘 살펴봐요.</div>"
            '<span class="zz-stamp ok">멈춤 성공!</span>'
            + sparks(["✨", "💛", "⭐", "✨", "🛑", "⭐", "💛", "✨"])
            + "</div>",
            unsafe_allow_html=True,
        )
    if not last["lesson"]:
        return
    if last["key"] in ("scold", "snatch") or last.get("over") or (
        EVENTS[last["step"]]["real"] and last["key"] in DOUBT_KEYS
    ):
        st.warning(f"💬 {last['lesson']}")
    else:
        st.info(f"💬 {last['lesson']}")


def show_intro():
    show_hero(f"📱 가족 지키기 게임 · 연락 {len(EVENTS)}개", "할머니 휴대폰을 지켜라",
              "", tone="pink")
    show_mascot("grandma", "모르겠으면 잠깐 멈추고, 할머니와 함께 확인해요.")
    st.button("👵 할머니 댁 들어가기", type="primary", on_click=start_game, key="grandma_start_top", width="stretch")
    st.markdown("#### 🎯 미션: 할머니의 돈을 지켜라")
    show_tiles([
        ("🔀", "진짜와 피싱이 섞여 있어요", "무엇이 피싱인지 직접 판단해요."),
        ("🔎", "단서 살펴보기", "정답 대신 사실을 보여 줘요. 단서를 짚으면 설득이 더 잘 통해요."),
        ("🗣️", "어떻게 말할지가 중요", "지켜볼지, 끼어들지, 어떻게 말할지 골라요."),
        ("✍️", "내 말로 직접 설득하기", "내 말로 쓰면 AI가 0~2점으로 채점해요. 잘 맞을수록 더 잘 통해요."),
        ("💔", "다그치면 안 통해요", "다그치거나 진짜 연락까지 막으면 할머니가 나를 덜 믿어요."),
        ("🔁", "사기범은 다시 와요", "마지막 송금까지 지켜 내야 해요."),
    ])
    st.markdown("#### 📊 게이지 읽는 법")
    show_tiles([
        ("😟", "사기범을 믿는 정도", "피싱 연락이 올 때마다 올라가요. 설득하면 내려가요."),
        ("💛", "할머니가 나를 믿는 정도", "높을수록 같은 말도 더 잘 통해요."),
        ("💸", "송금까지", "4단계는 송금 직전! 일찍 멈출수록 좋은 결말이 나와요."),
    ])
    st.button("👵 할머니 댁 들어가기", type="primary", on_click=start_game, width="stretch")


def grandma_mood(last, game):
    """방금 상황에 맞는 할머니 표정(grandma_face의 이름)과 마음 상태 한마디, 글자색을 골라요."""
    real = EVENTS[last["step"]]["real"]
    key, belief, trust = last["key"], last["belief"], last["trust"]
    if last["stopped"]:
        return ("grateful", "고마워하며 안심했어요", "#15803D") if trust >= 70 else ("relieved", "한숨 돌렸어요", "#15803D")
    if key == "police":
        return "shocked", "깜짝 놀랐어요", "#B42318"
    if key == "scold":
        return ("hurt", "서운하고 겁이 났어요", "#B42318") if trust < 50 else ("angry", "꾸중 들은 것 같아 화났어요", "#B42318")
    if key == "snatch":
        return "huffy", "무시당한 것 같아 언짢아요", "#B42318"
    if real:
        if last.get("fine"):
            return "calm", "맞장구에 마음이 편해요", "#0F766E"
        if last.get("over"):
            return "tired", "자꾸 확인하자니 지쳤어요", "#8A5A00"
        if key in DOUBT_KEYS:
            return "annoyed", "괜한 의심에 불편해요", "#8A5A00"
        return "calm", "평소처럼 편안해요", "#0F766E"
    if trust < 40:
        return "down", "내 말을 잘 안 믿으려 해요", "#8A5A00"
    if belief > 70:
        return "terrified", "사기범 말에 완전히 겁먹었어요", "#B42318"
    if belief > 45:
        return "anxious", "불안해서 사기범 말을 믿고 있어요", "#B42318"
    if belief > STOP_LINE:
        return "puzzled", "긴가민가 흔들리고 있어요", "#8A5A00"
    return "neutral", "조금 이상하다고 느끼기 시작했어요", "#0F766E"


@st.dialog("👵 할머니 반응", width="large")
def reaction_popup(game):
    """방금 내 말·행동에 할머니가 어떻게 반응했는지 화면 가운데 큰 창으로 보여 줘요."""
    last = game["log"][-1]
    mood, feeling, color = grandma_mood(last, game)
    st.markdown(
        f'<div style="display:flex;justify-content:center;">{face_svg(mood, 230)}</div>'
        f'<div style="text-align:center;font-weight:900;color:{color};font-size:1.05rem;margin-top:2px;">{esc(feeling)}</div>'
        f'<div style="background:#FFF7ED;border:2px solid #FED7AA;border-radius:18px;padding:16px 18px;margin:8px 0 10px;'
        f'font-size:1.35rem;font-weight:800;color:#172B3A;line-height:1.6;word-break:keep-all;text-align:center;">'
        f'“{esc(last["reaction"])}”</div>'
        f'<div style="color:#52616B;font-weight:700;text-align:center;">🙋 내가 한 말 · {esc(last["said"])}</div>',
        unsafe_allow_html=True,
    )
    if last["stopped"]:
        st.success("🛑 할머니가 연락을 멈췄어요! 하지만 사기범은 다시 연락할 수 있어요.")
    elif last["lesson"]:
        (st.warning if (last["key"] in ("scold", "snatch") or last.get("over")) else st.info)(f"💬 {last['lesson']}")
    if st.button("다음 연락 보기 ▶", type="primary", width="stretch", key="gp_reaction_ok"):
        st.rerun()


def show_play(game):
    if game.pop("show_reaction", False) and game["log"]:
        reaction_popup(game)
    enter_event(game)
    step = game["step"]
    event = EVENTS[step]

    # 게임 중에도 바로 전 화면(앞 연락, 첫 연락이면 게임 설명)으로 돌아갈 수 있어요.
    top_left, top_right = st.columns([3, 1.3], vertical_alignment="center")
    top_left.caption(f"연락 {step + 1} / {len(EVENTS)}")
    top_right.button("← 이전 화면으로", on_click=go_back, key="gp_quit", width="stretch",
                     help="앞 연락을 고르기 전으로 돌아가요. 첫 연락이면 게임 설명 화면으로 가요.")
    show_last_feedback(game)

    phone_col, side_col = st.columns([1.1, 1], vertical_alignment="center")
    with phone_col:
        st.markdown(phone_html(step), unsafe_allow_html=True)
        show_voice_call(event, step)
    with side_col:
        log = game["log"]
        prev = log[-1]["reaction"] if log else None
        belief = game["belief"]
        # 오른쪽 얼굴은 '지금 하는 말'(새 연락을 받은 할머니)에 맞춰요. 내 행동에 대한 반응은 큰 창에서 보여 줘요.
        if event["real"]:
            current = "calm"
        elif belief > 70:
            current = "terrified"
        elif belief > 45:
            current = "anxious"
        elif belief > STOP_LINE:
            current = "puzzled"
        else:
            current = "neutral"
        now = event["grandma_alert"] if (game["alert"] and not event["real"]) else event["grandma"]
        bubble = f'<div class="say prev">{esc(prev)}</div>' if prev else ""
        from pathlib import Path as _P
        if (_P(__file__).resolve().parent.parent / "static" / "scene_grandma.jpg").exists():
            # 할머니 댁 거실 그림 속 소파에 할머니가 앉아 있고, 표정이 상황에 따라 바뀌어요.
            # 사기범을 믿는 정도가 높을수록 화면이 붉게 물들어 긴장감을 보여 줘요.
            tint = "rgba(220,38,38,.22)" if (not event["real"] and belief > 70) else ("rgba(245,158,11,.16)" if (not event["real"] and belief > 45) else "rgba(0,0,0,0)")
            st.markdown(
                "<style>.gp-room{position:relative;border-radius:18px;overflow:hidden;border:3px solid #E2C98A;aspect-ratio:754/314;"
                "background:url(app/static/scene_grandma.jpg) center/cover;box-shadow:0 4px 12px rgba(60,40,10,.15)}"
                ".gp-room .tint{position:absolute;inset:0;transition:background .6s}"
                ".gp-room .gm{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:27%;filter:drop-shadow(0 4px 4px rgba(0,0,0,.25))}"
                ".gp-room .gm img,.gp-room .gm svg{width:100%!important;height:auto!important;margin:0!important;border-radius:50%!important;border:4px solid #fff!important;box-shadow:0 0 0 3px #F2B6C6!important;aspect-ratio:1;object-fit:cover}"
                ".gp-room .ph{position:absolute;left:62%;top:58%;font-size:clamp(1.2rem,3vw,2rem);animation:gp-buzz .6s ease-in-out infinite}"
                "@keyframes gp-buzz{0%,100%{transform:rotate(0)}25%{transform:rotate(-12deg)}75%{transform:rotate(12deg)}}"
                ".gp-room .tag{position:absolute;left:10px;bottom:8px;background:rgba(255,253,240,.95);border:2px solid #C9A86A;border-radius:999px;padding:2px 10px;font-weight:900;color:#5B3A12;font-size:.85rem}</style>"
                f'<div class="gp-room"><div class="tint" style="background:{tint}"></div><div class="gm">{face_svg(current, 160)}</div>'
                + ('<span class="ph">📱</span>' if not event["real"] else "")
                + '<span class="tag">🏡 할머니 댁 거실</span></div>'
                f'<div class="gp-grandma" style="margin-top:8px">{bubble}<div class="say">{esc(now)}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            mood = face_svg(current, 130)
            st.markdown(
                f'<div class="gp-grandma"><div class="face">{mood}</div>'
                f"{bubble}"
                f'<div class="say">{esc(now)}</div></div>',
                unsafe_allow_html=True,
            )
        clue_block(game, event)
    show_gauges(game)

    st.markdown(f"#### {event['time']} · 새 연락이 왔어요. 어떻게 할까요?")
    options = list(FINAL_OPTIONS if event.get("final") else NORMAL_OPTIONS)
    # 선택지 순서를 연락마다 섞어서 '몇 번째만 누르면 되는' 요령이 생기지 않게 해요.
    random.Random(f"grandma-{step}").shuffle(options)
    typing = game.get("typing")
    if typing:
        show_typing_box(game, event, typing)
        return
    # '직접 말하기' 선택지는 내 말로 써서 설득하는 핵심 선택지라 초록 테두리·배지로 눈에 띄게 해요.
    st.markdown(
        """<style>
        [class*="st-key-gp_typed_"] button p::before{content:"✍️ 직접 말하기";display:inline-block;background:linear-gradient(135deg,#16A34A,#22C55E);color:#fff;border-radius:999px;
        padding:3px 12px;margin-right:8px;font-size:.92rem;font-weight:900;vertical-align:1px;box-shadow:0 2px 0 #15803D;animation:gp-badge 1.6s ease-in-out infinite}
        @keyframes gp-badge{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
        [class*="st-key-gp_typed_"] button:disabled p::before{background:#94A3B8;box-shadow:none;animation:none}</style>""",
        unsafe_allow_html=True,
    )
    for key in options:
        # 수상한 점은 단서를 봐야 알 수 있으니, 단서를 보기 전에는 이 선택지를 잠가 둬요.
        locked = key == "reason" and not game["clue_open"]
        typed = key in TYPED_KEYS
        with st.container(key=f"gp_typed_{step}_{key}" if typed else None):
            st.button(
                APPROACHES[key]["label"] + (" · 🔒 단서를 먼저 보세요" if locked else ""),
                key=f"gp3_btn_{step}_{key}",
                on_click=start_typing if typed else act,
                args=(key,),
                disabled=locked,
                use_container_width=True,
            )


def show_typing_box(game, event, key):
    """수상한 점 짚기·함께 확인하기는 단서를 보고 내 말로 직접 써요. AI가 단서와 맞는지 채점해요."""
    guide = ("단서를 보고 **어디가 수상한지** 할머니께 말해 보세요. 예: “검찰은 앱 설치를 시키지 않아요.”"
             if key == "reason" else
             "할머니를 안심시키고 **어디로, 어떻게 함께 확인할지** 말해 보세요. 예: “같이 은행 앱에서 직접 확인해 봐요.”")
    with st.container(border=True):
        st.markdown(f"**{APPROACHES[key]['label']}**")
        st.markdown(guide)
        st.caption("🔒 실제 이름·전화번호·계좌번호 같은 개인정보는 쓰지 마세요. 쓴 문장은 채점을 위해 AI(Gemini)로 보내져요.")
        with st.form(f"gp_type_{game['step']}_{key}"):
            text = st.text_area("할머니께 할 말", max_chars=120, height=90, placeholder="여기에 내 말로 써 보세요")
            send, cancel = st.columns([2, 1])
            ok = send.form_submit_button("👵 할머니께 말하기", type="primary", width="stretch")
            back = cancel.form_submit_button("다른 방법 고르기", width="stretch")
    if back:
        stop_typing()
        st.rerun()
    if ok:
        text = text.strip()
        if len(text) < 5:
            st.warning("조금 더 구체적으로 써 주세요.")
        elif __import__("re").search(r"\d{6,}", text.replace("-", "").replace(" ", "")):
            st.warning("🔒 긴 숫자는 개인정보일 수 있어서 보내지 않았어요. 숫자 없이 써 주세요.")
        else:
            if event["real"]:
                quality, feedback = None, ""  # 진짜 연락은 점수 대신, 의심했는지만 봐요
                with st.spinner("할머니가 듣고 있어요…"):
                    doubt, reply = read_real_words(event, text)
                act(key, typed=text, reply=reply, real_fine=not doubt)
                st.rerun()
            else:
                with st.spinner("할머니가 듣고 있어요…"):
                    quality, reply, feedback = grade_words(event, key, text)
            act(key, typed=text, quality=quality, reply=reply, feedback=feedback)
            st.rerun()


def show_ending(game):
    log = game["log"]
    ending = decide_ending(game)
    title, story, color = ENDINGS[ending]
    trust = game["trust"]

    fresh = game.pop("fresh_end", False)
    if fresh:
        # 결말만 이름 없이 숫자로 통계에 더해요.
        dd.record("grandma", {"plays": 1, f"end_{ending}": 1})
        dd.note_mine("grandma", f"결말: {title}")
        dd.stamp("01")
        if ending == "best":
            dd.achieve("grandma_best")  # 업적: 최고 결말
        scroll_top()
        drumroll((("🥁", "두구두구…"), ("📱", "할머니 휴대전화를 확인하는 중…"), ("👵", "그날 오전의 결말은?")))
    stamp = {
        "best": '<span class="zz-stamp ok">송금 차단!</span>' + sparks(["🛡️", "✨", "⭐", "💛", "🎉", "✨", "🛡️", "⭐", "🎉", "✨", "💫", "💛"]),
        "good": '<span class="zz-stamp ok">송금 차단!</span>' + sparks(["🛡️", "✨", "⭐", "💛", "✨", "⭐", "💫", "✨"]),
        "close": '<span class="zz-stamp">아슬아슬 차단</span>',
        "bad": '<span class="zz-stamp miss">송금 완료…</span>',
    }[ending]
    mood = "lose" if ending == "bad" else "win"
    st.markdown(
        f'<div class="gp-ending zz-card {mood}{" go" if fresh else ""}" style="background:{color};text-align:center;">'
        f'<div class="t">{esc(title)}</div><div style="text-align:left;">{esc(story)}</div>{stamp}</div>',
        unsafe_allow_html=True,
    )
    # 결말에 맞는 깡지: 돈을 지켰으면 금고를 끌어안은 깡지, 송금됐으면 할머니와 서로 위로하는 깡지
    show_mascot("sad" if ending == "bad" else "safe",
                "괜찮아요. 다음엔 더 일찍, 다정하게 같이 확인해 봐요." if ending == "bad" else "할머니의 돈을 지켜 냈어요! 함께 확인한 덕분이에요.", width=140)
    data = dd.stats("grandma")
    plays = data.get("plays", 0)
    if plays:
        dd.show_others([
            f"지금까지 <b>{plays}번</b>의 도전 중 <b>{dd.pct(data.get(f'end_{ending}', 0), plays)}%</b>가 ‘{esc(title)}’ 결말을 봤어요.",
            "결말 분포 · " + " · ".join(f"{esc(ENDINGS[k][0])} {dd.pct(data.get(f'end_{k}', 0), plays)}%" for k in ENDINGS),
        ])
    if ending != "bad" and trust < 40:
        st.warning("💔 막기는 했지만 할머니 마음이 많이 상했어요. 다그치거나 몰래 막은 일이 있었는지 아래 기록에서 확인해 보세요.")

    right = sum(judged_right(r) for r in log)
    checked = sum(1 for r in log if r["checked"])
    harsh = sum(1 for r in log if r["key"] in ("scold", "snatch"))
    # 결과 숫자를 색깔 카드로 크게 보여 줘요.
    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:6px 0 4px;">'
        + "".join(
            f'<div style="background:{bg};border:2px solid {line};border-radius:16px;padding:10px 12px;text-align:center;">'
            f'<div style="font-weight:800;color:#3E4A46;font-size:.92rem;">{esc(label)}</div>'
            f'<div style="font-size:1.7rem;font-weight:900;color:{ink};">{esc(value)}</div></div>'
            for label, value, bg, line, ink in [
                ("✅ 판단이 맞은 연락", f"{right} / {len(log)}", "#EAF6F0", "#9ED3BC", "#0F766E"),
                ("🔎 단서를 살펴본 연락", f"{checked}번", "#FFFBE6", "#F1DFA6", "#8A5A00"),
                ("💛 마지막 신뢰", str(trust), "#FDF0F5", "#F2C3D6", "#A3305F"),
                ("😠 다그치거나 몰래 막음", f"{harsh}번", "#FDECEC", "#F6CACA", "#B42318"),
            ]
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption("학습 기록이며 실제 대응 능력이나 피해 확률을 나타내지 않아요.")
    if fresh:
        st.session_state["grandma_hall"] = dd.save_hall(
            "grandma", {"right": right, "trust": trust},
            lambda old, new: (new["right"], new["trust"]) > (old.get("right", 0), old.get("trust", 0)),
        )
    dd.show_hall_note(st.session_state.get("grandma_hall"))

    # 내가 직접 쓴 말을 한곳에 모아, 점수·피드백과 '이렇게도 말할 수 있어요' 예시를 함께 보여 줘요.
    typed_logs = [r for r in log if r.get("typed")]
    if typed_logs:
        st.subheader("✍️ 내가 직접 쓴 말 돌아보기")
        scored = [r["quality"] for r in typed_logs if r.get("quality") is not None]
        if scored:
            st.caption(f"피싱 연락에서 직접 쓴 말 {len(scored)}개 · 평균 {sum(scored) / len(scored):.1f}점 / 2점")
        for r in typed_logs:
            event = EVENTS[r["step"]]
            with st.container(border=True):
                kind = "💡 수상한 점 짚기" if r["key"] == "reason" else "🤝 함께 확인하자고 하기"
                st.markdown(f"**{event['time']} · {esc(event['sender'])}** — {kind}")
                st.markdown(f"🙋 **내가 쓴 말:** “{esc(r['said'])}”")
                if r.get("quality") is None and r.get("fine"):
                    st.caption("✅ 진짜 연락임을 알아보고 차분하게 말했어요. 진짜 연락은 이렇게 넘기면 충분해요.")
                elif r.get("quality") is None:
                    st.caption("진짜 연락인데 의심하는 말을 했어요. 진짜 연락은 지켜보기만 해도 충분해요.")
                else:
                    star = "⭐" * r["quality"] + "☆" * (2 - r["quality"])
                    st.markdown(f"**점수 {star} ({r['quality']}/2)** · {esc(r.get('feedback') or '')}")
                    example = event.get(r["key"])
                    if example:
                        st.markdown(f"💬 **이렇게도 말할 수 있어요:** “{esc(example)}”")

    st.subheader("📋 그날 오전의 기록")
    st.caption("게임 중에는 알려 주지 않았던, 각 연락이 진짜였는지 피싱이었는지와 확인 방법을 공개해요.")
    for record in log:
        event = EVENTS[record["step"]]
        label = "✅ 진짜 연락" if event["real"] else f"🚨 피싱 · {event['stage']}"
        with st.expander(f"{event['time']} · {event['sender']} — {label}"):
            st.write("**연락 내용:**", " / ".join(event["lines"] + event.get("call_lines", [])))
            st.write("**내가 한 말·행동:**", record["said"])
            st.write("**할머니 반응:**", record["reaction"])
            st.write("**내 판단:**", judgment_text(record))
            if record["lesson"]:
                st.write("**돌아보기:**", record["lesson"])
            st.write("**이렇게 확인할 수 있어요:**", event["route"])
            st.write("**가상 확인 결과:**", event["result"])
            if not record["checked"]:
                st.caption("이 연락은 단서를 살펴보지 않고 선택했어요.")
            st.caption(f"이후 상태 · 사기범을 믿는 정도 {record['belief']} · 나를 믿는 정도 {record['trust']}")

    st.markdown("#### 주변 사람이 속고 있을 때, 이렇게 도와요")
    st.markdown(
        "1. **다그치지 말고 먼저 안심시키기** — “놀라셨죠, 잘못한 거 아니에요.” 겁먹은 사람은 꾸중을 들으면 더 숨어요.\n"
        "2. **근거는 짧고 분명하게** — “검찰은 전화로 돈을 옮기라고 하지 않아요.” 한 가지면 충분해요.\n"
        "3. **함께 확인하기** — 상대가 준 번호가 아니라 공식 대표번호·은행 창구로 ‘같이’ 확인해요. 판단은 본인이 하게 도와요.\n"
        "4. **진짜 연락은 막지 않기** — 모든 연락을 의심하면 정작 중요한 순간에 내 말을 믿지 않아요.\n"
        "5. **한 번 막아도 끝이 아니에요** — 사기범은 번호를 바꿔 다시 연락해요. 계속 곁에서 함께 확인해요.\n"
        "6. **급하면 바로 신고** — 송금 직전·직후라면 112, 은행 지급정지, 금융감독원(1332)에 알리고 다른 가족과 함께해요."
    )

    # 긴 글 파일 대신, 결말·숫자·기억할 점 3줄을 담은 결과 카드(사진)로 내려받아요.
    tips = []
    if harsh:
        tips.append("다그치거나 몰래 막기보다 먼저 안심시켜 드리기")
    if checked < len(log):
        tips.append("답하기 전에 🔎 단서부터 살펴보기")
    if right < len(log):
        tips.append("진짜 연락은 막지 않고, 피싱만 골라 함께 확인하기")
    for tip in ("상대가 준 번호 말고 공식 대표번호로 함께 확인하기", "근거는 짧고 분명하게 한 가지만 말하기",
                "급하면 112·은행 지급정지에 바로 알리기"):
        if len(tips) < 3:
            tips.append(tip)
    icon, _, name = title.partition(" ")
    me = dd.citizen()
    st.markdown("#### 🖼️ 나의 결과 카드")
    show_result_card(
        {
            "color": {"best": "#0F766E", "good": "#15803D", "close": "#C2410C", "bad": "#6B7280"}[ending],
            "place": "할머니 댁", "game": "할머니 폰 지키기", "emoji": icon or "👵", "title": name or title,
            "subtitle": {"best": "송금 차단!", "good": "송금 차단!", "close": "아슬아슬 차단", "bad": "송금 완료…"}[ending],
            "stats": [("판단이 맞은 연락", f"{right} / {len(log)}"), ("단서를 살펴본 연락", f"{checked}번"),
                      ("💛 마지막 신뢰", str(trust)), ("다그치거나 몰래 막음", f"{harsh}번")],
            "sections": [("💡 다음에 기억할 점", tips[:3])],
            "nickname": me["nickname"] if me else "",
            "mascot": "retry" if ending == "bad" else "trophy",
        },
        "jamkkan_grandma_card.png",
    )
    show_mascot("retry", "다른 선택도 연습해 볼까요?", width=100)
    st.button("🔄 다른 방법으로 다시 도전", type="primary", on_click=back_to_intro, width="stretch")


# ─────────────────────────────────────
# 화면
# ─────────────────────────────────────

with intro("01", suffix=""):
    st.title("✋ 잠깐! · 할머니 폰 지키기")
    from mascot_ui import show_scene
    import scene_ui
    if scene_ui.ready("scene_grandma"):
        # 시작 화면: 소파의 할머니, 울리는 휴대폰, 차례로 도착하는 연락 알림
        st.markdown(scene_ui.grandma_cover(face_svg("neutral", 160)), unsafe_allow_html=True)
    show_key_question("내가 아니라 **옆에 있는 가족이 속고 있을 때**, 어떻게 말하고 언제 끼어들어야 할까요?", "🤔")

if KEY not in st.session_state:
    st.session_state[KEY] = new_game()

game = st.session_state[KEY]

if not game["started"]:
    show_intro()
elif game["result"]:
    show_ending(game)
else:
    show_play(game)
