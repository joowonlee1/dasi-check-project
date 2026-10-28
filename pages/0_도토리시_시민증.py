"""도토리시 시민증: 닉네임만으로 로그인해 명예의 전당에 기록을 남기는 페이지.
이름·학번·이메일은 받지 않아요. 닉네임 + 비밀 숫자 6자리로 다시 들어올 수 있어요.
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
    """시민증 도장판: 도토리시 곳곳에서 받은 도장(시민증이 있으면 저장돼요)."""
    got = dd.stamps()
    total = len(dd.STAMP_PLACES)
    st.subheader(f"🏅 시민증 도장판  {len(got)}/{total}")
    st.progress(len(got) / total)
    cells = []
    for code, (icon, place, how) in dd.STAMP_PLACES.items():
        if code in got:
            cells.append(
                f'<div class="stp on"><div class="ring">{icon}</div><b>{escape(place)}</b>'
                f'<small>{escape(dd.stamp_time(got[code]))} 받음</small></div>'
            )
        else:
            cells.append(
                f'<div class="stp"><div class="ring">{icon}</div><b>{escape(place)}</b>'
                f'<small>{escape(how)}</small></div>'
            )
    st.markdown(
        """<style>
        /* 14곳을 7칸 × 2줄로 꽉 채워 빈 곳이 남지 않게 해요(휴대폰은 4칸씩). */
        .stpgrid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;margin:8px 0 12px;}
        .stp{background:#F7F7F4;border:2px dashed #C9CFCB;border-radius:16px;padding:10px 4px;text-align:center;
          word-break:keep-all;line-height:1.3;color:#6B7280;min-width:0;}
        .stp .ring{width:52px;height:52px;margin:0 auto 5px;border-radius:50%;border:3px dashed #C9CFCB;
          display:flex;align-items:center;justify-content:center;font-size:25px;filter:grayscale(1);opacity:.45;}
        .stp b{display:block;font-size:.86rem;color:#52616B;}
        .stp small{display:block;font-size:.74rem;margin-top:3px;}
        @media (max-width:760px){.stpgrid{grid-template-columns:repeat(4,minmax(0,1fr));}}
        .stp.on{background:#FFF8E6;border:2px solid #E2C98A;color:#6B4A1E;}
        .stp.on .ring{border:3px solid #B42318;color:#B42318;filter:none;opacity:1;transform:rotate(-8deg);
          box-shadow:inset 0 0 0 3px #FFF8E6,inset 0 0 0 5px #B42318;background:#FFF;}
        .stp.on b{color:#20483F;}
        .stp.on small{color:#B42318;font-weight:800;}
        .stp-done{background:linear-gradient(135deg,#FFF4D6,#E8F4EC);border:3px solid #B42318;border-radius:20px;
          padding:14px;text-align:center;font-weight:900;color:#20483F;font-size:1.2rem;margin-bottom:10px;}
        </style>"""
        + (f'<div class="stp-done">🎖️ {total}곳 도장 완성! 도토리시 명예 시민이에요.</div>' if len(got) == total else "")
        + '<div class="stpgrid">' + "".join(cells) + "</div>",
        unsafe_allow_html=True,
    )
    if dd.citizen():
        st.caption("도장은 시민증에 저장돼요. 창을 닫았다가 닉네임과 비밀 숫자로 다시 들어오면 이어서 모을 수 있어요.")
    elif st.session_state.get("admin_open"):
        st.caption("관리자 도장은 서버에 저장되며 관리자 코드로 다시 인증한 뒤 불러와요. 저장 오류가 표시되면 재시도해 주세요.")
    else:
        st.caption("도장은 시민증이 없어도 모을 수 있어요. 다만 저장되지 않아서 창을 닫으면 처음부터 다시 모아야 해요. 시민증을 만들면 지금까지 모은 도장도 함께 저장돼요.")
    if len(got) == total:
        # 모든 곳을 모으면 깡지와 함께하는 명예 시민증 카드를 사진으로 저장할 수 있어요.
        me = dd.citizen()
        st.markdown("#### 🎖️ 명예 시민증")
        show_result_card(
            {
                "color": "#B7791F", "place": "시민 등록소", "game": "명예 시민증", "emoji": "🎖️",
                "title": "도토리시 명예 시민", "subtitle": f"{total}곳 완주!",
                "stats": [("모은 도장", f"{len(got)} / {total}"), ("완주한 날", max(str(v) for v in got.values()))],
                "sections": [("🏅 다녀온 곳", [" · ".join(place for _, place, _ in dd.STAMP_PLACES.values())])],
                "nickname": me["nickname"] if me else "", "mascot": "trophy",
            },
            "jamkkan_honorary_citizen.png",
        )


if st.session_state.get("admin_open"):
    from admin_ui import card, tools_button
    from admin_progress import status
    card()
    show_stamps()
    status("citizen")
    tools_button("citizen")
    st.stop()

account = dd.citizen()

if account:
    # 시민증 사진 자리에 깡지 증명사진을 넣어요. 사이드바와 같은 사진이에요. (사진 파일이 없으면 다람쥐 그림으로 대신해요.)
    try:
        photo_html = (
            f'<img src="data:image/png;base64,{id_photo(dd.my_photo())}" alt="깡지 증명사진" '
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
    st.caption("방금 끝낸 게임의 순위는 여기에 보이기까지 최대 1분쯤 걸릴 수 있어요. (데이터베이스 사용량을 아끼려고 1분마다 새로 읽어요.)")

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
    dd.show_login_forms("page")

    st.markdown("#### 알아 두세요")
    st.markdown(
        "- **닉네임은 명예의 전당에서 다른 사람도 볼 수 있어요.** 실제 이름이나 학교를 넣으면 누구나 보게 되니 알고 정해 주세요.\n"
        "- 한 번 만든 닉네임은 **그 사람만 계속** 쓸 수 있어요. 창을 닫았다가 와도 **닉네임 + 비밀 숫자**로 다시 들어오면 돼요.\n"
        "- 비밀 숫자는 이 앱이 저장하지 않고 Firebase가 암호화해서 보관해요. **다른 곳에서 쓰는 비밀번호나 생일은 쓰지 마세요.**\n"
        "- 비밀 숫자를 잊으면 원래 숫자는 누구도 볼 수 없어요. 관리자에게 말하면 새 비밀 숫자로 바꿔 줄 수 있어요.\n"
        "- 다른 사람이 불쾌할 수 있는 닉네임은 쓰지 않아요."
    )

    show_stamps()

st.page_link("pages/13_도토리시_통계청.py", label="도토리시 통계청에서 모두의 기록 보기", icon="📊")

# 맨 아래: 관리자만 쓰는 상자(관리자 코드가 Secrets에 있을 때만 보여요)



