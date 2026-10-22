"""도토리시 시민증: 닉네임만으로 로그인해 명예의 전당에 기록을 남기는 페이지.
이름·학번·이메일·비밀번호는 받지 않아요. 창을 닫으면 로그아웃돼요.
"""
from html import escape

import streamlit as st
from mascot_ui import show_key_question, show_mascot
import dotori_data as dd
from firebase_support import ConnectionProblem, explain


st.title("🪪 도토리시 시민증")
show_key_question("닉네임 하나로 시민증을 만들면 **명예의 전당**에 내 최고 기록이 올라가요.", "🪪")

account = dd.citizen()

if account:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#FFF4D6,#E8F4EC);border:3px solid #E2C98A;border-radius:22px;'
        'padding:20px;margin:6px 0 14px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;">'
        '<div style="font-size:64px;">🐿️</div><div style="flex:1;min-width:180px;">'
        '<div style="font-weight:800;color:#6B4A1E;">도토리시 시민증</div>'
        f'<div style="font-size:1.8rem;font-weight:900;color:#20483F;">{escape(account["nickname"])}</div>'
        '<div style="color:#52616B;font-weight:600;">게임을 끝내면 최고 기록이 명예의 전당에 저장돼요.</div></div></div>',
        unsafe_allow_html=True,
    )

    st.subheader("🏆 명예의 전당 속 내 순위")
    rows = []
    for game in dd.HALL_SORT:
        entries = sorted(dd.hall(game), key=dd.HALL_SORT[game])
        mine = next((i for i, r in enumerate(entries) if r["uid"] == account["uid"]), None)
        icon, name = dd.GAMES[game]
        rows.append({"게임": f"{icon} {name}", "내 순위": f"{mine + 1}위 / {len(entries)}명" if mine is not None else "아직 기록 없음"})
    st.dataframe(rows, hide_index=True, width="stretch")
    st.caption("기록은 최대 1분 동안 같은 결과를 보여 줘요.")

    st.subheader("📒 이번 방문에서 한 기록")
    mine = st.session_state.get(dd.MY, [])
    if mine:
        for game, text, at in reversed(mine):
            icon, name = dd.GAMES.get(game, ("🎮", game))
            st.markdown(f"- `{at}` {icon} **{name}** · {escape(text)}")
    else:
        st.info("아직 끝낸 게임이 없어요. 왼쪽 메뉴에서 게임을 골라 보세요!")

    if st.button("🚪 로그아웃", width="stretch"):
        dd.logout()
        st.rerun()
else:
    show_mascot("welcome", "로그인하지 않아도 모든 게임을 할 수 있어요. 기록을 남기고 싶을 때만 만들어요!", width=100)
    with st.form("dotori_login"):
        nickname = st.text_input("닉네임 (한글·영문·숫자·밑줄 2~12자)", max_chars=12, placeholder="예: 도토리탐정")
        ok = st.form_submit_button("🪪 시민증 만들기", type="primary")
    if ok:
        try:
            with st.spinner("시민증을 만들고 있어요…"):
                name = dd.login(nickname)
            st.success(f"환영해요, {name}님! 이제 게임 기록이 명예의 전당에 올라가요.")
            st.rerun()
        except ConnectionProblem as exc:
            if exc.reason == "NICKNAME_TAKEN":
                st.error("오늘 다른 사람이 쓰고 있는 닉네임이에요. 다른 닉네임을 골라 주세요.")
            else:
                st.error(explain(exc))

    st.markdown("#### 알아 두세요")
    st.markdown(
        "- **실제 이름·학번·학교는 닉네임으로 쓰지 마세요.** 명예의 전당에 공개돼요.\n"
        "- 비밀번호는 없어요. **창을 닫거나 새로고침하면 로그아웃**돼요.\n"
        "- 같은 닉네임은 **하루 동안** 처음 만든 사람만 쓸 수 있어요. 하루가 지나면 다른 사람도 쓸 수 있어요.\n"
        "- 다른 사람이 불쾌할 수 있는 닉네임은 쓰지 않아요."
    )

st.page_link("pages/13_도토리시_통계청.py", label="도토리시 통계청에서 모두의 기록 보기", icon="📊")
