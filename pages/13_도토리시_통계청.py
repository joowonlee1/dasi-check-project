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
# 피싱 필터 문자(보낸 곳, 진짜 여부) — 피싱 필터 만들기 페이지의 문자 순서와 같아요.
FILTER_MSGS = [
    [("도토리택배", "진짜"), ("010-48○○", "가짜"), ("도토리수학학원", "진짜"), ("070 국제택배", "가짜"), ("엄마", "진짜"), ("도토리고 가정통신문", "진짜")],
    [("010-73○○ 엄마 사칭", "가짜"), ("동아리 총무", "진짜"), ("○○은행 사칭 앱 설치", "가짜"), ("○○은행 승인 알림", "진짜"),
     ("도토리지검 사칭", "가짜"), ("친구 지후", "진짜"), ("도토리고 앱 안내", "진짜"), ("도토리병원", "진짜")],
    [("010-91○○ 택배", "가짜"), ("010-35○○ 아빠 사칭", "가짜"), ("친구 서연(계정 도용)", "가짜"), ("친구 민준", "진짜"), ("도토리고 학부모 앱", "진짜"),
     ("도토리치과", "진짜"), ("○○카드 사칭", "가짜"), ("엄마", "진짜"), ("도토리지검 사칭", "가짜"), ("택배 기사", "진짜")],
]
CODES = [a + b + c + d for a in "QS" for b in "RE" for c in "IT" for d in "HB"]

st.title("📊 도토리시 통계청")
show_key_question("시민들이 게임에서 남긴 **진짜 기록**으로, 사람들이 **어디서 많이 속는지** 살펴봐요.", "📊")
show_mascot("hint", "숫자는 처음엔 0이에요. 누군가 게임을 끝낼 때마다 하나씩 늘어나요!", width=100)


def bar(rows, label, value, unit="%"):
    df = pd.DataFrame(rows, columns=[label, value])
    st.bar_chart(df, x=label, y=value, horizontal=True, color=GREEN, height=max(160, 46 * len(rows)))


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

    st.caption("통계는 최대 1분 동안 같은 결과를 보여 줘요. 이름 없이 숫자만 모은 교육용 기록이에요.")

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
        "- **이름·학번·이메일·비밀번호를 받지 않아요.** 통계에는 ‘몇 번 나왔는지’ 숫자만 더해요.\n"
        "- 누가 어떤 답을 했는지는 저장하지 않아요. 예를 들어 대처유형 테스트는 답변 없이 결과 유형 칸만 +1 해요.\n"
        "- 명예의 전당에는 **시민증 닉네임과 점수만** 올라가요. 실제 이름은 닉네임으로 쓰지 마세요.\n"
        "- 데이터베이스 규칙으로 ‘숫자를 늘리기만’ 할 수 있게 막고, 남의 명예의 전당 기록은 고칠 수 없게 했어요."
    )
    st.markdown("### 🗂️ 저장 구조 (정보 과목 연계)")
    st.code(
        "stats/                  ← 게임마다 문서 1개\n"
        "  filter: { s0_runs: 12, s0_clear: 9, s0_m2_wrong: 4, ... }\n"
        "  grandma: { plays: 30, end_best: 7, end_bad: 5, ... }\n"
        "halloffame/filter/entries/{익명 번호}: { nickname: \"도토리탐정\", stars: 9, blocks: 9 }\n"
        "citizens/{닉네임}: { uid: 익명 번호, created_at: 만든 시각 }",
        language="text",
    )
    st.caption("위 숫자는 저장 모양을 보여 주는 예시예요. 실제 통계는 ‘게임별 통계’ 탭에서 확인하세요.")
