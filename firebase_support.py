"""Firebase 익명 인증과 공동 랭킹 연결."""

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st


CASE = "case01_v1"


class ConnectionProblem(Exception):
    def __init__(self, status=0, reason="UNKNOWN"):
        self.status = status
        self.reason = reason
        super().__init__(f"연결 오류 ({status})")


def config():
    """Streamlit Secrets에서 연결 정보를 읽습니다."""
    try:
        cfg = st.secrets["firebase"]
        return (
            str(cfg["api_key"]).strip(),
            str(cfg["project_id"]).strip(),
        )
    except (KeyError, FileNotFoundError):
        raise ConnectionProblem(-1) from None


def request(url, method="GET", payload=None, token=None, form=False):
    """요청을 보내고, 키가 노출되지 않도록 오류 종류만 전달합니다."""
    headers = {}
    data = None

    if payload is not None:
        body = urlencode(payload) if form else json.dumps(payload)
        data = body.encode("utf-8")
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded"
            if form
            else "application/json"
        )

    if token:
        headers["Authorization"] = "Bearer " + token

    try:
        req = Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        with urlopen(req, timeout=12) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}

    except HTTPError as exc:
        reason = "UNKNOWN"

        allowed = {
            "OPERATION_NOT_ALLOWED",
            "ADMIN_ONLY_OPERATION",
            "CONFIGURATION_NOT_FOUND",
            "API_KEY_INVALID",
            "API_KEY_SERVICE_BLOCKED",
            "API_KEY_HTTP_REFERRER_BLOCKED",
            "API_KEY_IP_ADDRESS_BLOCKED",
            "SERVICE_DISABLED",
            "PROJECT_NOT_FOUND",
            "TOO_MANY_ATTEMPTS_TRY_LATER",
            "QUOTA_EXCEEDED",
            "BILLING_NOT_ENABLED",
            "INVALID_APP_CREDENTIAL",
            "INVALID_REFRESH_TOKEN",
            "TOKEN_EXPIRED",
            "USER_DISABLED",
            "PERMISSION_DENIED",
            "INVALID_ARGUMENT",
        }

        try:
            error = json.loads(exc.read()).get("error", {})

            if isinstance(error, dict):
                message = str(error.get("message", ""))
                candidates = []

                for detail in error.get("details", []):
                    if isinstance(detail, dict):
                        candidates.append(detail.get("reason"))

                candidates.append(message.split(" : ")[0].strip())

                if message.startswith("API key not valid"):
                    candidates.append("API_KEY_INVALID")

                candidates.append(error.get("status"))

                reason = next(
                    (
                        value
                        for value in candidates
                        if isinstance(value, str) and value in allowed
                    ),
                    "UNKNOWN",
                )

        except (ValueError, TypeError, AttributeError, OSError):
            pass

        raise ConnectionProblem(exc.code, reason) from None

    except (URLError, TimeoutError, ValueError, OSError):
        raise ConnectionProblem() from None


def explain(exc):
    """오류 코드에 맞는 안내 문구를 만듭니다."""
    reasons = {
        "OPERATION_NOT_ALLOWED": (
            "이 키가 속한 프로젝트에서 익명 인증을 허용하지 않았어요. "
            "익명 인증을 켠 프로젝트의 웹앱 apiKey인지 확인하세요."
        ),
        "ADMIN_ONLY_OPERATION": (
            "이 프로젝트의 사용자 가입이 관리자에게만 허용되어 있어요. "
            "Authentication의 가입 허용 설정을 확인하세요."
        ),
        "CONFIGURATION_NOT_FOUND": (
            "이 키가 속한 프로젝트에서 Authentication 설정을 찾지 못했어요. "
            "jamkkan-project 웹앱의 apiKey와 비교하세요."
        ),
        "API_KEY_INVALID": (
            "API 키가 유효하지 않아요. Firebase 웹앱 설정의 apiKey를 "
            "Secrets의 [firebase] api_key에 다시 복사하세요."
        ),
        "API_KEY_SERVICE_BLOCKED": (
            "키의 API 제한에서 Firebase Authentication 요청을 차단하고 있어요. "
            "Identity Toolkit API 허용 여부를 확인하세요."
        ),
        "API_KEY_HTTP_REFERRER_BLOCKED": (
            "웹사이트 주소 제한이 서버에서 보내는 로그인 요청을 차단하고 있어요. "
            "이 키의 애플리케이션 제한을 확인하세요."
        ),
        "API_KEY_IP_ADDRESS_BLOCKED": (
            "이 API 키의 IP 주소 제한으로 요청이 차단됐어요."
        ),
        "SERVICE_DISABLED": (
            "프로젝트에서 요청한 API가 비활성화되어 있어요. "
            "로그인 오류라면 Identity Toolkit API 상태를 확인하세요."
        ),
        "TOO_MANY_ATTEMPTS_TRY_LATER": (
            "짧은 시간에 가입 요청이 많아 제한됐어요. "
            "반복 클릭을 멈추고 잠시 뒤 시도하세요."
        ),
        "QUOTA_EXCEEDED": (
            "서비스 사용량 제한에 도달했어요. Firebase 사용량을 확인하세요."
        ),
    }

    detail = reasons.get(exc.reason)

    fallback = {
        -1: "Streamlit Secrets의 [firebase] api_key와 project_id를 확인해 주세요.",
        400: "요청이 거절됐어요. 아래 오류 코드로 원인을 확인해야 해요.",
        401: "로그인 인증을 갱신하지 못했어요. 잠시 후 다시 시도하세요.",
        403: "접근이 거부됐어요. Firebase 프로젝트와 게시한 Firestore 규칙을 확인하세요.",
        404: "프로젝트 ID와 Firestore (default) 데이터베이스를 확인하세요.",
        429: "요청이 많거나 무료 한도에 도달했어요. 잠시 후 다시 시도하세요.",
    }.get(
        exc.status,
        "저장소에 연결하지 못했어요. 게임은 계속 이용할 수 있어요.",
    )

    return f"{detail or fallback} [HTTP {exc.status} / {exc.reason}]"


def user():
    return st.session_state.get("firebase_user")


def sign_in(nickname):
    """익명 계정을 만들고 현재 세션에 연결합니다."""
    key, _ = config()

    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signUp?"
        + urlencode({"key": key})
    )

    result = request(
        url,
        "POST",
        {"returnSecureToken": True},
    )

    st.session_state["firebase_user"] = {
        "uid": result["localId"],
        "token": result["idToken"],
        "refresh": result["refreshToken"],
        "expires": time.time() + int(result["expiresIn"]),
        "nickname": nickname,
    }


def access_token():
    """현재 세션의 인증 토큰이 만료되기 전에 갱신합니다."""
    account = user()

    if not account:
        raise ConnectionProblem(401)

    if time.time() >= account["expires"] - 60:
        key, _ = config()

        url = (
            "https://securetoken.googleapis.com/v1/token?"
            + urlencode({"key": key})
        )

        result = request(
            url,
            "POST",
            {
                "grant_type": "refresh_token",
                "refresh_token": account["refresh"],
            },
            form=True,
        )

        account.update(
            token=result["id_token"],
            refresh=result["refresh_token"],
            expires=time.time() + int(result["expires_in"]),
        )

    return account["token"]


def root():
    _, project = config()
    return f"projects/{project}/databases/(default)/documents"


def entry_path():
    uid = quote(user()["uid"], safe="")
    return root() + f"/leaderboards/{CASE}/entries/{uid}"


def save_result(game):
    """완료한 게임을 계정별 한 번만 저장합니다."""
    account = user()

    if (
        not account
        or game.get("rank_uid") != account["uid"]
        or game.get("unlocked") != 3
    ):
        raise ConnectionProblem(401)

    path = entry_path()
    token = access_token()

    # 이전 요청이 성공했다면 기존 기록을 유지합니다.
    try:
        request(
            "https://firestore.googleapis.com/v1/" + path,
            token=token,
        )
        return "existing"

    except ConnectionProblem as exc:
        if exc.status != 404:
            raise

    seconds = max(
        0,
        int(game["finished"] - game["started"]),
    )

    fields = {
        "nickname": {
            "stringValue": game["rank_nickname"],
        },
        "hints": {
            "integerValue": str(sum(game["hints"].values())),
        },
        "mistakes": {
            "integerValue": str(game["mistakes"]),
        },
        "seconds": {
            "integerValue": str(seconds),
        },
        "completed": {
            "booleanValue": True,
        },
    }

    payload = {
        "writes": [
            {
                "update": {
                    "name": path,
                    "fields": fields,
                },
                "currentDocument": {
                    "exists": False,
                },
                "updateTransforms": [
                    {
                        "fieldPath": "created_at",
                        "setToServerValue": "REQUEST_TIME",
                    }
                ],
            }
        ]
    }

    try:
        request(
            "https://firestore.googleapis.com/v1/" + root() + ":commit",
            "POST",
            payload,
            token,
        )

    except ConnectionProblem as exc:
        if exc.status not in (409, 403):
            raise

        # 동시에 요청이 실행된 경우에도 기존 기록을 덮어쓰지 않습니다.
        request(
            "https://firestore.googleapis.com/v1/" + path,
            token=token,
        )
        return "existing"

    return "saved"


@st.cache_data(ttl=60, show_spinner=False)
def rankings(project):
    """공개 기록을 읽어 공동 순위를 계산합니다."""
    base = (
        "https://firestore.googleapis.com/v1/"
        f"projects/{project}/databases/(default)/documents/"
        f"leaderboards/{CASE}/entries"
    )

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
        # 일부 기록만 읽고 전체 순위인 것처럼 표시하지 않습니다.
        raise ConnectionProblem(0)

    rows = []

    for document in documents:
        fields = document["fields"]

        rows.append(
            {
                "닉네임": fields["nickname"]["stringValue"],
                "힌트": int(fields["hints"]["integerValue"]),
                "재검토": int(fields["mistakes"]["integerValue"]),
                "경과 시간(초)": int(fields["seconds"]["integerValue"]),
            }
        )

    rows.sort(
        key=lambda row: (
            row["힌트"],
            row["재검토"],
            row["닉네임"],
        )
    )

    previous = None
    rank = 0

    for index, row in enumerate(rows, 1):
        score = (row["힌트"], row["재검토"])

        if score != previous:
            rank = index

        row["순위"] = rank
        previous = score

    return [{"순위": row["순위"], **row} for row in rows]


def show_ranking(embedded=False):
    st.title("🏆 함께한 탈출 기록")

    st.caption(
        "사건 01 · 버전 1 / 익명 계정별 첫 저장 기록 / "
        "힌트 적은 순 → 재검토 적은 순, 같으면 공동 순위"
    )

    st.write(
        "경과 시간은 참고 정보예요. 반복 참여가 가능한 학습용 랭킹이며, "
        "사람별 최초 도전이나 부정행위 방지를 보장하지 않아요."
    )

    try:
        _, project = config()
        rows = rankings(project)

        if rows:
            st.dataframe(
                rows,
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("아직 저장된 기록이 없어요. 첫 탈출에 도전해 보세요!")

        st.caption(
            "무료 사용량을 아끼기 위해 랭킹은 최대 60초 동안 "
            "같은 결과를 보여줘요."
        )

    except ConnectionProblem as exc:
        st.warning(explain(exc))
        st.caption(
            "기록 조회에 실패했어요. 저장된 기록이 삭제됐다는 뜻은 아니에요."
        )

    if not embedded:
        st.page_link(
            "pages/3_피싱_방탈출.py",
            label="방탈출 도전",
            icon="🗝️",
        )

    if user():
        with st.expander("내 공개 기록 삭제"):
            confirm = st.checkbox(
                "현재 익명 계정의 공개 기록을 삭제합니다."
            )

            if st.button("내 기록 삭제", disabled=not confirm):
                try:
                    request(
                        "https://firestore.googleapis.com/v1/" + entry_path(),
                        "DELETE",
                        token=access_token(),
                    )

                    game = st.session_state.get("escape_game", {})
                    game["rank_status"] = "deleted"
                    rankings.clear()

                    st.success(
                        "삭제했어요. 다음에 이 메뉴를 열면 반영돼요."
                    )

                except ConnectionProblem as exc:
                    st.error(explain(exc))


def result_panel(game):
    """결과를 자동 저장하거나 실패 시 재시도 버튼을 보여줍니다."""
    if not game.get("rank_uid"):
        st.info(
            "연습 모드의 기록이에요. 공개 저장하지 않습니다. "
            "랭킹에 참여하려면 ‘시작 안내·입장’에서 "
            "랭킹 참여로 새 게임을 시작해 주세요."
        )
        return

    status = game.get("rank_status")

    if status == "deleted":
        st.caption("이 게임의 공개 기록은 삭제했어요.")
        return

    if status in ("saved", "existing"):
        if status == "saved":
            st.success("공동 랭킹에 저장했어요.")
        else:
            st.success(
                "이 익명 계정의 기록이 이미 있어요. "
                "기존 결과를 유지했어요."
            )
        return

    retry = False

    if status == "failed":
        st.warning(game.get("rank_error", "저장하지 못했어요."))

        st.caption(
            "결과는 아래에서 다운로드할 수 있어요. "
            "재시도 전에 페이지를 새로고침하거나 게임을 초기화하지 마세요."
        )

        retry = st.button(
            "기록 저장 다시 시도",
            key="escape_retry_save",
        )

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
