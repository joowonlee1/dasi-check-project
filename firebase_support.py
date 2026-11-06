"""Firebase(인증·Firestore)와 통신하는 공통 도구.

- config(): Streamlit Secrets에서 Firebase 연결 정보를 읽어요.
- request(): Firebase REST API에 요청을 보내고, 실패하면 원인(reason)을 담은 ConnectionProblem을 일으켜요.
- explain(): 실패 원인을 사용자가 이해할 수 있는 한국어 안내로 바꿔요. (API 키 같은 비밀 정보는 화면에 보여 주지 않아요.)
- normalize_nickname(): 닉네임 형식(한글·영문·숫자·밑줄 2~12자)을 검사해요.
시민증·통계·명예의 전당 같은 실제 기능은 dotori_data.py가 이 도구를 불러 써요.
"""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st



class ConnectionProblem(Exception):
    # status는 HTTP 상태 코드, reason은 실패 원인 이름(예: EMAIL_EXISTS)이에요.
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
            # 닉네임 + 비밀 숫자 시민증(이메일·비밀번호 방식)에서 쓰는 오류
            "EMAIL_EXISTS",
            "EMAIL_NOT_FOUND",
            "INVALID_PASSWORD",
            "INVALID_LOGIN_CREDENTIALS",
            "WEAK_PASSWORD",
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

    if exc.reason == "NICKNAME_TAKEN":
        return (
            "이미 사용 중인 닉네임입니다. "
            "다른 이름을 입력해 주세요."
        )

    if exc.reason == "NICKNAME_INVALID":
        return (
            "닉네임은 한글·영문·숫자·밑줄을 사용해 "
            "2~12자로 입력해 주세요."
        )


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


def normalize_nickname(nickname):
    """앞뒤 공백을 제거하고 닉네임 형식을 확인합니다."""
    name = nickname.strip()

    if not re.fullmatch(r"[가-힣a-zA-Z0-9_]{2,12}", name):
        raise ConnectionProblem(400, "NICKNAME_INVALID")

    # Test와 test를 같은 이름으로 취급합니다.
    return name, name.lower()


