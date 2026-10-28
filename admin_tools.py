"""관리자 도구: 로그인 화면 '🔑 관리자이신가요?'에서 관리자 코드를 넣으면 열려요.

- 관리자 코드는 Streamlit Secrets의 [admin] code 에만 있어요(코드·GitHub에 없음).
- 비밀 숫자를 '보는' 기능은 없어요. Firebase가 암호화해 보관해서 누구도 원래 숫자를 볼 수 없어요.
  대신 잊어버린 친구에게 새 비밀 숫자를 정해 줄 수 있어요.
- 비밀 숫자 재설정·계정 삭제에는 Firebase 서비스 계정 키가 필요해요. Secrets의 [firebase_admin]에 넣어요.
"""
import hmac
import secrets as pyrandom
from urllib.parse import quote, urlencode

import streamlit as st
import dotori_data as dd
from firebase_support import ConnectionProblem, config, normalize_nickname, request

TRIES = "admin_tries"
OPEN = "admin_open"


def _admin_code():
    try:
        return str(st.secrets["admin"]["code"]).strip()
    except (KeyError, FileNotFoundError):
        return ""


def _token():
    """서비스 계정 키로 관리자용 접근 토큰을 받아요(50분 동안 다시 써요)."""
    cached = st.session_state.get("admin_token")
    import time

    if cached and time.time() < cached[1]:
        return cached[0]
    try:
        info = dict(st.secrets["firebase_admin"])
    except (KeyError, FileNotFoundError):
        raise ConnectionProblem(-2, "NO_ADMIN_KEY") from None
    from google.auth.transport.requests import Request as GoogleRequest
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/cloud-platform",
                      "https://www.googleapis.com/auth/identitytoolkit",
                      "https://www.googleapis.com/auth/datastore"])
    creds.refresh(GoogleRequest())
    st.session_state["admin_token"] = (creds.token, time.time() + 50 * 60)
    return creds.token


def _tk(action, body):
    _, project = config()
    return request(f"https://identitytoolkit.googleapis.com/v1/projects/{project}/accounts:{action}",
                   "POST", body, _token())


def _uid_of(canonical):
    """닉네임으로 Firebase 계정 번호(uid)를 찾아요."""
    found = _tk("lookup", {"email": [dd._login_email(canonical)]}).get("users", [])
    return found[0]["localId"] if found else None


def _delete_doc(path):
    try:
        request("https://firestore.googleapis.com/v1/" + quote(path, safe="/"), "DELETE", token=_token())
    except ConnectionProblem as exc:
        if exc.status != 404:
            raise


def _citizens():
    _, project = config()
    base = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/citizens"
    rows, page = [], None
    for _ in range(10):
        params = {"pageSize": 300}
        if page:
            params["pageToken"] = page
        result = dd._public_get(base + "?" + urlencode(params)) or {}
        for doc in result.get("documents", []):
            f = {k: dd._value(v) for k, v in doc.get("fields", {}).items()}
            stamps = doc.get("fields", {}).get("stamps", {}).get("mapValue", {}).get("fields", {})
            rows.append({"닉네임": f.get("nickname") or doc["name"].rsplit("/", 1)[-1],
                         "방식": "비밀 숫자" if f.get("kind") == "password" else "예전(하루)",
                         "도장": len(stamps), "만든 날": str(f.get("created_at", ""))[:10]})
        page = result.get("nextPageToken")
        if not page:
            break
    return rows


def _problem(exc):
    if exc.reason == "NO_ADMIN_KEY":
        st.error("Secrets에 [firebase_admin](서비스 계정 키)이 없어서 이 기능을 쓸 수 없어요.")
    elif exc.reason == "NICKNAME_INVALID":
        st.error("닉네임 형식이 맞지 않아요.")
    else:
        st.error(f"처리하지 못했어요. [HTTP {exc.status} / {exc.reason}]")


def show_admin_box():
    """로그인 화면의 '관리자이신가요?' 상자."""
    code = _admin_code()
    if not code:
        return  # 관리자 코드를 정하지 않았으면 상자를 보여 주지 않아요.
    with st.expander("🔑 관리자이신가요?", expanded=bool(st.session_state.get(OPEN))):
        if not st.session_state.get(OPEN):
            tries = st.session_state.get(TRIES, 0)
            if tries >= 5:
                st.error("관리자 코드를 여러 번 틀렸어요. 창을 닫았다가 다시 시도해 주세요.")
                return
            with st.form("admin_login"):
                typed = st.text_input("관리자 코드", type="password")
                ok = st.form_submit_button("확인")
            if ok:
                if hmac.compare_digest(typed.strip().encode(), code.encode()):
                    st.session_state[OPEN] = True
                    st.rerun()
                st.session_state[TRIES] = tries + 1
                st.error("관리자 코드가 맞지 않아요.")
            return
        _admin_tools()


def _admin_tools():
    if not st.session_state.get(OPEN):
        return
    from admin_answers import show_answers
    # 관리 메뉴(탭)가 '관리자이신가요?' 바로 아래에 오도록, 게임 정답은 맨 위가 아니라 네 번째 탭에 넣어요.
    t_reset, t_people, t_hall, t_answers = st.tabs(["🔑 비밀 숫자 재설정", "👥 시민 목록·삭제", "🏆 명예의 전당 정리", "📋 게임 정답"])
    with st.expander("관리자 이용 안내", expanded=False):
        st.caption("🔑 관리자 모드예요. 창을 닫거나 맨 아래 ‘관리자 모드 끝내기’를 누르면 닫혀요.")
        from mascot_ui import show_mascot
        show_mascot("badge", "관리자 모드예요! 정답 확인·시민 관리·기록 정리를 할 수 있어요.", width=120)
        st.info("🎖️ **관리자 공용 도장판** · 관리자 모드로 게임을 하면 도장이 개인 시민증이 아니라 관리자 전용 도장판 하나에 서버로 저장돼요. "
                "같은 관리자 코드로 들어온 사람끼리 이 도장판을 함께 써요. 학생들 시민증 도장과는 따로 저장돼요.")
    with t_answers:
        show_answers()

    with t_reset:
        st.caption("비밀 숫자는 누구도 원래 숫자를 볼 수 없어요. 잊어버린 친구에게 새 비밀 숫자를 정해 주고 알려 주세요.")
        with st.form("admin_reset"):
            nick = st.text_input("닉네임")
            new = st.text_input("새 비밀 숫자 6자리 (비워 두면 자동으로 정해요)", max_chars=6)
            ok = st.form_submit_button("새 비밀 숫자로 바꾸기", type="primary")
        if ok:
            try:
                _, canonical = normalize_nickname(nick)
                new = new.strip() or f"{pyrandom.randbelow(10 ** 6):06d}"
                dd._check_secret(new)
                uid = _uid_of(canonical)
                if not uid:
                    st.error("그 닉네임의 시민증(비밀 숫자 방식)을 찾지 못했어요.")
                else:
                    _tk("update", {"localId": uid, "password": new})
                    st.success(f"‘{nick.strip()}’의 새 비밀 숫자: **{new}** — 본인에게만 알려 주고, 화면을 닫아 주세요.")
            except ConnectionProblem as exc:
                if exc.reason == "SECRET_INVALID":
                    st.error("비밀 숫자는 숫자 6개로 입력해 주세요.")
                else:
                    _problem(exc)

    with t_people:
        try:
            people = _citizens()
            st.metric("시민증 수", f"{len(people)}명")
            if people:
                st.dataframe(people, hide_index=True, width="stretch")
        except ConnectionProblem as exc:
            _problem(exc)
        st.markdown("**닉네임 삭제** · 부적절한 닉네임이나 실명이 들어간 닉네임을 지워요. 그 사람의 명예의 전당 기록과 도장도 함께 지워져요.")
        with st.form("admin_delete"):
            nick = st.text_input("지울 닉네임")
            sure = st.checkbox("되돌릴 수 없다는 걸 알고 지웁니다.")
            ok = st.form_submit_button("닉네임 삭제")
        if ok:
            if not sure:
                st.warning("체크칸을 먼저 눌러 주세요.")
            else:
                try:
                    _, canonical = normalize_nickname(nick)
                    uid = _uid_of(canonical)
                    root = dd._root()
                    if uid:
                        for game in dd.HALL_SORT:
                            _delete_doc(root + f"/halloffame/{game}/entries/{uid}")
                        _tk("delete", {"localId": uid})
                    _delete_doc(root + "/citizens/" + quote(canonical, safe=""))
                    dd.load_hall.clear()
                    st.success(f"‘{nick.strip()}’ 닉네임을 지웠어요. 이제 다른 사람이 새로 만들 수 있어요.")
                except ConnectionProblem as exc:
                    _problem(exc)

    with t_hall:
        game = st.selectbox("게임", list(dd.HALL_SORT), format_func=lambda g: f"{dd.GAMES[g][0]} {dd.GAMES[g][1]}")
        entries = sorted(dd.hall(game), key=dd.HALL_SORT[game])
        if not entries:
            st.info("이 게임은 아직 기록이 없어요.")
        else:
            labels = {r["uid"]: f"{r.get('nickname', '시민')} · {dd.HALL_TEXT[game](r)}" for r in entries}
            pick = st.selectbox("지울 기록", list(labels), format_func=labels.get)
            if st.button("이 기록 지우기"):
                try:
                    _delete_doc(dd._root() + f"/halloffame/{game}/entries/{pick}")
                    dd.load_hall.clear()
                    st.success("지웠어요.")
                    st.rerun()
                except ConnectionProblem as exc:
                    _problem(exc)

    if st.button("관리자 모드 끝내기"):
        st.session_state.pop(OPEN, None)
        st.session_state.pop("admin_token", None)
        st.rerun()
