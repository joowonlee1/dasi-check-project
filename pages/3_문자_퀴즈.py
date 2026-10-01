import html
import re
import time

import streamlit as st
from firebase_support import user, result_panel


# 모든 인물, 번호, 기록, 연락 결과는 교육용 가상 자료입니다.
# 번호는 실제로 쓰이지 않도록 지어낸 가상 번호입니다.
MOM = "01031570924"
AUNT = "01066201148"
DAD = "01072290356"
SCAM = "01066201184"  # 저장된 이모 번호와 끝 두 자리만 뒤바뀐 번호

# 게임 속 시계: 09:00 기준 분 단위. 행동할 때마다 흐릅니다.
START_CLOCK = 13
TRUE_ENDING_LIMIT = 45  # 09:45 안에 탈출하면 트루 엔딩 조건 충족
TIME_LIMIT_MINUTES = 30  # 실제 제한 시간(분). 이 숫자만 바꾸면 제한 시간이 바뀝니다.
COST = {"visit": 1, "collect": 1, "wrong": 2, "hint": 3, "dial": 2, "scam": 5, "bad_number": 1}

EVIDENCE = {
    "call": {
        "title": "E01 · 09:10 통화 기록",
        "kind": "call",
        "name": "엄마",
        "number": "010-3157-0924",
        "time": "09:10 · 통화 2분 14초",
        "lines": [
            "민서야. 나 엄마야. 우리 강아지 보리 알지? 오늘 10시에 도서관 가기로 했잖아.",
            "나 지금 급한 일이 생겼어. 다른 가족한테는 절대 연락하지 마. 내가 보내는 안내부터 봐.",
        ],
        "note": "통화 화면의 이름과 번호는 저장된 엄마 연락처와 똑같이 표시됐습니다.",
    },
    "message": {
        "title": "E02 · 09:12 후속 문자",
        "kind": "sms",
        "sender": "010-6620-1184",
        "saved": False,
        "time": "09:12",
        "lines": [
            "아까 전화한 엄마야. 엄마 폰 고장 나서 이모 폰 빌렸어.",
            "확인은 이 번호로만 해. 여기서 알려주는 앱 깔면 돼. 다른 사람한테 말하면 일 커져.",
        ],
        "link": "가상의 설치 링크 · 눌러도 실행되지 않음",
        "note": "저장되지 않은 번호입니다.",
    },
    "parcel": {
        "title": "E03 · 09:05 택배 알림 문자",
        "kind": "sms",
        "sender": "1588-○○○○",
        "saved": False,
        "time": "09:05",
        "lines": ["[택배] 주소지 불일치로 보관 중입니다. 아래에서 주소를 수정해 주세요."],
        "link": "가상의 주소 수정 링크 · 눌러도 실행되지 않음",
        "note": "주문 내역 앱에는 배송 중인 택배가 없습니다.",
    },
    "notice": {
        "title": "E04 · 09:00 도서관 알림",
        "kind": "notice",
        "app": "도서관",
        "icon": "📚",
        "time": "09:00",
        "text": "대출 도서의 반납 예정일은 내일입니다. 대출 내역은 도서관 앱에서 확인하세요.",
        "note": "링크·결제·앱 설치 요청 없음",
    },
    "contacts": {
        "title": "E05 · 휴대전화 연락처 목록",
        "kind": "contacts",
        "rows": [
            ("엄마", "010-3157-0924", "1년 전 저장"),
            ("이모", "010-6620-1148", "3년 전 저장"),
            ("아빠", "010-7229-0356", "메모: 이번 주 해외 출장"),
        ],
    },
    "sns_pet": {
        "title": "E06 · 엄마의 SNS 게시물",
        "kind": "sns",
        "author": "민서맘",
        "scope": "🌐 전체 공개",
        "time": "사건 전날 18:00",
        "image": "🐕 🚶‍♀️ 🌳",
        "text": "민서와 보리의 산책! 보리가 가족이 된 지 3년 🐾",
        "reactions": "♥ 24 · 💬 3",
    },
    "sns_plan": {
        "title": "E07 · 엄마의 SNS 일정 글",
        "kind": "sns",
        "author": "민서맘",
        "scope": "🌐 전체 공개",
        "time": "사건 전날 20:00 · 수정 기록 없음",
        "image": "📚 🏛️",
        "text": "내일 오전 10시, 민서랑 도서관에 가기로!",
        "reactions": "♥ 11 · 💬 1",
    },
    "blog": {
        "title": "E08 · 2년 전 가족 블로그 글",
        "kind": "sns",
        "author": "민서네 이야기",
        "scope": "🌐 전체 공개",
        "time": "2년 전 14:00",
        "image": "🏫 🎒",
        "text": "우리 민서 중학교 입학! 교복이 아직 커요.",
        "reactions": "♥ 7 · 반려견 이야기 없음",
    },
    "family_chat": {
        "title": "E09 · 가족 단톡방 (PC 메신저)",
        "kind": "chat",
        "room": "우리 가족 (4)",
        "scope": "🔒 가족만",
        "lines": [
            ("엄마", "08:57", "도서관 말고 과학관 10:30으로 바꿨어! 달력에도 바꿔 놨어."),
            ("엄마", "08:58", "보리는 오늘 이모네 맡길게."),
        ],
        "note": "안 읽음 1 · 민서는 아직 이 메시지를 읽지 않았습니다.",
    },
    "calendar": {
        "title": "E10 · 가족 달력 수정 기록",
        "kind": "calendar",
        "day": "오늘",
        "old": "10:00 도서관",
        "new": "10:30 과학관",
        "edited": "엄마가 08:55에 수정",
        "note": "공유 범위: 가족만 · 일정은 계획이며 실제 방문 여부를 증명하지 않습니다.",
    },
    "photo": {
        "title": "E11 · 디지털 액자 사진 정보",
        "kind": "frame",
        "big_time": "09:03",
        "image": "👩 🐕 🛋️",
        "caption": "엄마가 집 거실에서 보리와 함께 있는 사진",
        "info": [("원본 촬영", "사건 전날 19:40"), ("액자로 전송", "오늘 09:03")],
    },
    "memo": {
        "title": "E12 · 냉장고에 붙어 있던 가족 약속",
        "kind": "sticky",
        "lines": [
            "급한 연락일수록, 받은 연락 속 새 번호로 확인하지 않기.",
            "휴대전화에 원래 저장돼 있던 번호로 직접 걸어서 확인하기.",
            "연락이 안 되면 바로 결론 내리지 말고, 다른 가족에게 확인하기.",
        ],
    },
    "no_answer": {
        "title": "E13 · 저장된 엄마 번호로 건 결과",
        "kind": "dial",
        "name": "엄마",
        "number": "010-3157-0924",
        "status": "응답 없음",
        "lines": [],
        "note": "전화가 연결되지 않았습니다. 응답이 없는 이유는 확인되지 않았습니다.",
    },
    "dad_off": {
        "title": "E14 · 저장된 아빠 번호로 건 결과",
        "kind": "dial",
        "name": "아빠",
        "number": "010-7229-0356",
        "status": "전원 꺼짐",
        "lines": [],
        "note": "“전원이 꺼져 있어 음성사서함으로 연결됩니다.” 출장 중 비행기 안일 수 있습니다.",
    },
    "new_contact": {
        "title": "E15 · 문자 속 새 번호로 건 결과",
        "kind": "dial",
        "name": "저장되지 않은 번호",
        "number": "010-6620-1184",
        "status": "통화 0분 31초",
        "lines": [("상대", "어, 민서야. 이모야. 엄마 옆에 있어. 지금 바빠서 통화는 못 하니까 문자로 보낸 앱부터 설치해.")],
        "note": "최초 연락 상대가 알려 준 번호입니다. 목소리를 확인할 기회는 주지 않고 같은 요구만 반복했습니다.",
    },
    "aunt": {
        "title": "E16 · 저장된 이모 번호로 건 결과",
        "kind": "dial",
        "name": "이모",
        "number": "010-6620-1148",
        "status": "통화 3분 02초",
        "lines": [
            ("이모", "민서야? 나 엄마랑 같이 과학관 주차장이야. 바꿔 줄게."),
            ("엄마", "09:10에 전화한 적 없어. 폰도 멀쩡해. 앱 깔라는 문자도 내가 보낸 게 아니야."),
            ("이모", "내 번호는 바뀐 적 없어."),
        ],
        "note": "평소 저장된 번호로 연결된 독립 확인입니다. 이 게임에서는 이 결과를 검증된 사실로 제공합니다.",
    },
}

PLACES = {
    "📱 휴대전화": ["call", "message", "parcel", "notice", "contacts"],
    "💻 노트북": ["sns_pet", "sns_plan", "blog", "family_chat"],
    "📅 달력": ["calendar"],
    "🖼️ 사진 액자": ["photo"],
    "🗄️ 잠긴 서랍": [],
    "🚪 출입문": [],
}

# 상대가 보내는 압박 메시지와, 엔딩에서 해설할 수법
PRESSURE = [
    (16, "왜 답 안 해? 새 번호로 확인했어?", "재촉 · 생각할 시간 빼앗기"),
    (21, "다른 가족한테 말하면 엄마 진짜 곤란해져. 엄마만 믿어.", "고립 · 확인 경로 끊기"),
    (27, "앱 설치 아직이야? 10분 안에 안 하면 오늘 해결 못 해.", "긴급성 · 마감 시간 만들기"),
    (33, "엄마 지금 큰일 났어. 너 때문에 더 늦어지고 있어.", "공포·죄책감 · 감정 흔들기"),
    (40, "마지막이야. 지금 안 하면 나중에 엄마 원망하지 마.", "최후통첩 · 압박 극대화"),
]
SCAM_REPLY = (0, "그래, 그 번호 맞아. 이모가 확인해 줬지? 이제 앱만 깔면 돼.", "신뢰 확인 흉내 · 스스로 만든 확인 경로")

HINTS = {
    1: [
        "통화에서 상대가 말한 정보가 어디에 공개돼 있었는지 노트북을 살펴보세요.",
        "‘전체 공개’와 ‘가족만’은 다릅니다. 누구나 볼 수 있는 자료만 출처가 될 수 있어요.",
        "보리는 E06, 10시 도서관은 E07에 있어요. 상대는 08:55 이후 가족끼리만 바꾼 일정을 몰랐어요.",
    ],
    2: [
        "네 사건의 시각은 휴대전화, 달력, 사진 액자에 흩어져 있어요. 액자 화면의 큰 숫자를 그대로 믿지 마세요.",
        "사진은 ‘찍힌 시각’과 ‘액자로 보낸 시각’이 따로 있어요. 원본 촬영은 전날이에요.",
        "순서는 원본 촬영(19:40) → 달력 수정(08:55) → 액자 전송(09:03) → 통화(09:10)예요. 위치는 아직 확정할 수 없어요.",
    ],
    3: [
        "냉장고 가족 약속(E12)을 다시 읽고, 서랍 속 확인 장치에서 어떤 번호로 걸어야 할지 생각해 보세요.",
        "문자 속 번호와 저장된 이모 번호를 한 자리씩 비교해 보세요. 독립 확인은 원래 저장된 번호로만 가능해요.",
        "핵심 증거는 최초 통화(E01), 후속 문자(E02), 저장된 이모 번호로 확인한 결과(E16)예요. 차단할 번호는 문자 발신 번호예요.",
    ],
}


st.markdown(
    """
    <style>
    .ev-wrap {max-width: 400px; margin: 6px 0 10px;}
    .phone {background:#0B1220; border-radius:30px; padding:10px 12px 14px; border:3px solid #2B3645;
            box-shadow:0 8px 22px rgba(15,23,42,.25); color:#E5ECF4;}
    .phone .status {display:flex; justify-content:space-between; font-size:.72rem; color:#AAB7C6;
                    padding:2px 10px 8px; font-variant-numeric:tabular-nums;}
    .phone .notch {width:90px; height:6px; background:#2B3645; border-radius:6px; margin:0 auto 6px;}
    .call-top {text-align:center; padding:6px 0 10px;}
    .avatar {width:58px; height:58px; border-radius:50%; background:linear-gradient(135deg,#F59E0B,#EF4444);
             color:#fff; font-weight:900; font-size:1.5rem; display:flex; align-items:center;
             justify-content:center; margin:0 auto 6px;}
    .avatar.gray {background:#475569;}
    .avatar.small {width:34px; height:34px; font-size:.95rem; margin:0;}
    .call-name {font-size:1.35rem; font-weight:800; color:#fff;}
    .call-sub {font-size:.8rem; color:#9FB0C3;}
    .say {background:#1E293B; border-radius:14px 14px 14px 4px; padding:8px 12px; margin:6px 30px 6px 0;
          font-size:.93rem; line-height:1.55; color:#F1F5F9;}
    .say .who {display:block; font-size:.72rem; color:#93C5FD; font-weight:700; margin-bottom:2px;}
    .call-btns {display:flex; justify-content:center; gap:34px; margin-top:12px;}
    .call-btns span {width:42px; height:42px; border-radius:50%; display:flex; align-items:center;
                     justify-content:center; font-size:1.1rem;}
    .end {background:#DC2626;} .mute {background:#334155;}
    .sms-head {display:flex; align-items:center; gap:8px; border-bottom:1px solid #1E293B; padding:0 4px 8px;}
    .sms-head b {font-size:.95rem; color:#fff;}
    .warn-tag {font-size:.68rem; background:#7F1D1D; color:#FECACA; border-radius:6px; padding:1px 6px;}
    .bubble {background:#E5E7EB; color:#111827; border-radius:16px 16px 16px 4px; padding:9px 12px;
             margin:8px 40px 4px 4px; font-size:.93rem; line-height:1.55;}
    .linkpill {display:inline-block; margin:2px 0 0 4px; background:#1D4ED8; color:#DBEAFE; border-radius:10px;
               padding:6px 10px; font-size:.8rem; opacity:.75; cursor:not-allowed;}
    .stamp {font-size:.7rem; color:#7C8BA0; margin:2px 6px;}
    .phone-note {margin-top:10px; font-size:.76rem; color:#94A3B8; border-top:1px dashed #334155; padding-top:8px;}
    .noti {background:rgba(255,255,255,.08); border-radius:16px; padding:10px 12px; display:flex; gap:10px;}
    .noti .ic {font-size:1.4rem;} .noti .t {font-size:.75rem; color:#AAB7C6;} .noti .x {font-size:.92rem; color:#F8FAFC;}
    .contact {display:flex; align-items:center; gap:10px; padding:8px 4px; border-bottom:1px solid #1E293B;}
    .contact .n {font-weight:700; color:#fff;} .contact .p {font-size:.85rem; color:#CBD5E1; letter-spacing:.04em;
                 font-variant-numeric:tabular-nums;} .contact .m {font-size:.72rem; color:#7C8BA0;}
    .post {background:#fff; border:1px solid #DDE3EA; border-radius:16px; overflow:hidden; color:#172B3A;}
    .post-head {display:flex; align-items:center; gap:10px; padding:10px 12px;}
    .post-head .n {font-weight:800;} .post-head .s {font-size:.75rem; color:#64748B;}
    .post-img {height:120px; background:linear-gradient(135deg,#FDE68A,#A7F3D0); display:flex; align-items:center;
               justify-content:center; font-size:2.6rem; letter-spacing:.3em;}
    .post-body {padding:10px 12px 4px; font-size:.95rem;}
    .post-foot {padding:4px 12px 10px; font-size:.78rem; color:#64748B;}
    .chatwin {background:#B2C7D9; border-radius:14px; overflow:hidden; color:#111;}
    .chat-title {background:#9FB6CB; padding:8px 12px; font-weight:800; display:flex; justify-content:space-between;}
    .chat-title span {font-weight:600; font-size:.78rem;}
    .chat-row {display:flex; gap:8px; padding:8px 12px 0; align-items:flex-start;}
    .chat-row .nm {font-size:.75rem; color:#334155;}
    .chat-bub {background:#fff; border-radius:4px 14px 14px 14px; padding:7px 11px; font-size:.92rem; max-width:240px;}
    .chat-time {font-size:.68rem; color:#475569; align-self:flex-end;}
    .chat-unread {padding:8px 12px 10px; font-size:.75rem; color:#B45309; font-weight:700;}
    .cal {background:#fff; border:1px solid #DDE3EA; border-radius:16px; overflow:hidden; color:#172B3A;}
    .cal-head {background:#0F766E; color:#fff; padding:8px 12px; font-weight:800;}
    .cal-ev {margin:10px 12px; padding:8px 10px; border-left:4px solid #94A3B8; background:#F1F5F9; border-radius:6px;}
    .cal-ev.old {text-decoration:line-through; color:#94A3B8;}
    .cal-ev.new {border-left-color:#0F766E; background:#ECFDF5; font-weight:700;}
    .cal-foot {font-size:.75rem; color:#64748B; padding:0 12px 10px;}
    .frame {background:#3F2A1D; padding:12px; border-radius:10px; box-shadow:inset 0 0 0 3px #7C5A3A;}
    .frame-pic {position:relative; height:160px; background:linear-gradient(160deg,#FCD34D,#FB923C 60%,#7C2D12);
                display:flex; align-items:center; justify-content:center; font-size:3rem; letter-spacing:.25em;}
    .frame-time {position:absolute; right:10px; bottom:6px; color:#fff; font-size:2rem; font-weight:900;
                 text-shadow:0 2px 6px rgba(0,0,0,.6); font-variant-numeric:tabular-nums; letter-spacing:0;}
    .frame-cap {color:#E7D5C3; font-size:.8rem; margin-top:8px;}
    .meta-table {cursor:pointer; padding:6px 0 0; background:#fff; border:1px solid #DDE3EA; border-radius:10px; margin-top:8px; font-size:.82rem; color:#172B3A;}
    .meta-table summary {padding:4px 10px; font-weight:700;} .meta-table div {display:flex; justify-content:space-between; padding:6px 10px; border-bottom:1px solid #EEF2F6;}
    .sticky {background:#FEF08A; color:#3F3A12; padding:16px 18px 12px; transform:rotate(-1.2deg);
             box-shadow:0 6px 14px rgba(0,0,0,.15); font-size:.95rem; line-height:1.7;}
    .sticky .pin {text-align:center; margin-top:-10px; font-size:1.2rem;}
    .lock-banner {background:#1F2937; color:#F9FAFB; border-radius:14px; padding:10px 14px; margin:6px 0 10px;}
    .lock-banner .from {color:#FCA5A5; font-weight:700; font-size:.85rem;}
    .lock-banner .text {font-size:1rem;}
    .clock {font-variant-numeric:tabular-nums; font-weight:900; font-size:1.6rem; color:#B91C1C;}
    </style>
    """,
    unsafe_allow_html=True,
)


def digits(text):
    return re.sub(r"\D", "", text or "")


def clock_text(minutes):
    hour, minute = divmod(minutes, 60)
    return f"{9 + hour:02d}:{minute:02d}"


def spend(kind):
    game["clock"] += COST[kind]


def fresh_game():
    """게임 데이터와 퍼즐 입력값을 초기화합니다."""
    for key in list(st.session_state):
        if key.startswith("escape_"):
            del st.session_state[key]

    st.session_state["escape_game"] = {
        "started": time.time(),
        "evidence": [],
        "unlocked": 0,
        "mistakes": 0,
        "hints": {1: 0, 2: 0, 3: 0},
        "place": "📱 휴대전화",
        "visited": ["📱 휴대전화"],
        "clock": START_CLOCK,
        "scam_dialed_at": None,
        "dialed": [],
        "feedback": None,
        "finished": None,
        "finished_clock": None,
        "rank_uid": user()["uid"] if user() else None,
        "rank_nickname": user()["nickname"] if user() else None,
        "rank_status": None,
    }


def save_evidence(evidence_id):
    if evidence_id not in game["evidence"]:
        game["evidence"].append(evidence_id)


def esc(text):
    return html.escape(str(text))


def phone_shell(inner):
    clock = clock_text(game["clock"]) if "escape_game" in st.session_state else "09:13"
    return (
        '<div class="ev-wrap"><div class="phone">'
        '<div class="notch"></div>'
        f'<div class="status"><span>{clock}</span><span>📶 LTE 🔋 64%</span></div>'
        f"{inner}</div></div>"
    )


def evidence_html(item):
    kind = item["kind"]

    if kind == "call":
        lines = "".join(f'<div class="say"><span class="who">상대</span>{esc(t)}</div>' for t in item["lines"])
        inner = (
            '<div class="call-top">'
            f'<div class="avatar">{esc(item["name"][0])}</div>'
            f'<div class="call-name">{esc(item["name"])}</div>'
            f'<div class="call-sub">휴대전화 {esc(item["number"])}</div>'
            f'<div class="call-sub">{esc(item["time"])}</div>'
            "</div>"
            f"{lines}"
            '<div class="call-btns"><span class="mute">🔇</span><span class="end">📞</span><span class="mute">🔊</span></div>'
            f'<div class="phone-note">{esc(item["note"])}</div>'
        )
        return phone_shell(inner)

    if kind == "sms":
        tag = "" if item["saved"] else '<span class="warn-tag">저장되지 않은 번호</span>'
        bubbles = "".join(f'<div class="bubble">{esc(t)}</div>' for t in item["lines"])
        inner = (
            '<div class="sms-head"><div class="avatar small gray">?</div>'
            f'<b>{esc(item["sender"])}</b>{tag}</div>'
            f"{bubbles}"
            f'<div class="linkpill">🔗 {esc(item["link"])}</div>'
            f'<div class="stamp">{esc(item["time"])}</div>'
            f'<div class="phone-note">{esc(item["note"])}</div>'
        )
        return phone_shell(inner)

    if kind == "notice":
        inner = (
            f'<div class="noti"><div class="ic">{item["icon"]}</div><div>'
            f'<div class="t">{esc(item["app"])} · {esc(item["time"])}</div>'
            f'<div class="x">{esc(item["text"])}</div></div></div>'
            f'<div class="phone-note">{esc(item["note"])}</div>'
        )
        return phone_shell(inner)

    if kind == "contacts":
        rows = "".join(
            '<div class="contact">'
            f'<div class="avatar small">{esc(name[0])}</div>'
            f'<div><div class="n">{esc(name)}</div><div class="p">{esc(number)}</div>'
            f'<div class="m">{esc(memo)}</div></div></div>'
            for name, number, memo in item["rows"]
        )
        return phone_shell(f'<div class="sms-head"><b>👥 연락처</b></div>{rows}')

    if kind == "dial":
        lines = "".join(
            f'<div class="say"><span class="who">{esc(who)}</span>{esc(t)}</div>' for who, t in item["lines"]
        )
        gray = " gray" if item["name"].startswith("저장되지") else ""
        inner = (
            '<div class="call-top">'
            f'<div class="avatar{gray}">{esc(item["name"][0])}</div>'
            f'<div class="call-name">{esc(item["name"])}</div>'
            f'<div class="call-sub">{esc(item["number"])} · 발신</div>'
            f'<div class="call-sub">{esc(item["status"])}</div>'
            "</div>"
            f"{lines}"
            f'<div class="phone-note">{esc(item["note"])}</div>'
        )
        return phone_shell(inner)

    if kind == "sns":
        return (
            '<div class="ev-wrap"><div class="post">'
            f'<div class="post-head"><div class="avatar small">{esc(item["author"][0])}</div>'
            f'<div><div class="n">{esc(item["author"])}</div>'
            f'<div class="s">{esc(item["scope"])} · {esc(item["time"])}</div></div></div>'
            f'<div class="post-img">{item["image"]}</div>'
            f'<div class="post-body">{esc(item["text"])}</div>'
            f'<div class="post-foot">{esc(item["reactions"])}</div>'
            "</div></div>"
        )

    if kind == "chat":
        rows = "".join(
            f'<div class="chat-row"><div class="avatar small">{esc(who[0])}</div>'
            f'<div><div class="nm">{esc(who)}</div><div class="chat-bub">{esc(t)}</div></div>'
            f'<div class="chat-time">{esc(at)}</div></div>'
            for who, at, t in item["lines"]
        )
        return (
            '<div class="ev-wrap"><div class="chatwin">'
            f'<div class="chat-title">{esc(item["room"])}<span>{esc(item["scope"])}</span></div>'
            f"{rows}"
            f'<div class="chat-unread">{esc(item["note"])}</div>'
            "</div></div>"
        )

    if kind == "calendar":
        return (
            '<div class="ev-wrap"><div class="cal">'
            f'<div class="cal-head">📅 {esc(item["day"])}</div>'
            f'<div class="cal-ev old">{esc(item["old"])}</div>'
            f'<div class="cal-ev new">{esc(item["new"])}</div>'
            f'<div class="cal-foot">✏️ {esc(item["edited"])}</div>'
            f'<div class="cal-foot">{esc(item["note"])}</div>'
            "</div></div>"
        )

    if kind == "frame":
        return (
            '<div class="ev-wrap"><div class="frame">'
            f'<div class="frame-pic">{item["image"]}<div class="frame-time">{esc(item["big_time"])}</div></div>'
            f'<div class="frame-cap">{esc(item["caption"])}</div>'
            "</div>"
            '<details class="meta-table"><summary>🔍 사진 정보 더 보기</summary>'
            + "".join(f"<div><span>{esc(a)}</span><b>{esc(b)}</b></div>" for a, b in item["info"])
            + "</details></div>"
        )

    if kind == "sticky":
        lines = "<br>".join(f"{number}. {esc(t)}" for number, t in enumerate(item["lines"], 1))
        return (
            '<div class="ev-wrap"><div class="sticky"><div class="pin">📌</div>'
            f"<b>우리 가족 확인 약속</b><br>{lines}</div></div>"
        )

    return f"<p>{esc(item.get('body', ''))}</p>"


def render_evidence(evidence_id):
    st.markdown(evidence_html(EVIDENCE[evidence_id]), unsafe_allow_html=True)


def evidence_card(evidence_id):
    with st.container(border=True):
        st.markdown(f"**{EVIDENCE[evidence_id]['title']}**")
        render_evidence(evidence_id)

        if evidence_id in game["evidence"]:
            st.caption("✓ 증거 보관함에 저장됨")
        elif st.button("증거 보관함에 넣기 (+1분)", key=f"escape_collect_{evidence_id}"):
            save_evidence(evidence_id)
            spend("collect")
            st.rerun()


def evidence_name(evidence_id):
    return EVIDENCE[evidence_id]["title"]


def wrong(message):
    game["mistakes"] += 1
    spend("wrong")
    st.warning(message + " (게임 시계 +2분)")


def pressure_messages():
    shown = [item for item in PRESSURE if item[0] <= game["clock"]]
    if game["scam_dialed_at"] is not None:
        shown.append((game["scam_dialed_at"],) + SCAM_REPLY[1:])
        shown.sort(key=lambda item: item[0])
    return shown


def show_status_bar():
    left, right = st.columns([1, 3])
    with left:
        st.markdown(f'<div class="clock">{clock_text(game["clock"])}</div>', unsafe_allow_html=True)
        st.caption("게임 속 시각")
    with right:
        messages = pressure_messages()
        if messages:
            at, text, _ = messages[-1]
            st.markdown(
                '<div class="lock-banner">'
                f'<div class="from">🔒 잠금화면 알림 · 010-6620-1184 · {clock_text(at)}</div>'
                f'<div class="text">{html.escape(text)}</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("휴대전화가 조용합니다. 아직은.")


def hint_panel(stage):
    with st.expander("💡 막혔을 때 힌트 (힌트 하나당 게임 시계 +3분)"):
        used = game["hints"][stage]

        if used < len(HINTS[stage]):
            if st.button("힌트 하나 더 보기", key=f"escape_hint_{stage}"):
                game["hints"][stage] += 1
                spend("hint")
                st.rerun()

        for text in HINTS[stage][:game["hints"][stage]]:
            st.write(text)


def show_feedback():
    if game.get("feedback"):
        st.success(game["feedback"])
        game["feedback"] = None


def lock_one():
    st.subheader("🔒 잠금 1 · 상대는 어떻게 알고 있었을까?")
    st.write(
        "서랍에는 4자리 번호 자물쇠가 달려 있습니다. 자물쇠 옆 쪽지에는 이렇게 적혀 있어요."
    )
    st.info(
        "“통화에서 상대가 말한 **보리**와 **10시 도서관**. "
        "누구나 볼 수 있었던 출처를 찾아, 그 글이 작성된 시각의 ‘시’를 통화에 나온 순서대로 적어라.”"
    )

    with st.form("escape_source_form"):
        code = st.text_input("자물쇠 번호 (4자리)", max_chars=4, placeholder="예: 0000")
        unknown = st.radio(
            "그런데 상대가 몰랐던 것으로 보이는 정보가 하나 있습니다. 무엇일까요?",
            [
                "민서의 이름",
                "반려견 보리의 이름",
                "원래 도서관에 가기로 한 시각",
                "가족끼리만 공유한, 바뀐 오늘 일정",
            ],
            index=None,
        )
        submitted = st.form_submit_button("서랍 잠금 해제")

    if submitted:
        if len(digits(code)) != 4 or unknown is None:
            st.warning("번호 4자리와 판단을 모두 입력하세요.")
        elif digits(code) == "1820" and unknown.startswith("가족끼리만"):
            game["unlocked"] = 1
            game["feedback"] = (
                "🔓 서랍이 열렸습니다. 상대가 아는 정보는 모두 전체 공개 게시물에 있던 것이었고, "
                "08:55에 가족끼리 바꾼 일정은 몰랐습니다. 다만 이것만으로 사칭이 ‘확정’되지는 않아요. "
                "엄마가 깜빡했을 수도 있으니까요. 확인이 더 필요합니다."
            )
            st.rerun()
        elif digits(code) == "1820":
            wrong("번호는 맞았습니다. 상대가 통화에서 말한 일정과, 오늘 실제로 바뀐 일정을 비교해 보세요.")
        else:
            wrong("자물쇠가 꿈쩍하지 않습니다. 출처의 공개 범위를 다시 확인해 보세요.")

    hint_panel(1)


def lock_two():
    st.subheader("🔒 잠금 2 · 뒤섞인 시간")
    st.write("서랍 안 확인 장치에는 8자리 시간 자물쇠가 걸려 있습니다.")
    st.info(
        "“아래 네 사건을 **실제로 일어난 순서**대로 놓고, 각 시각의 ‘분’ 두 자리만 이어 붙여라.”\n\n"
        "· 수상한 통화가 걸려 옴 · 가족 달력의 일정이 수정됨 · 액자 속 사진이 처음 촬영됨 · 사진이 액자로 전송됨"
    )

    with st.form("escape_time_form"):
        code = st.text_input("시간 자물쇠 (8자리)", max_chars=8, placeholder="예: 00000000")
        location = st.radio(
            "그렇다면 09:10에 엄마는 어디에 있었다고 말할 수 있을까요?",
            [
                "액자에 09:03이 표시돼 있으므로 그 무렵 집에 있었다.",
                "달력이 과학관으로 바뀌었으므로 과학관에 있었다.",
                "통화 화면에 ‘엄마’가 떴으므로 엄마 휴대전화 근처에 있었다.",
                "사진은 과거 촬영본이고 일정은 계획이므로, 아직 확정할 수 없다.",
            ],
            index=None,
        )
        submitted = st.form_submit_button("확인 장치 잠금 해제")

    if submitted:
        if len(digits(code)) != 8 or location is None:
            st.warning("8자리 숫자와 판단을 모두 입력하세요.")
        elif digits(code) == "40550310" and location.startswith("사진은 과거"):
            game["unlocked"] = 2
            game["feedback"] = (
                "🔓 확인 장치가 켜졌습니다. 액자의 09:03은 ‘보낸’ 시각일 뿐 사진은 전날 찍혔고, "
                "달력은 계획일 뿐입니다. 통화 화면의 이름과 번호도 조작될 수 있어요(발신번호 변작). "
                "결국 위치를 알려면 직접 확인하는 수밖에 없습니다. 서랍을 조사해 보세요."
            )
            st.rerun()
        elif digits(code) == "40550310":
            wrong("순서는 맞았습니다. 그 증거가 ‘현재 위치’를 증명하는지, 아니면 과거나 계획일 뿐인지 생각해 보세요.")
        elif digits(code).startswith("03"):
            wrong("액자 화면의 큰 숫자가 사진이 찍힌 시각일까요?")
        else:
            wrong("시간 자물쇠가 열리지 않습니다. 각 시각이 ‘언제’의 시각인지 다시 확인하세요.")

    hint_panel(2)


def lock_three():
    st.subheader("🔒 잠금 3 · 출입문의 사건 보고서")
    st.write("출입문 화면에 사건 보고서 양식이 떠 있습니다. 모든 칸이 맞아야 문이 열립니다.")

    with st.form("escape_final_form"):
        conclusion = st.radio(
            "① 사건 판단",
            [
                "엄마 휴대전화가 해킹당했다고 확정할 수 있다.",
                "이모 번호가 바뀌었으므로 문자 속 번호도 믿을 수 있다.",
                "연락 내용이 실제 가족의 요청과 일치하지 않는다.",
                "엄마가 전화를 받지 않았으므로 위험에 처해 있다.",
            ],
            index=None,
        )
        proof = st.multiselect(
            "② 최초 요청과 독립 확인 결과를 대조할 핵심 증거 3개",
            game["evidence"],
            format_func=evidence_name,
        )
        block = st.text_input("③ 차단하고 신고할 번호 (숫자만)", max_chars=13)
        action = st.radio(
            "④ 지금 할 행동",
            [
                "문자 속 번호로 다시 전화해 정체를 따져 묻는다.",
                "앱은 설치하되, 권한 요청은 모두 거절한다.",
                "요구를 멈추고 확인된 가족 번호로 소통한 뒤, 112에 신고한다.",
                "문자를 지우고 아무 일 없었던 것처럼 넘어간다.",
            ],
            index=None,
        )
        submitted = st.form_submit_button("최종 잠금 해제", type="primary")

    if submitted:
        if conclusion is None or action is None or len(proof) != 3 or not digits(block):
            st.warning("네 칸을 모두 채우고 핵심 증거는 정확히 3개 선택하세요.")
        elif (
            conclusion.startswith("연락 내용이")
            and set(proof) == {"call", "message", "aunt"}
            and digits(block) == SCAM
            and action.startswith("요구를 멈추고")
        ):
            game["unlocked"] = 3
            game["finished"] = time.time()
            game["finished_clock"] = game["clock"]
            st.rerun()
        elif digits(block) == AUNT:
            wrong("그 번호는 1년 넘게 저장돼 있던 진짜 이모 번호입니다. 숫자를 한 자리씩 다시 비교해 보세요.")
        elif "aunt" not in proof:
            wrong("상대가 알려 주지 않은, 독립된 경로로 확인한 결과가 보고서에 들어가야 합니다.")
        else:
            wrong("보고서가 반려됐습니다. 최초 요청과 독립 확인 결과가 정확히 대조되는지 확인하세요.")

    hint_panel(3)


def show_dialer():
    st.subheader("📞 확인 장치 · 다이얼")
    st.caption("번호를 직접 입력해 전화를 겁니다. 한 번 걸 때마다 게임 시계가 흐릅니다. 모든 연결은 가상입니다.")

    with st.form("escape_dial_form", clear_on_submit=True):
        number = st.text_input("전화번호", max_chars=13, placeholder="010-0000-0000")
        dialed = st.form_submit_button("📞 전화 걸기")

    if dialed:
        number = digits(number)
        result = {MOM: "no_answer", DAD: "dad_off", AUNT: "aunt", SCAM: "new_contact"}.get(number)
        if result is None:
            spend("bad_number")
            st.warning("“지금 거신 번호는 없는 번호입니다.” (+1분)")
        else:
            if result == "new_contact" and game["scam_dialed_at"] is None:
                spend("scam")
                game["scam_dialed_at"] = game["clock"]
            else:
                spend("dial")
            save_evidence(result)
            if result not in game["dialed"]:
                game["dialed"].append(result)
            st.rerun()

    for evidence_id in game["dialed"]:
        with st.expander(EVIDENCE[evidence_id]["title"], expanded=evidence_id == game["dialed"][-1]):
            render_evidence(evidence_id)

    if game["scam_dialed_at"] is not None:
        st.error(
            "문자 속 번호로 건 순간, 상대는 당신이 흔들리고 있다는 걸 알게 됐습니다. "
            "상대가 알려 준 번호로는 상대의 말을 확인할 수 없어요."
        )


def show_drawer():
    if game["unlocked"] < 1:
        st.warning("서랍이 잠겨 있습니다. 4자리 번호 자물쇠가 달려 있어요. ‘잠금 해제’ 탭을 확인하세요.")
        return

    evidence_card("memo")

    if game["unlocked"] < 2:
        st.info("서랍 안쪽에 확인 장치가 보입니다. 8자리 시간 자물쇠로 잠겨 있어요.")
        return

    show_dialer()


def show_room():
    st.write("장소를 눌러 조사하세요. 처음 가는 곳은 게임 시계가 1분 흐릅니다. 모든 자료가 사건과 관련 있는 것은 아니에요.")

    places = list(PLACES)
    for start in (0, 3):
        columns = st.columns(3)
        for column, place in zip(columns, places[start:start + 3]):
            with column:
                if st.button(place, use_container_width=True, key=f"escape_place_{place}"):
                    game["place"] = place
                    if place not in game["visited"]:
                        game["visited"].append(place)
                        spend("visit")
                    st.rerun()

    st.divider()
    place = game["place"]
    st.subheader(place)

    if place == "🗄️ 잠긴 서랍":
        show_drawer()
    elif place == "🚪 출입문":
        st.write("출입문에는 세 개의 잠금이 있습니다.")
        st.write("공개 정보의 출처 → 시간의 의미 → 독립 확인")
        st.info("‘잠금 해제’ 탭에서 현재 퍼즐에 도전하세요.")
    else:
        for evidence_id in PLACES[place]:
            evidence_card(evidence_id)


def show_inventory():
    if not game["evidence"]:
        st.info("아직 수집한 증거가 없습니다.")
        return

    for evidence_id in game["evidence"]:
        with st.expander(evidence_name(evidence_id)):
            render_evidence(evidence_id)

    st.caption("모든 자료가 결정적 증거인 것은 아닙니다. 공개 범위·시각·확인 경로를 비교하세요.")


def ending():
    if game["scam_dialed_at"] is not None:
        return (
            "🟡 노멀 엔딩 · 흔들린 확인",
            "결국 진실에 도달했지만, 중간에 상대가 알려 준 번호로 전화를 걸었습니다. "
            "그 번호 너머의 사람은 ‘이모’인 척 같은 요구를 반복했을 뿐, 아무것도 확인해 주지 않았어요. "
            "실제 상황이었다면 상대는 당신이 의심하기 시작했다는 걸 알고 수법을 바꿨을 겁니다.",
        )
    if game["finished_clock"] <= TRUE_ENDING_LIMIT:
        return (
            "⭐ 트루 엔딩 · 번호보다 근거",
            "상대가 준 번호에는 한 번도 걸지 않고, 원래 저장된 번호로만 확인했습니다. "
            "압박 문자가 쏟아지는 동안에도 근거를 하나씩 쌓아 진실에 도착했어요.",
        )
    return (
        "🟢 굿 엔딩 · 늦었지만 정확한 확인",
        "올바른 경로로 확인했지만 시간이 꽤 걸렸습니다. 그 사이 상대는 계속 압박했죠. "
        "실제 상황에서는 ‘확인 먼저’를 바로 떠올릴 수 있도록, 가족끼리 확인 약속을 미리 정해 두세요.",
    )


def show_ending():
    seconds = max(0, int(game["finished"] - game["started"]))
    minutes, remaining = divmod(seconds, 60)
    hint_count = sum(game["hints"].values())
    title, story = ending()

    st.success("🚪 잠금 해제! 사건의 확인 경로를 완성했습니다.")
    st.subheader(title)
    st.write(story)

    first, second, third, fourth = st.columns(4)
    first.metric("탈출 시각", clock_text(game["finished_clock"]))
    second.metric("실제 경과", f"{minutes}분 {remaining}초")
    third.metric("힌트 사용", f"{hint_count}회")
    fourth.metric("퍼즐 재검토", f"{game['mistakes']}회")

    st.markdown("#### 상대가 쓴 압박 기술")
    st.caption("탈출하는 동안 잠금화면에 도착한 메시지예요. 각각 어떤 심리를 노렸는지 확인해 보세요.")
    seen = pressure_messages()
    for at, text, tactic in seen:
        st.markdown(f"- `{clock_text(at)}` “{text}” → **{tactic}**")
    if not seen:
        st.write("너무 빨리 탈출해서 상대가 압박할 틈도 없었어요!")

    st.markdown("#### 이번 사건에서 배운 것")
    lessons = [
        "1. 상대가 내 정보를 안다고 본인은 아니다. 공개된 게시물만으로도 알 수 있다.",
        "2. 사진의 촬영 시각과 전송 시각, 계획과 실제는 다르다.",
        "3. 통화 화면에 뜬 이름과 번호도 조작될 수 있다.",
        "4. 상대가 알려 준 번호로는 상대를 확인할 수 없다. 원래 저장된 번호로 직접 확인한다.",
        "5. ‘다른 가족에게 말하지 마’, ‘10분 안에’는 대표적인 압박 신호다.",
    ]
    st.markdown("\n".join(lessons))
    st.caption("시간과 실패 횟수로 능력을 평가하지 않습니다. 실제 경과 시간은 페이지를 떠난 동안도 포함됩니다.")

    report = (
        "잠깐! 피싱 방탈출 — 엄마의 번호, 두 개의 진실\n\n"
        f"엔딩: {title}\n"
        f"탈출 시각(게임 속): {clock_text(game['finished_clock'])}\n"
        f"실제 경과 시간: {minutes}분 {remaining}초\n"
        f"힌트 사용: {hint_count}회\n"
        f"퍼즐 재검토: {game['mistakes']}회\n\n"
        "[상대가 쓴 압박 기술]\n"
        + "\n".join(f"{clock_text(at)} {text} → {tactic}" for at, text, tactic in seen)
        + "\n\n[배운 것]\n"
        + "\n".join(lessons)
        + "\n\n교육용 가상 사건의 결과이며 실제 신원 확인을 보장하지 않는다."
    )

    result_panel(game)

    st.download_button(
        "탈출 기록 내려받기",
        data=report.encode("utf-8-sig"),
        file_name="jamkkan_escape_report.txt",
        mime="text/plain",
    )


def seconds_left():
    return TIME_LIMIT_MINUTES * 60 - (time.time() - game["started"])


def is_timed_out():
    return game["unlocked"] < 3 and seconds_left() <= 0


@st.fragment(run_every=1)
def countdown():
    """남은 실제 시간을 1초마다 갱신하고, 0이 되면 전체 화면을 다시 그려 실패 엔딩으로 넘깁니다."""
    current = st.session_state.get("escape_game")
    if not current or current["unlocked"] >= 3:
        return
    left = TIME_LIMIT_MINUTES * 60 - (time.time() - current["started"])
    if left <= 0:
        st.rerun(scope="app")
    minutes, seconds = divmod(int(left), 60)
    color = "#B91C1C" if left <= 300 else "#172B3A"
    note = " · 서두르세요!" if left <= 300 else ""
    st.markdown(
        f'<div style="text-align:right;font-weight:900;font-size:1.25rem;color:{color};'
        f'font-variant-numeric:tabular-nums;">⏳ 남은 시간 {minutes:02d}:{seconds:02d}{note}</div>',
        unsafe_allow_html=True,
    )


def show_failure():
    st.error(f"⏰ 제한 시간 {TIME_LIMIT_MINUTES}분이 지났습니다.")
    st.subheader("🔴 배드 엔딩 · 확인이 끝나기 전에")
    st.write(
        "확인을 마치기 전에 시간이 다 됐습니다. 실제 상황이었다면 상대는 그사이 쉬지 않고 재촉했을 거예요. "
        "사칭범이 ‘10분 안에’, ‘지금 당장’을 외치는 이유가 바로 이것입니다. 생각할 시간을 빼앗으면 확인을 건너뛰게 되니까요."
    )
    st.info(
        "그래도 기억할 것: 실제 상황에는 제한 시간이 없습니다. 상대가 아무리 재촉해도 "
        "요구를 멈추고, 원래 저장된 번호로 직접 확인하는 데 시간을 써도 괜찮아요."
    )

    first, second, third = st.columns(3)
    first.metric("해제한 잠금", f"{game['unlocked']} / 3")
    second.metric("수집한 증거", f"{len(game['evidence'])}개")
    third.metric("힌트 사용", f"{sum(game['hints'].values())}회")

    seen = pressure_messages()
    if seen:
        st.markdown("#### 그사이 도착한 압박 문자")
        for at, text, tactic in seen:
            st.markdown(f"- `{clock_text(at)}` “{text}” → **{tactic}**")

    st.button("다시 도전하기", type="primary", on_click=fresh_game)
    st.caption("실패한 기록은 공동 랭킹에 저장되지 않습니다.")


def show_game_guide():
    with st.expander("📖 처음 오셨나요? 게임 방법 보기", expanded="escape_game" not in st.session_state):
        st.markdown("### 당신은 이 연락의 진실을 확인할 조사자입니다")
        st.write(
            "09:10, 휴대전화에 ‘엄마’가 뜹니다. 상대는 나에 대해 잘 알고 있지만, 다른 가족에게 연락하지 말라고 해요. "
            "곧이어 낯선 번호로 앱을 설치하라는 문자가 옵니다. 방 안의 기록을 비교해 무엇을 믿을 수 있는지 판단하고, "
            "출입문의 세 잠금을 풀어 보세요."
        )
        st.markdown("### 이렇게 진행해요")
        st.markdown(
            "1. **방 조사** — 장소 버튼을 눌러 자료를 읽어요. 사건과 상관없는 자료도 섞여 있어요.\n"
            "2. **증거 수집** — 필요해 보이는 자료만 ‘증거 보관함에 넣기’를 눌러요. 마지막 보고서는 보관함에 넣은 증거로만 쓸 수 있어요.\n"
            "3. **잠금 해제** — 자물쇠 번호는 증거 속 숫자를 조합해서 만들어요. 번호와 판단이 모두 맞아야 열려요.\n"
            "4. **다시 조사** — 잠금을 풀면 서랍 안에 새로 조사할 것이 생겨요.\n"
            "5. **탈출 완료** — 엔딩과 상대가 쓴 압박 기술 해설을 확인하고 기록을 내려받아요."
        )
        st.markdown("### 제한 시간과 게임 속 시계")
        st.write(
            f"방에 들어간 순간부터 실제 시간 {TIME_LIMIT_MINUTES}분 안에 탈출해야 해요. 시간이 다 되면 실패 엔딩이에요. "
            "화면을 떠나 있어도 시간은 흐르니 주의하세요."
        )
        st.write(
            "그와 별개로 새 장소 조사(+1분), 증거 수집(+1분), 오답(+2분), 힌트(+3분), 전화(+2분)마다 "
            "게임 속 시각이 흐르고, 시간이 지날수록 상대의 압박 문자가 도착해요. "
            "09:45 전에, 올바른 경로로만 확인해서 탈출하면 트루 엔딩을 볼 수 있어요."
        )
        st.markdown("### 연습할까요, 기록을 공유할까요?")
        st.markdown(
            "- **혼자 연습:** 로그인 없이 바로 시작하고, 탈출 후 결과 파일을 받을 수 있어요.\n"
            "- **공동 랭킹 참여:** 왼쪽 ‘닉네임 입장’에서 공개에 동의한 뒤 새 게임을 시작하세요. 탈출하면 자동 저장을 시도해요.\n"
            "- **이미 연습 중이라면:** 입장 후 ‘게임 다시 시작’을 눌러 새 게임부터 랭킹에 참여하세요."
        )
        st.info("새로고침하거나 접속을 종료하면 진행 중인 게임이 사라질 수 있으니, 완료 후 결과를 다운로드해 주세요.")
        st.caption("랭킹은 힌트가 적은 순, 재검토가 적은 순이며 같으면 공동 순위예요. 정답을 빨리 맞히기보다 판단의 근거를 찾는 연습입니다.")


st.title("🗝️ 잠깐! · 피싱 방탈출")
st.subheader("사건 01 — 엄마의 번호, 두 개의 진실")
st.caption(f"교육용 가상 사건 · 제한 시간 {TIME_LIMIT_MINUTES}분 · 실제 전화나 앱 설치는 실행되지 않아요")

show_game_guide()

if user():
    st.caption(f"참여 닉네임: {user()['nickname']} · 새로 시작한 게임의 완료 기록을 공개 저장합니다.")
else:
    st.info("로그인 없이 연습할 수 있어요. 공동 랭킹 참여는 왼쪽 ‘닉네임 입장’에서 먼저 진행하세요.")

if "escape_game" not in st.session_state:
    if st.button("방에 들어가기", type="primary"):
        fresh_game()
        st.rerun()

    st.info(
        "책상 위 휴대전화에 ‘엄마’가 표시됐었습니다. 상대는 다른 가족에게 연락하지 말라고 했고, "
        "2분 뒤 낯선 번호로 문자가 왔습니다. 지금은 09:13입니다."
    )
    st.write(f"‘방에 들어가기’를 누르는 순간 {TIME_LIMIT_MINUTES}분 타이머가 시작됩니다. 정답을 추측하기보다 확인 가능한 근거를 모으세요.")

else:
    game = st.session_state["escape_game"]

    if is_timed_out():
        show_failure()
        st.stop()

    if game["unlocked"] < 3:
        countdown()
        show_status_bar()

    st.progress(game["unlocked"] / 3)
    st.caption(
        f"해제한 잠금 {game['unlocked']} / 3 · "
        f"수집한 증거 {len(game['evidence'])}개"
    )
    show_feedback()

    room_tab, inventory_tab, lock_tab = st.tabs(
        ["🔎 방 조사", "📁 증거 보관함", "🔐 잠금 해제"]
    )

    with room_tab:
        show_room()

    with inventory_tab:
        show_inventory()

    with lock_tab:
        if game["unlocked"] == 0:
            lock_one()
        elif game["unlocked"] == 1:
            lock_two()
        elif game["unlocked"] == 2:
            lock_three()
        else:
            show_ending()

    st.divider()

    with st.expander("게임 다시 시작"):
        st.write("현재 증거와 잠금 기록이 초기화됩니다. 아직 저장하지 못한 결과는 먼저 다운로드하세요. Firebase에 저장된 공개 기록은 유지됩니다.")
        st.button(
            "기록을 지우고 다시 시작",
            on_click=fresh_game,
        )
