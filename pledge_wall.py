"""잠깐! 서약의 벽.

- 정해진 서약 중에서만 고르게 해서, 자유롭게 쓴 글은 저장하지 않습니다.
- 익명 계정마다 한 번만 남길 수 있고, 별명은 비워 두면 '익명'으로 표시합니다.
- 무료 사용량을 아끼기 위해 공동 기록은 60초에 한 번만 새로 읽습니다.
"""
import html
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st
from firebase_support import ConnectionProblem, config, explain, request

WALL = "wall_v1"
STATE = "pledge_wall_"
PLEDGES = [
    ("🔗", "모르는 링크는 누르지 않기"),
    ("📞", "돈 이야기는 원래 번호로 다시 확인하기"),
    ("🔢", "인증번호는 누구에게도 알려주지 않기"),
    ("📲", "설치하라는 앱은 설치하지 않기"),
    ("👨‍👩‍👧", "가족과 확인 질문 정해 두기"),
    ("🚨", "의심되면 112·1332에 먼저 묻기"),
]
FIELDS = [f"p{i}" for i in range(len(PLEDGES))]
NOTE_COLORS = ["#FFF3B0", "#FFD6E0", "#D7F2E3", "#DCEBFF", "#FFE2C6", "#EADCFF"]
REFRESH = 60  # 초. 공동 기록을 다시 읽는 간격

CSS = """
<style>
@keyframes pw-pop {0%{transform:scale(.6) rotate(var(--r));opacity:0} 100%{transform:scale(1) rotate(var(--r));opacity:1}}
.pw-count {background:linear-gradient(135deg,#FF7A45,#FFB347);border-radius:24px;padding:20px 16px;text-align:center;color:#fff;
  box-shadow:0 8px 20px rgba(255,122,69,.3);margin:6px 0 14px;}
.pw-count b {display:block;font-size:3rem;line-height:1.1;font-weight:900;}
.pw-count span {font-weight:800;font-size:1.05rem;}
.pw-bar {margin:6px 0;}
.pw-bar-head {display:flex;justify-content:space-between;font-weight:700;color:#20483F;font-size:1rem;word-break:keep-all;}
.pw-bar-track {background:#E8EFE6;border-radius:999px;height:12px;overflow:hidden;margin-top:3px;}
.pw-bar-fill {background:linear-gradient(90deg,#3BA99C,#7FD1B9);height:100%;border-radius:999px;}
.pw-wall {display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:10px 0 6px;}
.pw-note {--r:0deg;border-radius:6px;padding:12px 10px;box-shadow:0 4px 10px rgba(0,0,0,.08);transform:rotate(var(--r));
  animation:pw-pop .4s ease-out both;word-break:keep-all;color:#2B3A36;min-height:92px;}
.pw-note b {display:block;font-size:1.05rem;margin-bottom:4px;}
.pw-note div {font-size:1.6rem;letter-spacing:2px;}
.pw-note.me {outline:3px solid #FF7A45;}
@media (max-width:640px) {.pw-wall {grid-template-columns:repeat(2,1fr);}}
.pw-banner {background:linear-gradient(135deg,#FFF1E6,#E6F4F1);border:2px solid #FFC9A8;border-radius:24px;
  padding:18px 16px;text-align:center;margin:4px 0 12px;}
.pw-banner b {display:block;font-size:1.6rem;font-weight:900;color:#20483F;}
.pw-banner span {color:#33524A;font-size:1.05rem;font-weight:600;word-break:keep-all;}
.st-key-pledge_wall_choice [data-testid="stButtonGroup"] button {min-height:48px;font-size:1.02rem;padding:8px 14px;}
.st-key-pledge_wall_choice label p {font-size:1.1rem !important;font-weight:800 !important;}
.st-key-pledge_wall_save button {background:linear-gradient(135deg,#FF7A45,#FFB347) !important;border:none !important;
  padding:.8rem 1rem !important;}
.st-key-pledge_wall_save button p {color:#fff !important;font-weight:800 !important;font-size:1.1rem !important;}
</style>
"""


# ───────── 저장소 ─────────

def _documents_url():
    _, project = config()
    return f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents"


def _wall_parent():
    return _documents_url() + f"/pledges/{WALL}"


def _read(url):
    """공개 기록을 읽습니다. 실패하면 Google이 알려 준 원인 메시지를 함께 전달합니다.
    읽기 주소에는 API 키가 들어가지 않아 메시지를 보여 줘도 안전합니다."""
    try:
        with urlopen(Request(url), timeout=12) as response:
            return json.loads(response.read() or b"{}")
    except HTTPError as exc:
        reason = "UNKNOWN"
        try:
            body = json.loads(exc.read())
            body = body[0] if isinstance(body, list) and body else body
            reason = str(body.get("error", {}).get("message", "UNKNOWN"))[:160]
        except (ValueError, AttributeError, OSError):
            pass
        raise ConnectionProblem(exc.code, reason) from None
    except (URLError, TimeoutError, ValueError, OSError):
        raise ConnectionProblem() from None


@st.cache_data(ttl=REFRESH, show_spinner=False)
def load_summary(project):
    """전체 참여자 수, 서약별 선택 수, 최근 서약 12개를 계산합니다.
    방탈출 랭킹과 같은 '목록 읽기' 방식을 씁니다."""
    base = _wall_parent() + "/entries"
    documents, page = [], None
    for _ in range(10):  # 최대 3,000개까지 읽습니다.
        params = {"pageSize": 300}
        if page:
            params["pageToken"] = page
        result = _read(base + "?" + urlencode(params))
        documents.extend(result.get("documents", []))
        page = result.get("nextPageToken")
        if not page:
            break

    counts = [0] * len(FIELDS)
    notes = []
    for doc in documents:
        f = doc.get("fields", {})
        picks = [i for i, name in enumerate(FIELDS) if f.get(name, {}).get("integerValue") == "1"]
        for i in picks:
            counts[i] += 1
        notes.append({
            "uid": doc["name"].rsplit("/", 1)[-1],
            "name": f.get("nickname", {}).get("stringValue", "익명"),
            "picks": picks,
            "time": doc.get("createTime", ""),
        })
    notes.sort(key=lambda n: n["time"], reverse=True)
    return len(documents), counts, notes[:12]


def _anonymous_account():
    account = st.session_state.get(STATE + "user")
    if account and time.time() < account["expires"] - 60:
        return account
    key, _ = config()
    result = request(
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp?" + urlencode({"key": key}),
        "POST", {"returnSecureToken": True},
    )
    account = {"uid": result["localId"], "token": result["idToken"],
               "expires": time.time() + int(result["expiresIn"])}
    st.session_state[STATE + "user"] = account
    return account


def _entry_name(uid):
    _, project = config()
    return f"projects/{project}/databases/(default)/documents/pledges/{WALL}/entries/" + quote(uid, safe="")


def save_pledge(nickname, picks):
    account = _anonymous_account()
    fields = {"nickname": {"stringValue": nickname}}
    fields.update({f: {"integerValue": "1" if i in picks else "0"} for i, f in enumerate(FIELDS)})
    payload = {"writes": [{
        "update": {"name": _entry_name(account["uid"]), "fields": fields},
        "currentDocument": {"exists": False},  # 한 계정에 한 번만
        "updateTransforms": [{"fieldPath": "created_at", "setToServerValue": "REQUEST_TIME"}],
    }]}
    request(_documents_url() + ":commit", "POST", payload, account["token"])
    return account["uid"]


def delete_pledge():
    account = st.session_state.get(STATE + "user")
    if not account:
        raise ConnectionProblem(401)
    request("https://firestore.googleapis.com/v1/" + _entry_name(account["uid"]), "DELETE",
            token=account["token"])


# ───────── 화면 ─────────

def clean_nickname(text):
    name = text.strip()
    if not name:
        return "익명"
    if not re.fullmatch(r"[가-힣a-zA-Z0-9_]{2,12}", name):
        return None
    return name


def note_html(note, index, mine=False):
    color = NOTE_COLORS[index % len(NOTE_COLORS)]
    tilt = (-3, 2, -1, 3, -2, 1)[index % 6]
    icons = "".join(PLEDGES[p][0] for p in note["picks"])
    return (
        f'<div class="pw-note{" me" if mine else ""}" style="background:{color};--r:{tilt}deg;'
        f'animation-delay:{0.05 * index:.2f}s"><b>✍️ {html.escape(note["name"])}</b><div>{icons}</div></div>'
    )


def show_board():
    """참여자 수·서약별 막대·최근 메모. 일정 간격으로 이 부분만 새로 읽습니다."""
    try:
        _, project = config()
        total, counts, notes = load_summary(project)
    except ConnectionProblem as exc:
        st.info("서약 기록을 불러오지 못했어요. 서약 고르기는 계속할 수 있어요.")
        st.caption(explain(exc))
        return
    st.markdown(
        f'<div class="pw-count"><b>{total:,}명</b><span>이 ‘잠깐!’ 서약에 함께했어요</span></div>',
        unsafe_allow_html=True,
    )
    top = max(counts) if counts and max(counts) else 1
    bars = "".join(
        f'<div class="pw-bar"><div class="pw-bar-head"><span>{icon} {text}</span><span>{n:,}</span></div>'
        f'<div class="pw-bar-track"><div class="pw-bar-fill" style="width:{n * 100 / top:.0f}%"></div></div></div>'
        for (icon, text), n in zip(PLEDGES, counts)
    )
    st.markdown(bars, unsafe_allow_html=True)
    if notes:
        mine = st.session_state.get(STATE + "saved")
        st.markdown(
            '<div class="pw-wall">' + "".join(
                note_html(n, i, n["uid"] == mine) for i, n in enumerate(notes)) + "</div>",
            unsafe_allow_html=True,
        )
        st.caption(f"최근 서약 {len(notes)}개 · {REFRESH}초마다 새로 불러와요.")
    else:
        st.caption("아직 서약이 없어요. 첫 번째 서약을 남겨 보세요!")


@st.fragment(run_every=REFRESH)
def board_fragment():
    show_board()


def show_pledge_wall():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="pw-banner"><b>✍️ 잠깐! 서약의 벽</b>'
        '<span>지킬 약속을 고르고 별명을 남기면, 함께한 사람 수가 올라가요.</span></div>',
        unsafe_allow_html=True,
    )
    if st.session_state.pop(STATE + "celebrate", False):
        st.balloons()
    show_form()
    board_fragment()


def show_form():

    saved = st.session_state.get(STATE + "saved")
    with st.container(border=True):
        if saved:
            picks = st.session_state.get(STATE + "picks", [])
            st.success("서약을 남겼어요! 아래 벽에서 주황 테두리 메모가 내 서약이에요.")
            st.markdown("\n".join(f"- {PLEDGES[p][0]} {PLEDGES[p][1]}" for p in picks))
            with st.expander("방금 남긴 서약 지우기"):
                if st.button("내 서약 지우기", key=STATE + "delete"):
                    try:
                        delete_pledge()
                        st.session_state.pop(STATE + "saved", None)
                        load_summary.clear()
                        st.rerun()
                    except ConnectionProblem as exc:
                        st.error(explain(exc))
            return

        picks = st.pills(
            "지킬 약속을 골라 주세요 (여러 개 가능)",
            options=list(range(len(PLEDGES))),
            format_func=lambda i: f"{PLEDGES[i][0]} {PLEDGES[i][1]}",
            selection_mode="multi",
            key=STATE + "choice",
        )
        nickname = st.text_input(
            "별명 (선택)", max_chars=12, key=STATE + "nickname",
            placeholder="예: 도토리 · 비워 두면 ‘익명’",
            help="한글·영문·숫자·밑줄 2~12자. 실명이나 연락처는 쓰지 마세요.",
        )
        if st.button("✍️ 서약 남기기", key=STATE + "save", type="primary", width="stretch"):
            name = clean_nickname(nickname)
            if not picks:
                st.warning("약속을 한 개 이상 골라 주세요.")
            elif name is None:
                st.warning("별명은 한글·영문·숫자·밑줄로 2~12자만 쓸 수 있어요.")
            else:
                try:
                    with st.spinner("벽에 붙이는 중…"):
                        uid = save_pledge(name, sorted(picks))
                    st.session_state[STATE + "saved"] = uid
                    st.session_state[STATE + "picks"] = sorted(picks)
                    st.session_state[STATE + "celebrate"] = True
                    load_summary.clear()
                    st.rerun()
                except ConnectionProblem as exc:
                    if exc.status in (400, 409) and exc.reason in ("UNKNOWN", "INVALID_ARGUMENT") \
                            and st.session_state.get(STATE + "user"):
                        st.info("이 브라우저에서는 이미 서약을 남겼을 수 있어요. 잠시 뒤 벽을 확인해 주세요.")
                    else:
                        st.error(explain(exc))
        st.caption("정해진 약속과 별명만 공개돼요. 이름·연락처는 저장하지 않아요.")
