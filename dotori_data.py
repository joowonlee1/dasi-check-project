"""도토리시 데이터: 닉네임 시민증(로그인), 익명 통계(+1 집계), 명예의 전당.

- 이름·학번·이메일은 받지 않아요. 닉네임만 씁니다.
- 통계는 '몇 번 나왔는지' 숫자만 +1 해요. 누가 무엇을 골랐는지는 저장하지 않아요.
- 명예의 전당은 시민증(닉네임)을 만든 사람의 최고 기록만 저장해요.
- 연결 정보는 Streamlit Secrets의 [firebase]에서 읽어요(코드·GitHub에 키 없음).
- 저장에 실패해도 게임은 그대로 할 수 있어요.
"""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st
from firebase_support import ConnectionProblem, config, explain, normalize_nickname, request

CITIZEN = "dotori_citizen"     # 시민증(로그인) 정보
ANON = "dotori_anon"           # 로그인하지 않은 사람의 익명 계정(통계 저장용)
SEEN = "dotori_seen"           # 이미 집계한 결과(새로고침·다시 그리기 때 두 번 세지 않게)
MY = "dotori_my"               # 이번 방문에서 내가 한 기록
REFRESH = 60                   # 통계·명예의 전당을 다시 읽는 간격(초)

GAMES = {
    "grandma": ("📱", "할머니 폰 지키기"),
    "fakenews": ("🌐", "가짜뉴스 확산 막기"),
    "coping": ("🧭", "대처유형 테스트"),
    "mafia": ("🕵️", "단톡방 마피아"),
    "memo": ("🔐", "중고거래 사기단 추리"),
    "filter": ("🤖", "피싱 필터 만들기"),
    "nono": ("🧩", "큐싱 노노그램"),
}

# 명예의 전당: 정렬 기준(앞이 작을수록 높은 순위)과 기록 글자
HALL_SORT = {
    "filter": lambda r: (-r.get("stars", 0), r.get("blocks", 0)),
    "nono": lambda r: (-r.get("stars", 0), r.get("hints", 0)),
    "memo": lambda r: (-r.get("stars", 0), r.get("hints", 0), r.get("wrong", 0)),
    "fakenews": lambda r: (-r.get("stars", 0), -r.get("avg", 0)),
    "mafia": lambda r: (-r.get("score", 0),),
}
HALL_TEXT = {
    "filter": lambda r: f"⭐ {r.get('stars', 0)}/9 · 블록 {r.get('blocks', 0)}개",
    "nono": lambda r: f"⭐ {r.get('stars', 0)}/9 · 힌트 {r.get('hints', 0)}번",
    "memo": lambda r: f"⭐ {r.get('stars', 0)}/3 · 힌트 {r.get('hints', 0)}번 · 잘못 지목 {r.get('wrong', 0)}번",
    "fakenews": lambda r: f"⭐ {r.get('stars', 0)}/15 · 평균 {r.get('avg', 0)}% 지킴",
    "mafia": lambda r: f"{r.get('score', 0)}점 · 사건 {r.get('solved', 0)}/3 해결",
}


# ───────── 기본 주소 ─────────

def _root():
    _, project = config()
    return f"projects/{project}/databases/(default)/documents"


def _url(path=""):
    return "https://firestore.googleapis.com/v1/" + _root() + (("/" + path) if path else "")


def _public_get(url):
    """공개 읽기(키 없이). 문서가 없으면 None."""
    try:
        with urlopen(Request(url), timeout=12) as response:
            return json.loads(response.read() or b"{}")
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise ConnectionProblem(exc.code) from None
    except (URLError, TimeoutError, ValueError, OSError):
        raise ConnectionProblem() from None


def _value(field):
    for kind in ("integerValue", "doubleValue", "stringValue", "booleanValue", "timestampValue"):
        if kind in field:
            v = field[kind]
            return int(v) if kind == "integerValue" else v
    return None


# ───────── 계정 ─────────

def _sign_up():
    key, _ = config()
    result = request(
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp?" + urlencode({"key": key}),
        "POST", {"returnSecureToken": True},
    )
    return {"uid": result["localId"], "token": result["idToken"], "refresh": result["refreshToken"],
            "expires": time.time() + int(result["expiresIn"])}


def _fresh(account):
    """토큰이 만료되기 전에 갱신합니다."""
    if time.time() < account["expires"] - 60:
        return account
    key, _ = config()
    result = request(
        "https://securetoken.googleapis.com/v1/token?" + urlencode({"key": key}),
        "POST", {"grant_type": "refresh_token", "refresh_token": account["refresh"]}, form=True,
    )
    account.update(token=result["id_token"], refresh=result["refresh_token"],
                   expires=time.time() + int(result["expires_in"]))
    return account


def citizen():
    """로그인한 시민증 정보(없으면 None)."""
    return st.session_state.get(CITIZEN)


def _writer():
    """저장할 때 쓸 계정: 시민증이 있으면 그 계정, 없으면 익명 계정."""
    account = citizen() or st.session_state.get(ANON)
    if not account:
        account = _sign_up()
        st.session_state[ANON] = account
    return _fresh(account)


def login(nickname):
    """닉네임으로 시민증을 만들어요. 같은 닉네임은 하루 동안 한 사람만 쓸 수 있어요."""
    name, canonical = normalize_nickname(nickname)
    account = st.session_state.get(ANON) or _sign_up()
    account = _fresh(account)
    path = _root() + "/citizens/" + quote(canonical, safe="")
    write = {
        "update": {"name": path, "fields": {"uid": {"stringValue": account["uid"]},
                                             "nickname": {"stringValue": name}}},
        "updateTransforms": [{"fieldPath": "created_at", "setToServerValue": "REQUEST_TIME"}],
    }
    try:
        request(_url() + ":commit", "POST", {"writes": [dict(write, currentDocument={"exists": False})]},
                account["token"])
    except ConnectionProblem:
        doc = _public_get("https://firestore.googleapis.com/v1/" + quote(path, safe="/"))
        if not doc:
            raise
        owner = doc.get("fields", {}).get("uid", {}).get("stringValue")
        if owner != account["uid"]:
            # 하루가 지난 닉네임만 새 사람이 이어받을 수 있어요(보안 규칙에서도 확인).
            try:
                request(_url() + ":commit", "POST",
                        {"writes": [dict(write, currentDocument={"updateTime": doc["updateTime"]})]},
                        account["token"])
            except ConnectionProblem:
                raise ConnectionProblem(409, "NICKNAME_TAKEN") from None
    account["nickname"] = name
    st.session_state[CITIZEN] = account
    st.session_state[ANON] = account
    return name


def logout():
    st.session_state.pop(CITIZEN, None)
    st.session_state.pop(ANON, None)


# ───────── 결과 받기 ─────────

def take_event(value):
    """게임 화면이 보낸 결과 중 아직 처리하지 않은 것만 돌려줍니다."""
    if not isinstance(value, dict) or not value.get("id"):
        return None
    seen = st.session_state.setdefault(SEEN, set())
    if value["id"] in seen:
        return None
    seen.add(value["id"])
    return value


def once(event_id):
    """파이썬 화면에서 같은 결과를 한 번만 세도록 확인합니다."""
    seen = st.session_state.setdefault(SEEN, set())
    if event_id in seen:
        return False
    seen.add(event_id)
    return True


def note_mine(game, text):
    st.session_state.setdefault(MY, []).append((game, text, time.strftime("%H:%M")))


# ───────── 통계(+1) ─────────

def record(game, counts):
    """게임 통계 문서의 숫자 칸을 늘려요. 실패해도 게임은 계속돼요."""
    counts = {k: int(v) for k, v in counts.items() if int(v)}
    if not counts:
        return False
    try:
        account = _writer()
        transforms = [{"fieldPath": k, "increment": {"integerValue": str(v)}} for k, v in counts.items()]
        request(_url() + ":commit", "POST",
                {"writes": [{"transform": {"document": _root() + f"/stats/{game}", "fieldTransforms": transforms}}]},
                account["token"])
        load_stats.clear()
        return True
    except ConnectionProblem:
        return False


@st.cache_data(ttl=REFRESH, show_spinner=False)
def load_stats(project, game):
    doc = _public_get(f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/stats/{game}")
    if not doc:
        return {}
    return {k: _value(v) for k, v in doc.get("fields", {}).items() if isinstance(_value(v), int)}


def stats(game):
    """게임 통계를 읽어요. 연결이 안 되면 빈 값."""
    try:
        _, project = config()
        return load_stats(project, game)
    except ConnectionProblem:
        return {}


def pct(part, whole):
    return round(part * 100 / whole) if whole else 0


# ───────── 명예의 전당 ─────────

def save_hall(game, fields, better):
    """시민증이 있으면 최고 기록만 저장해요. better(이전, 새 기록) → 새 기록이 더 좋으면 True."""
    account = citizen()
    if not account:
        return "guest"
    try:
        account = _fresh(account)
        path = _root() + f"/halloffame/{game}/entries/" + quote(account["uid"], safe="")
        old = _public_get("https://firestore.googleapis.com/v1/" + quote(path, safe="/"))
        if old:
            prev = {k: _value(v) for k, v in old.get("fields", {}).items()}
            if not better(prev, fields):
                return "kept"
        body = {"nickname": {"stringValue": account["nickname"]}}
        body.update({k: {"integerValue": str(int(v))} for k, v in fields.items()})
        request(_url() + ":commit", "POST",
                {"writes": [{"update": {"name": path, "fields": body},
                             "updateTransforms": [{"fieldPath": "updated_at", "setToServerValue": "REQUEST_TIME"}]}]},
                account["token"])
        load_hall.clear()
        return "saved"
    except ConnectionProblem:
        return "failed"


@st.cache_data(ttl=REFRESH, show_spinner=False)
def load_hall(project, game):
    base = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/halloffame/{game}/entries"
    rows, page = [], None
    for _ in range(5):
        params = {"pageSize": 300}
        if page:
            params["pageToken"] = page
        result = _public_get(base + "?" + urlencode(params)) or {}
        for doc in result.get("documents", []):
            row = {k: _value(v) for k, v in doc.get("fields", {}).items()}
            row["uid"] = doc["name"].rsplit("/", 1)[-1]
            rows.append(row)
        page = result.get("nextPageToken")
        if not page:
            break
    return rows


def hall(game):
    try:
        _, project = config()
        return load_hall(project, game)
    except ConnectionProblem:
        return []


# ───────── 화면 조각 ─────────

def show_others(lines):
    """게임 결과 아래 '다른 친구들은?' 상자."""
    lines = [line for line in lines if line]
    if not lines:
        return
    body = "".join(f"<div>{line}</div>" for line in lines)
    st.markdown(
        '<div style="background:#F0F7FF;border:2px solid #B8D4F0;border-radius:16px;padding:12px 16px;margin:10px 0;'
        'word-break:keep-all;line-height:1.75;font-weight:600;color:#1E3A5F;">'
        f'<div style="font-weight:900;margin-bottom:2px;">🌍 다른 친구들은?</div>{body}</div>',
        unsafe_allow_html=True,
    )


def show_hall_note(status=None):
    """명예의 전당 저장 상태 안내."""
    account = citizen()
    if status == "saved":
        st.success(f"🏆 {account['nickname']}님의 기록을 명예의 전당에 저장했어요!")
    elif status == "kept":
        st.info("🏆 명예의 전당에 있는 예전 기록이 더 좋아서 그대로 두었어요.")
    elif status == "failed":
        st.warning("🏆 명예의 전당 저장에 실패했어요. 게임 기록은 그대로예요.")
    elif not account:
        st.page_link("pages/0_도토리시_시민증.py", label="시민증(닉네임)을 만들면 명예의 전당에 기록이 올라가요", icon="🪪")
