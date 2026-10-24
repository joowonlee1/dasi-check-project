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
            "probes": 0, "slips": 0, "found": None, "verdict": None}


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
        label = n if (c["mid"] == i or cls.endswith("hit")) else i + 1
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
        "번호부는 번호 순서로 정렬돼 있어서, 가운데를 펼쳐 보고 절반씩 줄이면 빨리 찾을 수 있어요."
    )
    st.caption("모든 기관·번호는 가상이에요. 실제 안내서의 번호로 전화하거나 QR을 찍지 마세요.")
    if st.button("🔍 감별 시작하기", type="primary", width="stretch"):
        S["step"] = "play"
        st.rerun()


def show_book(c, case):
    st.markdown(f"**📒 번호부 찾기** · 찾는 번호: **내선 {case['number']}**  ·  펼친 횟수 {c['probes']}번")
    st.markdown(book_html(c, case["number"]), unsafe_allow_html=True)
    if c["found"] is True:
        st.success(f"{c['probes']}번 펼쳐서 찾았어요. 번호부에 있는 공식 번호예요.")
        return
    if c["found"] is False:
        st.error(f"{c['probes']}번 펼쳐서 후보가 다 사라졌어요. 번호부에 없는 번호예요!")
        return
    if c["mid"] is None:
        mid = (c["lo"] + c["hi"]) // 2
        st.caption(f"남은 후보 {c['hi'] - c['lo'] + 1}칸 ({c['lo'] + 1}~{c['hi'] + 1}번째)")
        if st.button(f"📖 가운데 {mid + 1}번째 칸 펼치기", key=f"open{S['i']}"):
            c["mid"], c["probes"] = mid, c["probes"] + 1
            st.rerun()
        return
    value = BOOK[c["mid"]]
    st.markdown(f"{c['mid'] + 1}번째 칸은 **내선 {value}** 이에요. 찾는 번호 **{case['number']}** 와 비교하면?")
    a, b, d = st.columns(3)
    pick = None
    if a.button("⬅️ 더 앞에 있어요 (작아요)", key=f"lt{S['i']}", width="stretch"):
        pick = "lt"
    if b.button("🎯 이 번호예요", key=f"eq{S['i']}", width="stretch"):
        pick = "eq"
    if d.button("➡️ 더 뒤에 있어요 (커요)", key=f"gt{S['i']}", width="stretch"):
        pick = "gt"
    if pick:
        target = case["number"]
        right = "lt" if target < value else "gt" if target > value else "eq"
        if pick != right:
            c["slips"] += 1
            st.warning(f"다시 비교해 봐요. {target}은(는) {value}보다 {'작아요' if right == 'lt' else '커요' if right == 'gt' else '같아요'}.")
            return
        if right == "eq":
            c["found"] = True
        elif right == "lt":
            c["hi"] = c["mid"] - 1
        else:
            c["lo"] = c["mid"] + 1
        c["mid"] = None
        if c["found"] is None and c["lo"] > c["hi"]:
            c["found"] = False
        st.rerun()


def show_play():
    i = S["i"]
    case, c = CASES[i], S["cases"][i]
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
    with right:
        show_book(c, case)

    st.divider()
    if c["verdict"] is None:
        st.markdown("**판정하기** · 확인한 단서로 골라요.")
        v1, v2 = st.columns(2)
        verdict = None
        if v1.button("✅ 진짜 안내서예요", key=f"real{i}", width="stretch"):
            verdict = "real"
        if v2.button("🚫 가짜예요 · 떼고 신고", key=f"fake{i}", width="stretch", type="primary"):
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
    unused = [name for name, used in (("열 테스트", c["paper"]), ("떼기 테스트", c["attach"]), ("번호부 찾기", c["found"] is not None)) if not used]
    if unused:
        st.caption("쓰지 않은 도구: " + ", ".join(unused))
    if st.button("다음 현관문으로 ➡️" if i + 1 < len(CASES) else "감별 결과 보기 📋", type="primary", width="stretch"):
        if i + 1 < len(CASES):
            S["i"] += 1
        else:
            S["step"] = "end"
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

    st.title("📋 감별 결과")
    st.metric("맞힌 안내서", f"{score} / {len(CASES)}")
    st.markdown(
        "".join(f"- {'✅' if ok else '❌'} **{case['door']}** ({'진짜' if case['real'] else '가짜'}) · "
                f"번호부 {c['probes']}번 펼침\n" for case, c, ok in results)
    )

    st.markdown("#### 📒 번호부를 절반씩 줄이면 왜 빠를까? (이진 탐색)")
    if searched:
        st.write(f"이번에 번호부를 **{probes}번** 펼쳤어요. 처음부터 한 칸씩 넘겼다면 **{linear}번** 봐야 했어요.")
    st.markdown(
        "정렬된 64칸에서 가운데를 펼치면, 찾는 번호가 앞쪽인지 뒤쪽인지 알 수 있어서 후보가 절반으로 줄어요. "
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
