"""도토리시 데이터: 닉네임 시민증(로그인), 익명 통계(+1 집계), 명예의 전당.

- 이름·학번·이메일은 받지 않아요. 닉네임만 씁니다.
- 통계는 '몇 번 나왔는지' 숫자만 +1 해요. 누가 무엇을 골랐는지는 저장하지 않아요.
- 명예의 전당은 시민증(닉네임)을 만든 사람의 최고 기록만 저장해요.
- 연결 정보는 Streamlit Secrets의 [firebase]에서 읽어요(코드·GitHub에 키 없음).
- 저장에 실패해도 게임은 그대로 할 수 있어요.
"""
import json
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st
from firebase_support import ConnectionProblem, config, explain, normalize_nickname, request

CITIZEN = "dotori_citizen"     # 시민증(로그인) 정보
ANON = "dotori_anon"           # 로그인하지 않은 사람의 익명 계정(통계 저장용)
SEEN = "dotori_seen"           # 이미 집계한 결과(새로고침·다시 그리기 때 두 번 세지 않게)
MY = "dotori_my"               # 이번 방문에서 내가 한 기록
KST = timezone(timedelta(hours=9))  # 서버 시계(UTC)가 아니라 한국 시간으로 기록해요
STAMPS = "dotori_stamps"       # 모은 장소 도장(시민증이 있으면 시민증 문서에 저장해요)
PENDING_STAMPS = "dotori_pending_stamps"
REFRESH = 60                   # 통계·명예의 전당을 다시 읽는 간격(초)

GAMES = {
    "grandma": ("📱", "할머니 폰 지키기"),
    "escape": ("🗝️", "피싱 방탈출"),
    "fakenews": ("🌐", "가짜뉴스 확산 막기"),
    "coping": ("🧭", "대처유형 테스트"),
    "mafia": ("🕵️", "단톡방 마피아"),
    "memo": ("🔐", "중고거래 사기단 추리"),
    "filter": ("🤖", "피싱 필터 만들기"),
    "nono": ("🧩", "큐싱 노노그램"),
    "notice": ("📬", "가짜 안내서 감별소"),
}

# 시민증 도장판: 도토리시 지도의 장소들(번호, 아이콘, 장소, 도장 받는 방법)
STAMP_PLACES = {
    "01": ("🏡", "할머니 댁", "할머니 폰 지키기 결말 보기"),
    "02": ("🎙️", "대화 연습실", "모의대화 연습 끝내기"),
    "03": ("🗝️", "민서네 집", "피싱 방탈출 탈출하기"),
    "04": ("🚧", "사이버 검문소", "주소나 문자 한 번 검사하기"),
    "05": ("📚", "시립도서관", "개념과 통계 둘러보기"),
    "06": ("⛲", "도토리 광장", "가짜뉴스 한 단계 끝내기"),
    "07": ("🚑", "시민안전센터", "피해 대처 안내 위치 알아 두기"),
    "08": ("🪪", "시민 등록소", "대처유형 결과 받기"),
    "09": ("🏫", "2학년 3반 단톡방", "마피아 사건 하나 공개하기"),
    "10": ("🛒", "중고마켓", "사기단 검거하기"),
    "11": ("📮", "우체국 필터실", "필터 한 번 실행하기"),
    "12": ("🅿️", "공영주차장", "노노그램 그림 하나 복원하기"),
    "13": ("🏛️", "통계청", "통계청 둘러보기"),
    "14": ("🏢", "아파트 관리사무소", "안내서 3건 판단 완료하기"),
}

# 업적 배지: 게임 속 특별한 순간에 받아요(번호: 아이콘, 이름, 받는 방법). 시민증이 있으면 시민증 문서에 함께 저장해요.
BADGES = "dotori_badges"
PENDING_BADGES = "dotori_pending_badges"
ACHIEVEMENTS = {
    "escape_nohint": ("🧠", "힌트 없이 잠금 해제", "방탈출 잠금 하나를 힌트 없이 열기"),
    "verify_call": ("📞", "원래 번호로 확인", "방탈출에서 저장된 번호로 직접 확인 전화 걸기"),
    "escape_fast": ("⚡", "번개 탈출", "방탈출을 15분 안에 탈출하기"),
    "escape_true": ("⭐", "트루 엔딩", "방탈출 트루 엔딩 보기"),
    "grandma_best": ("👵", "할머니 지킴이", "할머니 폰 지키기 최고 결말 보기"),
    "memo_clean": ("🔍", "한 번에 검거", "중고거래 사기단을 잘못 지목 없이 검거하기"),
    "nono_nohint": ("🧩", "힌트 없이 복원", "노노그램 그림을 힌트 없이 복원하기"),
    "filter_final": ("🤖", "필터 완성", "피싱 필터 만들기 마지막 시험까지 끝내기"),
    "voice_talk": ("🎙️", "말로 대답하기", "AI 모의대화에서 목소리로 대답하기"),
    "qr_scan": ("🔲", "QR 탐정", "큐싱 노노그램에서 QR 속 주소 검사하기"),
}

# 명예의 전당: 정렬 기준(앞이 작을수록 높은 순위)과 기록 글자
HALL_SORT = {
    "escape": lambda r: (-r.get("escaped", 0), -r.get("unlocked", 0), r.get("gave_up", 0), r.get("hints", 0), r.get("mistakes", 0), r.get("seconds", 0)),
    "grandma": lambda r: (-r.get("right", 0), -r.get("trust", 0)),
    "notice": lambda r: (-r.get("score", 0) / max(r.get("total", 5), 1), r.get("probes", 0)),
    "filter": lambda r: (-r.get("stars", 0), r.get("blocks", 0)),
    "nono": lambda r: (-r.get("stars", 0), r.get("hints", 0)),
    "memo": lambda r: (-r.get("stars", 0), r.get("hints", 0), r.get("wrong", 0)),
    "fakenews": lambda r: (-r.get("stars", 0), -r.get("avg", 0)),
    "mafia": lambda r: (-r.get("score", 0),),
}
HALL_TEXT = {
    "escape": lambda r: (("🔓 탈출 성공" if r.get("escaped") else (f"🏳️ 탈출 포기 · 잠금 {r.get('unlocked', 0)}/3" if r.get("gave_up") else f"⏳ 탈출 실패 · 잠금 {r.get('unlocked', 0)}/3"))
                         + f" · 힌트 {r.get('hints', 0)}번 · 재검토 {r.get('mistakes', 0)}번 · {r.get('seconds', 0) // 60}분 {r.get('seconds', 0) % 60}초"),
    "grandma": lambda r: f"맞은 판단 {r.get('right', 0)}/7 · 마지막 신뢰 {r.get('trust', 0)}",
    "notice": lambda r: (f"첫 제출 정확도 {r.get('score',0)}/{r.get('total',3)} · 자료 조사" if r.get("version")==3 else f"맞힌 안내서 {r.get('score', 0)}/{r.get('total', 5)}" + (" · 따로 확인" if r.get("version") == 2 else f" · 이전 번호부 활동 {r.get('probes', 0)}번")),
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


def _login_email(canonical):
    """닉네임을 로그인용 가짜 이메일 주소로 바꿔요(실제 메일은 보내지 않아요).
    한글 닉네임도 쓸 수 있게 글자를 base32로 바꿔 영어·숫자로만 만들어요."""
    import base64

    code = base64.b32encode(canonical.encode("utf-8")).decode("ascii").rstrip("=").lower()
    return f"c{code}@citizen.jamkkan.app"


def _auth(action, email, secret):
    """Firebase 이메일·비밀번호 로그인. 비밀 숫자는 Firebase가 암호화해 보관하고, 이 앱은 저장하지 않아요."""
    key, _ = config()
    result = request(
        f"https://identitytoolkit.googleapis.com/v1/accounts:{action}?" + urlencode({"key": key}),
        "POST", {"email": email, "password": secret, "returnSecureToken": True},
    )
    return {"uid": result["localId"], "token": result["idToken"], "refresh": result["refreshToken"],
            "expires": time.time() + int(result["expiresIn"])}


def _check_secret(secret):
    if not re.fullmatch(r"[0-9]{6}", secret or ""):
        raise ConnectionProblem(400, "SECRET_INVALID")


def _claim(account, name, canonical):
    """시민증 문서(citizens/닉네임)에 이 계정을 주인으로 적어요.
    kind=password는 '비밀 숫자로 지키는 닉네임'이라는 표시라서, 다른 사람이 가져갈 수 없어요(보안 규칙)."""
    path = _root() + "/citizens/" + quote(canonical, safe="")
    write = {
        "update": {"name": path, "fields": {"uid": {"stringValue": account["uid"]},
                                             "nickname": {"stringValue": name},
                                             "kind": {"stringValue": "password"}}},
        "updateTransforms": [{"fieldPath": "created_at", "setToServerValue": "REQUEST_TIME"}],
    }
    request(_url() + ":commit", "POST", {"writes": [write]}, account["token"])


def register(nickname, secret):
    """새 시민증: 닉네임 + 비밀 숫자 6자리. 한 번 만든 닉네임은 그 사람만 계속 쓸 수 있어요."""
    name, canonical = normalize_nickname(nickname)
    _check_secret(secret)
    try:
        account = _auth("signUp", _login_email(canonical), secret)
    except ConnectionProblem as exc:
        if exc.reason == "EMAIL_EXISTS":
            raise ConnectionProblem(409, "NICKNAME_TAKEN") from None
        raise
    try:
        _claim(account, name, canonical)
    except ConnectionProblem:
        # 예전 방식(하루짜리)으로 다른 사람이 오늘 쓰고 있는 닉네임이면 여기서 막혀요.
        raise ConnectionProblem(409, "NICKNAME_TAKEN") from None
    name = _keep(account, name, canonical)
    _merge_badges({})  # 시민증 없이 받은 배지도 새 시민증에 저장해요
    return name


def login(nickname, secret):
    """다시 들어오기: 시민증을 만들 때 정한 닉네임과 비밀 숫자로 같은 시민증을 되찾아요."""
    name, canonical = normalize_nickname(nickname)
    _check_secret(secret)
    try:
        account = _auth("signInWithPassword", _login_email(canonical), secret)
    except ConnectionProblem as exc:
        if exc.reason in ("EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"):
            raise ConnectionProblem(401, "LOGIN_FAILED") from None
        raise
    doc = request("https://firestore.googleapis.com/v1/" + quote(_root() + "/citizens/" + quote(canonical, safe=""), safe="/"), token=account["token"])
    shown = (doc or {}).get("fields", {}).get("nickname", {}).get("stringValue", name)
    saved = (doc or {}).get("fields", {}).get("stamps", {}).get("mapValue", {}).get("fields", {})
    badges = (doc or {}).get("fields", {}).get("badges", {}).get("mapValue", {}).get("fields", {})
    name = _keep(account, shown, canonical, {k: _value(v) for k, v in saved.items() if k in STAMP_PLACES})
    _merge_badges({k: _value(v) for k, v in badges.items() if k in ACHIEVEMENTS})
    return name


def _keep(account, name, canonical, saved=None):
    previous = citizen()
    if previous and previous.get("uid") != account["uid"]:
        if not logout():
            raise ConnectionProblem(409, "UNSAVED_STAMPS")
    account["nickname"] = name
    account["canonical"] = canonical
    st.session_state[CITIZEN] = account
    st.session_state[ANON] = account
    saved = saved or {}
    got = st.session_state.setdefault(STAMPS, {})
    pending = {k: v for k, v in got.items() if k in STAMP_PLACES and k not in saved}
    # 서버에 있던 도장은 서버 시각을 유지하고, 이번 창의 새 도장만 추가해요.
    got.update(saved)
    st.session_state[PENDING_STAMPS] = pending
    if pending:
        _save_stamps()
    from login_resume import remember
    remember()
    return name


def logout(discard=False):
    from admin_progress import active, sync, PENDING as ADMIN_PENDING
    if active() and st.session_state.get(ADMIN_PENDING) and not discard:
        if not sync():
            st.session_state["stamp_logout_blocked"]=True
            return False

    # 저장하지 못한 도장이 있으면 먼저 재시도하고, 실패 시 선택권을 보여 줘요.
    if citizen() and st.session_state.get(PENDING_STAMPS) and not discard:
        if not _save_stamps():
            st.session_state["stamp_logout_blocked"] = True
            return False
    preferences = {"sound_on", "sound_volume", "big_text"}
    # 이미 그린 설정 위젯은 다시 대입하지 않고 그대로 두어요.
    # 게임 결과, 컴포넌트 이벤트, 관리자 권한은 다음 이용자에게 넘기지 않아요.
    for key in list(st.session_state):
        if key not in preferences:
            del st.session_state[key]
    from login_resume import clear
    clear()
    return True


def _save_stamps():
    """이번 창에서 새로 받은 도장만 저장해 다른 기기의 도장을 보존해요."""
    account = citizen()
    if not account or not account.get("canonical"):
        return False
    pending = dict(st.session_state.get(PENDING_STAMPS, {}))
    pending = {k: v for k, v in pending.items() if k in STAMP_PLACES}
    if not pending:
        return True
    try:
        account = _fresh(account)
        path = _root() + "/citizens/" + quote(account["canonical"], safe="")
        fields = {k: {"stringValue": str(v)} for k, v in pending.items()}
        request(_url() + ":commit", "POST",
                {"writes": [{"update": {"name": path, "fields": {"stamps": {"mapValue": {"fields": fields}}}},
                             "updateMask": {"fieldPaths": [f"stamps.`{k}`" for k in pending]},
                             "currentDocument": {"exists": True}}]},
                account["token"])
    except ConnectionProblem:
        return False
    waiting = st.session_state.setdefault(PENDING_STAMPS, {})
    for code, when in pending.items():
        if waiting.get(code) == when:
            waiting.pop(code, None)
    st.session_state.pop("stamp_logout_blocked", None)
    return True


def show_stamp_sync_status():
    from admin_progress import active, status
    if active():
        status()
        return

    """페이지가 중간에 종료돼도 보이도록 사이드바에서 호출해요."""
    if not citizen() or not st.session_state.get(PENDING_STAMPS):
        return
    count = len(st.session_state[PENDING_STAMPS])
    st.warning(f"도장 {count}개가 아직 계정에 저장되지 않았어요. 저장 전에는 새로고침하거나 창을 닫지 마세요.")
    if st.button("도장 저장 다시 시도", key="stamp_retry", width="stretch"):
        if _save_stamps():
            st.rerun()
        else:
            st.error("아직 저장하지 못했어요. 인터넷 연결과 저장 권한을 확인해 주세요.")
    if st.session_state.get("stamp_logout_blocked"):
        st.info("저장에 실패해 로그아웃을 잠시 멈췄어요. 다시 저장하거나, 미저장 도장을 버리고 나갈 수 있어요.")
        if st.button("미저장 도장을 버리고 로그아웃", key="stamp_discard_logout", width="stretch"):
            logout(discard=True)
            st.rerun()


def my_photo():
    """한 사람에게는 항상 같은 깡지 증명사진을 보여 줘요(닉네임으로 4장 중 하나를 골라요).
    시민증이 없으면 기본 사진, 도장을 다 모은 명예 시민은 활짝 웃는 사진이에요."""
    import zlib
    from mascot_ui import ID_PHOTOS

    me = citizen()
    if not me:
        return ID_PHOTOS[0]
    if len(stamps()) == len(STAMP_PLACES):
        return "ggangji_cream.png"
    return ID_PHOTOS[zlib.crc32(me["nickname"].lower().encode("utf-8")) % len(ID_PHOTOS)]


def scroll_top():
    """새 화면(게임 시작·다음 단계 등)으로 넘어갈 때 맨 위부터 보이게 표시해 둬요. app.py가 페이지를 다 그린 뒤 올려 줘요."""
    st.session_state["scroll_top"] = st.session_state.get("scroll_top", 0) + 1


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
    st.session_state.setdefault(MY, []).append((game, text, datetime.now(KST).strftime("%H:%M")))


def stamp(code, quiet=False):
    from admin_progress import active, award
    if active():return award(code,quiet)

    """그 장소의 도장을 찍어요. 이미 있으면 그대로 두고, 처음 받을 때만 알림을 띄워요.
    시민증이 있으면 시민증 문서에 저장해서 다음에 다시 들어와도 이어서 모을 수 있어요.
    시민증이 없으면 이번 방문(창)에만 있어요."""
    got = st.session_state.setdefault(STAMPS, {})
    if code not in STAMP_PLACES:
        return False
    if code in got:
        return False
    got[code] = datetime.now(KST).strftime("%m/%d %H:%M")
    if citizen():
        st.session_state.setdefault(PENDING_STAMPS, {})[code] = got[code]
        if not _save_stamps():
            st.warning("도장을 계정에 저장하지 못했어요. 새로고침하지 말고, 다른 메뉴로 이동한 뒤 사이드바에서 다시 저장해 주세요.")
    if not quiet:
        # 바로 그리지 않고 '보여 줄 도장'으로 맡겨 둬요. 페이지가 다시 그려져도(st.rerun) 사라지지 않게
        # app.py가 페이지를 다 그린 뒤 show_stamp_popup()으로 한 번만 보여 줘요.
        st.session_state["stamp_popup"] = (code, len(got))
    return True


# ───────── 업적 배지 ─────────

def _merge_badges(saved):
    """로그인할 때: 서버에 있던 배지와 이번 창에서 받은 배지를 합치고, 새로 받은 것만 저장해요."""
    got = st.session_state.setdefault(BADGES, {})
    pending = {k: v for k, v in got.items() if k not in saved}
    got.update(saved)
    st.session_state[PENDING_BADGES] = pending
    if pending:
        _save_badges()


def _save_badges():
    """새로 받은 배지만 시민증 문서의 badges 칸에 저장해요. 실패해도 이번 창에는 그대로 남아요."""
    account = citizen()
    pending = dict(st.session_state.get(PENDING_BADGES, {}))
    if not account or not account.get("canonical") or not pending:
        return not pending
    try:
        account = _fresh(account)
        path = _root() + "/citizens/" + quote(account["canonical"], safe="")
        fields = {k: {"stringValue": str(v)} for k, v in pending.items()}
        request(_url() + ":commit", "POST",
                {"writes": [{"update": {"name": path, "fields": {"badges": {"mapValue": {"fields": fields}}}},
                             "updateMask": {"fieldPaths": [f"badges.`{k}`" for k in pending]},
                             "currentDocument": {"exists": True}}]},
                account["token"])
    except ConnectionProblem:
        return False
    waiting = st.session_state.setdefault(PENDING_BADGES, {})
    for code in pending:
        waiting.pop(code, None)
    return True


def achieve(code):
    """업적 배지를 줘요. 처음 받을 때만 화면 위쪽에 배지 알림과 효과음이 나와요."""
    if code not in ACHIEVEMENTS:
        return False
    got = st.session_state.setdefault(BADGES, {})
    if code in got:
        return False
    got[code] = datetime.now(KST).strftime("%m/%d %H:%M")
    if citizen() and not st.session_state.get("admin_open"):
        st.session_state.setdefault(PENDING_BADGES, {})[code] = got[code]
        _save_badges()
    st.session_state.setdefault("badge_popup", []).append(code)
    return True


def badges():
    return st.session_state.get(BADGES, {})


def show_badge_popup():
    """맡겨 둔 배지 알림을 화면 위쪽 가운데에 게임 업적처럼 보여 줘요(효과음 포함)."""
    queue = st.session_state.pop("badge_popup", None)
    if not queue:
        return
    import json as _json
    import streamlit.components.v1 as components
    items = [{"icon": ACHIEVEMENTS[c][0], "name": ACHIEVEMENTS[c][1], "how": ACHIEVEMENTS[c][2]} for c in queue if c in ACHIEVEMENTS]
    total, have = len(ACHIEVEMENTS), len(badges())
    st.session_state["_badge_n"] = st.session_state.get("_badge_n", 0) + 1
    components.html(
        "<script>(()=>{const items=" + _json.dumps(items, ensure_ascii=False).replace("<", "\\u003c") + ";"
        f"const total={total},have={have};"
        """const D=parent.document,H=parent.__jamkkanSound;
let box=D.getElementById('jk-badges');if(!box){box=D.createElement('div');box.id='jk-badges';
box.innerHTML='<style>#jk-badges{position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:1000001;display:flex;flex-direction:column;gap:10px;pointer-events:none;width:min(440px,calc(100vw - 24px))}'
+'#jk-badges .b{display:flex;align-items:center;gap:14px;background:linear-gradient(135deg,#1f2937,#111827);color:#fff;border:3px solid #f6d55c;border-radius:20px;padding:12px 16px;box-shadow:0 12px 30px #0007;animation:jkb-in 4.6s ease-out forwards}'
+'#jk-badges .i{width:60px;height:60px;flex-shrink:0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:32px;background:radial-gradient(circle,#fff7d1,#f6d55c);box-shadow:0 0 0 4px #f6d55c55;animation:jkb-pop .6s .2s ease-out both}'
+'#jk-badges small{display:block;color:#f6d55c;font-weight:900;font-size:.85rem;letter-spacing:.04em}#jk-badges b{display:block;font-size:1.15rem;font-family:Pretendard Variable,Pretendard,system-ui,sans-serif}#jk-badges em{display:block;font-style:normal;color:#cbd5e1;font-size:.85rem}'
+'@keyframes jkb-in{0%{transform:translateY(-30px);opacity:0}10%{transform:none;opacity:1}85%{opacity:1}100%{opacity:0;transform:translateY(-10px)}}@keyframes jkb-pop{0%{transform:scale(0) rotate(-40deg)}70%{transform:scale(1.2) rotate(8deg)}100%{transform:scale(1)}}'
+'@media (prefers-reduced-motion:reduce){#jk-badges .b,#jk-badges .i{animation:none}}</style>';D.body.appendChild(box);}
items.forEach((it,k)=>{setTimeout(()=>{const b=D.createElement('div');b.className='b';b.style.fontFamily='Pretendard Variable,Pretendard,system-ui,sans-serif';
 const i=D.createElement('div');i.className='i';i.textContent=it.icon;const t=D.createElement('div');
 const s=D.createElement('small');s.textContent='🏅 업적 달성! ('+(have-items.length+k+1)+' / '+total+')';const n=D.createElement('b');n.textContent=it.name;const e=D.createElement('em');e.textContent=it.how;
 t.append(s,n,e);b.append(i,t);box.appendChild(b);setTimeout(()=>b.remove(),4700);
 try{if(H&&H.want){const go=()=>H.play('result');if(H.ctx&&H.ctx.state==='running')go();else if(H.activate)H.activate().then(go).catch(()=>{});}}catch(x){}
},k*1300);});})();</script>"""
        + f"<!-- {st.session_state['_badge_n']} -->",
        height=0,
    )


@st.cache_data(show_spinner=False)
def _ding(gain=1.0):
    """도장 효과음 '띵동'(짧은 두 음)을 WAV 소리 파일로 만들어요. 외부 파일 없이 숫자로 만든 소리예요.
    gain은 음량 배율이에요(1.0이 기본)."""
    import io
    import math
    import struct
    import wave

    rate, notes = 22050, [(1046.5, 0.12), (1318.5, 0.22)]  # 도(C6) → 미(E6)
    frames = bytearray()
    for freq, length in notes:
        n = int(rate * length)
        for i in range(n):
            fade = min(1.0, i / 300) * (1 - i / n)  # 딸깍 소리 없이 부드럽게 시작·끝
            frames += struct.pack("<h", int(9000 * gain * fade * math.sin(2 * math.pi * freq * i / rate)))
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    return buffer.getvalue()


def show_stamp_popup():
    """맡겨 둔 도장이 있으면 화면 오른쪽 위에 도장이 쾅 찍히는 알림과 '띵동' 소리를 한 번 보여 줘요."""
    pending = st.session_state.pop("stamp_popup", None)
    if not pending:
        return
    code, count = pending
    icon, place, _ = STAMP_PLACES[code]
    total = len(STAMP_PLACES)
    done = count == total
    title = "🎖️ 명예 시민 달성!" if done else f"{place} 도장 쾅!"
    sub = f"{total}곳 도장을 모두 모았어요!" if done else f"도장 {count} / {total}"
    if citizen() and code in st.session_state.get(PENDING_STAMPS, {}):
        sub += " · 계정 저장 대기 중"
    if st.session_state.get("admin_open") and code in st.session_state.get("admin_progress_pending", {}):
        sub += " · 관리자 저장 대기 중"
    st.markdown(
        """<style>
        @keyframes sp-in {0%{transform:translateY(-20px);opacity:0} 12%{transform:translateY(0);opacity:1}
          85%{opacity:1} 100%{opacity:0;visibility:hidden}}
        @keyframes sp-stamp {0%{transform:scale(2.6) rotate(-25deg);opacity:0} 55%{transform:scale(.9) rotate(-10deg);opacity:1}
          100%{transform:scale(1) rotate(-12deg);opacity:1}}
        .sp-pop {position:fixed;top:64px;right:20px;z-index:999999;display:flex;align-items:center;gap:12px;
          background:#FFFBF0;border:2px solid #F1DFA6;border-radius:18px;padding:12px 18px 12px 12px;
          box-shadow:0 10px 26px rgba(0,0,0,.15);animation:sp-in 3.6s ease-out forwards;pointer-events:none;}
        .sp-ring {width:58px;height:58px;border-radius:50%;border:3px solid #B42318;display:flex;align-items:center;
          justify-content:center;font-size:28px;background:#fff;box-shadow:inset 0 0 0 3px #FFFBF0,inset 0 0 0 5px #B42318;
          animation:sp-stamp .55s .15s ease-out both;}
        .sp-pop b {display:block;color:#20483F;font-size:1.05rem;} .sp-pop small {color:#B42318;font-weight:800;}
        .st-key-stamp_sound {position:absolute !important;width:1px;height:1px;overflow:hidden;opacity:0;}
        @media (prefers-reduced-motion: reduce) {.sp-pop,.sp-ring {animation:none !important;}}
        </style>"""
        f'<div class="sp-pop"><div class="sp-ring">{icon}</div><div><b>{title}</b><small>{sub}</small></div></div>',
        unsafe_allow_html=True,
    )
    # 사이드바에서 효과음을 껐거나 음량이 0이면 소리 없이 도장 알림만 보여 줘요.
    if st.session_state.get("sound_on", True):
        volume = st.session_state.get("sound_volume", 60)
        if volume > 0:
            with st.container(key="stamp_sound"):
                st.audio(_ding(min(volume / 60, 1.6)), format="audio/wav", autoplay=True)


def stamps():
    from admin_progress import active, load
    if active():return load()

    return st.session_state.get(STAMPS, {})


def stamp_time(text):
    """도장 받은 시각: 오늘 받은 건 시:분만, 예전에 받은 건 월/일만 보여 줘요."""
    text = str(text)
    if " " not in text:
        return text
    day, clock = text.split(" ", 1)
    return clock if day == datetime.now(KST).strftime("%m/%d") else day


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
    elif not account and st.session_state.get("admin_open"):
        st.info("🔑 관리자 모드는 연습 모드로만 플레이돼요. 명예의 전당 기록은 남지 않아요. 기록을 남기려면 시민증 닉네임으로 로그인해 주세요.")
    elif not account:
        st.page_link("pages/0_도토리시_시민증.py", label="시민증(닉네임)을 만들면 명예의 전당에 기록이 올라가요", icon="🪪")

# ───────── 시민증 만들기·다시 들어오기 화면 ─────────

def show_login_forms(prefix):
    """시민증 페이지와 첫 화면(로그인 화면)에서 함께 쓰는 '새 시민증 만들기 / 다시 들어오기' 입력 상자."""
    from firebase_support import explain

    # 처음이면 '새 시민증 만들기', 전에 만든 적이 있으면 '다시 들어오기'
    mode_key = f"login_mode_{prefix}"
    mode = st.session_state.get(mode_key, "new")
    with st.container(key=f"login_choices_{prefix}"):
        st.markdown("""<style>
        [class*="st-key-login_choices_"] button{min-height:58px!important;border-radius:12px!important;}
        [class*="st-key-login_choices_"] button p{white-space:normal!important;font-weight:800!important;}
        @media(max-width:640px){[class*="st-key-login_choices_"] [data-testid="stHorizontalBlock"]{flex-direction:column!important;}
        [class*="st-key-login_choices_"] [data-testid="stColumn"]{width:100%!important;flex:1 1 auto!important;}}
        </style>""",unsafe_allow_html=True)
        first, second, third = st.columns(3)
        if first.button("🪪 새 시민증 만들기",key=f"choose_new_{prefix}",width="stretch",type="primary" if mode=="new" else "secondary"):
            st.session_state[mode_key]="new"
            st.rerun()
        if second.button("🔑 다시 들어오기",key=f"choose_back_{prefix}",width="stretch",type="primary" if mode=="back" else "secondary"):
            st.session_state[mode_key]="back"
            st.rerun()
        if third.button("👀 로그인 없이 둘러보기",key=f"choose_guest_{prefix}",width="stretch"):
            st.session_state["guest"]=True
            # 홈으로 보내지 않고 보던 페이지에 그대로 있어요(시민증 페이지에서 눌렀으면 보던 페이지로 돌아가요).
            if prefix=="page":
                st.session_state["login_return"]=True
            st.rerun()
        third.caption("기록은 저장되지 않아요")

    if mode == "new":
        with st.form(f"dotori_register_{prefix}"):
            nickname = st.text_input("닉네임 (한글·영문·숫자·밑줄 2~12자)", max_chars=12, placeholder="예: 도토리탐정", key=f"new_nick_{prefix}")
            secret = st.text_input("비밀 숫자 6자리 (다시 들어올 때 필요해요)", max_chars=6, type="password", placeholder="숫자 6개", key=f"new_secret_{prefix}")
            again = st.text_input("비밀 숫자 한 번 더", max_chars=6, type="password", key=f"new_again_{prefix}")
            ok = st.form_submit_button("🪪 시민증 만들기", type="primary", width="stretch")
        if ok:
            if secret != again:
                st.error("두 비밀 숫자가 서로 달라요. 다시 입력해 주세요.")
            else:
                try:
                    with st.spinner("시민증을 만들고 있어요…"):
                        name = register(nickname, secret)
                    st.success(f"환영해요, {name}님! 닉네임과 비밀 숫자를 기억해 두면 다음에도 같은 시민증으로 들어올 수 있어요.")
                    if prefix=="page":
                        st.session_state["login_return"]=True  # 시민증을 만들면 보던 페이지로 돌아가요.
                    st.rerun()
                except ConnectionProblem as exc:
                    if exc.reason == "NICKNAME_TAKEN":
                        st.error("이미 다른 시민이 쓰고 있는 닉네임이에요. 내 닉네임이라면 ‘다시 들어오기’를 눌러 주세요.")
                    elif exc.reason == "SECRET_INVALID":
                        st.error("비밀 숫자는 숫자 6개로 입력해 주세요.")
                    else:
                        st.error(explain(exc))
    if mode == "back":
        with st.form(f"dotori_login_{prefix}"):
            nickname = st.text_input("닉네임", max_chars=12, key=f"back_nick_{prefix}")
            secret = st.text_input("비밀 숫자 6자리", max_chars=6, type="password", key=f"back_secret_{prefix}")
            ok = st.form_submit_button("🔑 내 시민증으로 들어가기", type="primary", width="stretch")
        if ok:
            try:
                with st.spinner("시민증을 찾고 있어요…"):
                    name = login(nickname, secret)
                st.success(f"다시 만나서 반가워요, {name}님!")
                if prefix=="page":
                    st.session_state["login_return"]=True  # 다시 들어오면 보던 페이지로 돌아가요.
                st.rerun()
            except ConnectionProblem as exc:
                if exc.reason == "LOGIN_FAILED":
                    st.error("닉네임이나 비밀 숫자가 맞지 않아요.")
                elif exc.reason == "SECRET_INVALID":
                    st.error("비밀 숫자는 숫자 6개로 입력해 주세요.")
                elif exc.reason == "TOO_MANY_ATTEMPTS_TRY_LATER":
                    st.error("여러 번 틀려서 잠시 막혔어요. 조금 뒤에 다시 시도해 주세요.")
                else:
                    st.error(explain(exc))
