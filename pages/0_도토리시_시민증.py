"""도토리시 시민증: 닉네임만으로 로그인해 명예의 전당에 기록을 남기는 페이지.
이름·학번·이메일·비밀번호는 받지 않아요. 창을 닫으면 로그아웃돼요.
"""
from html import escape

import streamlit as st
from mascot_ui import id_photo, show_key_question, show_mascot
import dotori_data as dd
from card_ui import show_result_card
from firebase_support import ConnectionProblem, explain


st.title("🪪 도토리시 시민증")
show_key_question("닉네임 하나로 시민증을 만들면 **명예의 전당**에 내 최고 기록이 올라가요.", "🪪")


def show_stamps():
    """시민증 도장판: 도토리시 13곳에서 받은 도장(이번 방문 기준)."""
    got = dd.stamps()
    total = len(dd.STAMP_PLACES)
    st.subheader(f"🏅 시민증 도장판  {len(got)}/{total}")
    st.progress(len(got) / total)
    cells = []
    for code, (icon, place, how) in dd.STAMP_PLACES.items():
        if code in got:
            cells.append(
                f'<div class="stp on"><div class="ring">{icon}</div><b>{escape(place)}</b>'
                f'<small>{got[code]} 받음</small></div>'
            )
        else:
            cells.append(
                f'<div class="stp"><div class="ring">{icon}</div><b>{escape(place)}</b>'
                f'<small>{escape(how)}</small></div>'
            )
    st.markdown(
        """<style>
        .stpgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:10px;margin:8px 0 12px;}
        .stp{background:#F7F7F4;border:2px dashed #C9CFCB;border-radius:18px;padding:12px 8px;text-align:center;
          word-break:keep-all;line-height:1.35;color:#6B7280;}
        .stp .ring{width:62px;height:62px;margin:0 auto 6px;border-radius:50%;border:3px dashed #C9CFCB;
          display:flex;align-items:center;justify-content:center;font-size:30px;filter:grayscale(1);opacity:.45;}
        .stp b{display:block;font-size:.95rem;color:#52616B;}
        .stp small{display:block;font-size:.8rem;margin-top:3px;}
        .stp.on{background:#FFF8E6;border:2px solid #E2C98A;color:#6B4A1E;}
        .stp.on .ring{border:3px solid #B42318;color:#B42318;filter:none;opacity:1;transform:rotate(-8deg);
          box-shadow:inset 0 0 0 3px #FFF8E6,inset 0 0 0 5px #B42318;background:#FFF;}
        .stp.on b{color:#20483F;}
        .stp.on small{color:#B42318;font-weight:800;}
        .stp-done{background:linear-gradient(135deg,#FFF4D6,#E8F4EC);border:3px solid #B42318;border-radius:20px;
          padding:14px;text-align:center;font-weight:900;color:#20483F;font-size:1.2rem;margin-bottom:10px;}
        </style>"""
        + ('<div class="stp-done">🎖️ 13곳 도장 완성! 도토리시 명예 시민이에요.</div>' if len(got) == total else "")
        + '<div class="stpgrid">' + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )
    st.caption("도장은 시민증이 없어도 모을 수 있어요. 저장하지 않아서 창을 닫으면 처음부터 다시 모아요.")
    if len(got) == total:
        # 13곳을 모두 모으면 깡지와 함께하는 명예 시민증 카드를 사진으로 저장할 수 있어요.
        me = dd.citizen()
        st.markdown("#### 🎖️ 명예 시민증")
        show_result_card(
            {
                "color": "#B7791F", "place": "시민 등록소", "game": "명예 시민증", "emoji": "🎖️",
                "title": "도토리시 명예 시민", "subtitle": "13곳 완주!",
                "stats": [("모은 도장", f"{len(got)} / {total}"), ("완주한 시각", max(got.values()))],
                "sections": [("🏅 다녀온 곳", [" · ".join(place for _, place, _ in dd.STAMP_PLACES.values())])],
                "nickname": me["nickname"] if me else "", "mascot": "trophy",
            },
            "jamkkan_honorary_citizen.png",
        )


account = dd.citizen()

if account:
    # 시민증 사진 자리에 깡지 증명사진을 넣어요. (사진 파일이 없으면 다람쥐 그림으로 대신해요.)
    try:
        photo_html = (
            f'<img src="data:image/png;base64,{id_photo("ggangji_cream.png")}" alt="깡지 증명사진" '
            'style="width:116px;height:102px;object-fit:cover;border:4px solid #fff;border-radius:6px;'
            'box-shadow:0 2px 8px rgba(0,0,0,.2);">'
        )
    except Exception:
        photo_html = '<div style="font-size:64px;">🐿️</div>'
    st.markdown(
        '<div style="background:linear-gradient(135deg,#FFF4D6,#E8F4EC);border:3px solid #E2C98A;border-radius:22px;'
        'padding:20px;margin:6px 0 14px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;">'
        f'{photo_html}<div style="flex:1;min-width:180px;">'
        '<div style="font-weight:800;color:#6B4A1E;">도토리시 시민증</div>'
        f'<div style="font-size:1.8rem;font-weight:900;color:#20483F;">{escape(account["nickname"])}</div>'
        '<div style="color:#52616B;font-weight:600;">게임을 끝내면 최고 기록이 명예의 전당에 저장돼요.</div></div></div>',
        unsafe_allow_html=True,
    )

    show_stamps()

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

    show_stamps()

st.page_link("pages/13_도토리시_통계청.py", label="도토리시 통계청에서 모두의 기록 보기", icon="📊")
