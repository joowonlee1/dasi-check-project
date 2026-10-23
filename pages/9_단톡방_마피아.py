"""단톡방 마피아: 친구 5명 중 마피아(사칭 계정) 1명을 조사 3번으로 찾아내는 추리 게임.

모든 인물·대화·링크는 교육용 가상 내용입니다. 실제 접속·송금·인증은 일어나지 않습니다.
"""
import time
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from mascot_ui import show_key_question, show_mascot
import dotori_data as dd

KEY = "mafia_v1"
MAX_CHECKS = 3  # 사건마다 쓸 수 있는 조사 횟수
KINDS = {
    "profile": "👤 프로필 보기",
    "question": "💬 1:1 질문",
    "history": "📜 이전 대화",
}
FRIENDS = {
    "민서": ("🐣", "#FFE7A3", "반에서 제일 활발한 분위기 메이커"),
    "지호": ("🎧", "#D6E4FF", "말수 적은 음악 덕후"),
    "하준": ("😜", "#FFD6E0", "장난이 끊이지 않는 장난꾸러기"),
    "서연": ("📋", "#D7F2E3", "꼼꼼한 2학년 3반 반장"),
    "도윤": ("⚽", "#FFE2C6", "축구부, 남자애들을 장난으로 ‘형’이라고 부름"),
}

# 사건: 단톡방 대화, 1:1로 물어볼 질문, 친구별 조사 결과, 정답과 해설
CASES = [
    {
        "title": "사건 1 · 잘못 간 인증번호",
        "stars": "★★★☆☆",
        "question": "지난주 체육대회 때 우리 반 몇 등 했지?",
        "chat": [
            ("21:02", "서연", "내일 진로 체험 신청서 오늘 밤까지 제출해 주세요! 담임쌤 공지 링크예요 → [가상 링크: 학교 알림 앱]"),
            ("21:03", "민서", "넹 반장님 🐣 지금 할게용"),
            ("21:05", "하준", "나폰액정나가서태블릿으로하는중ㅋㅋ 답늦을수있음"),
            ("21:07", "지호", "냄"),
            ("21:31", "도윤", "형들 ㅠ 나 계정 로그인하다가 인증번호가 하준이 번호로 잘못 갔대"),
            ("21:31", "도윤", "하준아 문자로 온 [가상 인증번호] 좀 불러줘 급해 ㅇㅋㅇㅋ?"),
            ("21:33", "하준", "??나지금폰없다니까 태블릿임"),
            ("21:33", "도윤", "아 그럼 민서한테 갔을 수도 있대 민서야 확인 좀 부탁드려요"),
            ("21:34", "민서", "헐 잠만 확인해 볼게"),
        ],
        "clues": {
            "민서": {
                "profile": "사진·이름 그대로. 상태 메시지 ‘시험 끝나면 떡볶이🐣’는 2주 전에 바꾼 것.",
                "question": "“3등!! 계주에서 지호가 넘어져서 ㅠㅠ 🐣” — 그날 있었던 일과 정확히 일치.",
                "history": "평소: “오늘 급식 미쳤당 ㅋㅋㅋ 🐣” — 메시지 끝에 🐣를 거의 항상 붙임.",
            },
            "지호": {
                "profile": "사진·이름 그대로. 상태 메시지 없음(원래 없음).",
                "question": "“3등. 계주에서 내가 넘어짐” — 정확함. 본인 실수까지 말함.",
                "history": "평소: “냄”, “ㅇㅇ”, “자러감” — 대부분 두세 글자.",
            },
            "하준": {
                "profile": "오늘 이름이 ‘하준(액정깨짐)’으로 바뀜. 사진은 그대로.",
                "question": "“3등이잖아ㄹㅇ 지호넘어진거평생놀릴거임” — 정확함.",
                "history": "평소에도 띄어쓰기를 거의 안 하고 ‘ㄹㅇ’를 자주 씀.",
            },
            "서연": {
                "profile": "사진·이름 그대로. 상태 메시지 ‘2-3 반장 📋’.",
                "question": "“3등이요! 계주 진짜 아쉬웠죠 ㅠ” — 정확함.",
                "history": "공지는 늘 ‘담임쌤 공지’라고 밝히고 학교 알림 앱 링크만 올림. ‘~해 주세요!’ 말투.",
            },
            "도윤": {
                "profile": "오늘 21:20에 프로필 사진이 기본 이미지로 바뀌고 상태 메시지가 지워짐.",
                "question": "“아 그건 기억 안 나 ㅋㅋ 지금 그게 중요한 게 아니라 인증번호 먼저 ㅠ” — 질문을 피함.",
                "history": "평소: “형 ㄱㄱ”, “ㅇㅋㅇㅋ” — 친구들에게 존댓말을 쓴 적이 한 번도 없음.",
            },
        },
        "answer": "도윤",
        "decisive": [
            "대화 직전(21:20)에 프로필 사진이 기본 이미지로 바뀌었어요.",
            "둘만 아는 질문(체육대회 등수)에 답하지 않고 인증번호 이야기로 돌렸어요.",
            "존댓말을 안 쓰는 도윤이 “부탁드려요”라고 썼어요. 말투가 한 번 미끄러졌죠.",
            "무엇보다 **인증번호는 친구에게도 불러 줄 이유가 없는 정보**예요.",
        ],
        "traps": [
            "하준의 ‘액정깨짐’ 이름 변경은 진짜였어요. 질문에 정확히 답했고, 말투도 평소와 같았어요.",
            "서연의 링크는 늘 그렇듯 ‘담임쌤 공지’와 학교 알림 앱이었어요.",
        ],
        "missed": "가짜 도윤은 민서에게서 [가상 인증번호]를 받아 진짜 도윤의 계정을 가져갔어요.",
    },
    {
        "title": "사건 2 · 수학여행 사진 앨범",
        "stars": "★★★★☆",
        "question": "수학여행 장기자랑 때 우리 반 뭐 했지?",
        "chat": [
            ("19:10", "민서", "나 내일 매점 천 원만 빌려줄 사람 🐣 지갑 두고 옴 ㅠㅠ"),
            ("19:11", "하준", "ㄴㄴ지난번에빌려간거부터갚으셈ㅋㅋ"),
            ("19:12", "지호", "내가 줌"),
            ("19:40", "서연", "여러분! 수학여행 사진 앨범이 올라왔습니다~ 선생님께서 공유해 주셨어요"),
            ("19:40", "서연", "[가상 링크] 들어가서 학교 계정으로 로그인하면 원본 받을 수 있어요! 오늘까지만 열려 있대요"),
            ("19:42", "도윤", "오 내 골 세리머니 사진 있냐ㅋㅋ 형들 빨리 봐"),
            ("19:43", "지호", "학교 앱엔 없던데"),
            ("19:43", "서연", "앱이 오류라서 따로 올렸대요~ 마감 전에 빨리 받아 가세요!"),
            ("19:45", "하준", "나이미로그인함ㅋㅋ근데사진안뜨는데?"),
        ],
        "clues": {
            "민서": {
                "profile": "사진·이름 그대로.",
                "question": "“아이돌 춤!! 하준이 센터였잖아 🐣” — 정확함.",
                "history": "가끔 천 원, 이천 원을 빌리고 다음 날 “어제 빌린 거 갚음 🐣”이라고 남김.",
            },
            "지호": {
                "profile": "사진·이름 그대로.",
                "question": "“아이돌 춤. 하준 센터” — 정확함.",
                "history": "평소: “학교 앱 확인함”, “공지 봄” — 링크보다 학교 앱을 먼저 확인하는 편.",
            },
            "하준": {
                "profile": "이름이 다시 ‘하준’으로 돌아옴(액정 수리 완료). 사진 그대로.",
                "question": "“아이돌춤ㄹㅇ내가센터였지ㅋㅋ” — 정확함.",
                "history": "평소에도 일단 눌러 보고 나중에 묻는 편.",
            },
            "서연": {
                "profile": "사진·이름·상태 메시지 모두 그대로. 겉보기엔 변화가 없음.",
                "question": "“사진 받아 보면 다 나와 있어요~ 링크부터 들어가 봐요!” — 질문에 답하지 않음.",
                "history": "공지할 때 늘 ‘담임쌤 공지’라고 쓰고 학교 알림 앱 링크만 공유함. ‘선생님께서’라고 쓴 적도, 마감을 재촉한 적도 없음.",
            },
            "도윤": {
                "profile": "3일 전 축구 경기 사진으로 프로필 변경.",
                "question": "“아이돌 춤 ㅋㅋ 하준 센터 ㅇㅋㅇㅋ” — 정확함.",
                "history": "평소: “형들 경기 보러 와 ㅇㅋㅇㅋ” — 말투 그대로.",
            },
        },
        "answer": "서연",
        "decisive": [
            "프로필은 그대로였어요. **계정을 통째로 빼앗기면 겉모습은 똑같아요.**",
            "학교 앱이 아닌 링크 + 학교 계정 로그인 + ‘오늘까지만’이라는 재촉이 한꺼번에 나왔어요.",
            "‘담임쌤 공지’라고 쓰던 서연이 ‘선생님께서’라고 쓰고, 둘만 아는 질문은 피했어요.",
            "지호가 학교 앱에 없다고 하자 ‘앱 오류’라고 둘러댔어요.",
        ],
        "traps": [
            "민서의 돈 부탁은 진짜였어요. 액수가 작고, 내일 직접 만나 받는 부탁이었고, 평소에도 꼭 갚았어요.",
            "도윤의 프로필 변경은 3일 전 경기 사진이었어요.",
            "하준은 마피아가 아니라 **이미 링크에 로그인한 피해자**예요.",
        ],
        "missed": "가짜 서연의 링크로 하준을 포함한 여러 친구의 학교 계정이 넘어갔어요.",
    },
    {
        "title": "사건 3 · 다들 해 봤대",
        "stars": "★★★★★",
        "question": "오늘 급식 후식 뭐였지?",
        "chat": [
            ("23:48", "민서", "얘들아 이거 봄?? 학생 인증하면 기프티콘 준대 🐣 [가상 링크]"),
            ("23:49", "하준", "ㄹㅇ?공짜?"),
            ("23:51", "지호", "ㅇㅇ 나 해 봄 진짜 줌ㅋㅋ"),
            ("23:51", "지호", "전화번호랑 [가상 인증번호] 넣으면 바로 옴 빨리 해 선착순임"),
            ("23:53", "서연", "이런 이벤트는 학교에서 조심하라고 했던 것 같은데요…"),
            ("23:54", "지호", "나 받았다니까 의심 ㄴㄴ 너네도 빨리"),
            ("23:56", "도윤", "형들 나 폰 바꿈 새 번호 저장 ㄱㄱ"),
            ("23:57", "하준", "나도해볼까"),
        ],
        "clues": {
            "민서": {
                "profile": "사진·이름 그대로.",
                "question": "“딸기 요거트!! 🐣 근데 이 링크 친척 언니가 보내 준 거라 올렸어” — 정확함.",
                "history": "재미있어 보이는 걸 찾으면 바로 단톡방에 공유하는 편.",
            },
            "지호": {
                "profile": "사진·이름 그대로. 변경 기록 없음.",
                "question": "“그런 거 왜 물어봄ㅋㅋ 링크나 해” — 질문을 피함.",
                "history": "평소: 매일 11시 전에 “자러감 ㅂㅂ”. ‘ㅋㅋ’를 거의 안 씀. 지난달에는 “이벤트 링크 다 사기임 누르지 마”라고 말함.",
            },
            "하준": {
                "profile": "사진·이름 그대로.",
                "question": "“딸기요거트ㄹㅇ맛있었음” — 정확함.",
                "history": "평소 말투 그대로. 공짜라면 일단 관심부터 보이는 편.",
            },
            "서연": {
                "profile": "사진·이름 그대로. (지난 사건 뒤 비밀번호를 바꾸고 2단계 인증을 켬)",
                "question": "“딸기 요거트요! 근데 저 링크는 누르지 마세요 ㅠ” — 정확함.",
                "history": "공지는 학교 알림 앱으로만. 지난 사건 뒤로 의심스러운 링크에 먼저 경고함.",
            },
            "도윤": {
                "profile": "오늘 23:55에 사진과 번호가 바뀜. 상태 메시지 ‘폰 바꿈 📱’.",
                "question": "“딸기 요거트 ㅇㅋㅇㅋ 근데 형 나 진짜 폰 바꾼 거임” — 정확함.",
                "history": "평소: “형 ㄱㄱ”, “ㅇㅋㅇㅋ” — 말투 그대로. 아무것도 요구하지 않음.",
            },
        },
        "answer": "지호",
        "decisive": [
            "링크를 올린 민서는 진짜였어요. **진짜 친구도 모르고 사기 링크를 퍼뜨릴 수 있어요.**",
            "마피아는 링크를 올린 사람이 아니라 “나도 해 봤어”라며 **부추긴 사람**이었어요.",
            "11시 전에 자던 지호가 새벽에 ‘ㅋㅋ’를 쓰며, 사기라고 말했던 이벤트를 권했어요.",
            "프로필 변화가 전혀 없었어요. 해킹된 계정은 겉모습이 똑같아요. 질문은 피했죠.",
        ],
        "traps": [
            "도윤의 사진·번호 변경은 가장 수상해 보였지만 진짜였어요. 질문에 정확히 답했고 아무것도 요구하지 않았어요.",
            "민서는 마피아가 아니라 링크를 믿고 퍼뜨린 친구예요.",
        ],
        "missed": "‘지호도 받았대’라는 말을 믿은 친구들이 [가상 인증번호]를 넣어 계정을 빼앗겼어요.",
    },
]

LESSONS = [
    ("💬 둘만 아는 질문", "사칭범은 둘만 아는 일을 몰라서 질문을 피하거나 다른 이야기로 돌려요."),
    ("📜 평소 말투와 습관", "말투, 활동 시간, 평소 생각이 갑자기 달라지면 의심해 보세요."),
    ("👤 프로필 변화", "변화가 있어도 진짜일 수 있고, 해킹된 계정은 겉모습이 그대로일 수 있어요."),
    ("📞 다른 경로로 확인", "가장 확실한 방법은 원래 번호로 전화하거나 직접 만나서 묻는 거예요."),
]

CSS = """
<style>
@keyframes mf-pop {0%{transform:scale(.5);opacity:0} 65%{transform:scale(1.06);opacity:1} 100%{transform:scale(1)}}
@keyframes mf-in {0%{transform:translateY(12px);opacity:0} 100%{transform:none;opacity:1}}
@keyframes mf-bounce {0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)}}
@keyframes mf-stamp {0%{transform:scale(3) rotate(-18deg);opacity:0} 60%{transform:scale(.9) rotate(-12deg);opacity:1}
  100%{transform:scale(1) rotate(-12deg);opacity:1}}
@keyframes mf-shake {0%,100%{transform:translateX(0)} 20%,60%{transform:translateX(-10px)} 40%,80%{transform:translateX(10px)}}
@keyframes mf-burst {0%{transform:translate(0,0) scale(.3);opacity:1} 100%{transform:translate(var(--x),var(--y)) scale(1.2);opacity:0}}
.mf-hero {background:linear-gradient(135deg,#1F5F55,#2E8B78);border-radius:26px;padding:22px 18px;color:#fff;text-align:center;
  animation:mf-pop .6s ease-out both;box-shadow:0 10px 26px rgba(32,72,63,.22);}
.mf-hero b {display:block;font-size:1.6rem;font-weight:900;margin:6px 0;word-break:keep-all;}
.mf-hero span {opacity:.9;font-weight:600;}
.mf-friends {display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:12px 0;}
.mf-friend {border-radius:18px;padding:10px 4px;text-align:center;animation:mf-pop .5s ease-out both;word-break:keep-all;}
.mf-friend div {font-size:34px;animation:mf-bounce 2.4s ease-in-out infinite;}
.mf-friend b {display:block;color:#1E2F2B;}
.mf-friend small {color:#3E5751;font-size:.78rem;line-height:1.35;display:block;}
.mf-chat {background:#DCEAE3;border-radius:24px;padding:14px 12px;margin:8px 0 14px;}
.mf-chat-top {text-align:center;font-weight:800;color:#20483F;margin-bottom:8px;}
.mf-msg {display:flex;gap:8px;align-items:flex-start;margin:8px 0;animation:mf-in .4s ease-out both;}
.mf-ava {width:40px;height:40px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}
.mf-name {font-size:.85rem;font-weight:800;color:#20483F;}
.mf-bubble {background:#fff;border-radius:4px 16px 16px 16px;padding:9px 12px;font-size:1.05rem;color:#1E2F2B;
  line-height:1.6;word-break:keep-all;display:inline-block;max-width:100%;}
.mf-time {font-size:.72rem;color:#5A7068;margin-left:6px;}
.mf-left {font-weight:900;font-size:1.15rem;color:#20483F;}
.mf-dots {font-size:1.5rem;letter-spacing:4px;}
.mf-note {border-radius:16px;padding:12px 14px;margin:8px 0;animation:mf-pop .45s ease-out both;
  border:2px solid rgba(0,0,0,.06);word-break:keep-all;}
.mf-note b {display:block;color:#20483F;margin-bottom:3px;}
.mf-note span {color:#1E2F2B;line-height:1.65;font-size:1.02rem;}
.mf-reveal {position:relative;overflow:hidden;border-radius:26px;padding:26px 18px;text-align:center;margin:8px 0 14px;}
.mf-reveal.win {background:linear-gradient(135deg,#FFF1C2,#FFD6A5);animation:mf-pop .6s ease-out both;}
.mf-reveal.lose {background:linear-gradient(135deg,#EEF2EF,#D3DED8);animation:mf-shake .6s ease-in-out both;}
.mf-reveal .who {font-size:72px;animation:mf-bounce 1.6s .8s ease-in-out infinite;}
.mf-reveal .line {font-size:1.45rem;font-weight:900;color:#20483F;word-break:keep-all;margin-top:4px;}
.mf-stamp {display:inline-block;margin-top:12px;border:5px solid #D7263D;color:#D7263D;border-radius:12px;padding:4px 18px;
  font-size:1.9rem;font-weight:900;letter-spacing:.1em;animation:mf-stamp .5s .45s ease-out both;background:rgba(255,255,255,.6);}
.mf-stamp.miss {border-color:#5A7068;color:#5A7068;}
.mf-stamp {max-width:92%;}
@media (max-width:640px) {.mf-stamp {font-size:1.5rem;}}
.mf-spark {position:absolute;left:50%;top:40%;font-size:26px;animation:mf-burst 1.1s .5s ease-out both;pointer-events:none;}
.st-key-mafia_v1_count button {font-size:1.2rem !important;font-weight:800;padding:12px 24px !important;min-height:54px;border-radius:16px !important;border-width:2px !important;}
.st-key-mafia_v1_count button p {font-size:1.2rem !important;font-weight:800;}
.st-key-mafia_v1_count [aria-checked="true"], .st-key-mafia_v1_count button[kind$="Active"] {background:#20483F !important;color:#fff !important;border-color:#20483F !important;}
.st-key-mafia_v1_count [aria-checked="true"] p, .st-key-mafia_v1_count button[kind$="Active"] p {color:#fff !important;}
.mf-drum {text-align:center;font-size:1.5rem;font-weight:900;color:#20483F;padding:40px 0;}
.mf-drum div {font-size:70px;animation:mf-bounce .45s ease-in-out infinite;}
.mf-score {display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:10px 0;}
.mf-score div {background:#fff;border:2px solid #CFDDD6;border-radius:18px;padding:12px;text-align:center;animation:mf-pop .5s ease-out both;}
.mf-score b {display:block;font-size:1.8rem;color:#20483F;}
@media (max-width:640px) {.mf-friends {grid-template-columns:repeat(3,1fr);}}
</style>
"""


# ───────── 상태 ─────────

def new_state(players=None):
    return {
        "phase": "setup",
        "case": 0,
        "players": players or ["나"],
        "scores": {},
        "checks": [],
        "votes": {},
        "voter": 0,
        "fresh": False,
        "results": [],
    }


def state():
    if KEY not in st.session_state:
        st.session_state[KEY] = new_state()
    return st.session_state[KEY]


def start_game():
    s = state()
    count = st.session_state.get(KEY + "_count") or 1
    names = []
    for i in range(count):
        name = (st.session_state.get(f"{KEY}_name_{i}") or "").strip()[:8]
        names.append(name or (f"플레이어 {i + 1}" if count > 1 else "나"))
    st.session_state[KEY] = new_state(names)
    st.session_state[KEY]["phase"] = "play"
    st.session_state[KEY]["scores"] = {n: 0 for n in names}
    st.session_state[KEY]["gid"] = str(time.time())  # 이번 판을 구분해 통계를 한 번만 세요.


def investigate(friend, kind):
    s = state()
    if len(s["checks"]) < MAX_CHECKS and (friend, kind) not in s["checks"]:
        s["checks"].append((friend, kind))


def cast_vote(player, pick_key):
    s = state()
    pick = st.session_state.get(pick_key)
    if not pick:
        return
    s["votes"][player] = pick
    s["voter"] += 1
    if s["voter"] >= len(s["players"]):
        finish_case()


def finish_case():
    s = state()
    case = CASES[s["case"]]
    left = MAX_CHECKS - len(s["checks"])
    winners = []
    for player, pick in s["votes"].items():
        if pick == case["answer"]:
            s["scores"][player] += 100 + 20 * left
            winners.append(player)
    s["results"].append({"case": s["case"], "votes": dict(s["votes"]), "winners": winners})
    s["phase"] = "reveal"
    s["fresh"] = True
    s["scroll"] = True


def next_case():
    s = state()
    s["case"] += 1
    s["checks"], s["votes"], s["voter"] = [], {}, 0
    s["phase"] = "final" if s["case"] >= len(CASES) else "play"
    s["fresh"] = s["phase"] == "final"
    s["scroll"] = True


def restart():
    st.session_state[KEY] = new_state()


# ───────── 화면 조각 ─────────

def friends_html():
    return '<div class="mf-friends">' + "".join(
        f'<div class="mf-friend" style="background:{color};animation-delay:{i * .08:.2f}s">'
        f'<div style="animation-delay:{i * .3:.1f}s">{emoji}</div><b>{name}</b><small>{escape(desc)}</small></div>'
        for i, (name, (emoji, color, desc)) in enumerate(FRIENDS.items())
    ) + "</div>"


def chat_html(case):
    rows = []
    for i, (when, name, text) in enumerate(case["chat"]):
        emoji, color, _ = FRIENDS[name]
        rows.append(
            f'<div class="mf-msg" style="animation-delay:{i * .12:.2f}s">'
            f'<div class="mf-ava" style="background:{color}">{emoji}</div>'
            f'<div><div class="mf-name">{name}</div>'
            f'<span class="mf-bubble">{escape(text)}</span><span class="mf-time">{when}</span></div></div>'
        )
    return (
        '<div class="mf-chat"><div class="mf-chat-top">🍀 2학년 3반 단톡방 (5)</div>'
        + "".join(rows) + "</div>"
    )


def note_html(case, friend, kind, index):
    emoji, color, _ = FRIENDS[friend]
    extra = f"<br><small>질문: “{escape(case['question'])}”</small>" if kind == "question" else ""
    return (
        f'<div class="mf-note" style="background:{color};animation-delay:{index * .05:.2f}s">'
        f'<b>{emoji} {friend} · {KINDS[kind]}{extra}</b><span>{escape(case["clues"][friend][kind])}</span></div>'
    )


def scroll_top():
    """투표·다음 사건 버튼은 화면 아래에 있어서, 새 장면이 열리면 맨 위로 올려 줍니다."""
    components.html(
        "<script>const m = window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if (m) { m.scrollTo({top: 0, behavior: 'instant'}); }"
        "window.parent.scrollTo(0, 0);</script>",
        height=0,
    )


def drumroll():
    box = st.empty()
    for icon, text in (("🥁", "두구두구…"), ("🔦", "계정을 추적하는 중…"), ("🕵️", "정체를 공개합니다!")):
        box.markdown(f'<div class="mf-drum"><div>{icon}</div>{text}</div>', unsafe_allow_html=True)
        time.sleep(0.6)
    box.empty()


def sparks():
    icons = ["🔍", "✨", "⭐", "🎉", "💥", "✨", "🔍", "⭐", "🎉", "✨", "💫", "⭐"]
    out = []
    for i, icon in enumerate(icons):
        x = [140, 120, 70, 0, -70, -120, -140, -120, -70, 0, 70, 120][i]
        y = [0, -70, -120, -140, -120, -70, 0, 70, 120, 140, 120, 70][i]
        out.append(f'<span class="mf-spark" style="--x:{x}px;--y:{y}px;animation-delay:{.45 + i * .02:.2f}s">{icon}</span>')
    return "".join(out)


# ───────── 화면 ─────────

def show_setup():
    st.markdown(
        '<div class="mf-hero"><span>🕵️ 추리 게임 · 사건 3개</span>'
        '<b>우리 반 단톡방에 마피아가 숨어 있다</b>'
        '<span>사건마다 친구 5명 중 1명은 해킹당했거나 사칭한 계정, 마피아예요. 나머지는 시민이에요.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(friends_html(), unsafe_allow_html=True)
    show_mascot("detective", "조사는 사건마다 딱 3번! 누구를, 어떻게 조사할지가 승부예요.", width=110)
    with st.container(border=True):
        st.markdown("**🎮 규칙**")
        st.markdown(
            "1. 단톡방 대화를 읽어요.\n"
            "2. **조사 3번**: 친구를 골라 👤 프로필 · 💬 1:1 질문 · 📜 이전 대화 중 하나를 확인해요. (모두 15가지 중 3개만!)\n"
            "3. **투표**: 마피아라고 생각하는 친구를 지목해요.\n"
            "4. 맞히면 100점 + 남은 조사 1번당 20점. 진짜 친구도 수상해 보이는 **함정**이 있어요."
        )
    st.markdown("#### 👥 몇 명이 함께 하나요?")
    st.pills("몇 명이 함께 하나요?", [1, 2, 3, 4], default=1, key=KEY + "_count", label_visibility="collapsed",
             format_func=lambda n: "🙋 혼자" if n == 1 else f"👥 {n}명")
    st.markdown("📱 **2명 이상이면 휴대폰 한 대를 돌려 가며 해요.**")
    count = st.session_state.get(KEY + "_count") or 1
    if count > 1:
        cols = st.columns(count)
        for i in range(count):
            cols[i].text_input(f"플레이어 {i + 1}", key=f"{KEY}_name_{i}", max_chars=8, placeholder=f"플레이어 {i + 1}")
        st.caption("조사는 함께 의논해서 고르고, 투표는 한 명씩 몰래 해요.")
    st.button("🔍 수사 시작", type="primary", width="stretch", on_click=start_game, key=KEY + "_start")
    st.caption("모든 인물·대화·링크는 교육용 가상 내용이에요. 실제 접속이나 인증은 일어나지 않아요.")


def show_play():
    s = state()
    case = CASES[s["case"]]
    st.progress(s["case"] / len(CASES), text=f"사건 {s['case'] + 1} / {len(CASES)}")
    st.markdown(
        f'<div class="mf-hero"><span>난이도 {case["stars"]}</span><b>{case["title"]}</b>'
        f'<span>이 대화방 안에 마피아가 한 명 숨어 있어요.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(chat_html(case), unsafe_allow_html=True)

    left = MAX_CHECKS - len(s["checks"])
    dots = "🔍" * left + "▫️" * (MAX_CHECKS - left)
    st.markdown(f'<div class="mf-left">🔎 조사하기 <span class="mf-dots">{dots}</span> 남은 횟수 {left}/{MAX_CHECKS}</div>',
                unsafe_allow_html=True)
    friend = st.pills("누구를 조사할까요?", list(FRIENDS), key=f"{KEY}_who_{s['case']}",
                      format_func=lambda n: f"{FRIENDS[n][0]} {n}")
    if friend:
        cols = st.columns(3)
        for col, (kind, label) in zip(cols, KINDS.items()):
            done = (friend, kind) in s["checks"]
            col.button(label + (" ✓" if done else ""), key=f"{KEY}_{s['case']}_{friend}_{kind}",
                       disabled=done or left == 0, width="stretch", on_click=investigate, args=(friend, kind))
    if left == 0:
        st.caption("조사를 모두 썼어요. 이제 수사 노트를 보고 투표하세요.")

    if s["checks"]:
        st.markdown("**🗒️ 수사 노트**")
        st.markdown("".join(note_html(case, f, k, i) for i, (f, k) in enumerate(s["checks"])), unsafe_allow_html=True)

    st.divider()
    player = s["players"][s["voter"]]
    multi = len(s["players"]) > 1
    st.markdown(f"### 🗳️ {'%s님의 ' % escape(player) if multi else ''}투표")
    if multi:
        done = ", ".join(f"{p} ✓" for p in s["players"][:s["voter"]])
        st.caption("다른 사람은 화면을 보지 마세요! " + (f"투표 완료: {done}" if done else ""))
    pick_key = f"{KEY}_pick_{s['case']}_{s['voter']}"
    st.radio("마피아라고 생각하는 친구", list(FRIENDS), index=None, horizontal=True, key=pick_key,
             format_func=lambda n: f"{FRIENDS[n][0]} {n}")
    st.button("🚨 이 친구가 마피아다!", type="primary", width="stretch",
              key=f"{KEY}_vote_{s['case']}_{s['voter']}", on_click=cast_vote, args=(player, pick_key),
              disabled=not st.session_state.get(pick_key))
    if left > 0:
        st.caption(f"지금 투표하면 남은 조사 {left}번만큼 보너스 +{left * 20}점! 단, 틀리면 0점이에요.")


def josa(name, with_final, without_final):
    """이름 끝 글자에 받침이 있으면 앞 조사, 없으면 뒤 조사를 붙여요. (도윤이었어요 / 지호였어요)"""
    last = name[-1]
    has_final = "가" <= last <= "힣" and (ord(last) - 0xAC00) % 28 != 0
    return name + (with_final if has_final else without_final)


def show_reveal():
    s = state()
    case = CASES[s["case"]]
    result = s["results"][-1]
    if s.pop("fresh", False):
        if dd.once(f"mafia-{s.get('gid')}-{s['case']}"):
            dd.record("mafia", {f"c{s['case']}_plays": 1, f"c{s['case']}_win": 1 if result["winners"] else 0})
        drumroll()
    answer = case["answer"]
    emoji = FRIENDS[answer][0]
    win = bool(result["winners"])
    multi = len(s["players"]) > 1
    if win:
        stamp = '<span class="mf-stamp">마피아 검거!</span>' + sparks()
        line = f"{josa(answer, '은', '는')} 마피아(사칭범)였습니다!"
    else:
        stamp = '<span class="mf-stamp miss">놓쳤다…</span>'
        line = f"진짜 마피아는 {josa(answer, '이었어요', '였어요')}"
    st.markdown(
        f'<div class="mf-reveal {"win" if win else "lose"}"><div class="who">{emoji}</div>'
        f'<div class="line">{line}</div>{stamp}</div>',
        unsafe_allow_html=True,
    )
    if multi:
        for player, pick in result["votes"].items():
            mark = "⭕" if pick == answer else "❌"
            st.markdown(f"- {mark} **{escape(player)}** → {FRIENDS[pick][0]} {pick}")
    elif not win:
        pick = result["votes"][s["players"][0]]
        st.warning(f"{FRIENDS[pick][0]} {josa(pick, '은', '는')} 시민(진짜 친구)이었어요. {case['missed']}")

    with st.container(border=True):
        st.markdown("**🔑 결정적 단서**")
        st.markdown("\n".join(f"- {d}" for d in case["decisive"]))
    with st.container(border=True):
        st.markdown("**🪤 함정이었던 것**")
        st.markdown("\n".join(f"- {t}" for t in case["traps"]))
    data, num = dd.stats("mafia"), s["case"]
    plays = data.get(f"c{num}_plays", 0)
    if plays:
        found = dd.pct(data.get(f"c{num}_win", 0), plays)
        dd.show_others([f"이 사건은 지금까지 <b>{plays}번</b> 수사됐고, 마피아를 찾아낸 비율은 <b>{found}%</b>예요."])
    st.info("📞 실제라면? 단톡방 안에서 따지기보다 **원래 번호로 전화하거나 직접 만나서** 확인하세요. "
            "계정이 해킹된 것 같으면 친구에게 알리고, 해당 서비스에 신고해요.")
    label = "다음 사건으로 ▶" if s["case"] + 1 < len(CASES) else "🏆 최종 결과 보기"
    st.button(label, type="primary", width="stretch", on_click=next_case, key=f"{KEY}_next_{s['case']}")


def show_final():
    s = state()
    if s.pop("fresh", False):
        drumroll()
    ranking = sorted(s["scores"].items(), key=lambda kv: -kv[1])
    best = MAX_CHECKS * 20 + 100
    solved = sum(1 for r in s["results"] if r["winners"])
    top_name, top_score = ranking[0]
    title = "🕵️ 명탐정" if top_score >= len(CASES) * 140 else "🔍 수습 탐정" if top_score >= 200 else "🐣 견습 탐정"
    st.markdown(
        f'<div class="mf-reveal win"><div class="who">🏆</div>'
        f'<div class="line">{escape(top_name)} · {title}</div>'
        f'<span class="mf-stamp">사건 종결</span>{sparks()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mf-score">' + "".join(
            f'<div style="animation-delay:{i * .1:.1f}s">{["🥇", "🥈", "🥉", "🏅"][i]} {escape(n)}<b>{sc}점</b></div>'
            for i, (n, sc) in enumerate(ranking)
        ) + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"사건 {len(CASES)}개 중 {solved}개 해결 · 한 사건 최고 {best}점")
    if len(s["players"]) == 1:
        # 혼자 한 판만 명예의 전당에 올려요(여럿이 한 판은 점수를 나눠 가져서 비교가 어려워요).
        if dd.once(f"mafia-final-{s.get('gid')}"):
            dd.note_mine("mafia", f"{top_score}점 · 사건 {solved}/{len(CASES)} 해결")
            st.session_state[KEY + "_hall"] = dd.save_hall(
                "mafia", {"score": top_score, "solved": solved},
                lambda old, new: new["score"] > old.get("score", -1),
            )
        dd.show_hall_note(st.session_state.get(KEY + "_hall"))
    show_mascot("trophy", "말투·질문·프로필은 단서일 뿐! 마지막 확인은 언제나 다른 경로로 해요.", width=110)
    st.markdown("### 🧠 오늘 배운 마피아(사칭범) 찾는 법")
    cols = st.columns(2)
    for i, (head, body) in enumerate(LESSONS):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{head}**")
            st.write(body)
    st.button("🔄 처음부터 다시", on_click=restart, width="stretch", key=KEY + "_again")


# ───────── 실행 ─────────

st.markdown(CSS, unsafe_allow_html=True)
st.title("🕵️ 단톡방 마피아")
show_key_question("친구 5명 중 **한 명은 마피아(사칭범)**예요. 말투·질문·프로필로 **마피아**를 찾아내세요.", "🕵️")

move_up = state().pop("scroll", False)
if move_up:
    scroll_top()

phase = state()["phase"]
if phase == "setup":
    show_setup()
elif phase == "play":
    show_play()
elif phase == "reveal":
    show_reveal()
else:
    show_final()

if move_up:  # 화면이 다 그려진 뒤에도 한 번 더 맨 위로 올립니다.
    scroll_top()
