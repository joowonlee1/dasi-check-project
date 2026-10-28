"""도토리시 통계청: 게임에서 모인 익명 통계(+1 숫자)와 명예의 전당을 보여 주는 페이지.
처음에는 모든 숫자가 0에서 시작하고, 실제 이용자가 게임을 끝낼 때마다 늘어나요(가짜 데이터 없음).
"""
from html import escape

import pandas as pd
import streamlit as st
from mascot_ui import show_key_question, show_mascot
import dotori_data as dd

GREEN = "#0F766E"
ENDINGS = [("best", "⭐ 든든한 손주"), ("good", "🟢 지켜 냈다"), ("close", "🟠 아슬아슬"), ("bad", "🔴 송금 완료")]
FAKENEWS_STAGES = ["1단계", "2단계", "3단계", "4단계", "5단계"]
MAFIA_CASES = ["사건 1", "사건 2", "사건 3"]
NONO_STAGES = ["📱 스마트폰", "🔒 자물쇠", "🔳 QR 코드"]
NOTICE_DOORS = ["101호 (가짜)", "102호 (진짜)", "103호 (가짜)", "104호 (진짜)", "105호 (가짜)"]
# 피싱 필터 문자(보낸 곳, 진짜 여부) — 피싱 필터 만들기 페이지의 문자 순서와 같아요.
FILTER_MSGS = [
    [("도토리택배", "진짜"), ("010-48○○", "가짜"), ("도토리수학학원", "진짜"), ("070 국제택배", "가짜"), ("엄마", "진짜"), ("도토리고 가정통신문", "진짜")],
    [("010-73○○ 엄마 사칭", "가짜"), ("동아리 총무", "진짜"), ("○○은행 사칭 앱 설치", "가짜"), ("○○은행 승인 알림", "진짜"),
     ("도토리지검 사칭", "가짜"), ("친구 지후", "진짜"), ("도토리고 앱 안내", "진짜"), ("도토리병원", "진짜")],
    [("010-91○○ 택배", "가짜"), ("010-35○○ 아빠 사칭", "가짜"), ("친구 서연(계정 도용)", "가짜"), ("친구 민준", "진짜"), ("도토리고 학부모 앱", "진짜"),
     ("도토리치과", "진짜"), ("○○카드 사칭", "가짜"), ("엄마", "진짜"), ("도토리지검 사칭", "가짜"), ("택배 기사", "진짜")],
]
CODES = [a + b + c + d for a in "QS" for b in "RE" for c in "IT" for d in "HB"]

st.title("📈 도토리시 통계청")
show_key_question("시민들이 게임에서 남긴 **진짜 기록**으로, 사람들이 **어디서 많이 속는지** 살펴봐요.", "📊")
show_mascot("chart", "숫자는 처음엔 0이에요. 누군가 게임을 끝낼 때마다 하나씩 늘어나요!", width=100)
dd.stamp("13")


# 숫자 카드(st.metric)를 색 있는 카드로 꾸며요.
st.markdown("""<style>
[data-testid=stMetric]{background:linear-gradient(135deg,#F0FDFA,#FFFFFF);border:2px solid #99F6E4;border-radius:16px;padding:12px 16px}
[data-testid=stMetricLabel] p{font-weight:800!important;color:#115E59!important}
[data-testid=stMetricValue]{font-size:2rem!important;font-weight:900!important;color:#0F766E!important}
.sb-row{display:grid;grid-template-columns:minmax(120px,38%) 1fr 64px;gap:10px;align-items:center;margin:7px 0}
.sb-label{font-weight:700;color:#1F2937;line-height:1.35;word-break:keep-all;font-size:.95rem}
.sb-track{height:24px;background:#EEF2F1;border-radius:999px;overflow:hidden}
.sb-fill{height:100%;border-radius:999px;min-width:6px;transition:width .6s}
.sb-val{font-weight:900;text-align:right;color:#0F766E}
.sb-box{background:#fff;border:1.5px solid #E2E8F0;border-radius:16px;padding:10px 16px;margin:6px 0 4px}
@media (max-width:640px){.sb-row{grid-template-columns:1fr 54px}.sb-label{grid-column:1/3}}
</style>""", unsafe_allow_html=True)


def bar(rows, label, value, unit="%"):
    """막대그래프: 이름을 자르지 않고 다 보여 주고, 막대 끝에 숫자를 붙여요. 가장 높은 막대는 주황색으로 강조해요."""
    rows = list(rows)
    if not rows:
        return
    top = max(v for _, v in rows)
    scale = 100 if unit == "%" else max(top, 1)
    html_rows = []
    for name, v in rows:
        color = "#F97316" if top > 0 and v == top else GREEN
        width = 0 if not v else max(3, min(100, v / scale * 100))
        html_rows.append(f'<div class="sb-row"><div class="sb-label">{escape(str(name))}</div>'
                         f'<div class="sb-track"><div class="sb-fill" style="width:{width:.1f}%;background:{color}"></div></div>'
                         f'<div class="sb-val">{v:g}{unit}</div></div>')
    note = "" if top > 0 else '<div style="color:#64748B;font-size:.9rem;margin-top:4px">👏 아직 모두 0이에요. 기록이 쌓이면 막대가 자라요.</div>'
    st.markdown(f'<div class="sb-box"><div style="font-size:.85rem;color:#64748B;font-weight:700">{escape(value)}</div>'
                + "".join(html_rows) + note + "</div>", unsafe_allow_html=True)


def empty():
    st.info("아직 모인 기록이 없어요. 이 게임을 끝까지 하면 첫 기록이 생겨요!")


tab_stats, tab_hall, tab_how = st.tabs(["📊 게임별 통계", "🏆 명예의 전당", "🔒 어떻게 모으나요?"])

with tab_stats:
    game = st.pills("게임 고르기", list(dd.GAMES), default="filter", key="stats_game",
                    format_func=lambda g: f"{dd.GAMES[g][0]} {dd.GAMES[g][1]}") or "filter"
    data = dd.stats(game)

    if game == "grandma":
        plays = data.get("plays", 0)
        if not plays:
            empty()
        else:
            st.metric("도전 횟수", f"{plays}번")
            bar([(name, dd.pct(data.get(f"end_{k}", 0), plays)) for k, name in ENDINGS], "결말", "비율(%)")
            st.caption("‘송금 완료’ 비율이 높다면, 가족이 속고 있을 때 끼어드는 연습이 더 필요하다는 뜻이에요.")

    elif game == "escape":
        plays = data.get("plays", 0)
        if not plays:
            empty()
        else:
            a, b, c = st.columns(3)
            a.metric("도전 횟수", f"{plays}번")
            b.metric("탈출 성공", f"{dd.pct(data.get('escaped', 0), plays)}%")
            c.metric("힌트 없이 탈출", f"{dd.pct(data.get('nohint', 0), plays)}%")
            bar([(f"🔒 잠금 {k}", dd.pct(data.get(f"lock{k}", 0), plays)) for k in (1, 2, 3)], "잠금", "푼 비율(%)")
            # 결말 나누기: 포기와 시간 초과 실패를 따로 세요.
            gave = data.get("gaveup", 0)
            bar([("🔓 탈출 성공", dd.pct(data.get("escaped", 0), plays)), ("🏳️ 포기", dd.pct(gave, plays)),
                 ("⏳ 시간 초과", dd.pct(max(0, plays - data.get("escaped", 0) - gave), plays))], "결말", "결말 비율(%)")
            st.caption("실패한 도전도 함께 세요. 비율이 뚝 떨어지는 잠금이 사람들이 가장 많이 막히는 곳이에요.")

    elif game == "fakenews":
        rows = [(name, round(data.get(f"s{i}_pctsum", 0) / data[f"s{i}_plays"]) if data.get(f"s{i}_plays") else 0)
                for i, name in enumerate(FAKENEWS_STAGES)]
        if not any(data.get(f"s{i}_plays") for i in range(5)):
            empty()
        else:
            cols = st.columns(5)
            for i, name in enumerate(FAKENEWS_STAGES):
                cols[i].metric(name, f"{data.get(f's{i}_plays', 0)}판")
            bar(rows, "단계", "평균 지킨 주민(%)")
            st.caption("단계가 올라갈수록 평균이 떨어진다면, 수법이 교묘해질수록 막기 어렵다는 뜻이에요.")

    elif game == "coping":
        plays = data.get("plays", 0)
        if not plays:
            empty()
        else:
            st.metric("테스트한 사람", f"{plays}명")
            top = sorted(((c, dd.pct(data.get(f"t_{c}", 0), plays)) for c in CODES), key=lambda x: -x[1])
            bar([t for t in top if t[1]], "유형", "비율(%)")
            st.caption("유형 이름과 뜻은 ‘대처유형 테스트’의 16가지 유형 탭에서 볼 수 있어요.")

    elif game == "mafia":
        if not any(data.get(f"c{i}_plays") for i in range(3)):
            empty()
        else:
            cols = st.columns(3)
            for i, name in enumerate(MAFIA_CASES):
                cols[i].metric(name, f"{data.get(f'c{i}_plays', 0)}번 수사")
            bar([(name, dd.pct(data.get(f"c{i}_win", 0), data.get(f"c{i}_plays", 0))) for i, name in enumerate(MAFIA_CASES)],
                "사건", "마피아를 찾은 비율(%)")
            st.caption("찾은 비율이 낮은 사건일수록 함정이 잘 먹힌 사건이에요.")

    elif game == "memo":
        plays = data.get("plays", 0)
        if not plays:
            empty()
        else:
            a, b, c = st.columns(3)
            a.metric("검거 횟수", f"{plays}번")
            b.metric("별 3개", f"{dd.pct(data.get('star3', 0), plays)}%")
            c.metric("한 번에 진짜 지목", f"{dd.pct(data.get('first_pick', 0), plays)}%")
            bar([(f"⭐ {k}개", dd.pct(data.get(f"star{k}", 0), plays)) for k in (1, 2, 3)], "별", "비율(%)")

    elif game == "filter":
        if not any(data.get(f"s{i}_runs") for i in range(3)):
            empty()
        else:
            cols = st.columns(3)
            for i in range(3):
                runs = data.get(f"s{i}_runs", 0)
                cols[i].metric(f"{i + 1}단계 목표 달성", f"{dd.pct(data.get(f's{i}_clear', 0), runs)}%", help=f"필터 실행 {runs}번 기준")
            stage = st.radio("어느 단계의 문자를 볼까요?", [0, 1, 2], format_func=lambda i: f"{i + 1}단계", horizontal=True)
            runs = data.get(f"s{stage}_runs", 0)
            if runs:
                rows = sorted(
                    ((f"문자 {i + 1} · {who} ({kind})", dd.pct(data.get(f"s{stage}_m{i}_wrong", 0), runs))
                     for i, (who, kind) in enumerate(FILTER_MSGS[stage])),
                    key=lambda x: -x[1],
                )
                st.markdown("**🎯 많이 틀린 문자 순서** (필터를 실행했을 때 그 문자를 잘못 거른 비율)")
                bar(rows, "문자", "틀린 비율(%)")
                st.caption("(가짜) 문자를 많이 틀렸다면 통과시킨 것(미탐), (진짜) 문자를 많이 틀렸다면 막아 버린 것(오탐)이에요.")
            else:
                st.info("이 단계는 아직 실행 기록이 없어요.")

    elif game == "nono":
        if not any(data.get(f"s{i}_clear") for i in range(3)):
            empty()
        else:
            cols = st.columns(3)
            for i, name in enumerate(NONO_STAGES):
                cols[i].metric(name, f"{data.get(f's{i}_clear', 0)}번 복원")
            bar([(name, dd.pct(data.get(f"s{i}_nohint", 0), data.get(f"s{i}_clear", 0))) for i, name in enumerate(NONO_STAGES)],
                "그림", "힌트 없이 푼 비율(%)")

    elif game == "notice":
        if data.get("v3_plays",0):
            st.markdown("#### 자료 조사 활동")
            a,b=st.columns(2)
            a.metric("조사 완료",f"{data['v3_plays']}회")
            b.metric("첫 제출에서 3건 모두 정확",f"{dd.pct(data.get('v3_perfect',0),data['v3_plays'])}%")
            st.caption("자료 조사와 재판단을 모두 마쳐야 완료됩니다. 정확도는 첫 제출 기준이며 이전 활동과 따로 집계합니다.")
        st.markdown("#### 이전 3건 확인 활동")
        plays = data.get("v2_plays", 0)
        if not plays:
            empty()
        else:
            a, b = st.columns(2)
            a.metric("이전 활동 완료 횟수", f"{plays}회")
            b.metric("3건 모두 판단·근거 일치", f"{dd.pct(data.get('v2_perfect', 0), plays)}%")
            bar([(name, dd.pct(data.get(f"v2_h{i}_ok", 0), plays))
                 for i,name in enumerate(["101호 · 정상 확인","102호 · 위조 확인","103호 · 판단 보류"])],
                "안내서", "판단과 근거 일치 비율(%)")
        st.caption("새 3건 활동만 집계해요. 이전 5장 활동 기록은 삭제하지 않고 별도로 보존돼요. 명예의 전당은 맞힌 비율로 비교해요.")

    st.caption("방금 끝낸 게임의 결과는 여기에 보이기까지 최대 1분쯤 걸릴 수 있어요(1분마다 새로 읽어요). 이름 없이 숫자만 모은 교육용 기록이에요.")

with tab_hall:
    hall_game = st.pills("게임 고르기", list(dd.HALL_SORT), default="filter", key="hall_game",
                         format_func=lambda g: f"{dd.GAMES[g][0]} {dd.GAMES[g][1]}") or "filter"
    entries = sorted(dd.hall(hall_game), key=dd.HALL_SORT[hall_game])
    me = dd.citizen()
    if not entries:
        st.info("아직 명예의 전당에 오른 시민이 없어요. 시민증을 만들고 첫 주인공이 되어 보세요!")
    else:
        medals = ["🥇", "🥈", "🥉"]
        rows, rank, prev = [], 0, None
        for i, r in enumerate(entries[:20]):
            key = dd.HALL_SORT[hall_game](r)
            if key != prev:
                rank, prev = i + 1, key
            name = r.get("nickname", "시민") + ("  ⭐ 나" if me and r["uid"] == me["uid"] else "")
            rows.append({"순위": medals[rank - 1] if rank <= 3 else f"{rank}위", "닉네임": name, "기록": dd.HALL_TEXT[hall_game](r)})
        st.dataframe(rows, hide_index=True, width="stretch")
        st.caption(f"전체 {len(entries)}명 중 상위 20명 · 기록이 같으면 같은 순위예요.")
    if hall_game == "escape":
        st.caption("방탈출 순위: 탈출 성공 → 많이 푼 잠금 → (같으면 포기보다 시간 초과가 위) → 힌트 적은 순 → 재검토 적은 순 → 빠른 순. 실패한 도전도 기록돼요.")
        # 예전 방탈출 페이지에 있던 '탈출 랭킹' 기록도 지우지 않고 그대로 보여 줘요.
        with st.expander("📜 예전 방탈출 탈출 랭킹 기록 보기"):
            try:
                from firebase_support import config as fb_config, rankings as old_rankings
                old = old_rankings(fb_config()[1])
                if old:
                    st.dataframe(old, hide_index=True, width="stretch")
                else:
                    st.caption("예전 기록이 없어요.")
            except Exception:
                st.caption("예전 기록을 불러오지 못했어요.")
    st.caption("🧭 대처유형 테스트는 점수를 겨루는 게임이 아니라서 명예의 전당이 없어요. 결과 분포는 ‘게임별 통계’에서 볼 수 있어요.")
    if not me:
        st.page_link("pages/0_도토리시_시민증.py", label="시민증(닉네임)을 만들면 명예의 전당에 올라갈 수 있어요", icon="🪪")

with tab_how:
    st.markdown("### 🔄 데이터가 모이는 과정")
    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:8px 0 14px;">'
        + "".join(
            f'<div style="background:#F4F8F6;border:1.5px solid #D7E2DD;border-radius:16px;padding:12px;text-align:center;word-break:keep-all;">'
            f'<div style="font-size:30px;">{ic}</div><b>{escape(t)}</b><div style="font-size:.9rem;color:#33524A;">{escape(d)}</div></div>'
            for ic, t, d in [
                ("🎮", "① 수집", "게임을 끝내면 결과가 나와요"),
                ("☁️", "② 저장", "Firebase 데이터베이스의 숫자 칸에 +1"),
                ("🧮", "③ 집계", "칸끼리 나눠 비율(%)을 계산"),
                ("📊", "④ 시각화", "이 페이지에서 그래프로 보여 줘요"),
            ]
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("### 🔒 개인정보는 이렇게 지켜요")
    st.markdown(
        "- **이름·학번·이메일은 받지 않아요.** 통계에는 ‘몇 번 나왔는지’ 숫자만 더해요. 시민증의 비밀 숫자는 이 앱이 저장하지 않고 Firebase가 암호화해서 보관해요.\n"
        "- 누가 어떤 답을 했는지는 저장하지 않아요. 예를 들어 대처유형 테스트는 답변 없이 결과 유형 칸만 +1 해요.\n"
        "- 명예의 전당에는 **시민증 닉네임과 점수만** 올라가요. 닉네임은 누구나 볼 수 있으니 실제 이름을 넣을지는 알고 정해 주세요.\n"
        "- 데이터베이스 규칙으로 ‘숫자를 늘리기만’ 할 수 있게 막고, 남의 명예의 전당 기록은 고칠 수 없게 했어요."
    )
