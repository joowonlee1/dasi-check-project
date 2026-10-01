"""Firebase anonymous auth and public rankings. No admin key is used."""
import json
import re
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from urllib.error import HTTPError, URLError
import streamlit as st

CASE = "case01_v1"

class ConnectionProblem(Exception):
    def __init__(self, status=0):
        self.status = status
        super().__init__(f"연결 오류 ({status})")

def config():
    try:
        cfg = st.secrets["firebase"]
        return str(cfg["api_key"]).strip(), str(cfg["project_id"]).strip()
    except (KeyError, FileNotFoundError):
        raise ConnectionProblem(-1) from None

def request(url, method="GET", payload=None, token=None, form=False):
    headers = {}
    data = None
    if payload is not None:
        data = (urlencode(payload) if form else json.dumps(payload)).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=12) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        # Never show URLs, keys or authentication tokens in the UI.
        raise ConnectionProblem(exc.code) from None
    except (URLError, TimeoutError, ValueError, OSError):
        raise ConnectionProblem() from None

def explain(exc):
    return {
        -1: "Streamlit Secrets의 [firebase] api_key와 project_id를 확인해 주세요.",
        400: "Firebase 설정을 확인해 주세요. 익명 인증이 켜져 있는지 확인하세요.",
        401: "로그인 인증을 갱신하지 못했어요. 잠시 후 다시 시도하세요.",
        403: "접근이 거부됐어요. Firebase 프로젝트와 게시한 Firestore 규칙을 확인하세요.",
        404: "프로젝트 ID와 Firestore (default) 데이터베이스를 확인하세요.",
        429: "요청이 많거나 무료 한도에 도달했어요. 잠시 후 다시 시도하세요.",
    }.get(exc.status, "저장소에 연결하지 못했어요. 게임은 계속 이용할 수 있어요.")

def user():
    return st.session_state.get("firebase_user")

def sign_in(nickname):
    key, _ = config()
    result = request("https://identitytoolkit.googleapis.com/v1/accounts:signUp?" + urlencode({"key": key}),
                     "POST", {"returnSecureToken": True})
    st.session_state["firebase_user"] = {
        "uid": result["localId"], "token": result["idToken"],
        "refresh": result["refreshToken"], "expires": time.time() + int(result["expiresIn"]),
        "nickname": nickname,
    }

def access_token():
    account = user()
    if not account:
        raise ConnectionProblem(401)
    if time.time() >= account["expires"] - 60:
        key, _ = config()
        result = request("https://securetoken.googleapis.com/v1/token?" + urlencode({"key": key}),
                         "POST", {"grant_type": "refresh_token", "refresh_token": account["refresh"]}, form=True)
        account.update(token=result["id_token"], refresh=result["refresh_token"],
                       expires=time.time() + int(result["expires_in"]))
    return account["token"]

def root():
    _, project = config()
    return f"projects/{project}/databases/(default)/documents"

def entry_path():
    return root() + f"/leaderboards/{CASE}/entries/" + quote(user()["uid"], safe="")

def save_result(game):
    account = user()
    if not account or game.get("rank_uid") != account["uid"] or game.get("unlocked") != 3:
        raise ConnectionProblem(401)
    path = entry_path()
    token = access_token()
    # An existing immutable entry is success, including a retried request after a timeout.
    try:
        request("https://firestore.googleapis.com/v1/" + path, token=token)
        return "existing"
    except ConnectionProblem as exc:
        if exc.status != 404:
            raise
    fields = {
        "nickname": {"stringValue": game["rank_nickname"]},
        "hints": {"integerValue": str(sum(game["hints"].values()))},
        "mistakes": {"integerValue": str(game["mistakes"])},
        "seconds": {"integerValue": str(max(0, int(game["finished"] - game["started"])))},
        "completed": {"booleanValue": True},
    }
    payload = {"writes": [{"update": {"name": path, "fields": fields},
                           "currentDocument": {"exists": False},
                           "updateTransforms": [{"fieldPath": "created_at", "setToServerValue": "REQUEST_TIME"}]}]}
    try:
        request("https://firestore.googleapis.com/v1/" + root() + ":commit", "POST", payload, token)
    except ConnectionProblem as exc:
        if exc.status not in (409, 403):
            raise
        # Another request may already have created this entry. Never overwrite it.
        request("https://firestore.googleapis.com/v1/" + path, token=token)
        return "existing"
    return "saved"

@st.cache_data(ttl=60, show_spinner=False)
def rankings(project):
    base = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/leaderboards/{CASE}/entries"
    documents = []
    page = None
    for _ in range(20):
        params = {"pageSize": 100}
        if page:
            params["pageToken"] = page
        result = request(base + "?" + urlencode(params))
        documents.extend(result.get("documents", []))
        page = result.get("nextPageToken")
        if not page:
            break
    if page:
        raise ConnectionProblem(0)  # Do not display a misleading partial ranking.
    rows = []
    for document in documents:
        f = document["fields"]
        rows.append({"닉네임": f["nickname"]["stringValue"],
                     "힌트": int(f["hints"]["integerValue"]),
                     "재검토": int(f["mistakes"]["integerValue"]),
                     "경과 시간(초)": int(f["seconds"]["integerValue"])})
    rows.sort(key=lambda row: (row["힌트"], row["재검토"], row["닉네임"]))
    previous, rank = None, 0
    for index, row in enumerate(rows, 1):
        score = (row["힌트"], row["재검토"])
        if score != previous:
            rank = index
        row["순위"] = rank
        previous = score
    return [{"순위": r["순위"], **r} for r in rows]

def show_login():
    st.title("👤 닉네임 입장")
    st.write("이메일과 비밀번호 없이 방탈출 기록을 공유해요.")
    st.info("이 버전의 익명 로그인은 현재 접속 동안 유지돼요. 새로고침·접속 종료 시 계정 연결이 사라질 수 있지만, 이미 저장한 공개 기록은 남아요. 같은 닉네임을 입력해도 이전 계정으로 복구되지는 않아요.")
    if user():
        st.success(f"{user()['nickname']} 님으로 입장했어요.")
        st.page_link("pages/3_문자_퀴즈.py", label="방탈출 시작하기", icon="🗝️")
        return
    with st.form("firebase_login"):
        nickname = st.text_input("닉네임 (2~12자)", max_chars=12)
        consent = st.checkbox("탈출하면 닉네임과 결과가 공동 랭킹에 공개되는 것에 동의합니다.")
        submit = st.form_submit_button("닉네임으로 입장", type="primary")
    if submit:
        nickname = nickname.strip()
        if not re.fullmatch(r"[가-힣a-zA-Z0-9_]{2,12}", nickname):
            st.warning("닉네임은 한글·영문·숫자·밑줄로 2~12자 입력하세요. 실명은 피해주세요.")
        elif not consent:
            st.warning("공개 기록 참여에 동의하거나, 로그인 없이 방탈출을 이용해 주세요.")
        else:
            try:
                sign_in(nickname)
                st.rerun()
            except ConnectionProblem as exc:
                st.error(explain(exc))
    st.page_link("pages/3_문자_퀴즈.py", label="로그인 없이 연습하기", icon="🗝️")

def show_ranking():
    st.title("🏆 함께한 탈출 기록")
    st.caption("사건 01 · 버전 1 / 익명 계정별 첫 저장 기록 / 힌트 적은 순 → 재검토 적은 순, 같으면 공동 순위")
    st.write("경과 시간은 참고 정보예요. 반복 참여가 가능한 학습용 랭킹이며, 사람별 최초 도전이나 부정행위 방지를 보장하지 않아요.")
    try:
        _, project = config()
        rows = rankings(project)
        if rows:
            st.dataframe(rows, hide_index=True, use_container_width=True)
        else:
            st.info("아직 저장된 기록이 없어요. 첫 탈출에 도전해 보세요!")
        st.caption("무료 사용량을 아끼기 위해 랭킹은 최대 60초 동안 같은 결과를 보여줘요.")
    except ConnectionProblem as exc:
        st.warning(explain(exc))
        st.caption("기록 조회에 실패했어요. 저장된 기록이 삭제됐다는 뜻은 아니에요.")
    st.page_link("pages/3_문자_퀴즈.py", label="방탈출 도전", icon="🗝️")
    if user():
        with st.expander("내 공개 기록 삭제"):
            confirm = st.checkbox("현재 익명 계정의 공개 기록을 삭제합니다.")
            if st.button("내 기록 삭제", disabled=not confirm):
                try:
                    request("https://firestore.googleapis.com/v1/" + entry_path(), "DELETE", token=access_token())
                    game = st.session_state.get("escape_game", {})
                    game["rank_status"] = "deleted"
                    rankings.clear()
                    st.success("삭제했어요. 다음에 이 페이지를 열면 반영돼요.")
                except ConnectionProblem as exc:
                    st.error(explain(exc))

def result_panel(game):
    if not game.get("rank_uid"):
        st.info("로그인 없이 시작한 연습 기록이에요. 공동 랭킹에 참여하려면 닉네임 입장 후 새 게임을 시작해 주세요.")
        return
    status = game.get("rank_status")
    if status == "deleted":
        st.caption("이 게임의 공개 기록은 삭제했어요.")
        return
    if status in ("saved", "existing"):
        st.success("공동 랭킹에 저장했어요." if status == "saved" else "이 익명 계정의 기록이 이미 있어요. 기존 결과를 유지했어요.")
        return
    retry = False
    if status == "failed":
        st.warning(game.get("rank_error", "저장하지 못했어요."))
        st.caption("결과는 아래에서 다운로드할 수 있어요. 재시도 전에 페이지를 새로고침하거나 게임을 초기화하지 마세요.")
        retry = st.button("기록 저장 다시 시도", key="escape_retry_save")
    if status is None or retry:
        try:
            with st.spinner("탈출 기록을 저장하고 있어요…"):
                game["rank_status"] = save_result(game)
            rankings.clear()
            st.rerun()
        except ConnectionProblem as exc:
            game["rank_status"] = "failed"
            game["rank_error"] = explain(exc)
            st.rerun()
