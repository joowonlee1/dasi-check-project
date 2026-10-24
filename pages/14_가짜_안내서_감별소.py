"""가짜 안내서 감별소: 현관문에 붙은 '우편물 도착 안내서' 5장을 감별하는 게임.

- 도구 3가지: 열 테스트(감열지인지), 떼기 테스트(붙인 흔적), 번호부 이진 탐색(집배원 번호가 공식 번호부에 있는지)
- 번호부는 번호 순서로 정렬된 64칸이라, 가운데를 펼쳐 절반씩 줄이면 6번 안에 찾을 수 있어요(이진 탐색).
- 모든 기관·번호·인물은 가상의 도토리시 이야기예요. 실제 우체국 양식을 따라 하지 않았어요.
- 수법과 구별법은 우정사업본부 주의 안내(2026년 9월 29일 보도)를 바탕으로 했어요.
"""
from html import escape

import streamlit as st
from mascot_ui import show_key_question, show_mascot
from card_ui import show_result_card
import dotori_data as dd

KEY = "notice_v1"

# 도토리 우체국 집배원 공식 번호부: 번호 순서로 정렬된 64칸(가상의 내선 번호)
BOOK = [1012 + 131 * i for i in range(64)]
GOAL = 7  # 64칸은 절반씩 줄이면 아무리 운이 나빠도 7번 안에 끝나요(64→32→16→8→4→2→1)

# 감별할 안내서 5장. paper: 감열지/일반 종이, attach: 붙인 방식, number: 적힌 집배원 번호, ask: 안내 문구
CASES = [
    {
        "door": "101호", "real": False, "paper": "plain", "attach": "tape", "number": 2817,
        "time": "10월 22일 오후 2:10", "ask": "부재중이라 등기를 가져가지 못했어요. 아래 번호로 전화 주세요.",
        "lesson": "일반 종이에 투명테이프로 붙어 있고, 번호도 번호부에 없었어요. 가짜 신호가 모두 모인 안내서예요.",
    },
    {
        "door": "102호", "real": True, "paper": "thermal", "attach": "clean", "number": BOOK[9],
        "time": "10월 22일 오후 2:25", "ask": "등기우편이 도착했어요. 다음 방문 때 받거나 우체국에서 찾아가세요.",
        "lesson": "감열지에 흔적 없이 떨어졌고, 번호도 번호부에 있었어요. 확인한 단서가 모두 진짜였어요.",
    },
    {
        "door": "103호", "real": False, "paper": "thermal", "attach": "clean", "number": 6390,
        "time": "10월 22일 오후 2:40", "ask": "등기우편이 도착했어요. 재배달을 원하면 아래 번호로 연락 주세요.",
        "lesson": "종이도 붙인 방식도 진짜와 같게 만든 정교한 위조였어요. 번호부에 없는 번호라는 것만이 결정적인 단서였어요. "
                  "요즘 가짜 안내서는 이렇게 겉모습만으로는 구별이 어려워요.",
    },
    {
        "door": "104호", "real": True, "paper": "thermal", "attach": "clean", "number": BOOK[41],
        "time": "10월 22일 오후 3:05", "ask": "등기 도착. 내일 오전에 다시 들를게요. (글씨가 조금 번졌어요)",
        "lesson": "구겨지고 글씨가 번져 수상해 보였지만, 확인한 단서는 모두 진짜였어요. "
                  "느낌이 아니라 확인한 사실로 판단해야 해요.",
        "messy": True,
    },
    {
        "door": "105호", "real": False, "paper": "plain", "attach": "residue", "number": BOOK[22],
        "time": "10월 22일 오후 3:20", "ask": "본인 확인을 위해 아래 번호로 전화해 주민등록번호와 계좌번호를 알려 주세요.",
        "lesson": "번호는 번호부에 있는 진짜 번호를 베껴 썼지만, 일반 종이에 끈적한 흔적이 남았어요. "
                  "무엇보다 우체국은 안내서·전화·인터넷 어디서도 주민등록번호나 계좌번호를 묻지 않아요.",
    },
]

PAPER = {"thermal": "🔥 검게 변했어요 → 영수증 같은 감열지예요", "plain": "🔥 아무 변화가 없어요 → 일반 프린터 종이예요"}
ATTACH = {
    "clean": "✋ 포스트잇처럼 쉽게 떨어지고 흔적이 남지 않았어요",
    "tape": "✋ 투명테이프로 붙어 있었어요",
    "residue": "✋ 떼어 낸 자리에 끈적한 접착 흔적이 남았어요",
}


def fresh():
    return {"step": "intro", "i": 0, "cases": [new_case() for _ in CASES], "recorded": False}


def new_case():
    return {"paper": False, "attach": False, "lo": 0, "hi": len(BOOK) - 1, "mid": None,
            "probes": 0, "found": None, "verdict": None, "opened": [], "log": [], "near_mid": 0}


S = st.session_state.setdefault(KEY, fresh())


# ───────── 그림 ─────────

def notice_html(case, peeled):
    """가상의 '도토리 우체국' 안내서. 투명테이프는 눈에 보이는 단서라 그려 두고, 접착 흔적은 떼어 봐야 보여요."""
    tape = '<div class="tape"></div>' if case["attach"] == "tape" else ""
    messy = " messy" if case.get("messy") else ""
    residue = '<div class="residue">끈적한 자국</div>' if peeled and case["attach"] == "residue" else ""
    return (
        f'<div class="nt-wrap"><div class="notice{messy}">{tape}'
        '<div class="nt-head">📮 도토리 우체국 · 우편물 도착 안내서</div>'
        f'<div class="nt-row"><span>받는 분</span><b>다람쥐아파트 {escape(case["door"])}</b></div>'
        '<div class="nt-row"><span>우편물</span><b>등기우편 1통</b></div>'
        f'<div class="nt-row"><span>방문 시각</span><b>{escape(case["time"])}</b></div>'
        f'<div class="nt-row"><span>담당 집배원</span><b>내선 {case["number"]}</b></div>'
        f'<div class="nt-msg">{escape(case["ask"])}</div>'
        '<div class="nt-foot">교육용 가상 안내서 · 실제 기관과 관계없음</div>'
        f'</div>{residue}</div>'
    )


def book_html(c, target):
    """번호부 64칸. 아직 후보인 칸만 밝게, 지운 칸은 흐리게, 방금 펼친 칸은 강조해요."""
    cells = []
    for i, n in enumerate(BOOK):
        cls = "bk"
        if i < c["lo"] or i > c["hi"]:
            cls += " out"
        if c["mid"] == i:
            cls += " mid"
        if c["found"] is True and BOOK[i] == target:
            cls += " hit"
        # 아직 안 펼친 칸은 '몇 번째 칸'인지만, 펼쳐 본 칸은 그 안의 집배원 번호를 보여 줘요.
        if i == c["mid"] or i in c["opened"] or cls.endswith("hit"):
            cls += " seen"
            label = f"<small>{i + 1}번째</small>{n}"
        else:
            label = i + 1
        cells.append(f'<div class="{cls}" title="{i + 1}번째 칸">{label}</div>')
    return '<div class="book">' + "".join(cells) + "</div>"


st.markdown(
    """<style>
    .nt-wrap{position:relative;max-width:440px;margin:4px auto 8px;}
    .notice{position:relative;background:#FFFDF6;border:2px solid #C9B98F;border-radius:6px;padding:16px 18px 12px;
      box-shadow:0 6px 16px rgba(0,0,0,.12);font-size:.95rem;color:#2B2B2B;}
    .notice.messy{transform:rotate(-2deg);filter:contrast(.92);background:#FBF6E8;}
    .nt-head{font-weight:900;color:#B42318;border-bottom:2px dashed #C9B98F;padding-bottom:8px;margin-bottom:8px;}
    .nt-row{display:flex;justify-content:space-between;gap:12px;padding:3px 0;border-bottom:1px dotted #E5DCC3;}
    .nt-row span{color:#6B6B6B;} .nt-msg{margin-top:10px;background:#F4EFE1;border-radius:6px;padding:8px 10px;line-height:1.5;}
    .nt-foot{margin-top:8px;font-size:.72rem;color:#9A9A9A;text-align:right;}
    .tape{position:absolute;top:-12px;left:50%;transform:translateX(-50%) rotate(-3deg);width:120px;height:26px;
      background:rgba(210,230,245,.65);border:1px solid rgba(150,180,200,.6);}
    .residue{margin:8px auto 0;width:fit-content;background:#EDE3B5;border:1px dashed #A8954B;border-radius:10px;
      padding:4px 12px;font-size:.85rem;color:#6B5A1E;}
    .book{display:grid;grid-template-columns:repeat(8,1fr);gap:4px;margin:6px 0 8px;}
    .bk{background:#E8F4EC;border:1.5px solid #B9D8C6;border-radius:8px;text-align:center;font-size:.78rem;
      padding:6px 0;color:#20483F;font-weight:700;}
    .bk.out{background:#F1F1F1;border-color:#E2E2E2;color:#C4C4C4;}
    .bk.mid{background:#FFE7A3;border-color:#E0A800;color:#5A3D00;font-size:.85rem;}
    .bk.hit{background:#0F766E;border-color:#0F766E;color:#fff;}
    .bk.seen{font-size:.8rem;line-height:1.15;padding:3px 0;} .bk small{display:block;font-size:.62rem;font-weight:600;opacity:.75;}
    .bk-head{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;margin-bottom:4px;}
    .bk-head b{font-size:1.05rem;margin-right:2px;}
    .chip{border-radius:999px;padding:3px 12px;font-size:.88rem;font-weight:700;}
    .chip strong{font-size:1.05rem;}
    .chip.find{background:#FDECEC;color:#B42318;border:1.5px solid #F2B8B5;}
    .chip.count{background:#E8F4EC;color:#0F766E;border:1.5px solid #B9D8C6;}
    .chip.bad{background:#FDECEC;color:#B42318;border:1.5px solid #B42318;}
    /* 펼칠 칸 입력칸: 지금 해야 할 일이라 눈에 띄게 */
    [class*="st-key-pick"] label p{font-size:1rem !important;font-weight:800 !important;color:#B4471B !important;}
    [class*="st-key-pick"] [data-testid="stNumberInputContainer"]{border:2.5px solid #E0A800 !important;border-radius:12px !important;
      background:#FFFBEA !important;box-shadow:0 0 0 4px rgba(224,168,0,.15);}
    [class*="st-key-pick"] input{font-size:1.35rem !important;font-weight:900 !important;color:#20483F !important;
      text-align:center;background:#FFFBEA !important;}
    [class*="st-key-pick"] button{background:#FFF4D6 !important;color:#5A3D00 !important;}
    .left-box{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 10px;background:#FFF4D6;border:2px solid #E0A800;
      border-radius:14px;padding:10px 14px;margin:4px 0 6px;color:#5A3D00;}
    .left-box span{font-weight:800;} .left-box b{font-size:1.25rem;color:#20483F;}
    .left-box em{font-style:normal;background:#0F766E;color:#fff;border-radius:999px;padding:1px 10px;font-weight:800;}
    .left-box small{flex-basis:100%;font-size:.85rem;color:#7A5A1A;}
    .log{display:flex;flex-direction:column;gap:4px;font-size:.86rem;line-height:1.45;margin-bottom:4px;}
    .log div{background:#F7F7F4;border-left:4px solid #0F766E;border-radius:6px;padding:5px 9px;}
    .tool-res{background:#F4F8F6;border:1.5px solid #D7E2DD;border-radius:12px;padding:8px 12px;margin:4px 0;}
    </style>""",
    unsafe_allow_html=True,
)


# ───────── 화면 ─────────

def show_intro():
    st.title("📬 가짜 안내서 감별소")
    show_key_question("현관문의 **우편물 도착 안내서**, 진짜일까요? 적힌 번호로 전화하기 전에 **감별**해요.", "📬")
    show_mascot("detective", "요즘 가짜 안내서는 진짜와 거의 똑같아요. 도구로 하나씩 확인해 봐요!", width=110)
    st.markdown(
        "다람쥐아파트 1층 현관문 다섯 곳에 안내서가 붙었다는 신고가 들어왔어요. "
        "가짜 안내서는 **받은 사람이 먼저 전화하게** 만들어요. 내가 건 전화라서 의심이 덜 생기거든요."
    )
    st.markdown(
        "**감별 도구 3가지**\n"
        "1. 🔥 **열 테스트**: 진짜 안내서는 영수증 같은 감열지예요.\n"
        "2. ✋ **떼기 테스트**: 진짜는 포스트잇처럼 쉽게 떨어지고 흔적이 없어요.\n"
        "3. 📒 **번호부 찾기**: 적힌 집배원 번호가 공식 번호부(64칸)에 있는지 찾아요. "
        "번호부는 번호 순서로 정렬돼 있어서, 가운데를 펼쳐 보고 절반씩 줄이면 빨리 찾을 수 있어요.\n\n"
        "세 가지를 모두 확인해야 판정할 수 있어요. 단서가 서로 다르게 말할 때는 어느 쪽을 믿을지가 핵심이에요!"
    )
    st.caption("모든 기관·번호는 가상이에요. 실제 안내서의 번호로 전화하거나 QR을 찍지 마세요.")
    if st.button("🔍 감별 시작하기", type="primary", width="stretch"):
        S["step"] = "play"
        dd.scroll_top()
        st.rerun()


def show_book(c, case):
    target = case["number"]
    over = c["probes"] > GOAL
    st.markdown(
        '<div class="bk-head"><b>📒 번호부 찾기</b>'
        f'<span class="chip find">찾는 번호 <strong>내선 {target}</strong></span>'
        f'<span class="chip {"bad" if over else "count"}">펼친 횟수 <strong>{c["probes"]}</strong> / 목표 {GOAL}번 이내</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("공식 집배원 번호 64개가 작은 번호부터 큰 번호 순서로 꽂혀 있어요. 칸의 숫자는 '몇 번째 칸'인지이고, "
               "펼쳐 본 칸에만 집배원 번호가 보여요. 회색 칸은 답이 있을 수 없어서 지운 칸이에요.")
    st.markdown(book_html(c, target), unsafe_allow_html=True)

    if c["found"] is not None:
        over = c["probes"] > GOAL
        if c["found"]:
            idx = BOOK.index(target)
            st.success(f"**{idx + 1}번째 칸에서 찾았어요.** 내선 {target}은 도토리 우체국에 등록된 공식 집배원 번호예요. "
                       "다만 번호는 진짜를 베껴 쓸 수도 있으니, 종이와 붙인 흔적도 함께 보고 판정하세요.")
        else:
            j = sum(1 for n in BOOK if n < target)  # 찾는 번호가 들어가야 할 자리
            if j == 0:
                where = f"맨 앞 칸(내선 {BOOK[0]})보다도 작은데"
            elif j == len(BOOK):
                where = f"맨 뒤 칸(내선 {BOOK[-1]})보다도 큰데"
            else:
                where = f"{j}번째 칸(내선 {BOOK[j - 1]})과 {j + 1}번째 칸(내선 {BOOK[j]}) 사이에 있어야 하는데"
            st.error(f"**번호부에 없는 번호예요.** 내선 {target}은 {where}, 그 사이에는 칸이 없어요. "
                     "번호부가 정렬돼 있으니 다른 곳을 더 찾을 필요도 없어요. "
                     "도토리 우체국 집배원 번호가 아니라는 뜻이라, 사기범이 지어낸 번호일 가능성이 커요.")
        if over:
            st.caption(f"목표({GOAL}번)보다 많이 펼쳤어요. 남은 후보의 가운데를 고르면 어떤 결과가 나와도 절반이 지워져요.")
        return



def show_book_controls(c, case):
    """남은 후보와 '몇 번째 칸을 펼칠지' 입력. 안내서 바로 아래(왼쪽)에 둬서 빈 공간 없이 이어지게 해요."""
    if c["found"] is not None:
        return
    target = case["number"]
    # 몇 번째 칸을 펼칠지는 직접 골라요. (어디를 고르느냐가 이진 탐색의 핵심)
    lo, hi = c["lo"], c["hi"]
    st.markdown(
        f'<div class="left-box"><span>남은 후보</span><b>{lo + 1}~{hi + 1}번째</b>'
        f'<em>{hi - lo + 1}칸</em><small>어느 칸을 펼쳐 볼까요?</small></div>',
        unsafe_allow_html=True,
    )
    n1, n2 = st.columns([1, 1], vertical_alignment="bottom")
    pick = n1.number_input("👉 펼칠 칸 (몇 번째)", min_value=lo + 1, max_value=hi + 1, value=lo + 1, step=1,
                           key=f"pick{S['i']}_{c['probes']}")
    if n2.button("📖 이 칸 펼치기", key=f"open{S['i']}", type="primary", width="stretch"):
        idx, mid = int(pick) - 1, (lo + hi) // 2
        value = BOOK[idx]
        c["probes"] += 1
        c["opened"].append(idx)
        c["mid"] = idx
        if abs(idx - mid) <= 1:
            c["near_mid"] += 1
        if value == target:
            c["found"] = True
            c["log"].append(f"{c['probes']}번째: {idx + 1}번째 칸 = <b>{value}</b> → 찾는 번호예요!")
        else:
            before = hi - lo + 1
            if target < value:
                c["hi"] = idx - 1
                reason = f"{target}이 더 작으니 {idx + 1}번째부터 뒤쪽은 볼 필요가 없어요"
            else:
                c["lo"] = idx + 1
                reason = f"{target}이 더 크니 {idx + 1}번째까지 앞쪽은 볼 필요가 없어요"
            left = max(0, c["hi"] - c["lo"] + 1)
            c["log"].append(f"{c['probes']}번째: {idx + 1}번째 칸 = <b>{value}</b> → {reason}. "
                            f"후보 {before}칸 → <b>{left}칸</b>")
            if left == 0:
                c["found"] = False
        st.rerun()


def show_book_log(c):
    """지금까지 펼친 기록: 어느 칸을 골랐고, 그 결과 후보가 몇 칸으로 줄었는지."""
    if not c["log"]:
        return
    st.markdown("**📒 번호부를 펼친 기록**")
    st.markdown('<div class="log">' + "".join(f"<div>{line}</div>" for line in c["log"]) + "</div>", unsafe_allow_html=True)
    if c["found"] is None:
        st.caption("💡 한 번 펼칠 때 후보가 얼마나 줄었는지 보세요. 어디를 펼쳐야 가장 많이 지울 수 있을까요?")


def show_play():
    i = S["i"]
    case, c = CASES[i], S["cases"][i]
    # 이전 현관문(첫 문이면 시작 안내)으로 돌아가는 버튼. 이미 판정한 문은 결과를 다시 볼 수 있어요.
    back = st.button("⬅️ 이전 현관문" if i else "⬅️ 시작 안내로", key=f"back{i}")
    if back:
        if i:
            S["i"] -= 1
        else:
            S["step"] = "intro"
        st.rerun()
    st.markdown(f"### 🚪 {i + 1} / {len(CASES)} · 다람쥐아파트 {case['door']}")
    st.progress(i / len(CASES))
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(notice_html(case, c["attach"]), unsafe_allow_html=True)
        if c["verdict"] is None:
            t1, t2 = st.columns(2)
            if t1.button("🔥 열 테스트", key=f"heat{i}", width="stretch", disabled=c["paper"]):
                c["paper"] = True
                st.rerun()
            if t2.button("✋ 떼기 테스트", key=f"peel{i}", width="stretch", disabled=c["attach"]):
                c["attach"] = True
                st.rerun()
        if c["paper"]:
            st.markdown(f'<div class="tool-res">{PAPER[case["paper"]]}</div>', unsafe_allow_html=True)
        if c["attach"]:
            st.markdown(f'<div class="tool-res">{ATTACH[case["attach"]]}</div>', unsafe_allow_html=True)
        if c["verdict"] is None:
            show_book_controls(c, case)
        show_book_log(c)
    with right:
        show_book(c, case)

    st.divider()
    if c["verdict"] is None:
        # 감으로 찍지 않도록, 도구 3가지로 모두 확인해야 판정 버튼이 열려요.
        todo = [name for name, done in (("🔥 열 테스트", c["paper"]), ("✋ 떼기 테스트", c["attach"]),
                                         ("📒 번호부 찾기", c["found"] is not None)) if not done]
        st.markdown("**판정하기** · 확인한 단서로 골라요.")
        if todo:
            st.info("아직 확인하지 않은 단서가 있어요: " + ", ".join(todo) + ". 모두 확인하면 판정할 수 있어요.")
        v1, v2 = st.columns(2)
        verdict = None
        if v1.button("✅ 진짜 안내서예요", key=f"real{i}", width="stretch", disabled=bool(todo)):
            verdict = "real"
        if v2.button("🚫 가짜예요 · 떼고 신고", key=f"fake{i}", width="stretch", type="primary", disabled=bool(todo)):
            verdict = "fake"
        if verdict:
            c["verdict"] = verdict
            dd.stamp("14")
            st.rerun()
        return

    correct = (c["verdict"] == "real") == case["real"]
    answer = "진짜" if case["real"] else "가짜"
    if correct:
        st.success(f"정답! {case['door']} 안내서는 **{answer}**였어요.")
    else:
        st.error(f"아쉬워요. {case['door']} 안내서는 **{answer}**였어요.")
    st.write(case["lesson"])
    if st.button("다음 현관문으로 ➡️" if i + 1 < len(CASES) else "감별 결과 보기 📋", type="primary", width="stretch"):
        if i + 1 < len(CASES):
            S["i"] += 1
        else:
            S["step"] = "end"
        dd.scroll_top()  # 다음 현관문은 위에서부터 보여 줘요.
        st.rerun()


def linear_steps(number):
    """번호부를 처음부터 한 칸씩 넘겼다면 몇 번 만에 끝났을지(없으면 64칸을 다 봐야 해요)."""
    return BOOK.index(number) + 1 if number in BOOK else len(BOOK)


def show_end():
    results = [(case, c, (c["verdict"] == "real") == case["real"]) for case, c in zip(CASES, S["cases"])]
    score = sum(ok for _, _, ok in results)
    searched = [(case, c) for case, c, _ in results if c["found"] is not None]
    probes = sum(c["probes"] for _, c in searched)
    linear = sum(linear_steps(case["number"]) for case, _ in searched)
    if not S["recorded"]:
        S["recorded"] = True
        dd.record("notice", {"plays": 1, "perfect": 1 if score == len(CASES) else 0,
                             **{f"h{k}_ok": 1 for k, (_, _, ok) in enumerate(results) if ok}})
        dd.note_mine("notice", f"{score}/{len(CASES)} 감별 · 번호부 {probes}번 펼침")
        S["hall"] = dd.save_hall(
            "notice", {"score": score, "probes": probes},
            lambda old, new: (new["score"], -new["probes"]) > (old.get("score", 0), -old.get("probes", 10**6)),
        )

    if st.button("⬅️ 마지막 현관문 다시 보기", key="back_end"):
        S["step"], S["i"] = "play", len(CASES) - 1
        st.rerun()
    st.title("📋 감별 결과")
    st.metric("맞힌 안내서", f"{score} / {len(CASES)}")
    dd.show_hall_note(S.get("hall"))
    st.markdown(
        "".join(f"- {'✅' if ok else '❌'} **{case['door']}** ({'진짜' if case['real'] else '가짜'}) · "
                f"번호부 {c['probes']}번 펼침\n" for case, c, ok in results)
    )

    st.markdown("#### 📒 번호부를 절반씩 줄이면 왜 빠를까? (이진 탐색)")
    if searched:
        near = sum(c["near_mid"] for _, c in searched)
        within = sum(1 for _, c in searched if c["probes"] <= GOAL)
        st.write(f"이번에 번호부를 **{probes}번** 펼쳤어요. 처음부터 한 칸씩 넘겼다면 **{linear}번** 봐야 했어요. "
                 f"{len(searched)}장 중 **{within}장**을 목표({GOAL}번) 안에 끝냈고, 펼친 칸 {probes}개 중 "
                 f"**{near}개**가 남은 후보의 가운데 근처였어요.")
    st.markdown(
        "가장자리를 펼치면 운이 좋을 때만 많이 지워지고, 대부분은 한두 칸밖에 못 지워요. "
        "정렬된 64칸에서 **가운데**를 펼치면, 찾는 번호가 앞쪽인지 뒤쪽인지에 상관없이 후보가 항상 절반으로 줄어요. "
        "**64 → 32 → 16 → 8 → 4 → 2 → 1**, 아무리 많아도 **6~7번**이면 끝나요. "
        "한 칸씩 넘기면(순차 탐색) 최대 64번이 걸려요. 번호부가 1,000칸이 되어도 이진 탐색은 10번 정도면 충분해요. "
        "단, 번호 순서대로 **정렬돼 있어야** 쓸 수 있어요."
    )

    st.markdown("#### 🏠 실제로 안내서를 받았다면")
    st.success(
        "**안내서에 적힌 번호로 전화하거나 QR을 찍지 마세요.** "
        "우편고객센터(1588-1300)나 가까운 우체국에 직접 연락해 진짜 우편물이 있는지 확인하세요."
    )
    st.markdown(
        "- 진짜 안내서는 감열지에, 쉽게 떨어지고 흔적이 안 남는 방식으로 붙어 있어요.\n"
        "- 투명테이프로 붙였거나 떼어 낸 뒤 접착 흔적이 남으면 위조를 의심하세요.\n"
        "- 우체국은 안내서·전화·인터넷 어디서도 주민등록번호나 계좌번호를 요구하지 않아요.\n"
        "- 위조가 의심되면 가까운 우체국이나 경찰(112)에 알려 주세요."
    )
    st.caption("참고: 우정사업본부 위조 우편물 도착안내서 주의 안내(2026년 9월 29일 보도). 게임 속 번호와 안내서는 모두 가상이에요.")

    me = dd.citizen()
    show_result_card(
        {
            "color": "#9A3412", "place": "다람쥐아파트 관리사무소", "game": "가짜 안내서 감별소", "emoji": "📬",
            "title": "감별 완료" if score == len(CASES) else "감별 결과",
            "subtitle": f"{score}/{len(CASES)} 감별!",
            "stats": [("맞힌 안내서", f"{score} / {len(CASES)}"), ("번호부 펼친 횟수", f"{probes}번"),
                      ("한 칸씩 넘겼다면", f"{linear}번"), ("찾는 방법", "이진 탐색")],
            "sections": [("🏠 진짜 안내서를 받았다면", ["적힌 번호 대신 1588-1300이나 우체국에 직접 확인", "주민등록번호·계좌번호를 묻는 안내서는 가짜"])],
            "nickname": me["nickname"] if me else "",
            "mascot": "trophy" if score == len(CASES) else "retry",
        },
        "jamkkan_notice_card.png",
    )
    if st.button("🔄 처음부터 다시 감별하기", width="stretch"):
        st.session_state[KEY] = fresh()
        st.rerun()


if S["step"] == "intro":
    show_intro()
elif S["step"] == "play":
    show_play()
else:
    show_end()
