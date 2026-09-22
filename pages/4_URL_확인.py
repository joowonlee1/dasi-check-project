import ipaddress
import re
from urllib.parse import urlsplit, unquote

import streamlit as st


# 이 목록은 모든 단축 주소 서비스를 포함하지 않습니다.
SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "url.kr",
    "vo.la",
    "me2.do",
}


def analyze_url(raw):
    """주소 문자열만 분석합니다. 네트워크 요청은 하지 않습니다."""
    raw = raw.strip()

    if not raw:
        raise ValueError("URL을 먼저 입력해 주세요.")

    if len(raw) > 2048:
        raise ValueError("주소가 너무 길어요. 2,048자 이하로 입력해 주세요.")

    if re.search(r"\s", raw):
        raise ValueError("주소 안에 공백이나 줄바꿈이 있어요. URL 하나만 입력해 주세요.")

    if "\\" in raw:
        raise ValueError("역슬래시가 포함되어 해석이 모호해요. 주소를 다시 확인해 주세요.")

    if re.search(r"%(?![0-9a-fA-F]{2})", raw):
        raise ValueError("주소의 퍼센트 인코딩 형식이 올바르지 않아요.")

    # 프로토콜이 없는 일반 주소는 분석을 위해 https://를 붙입니다.
    if raw.startswith("//"):
        candidate = "https:" + raw
        assumed = True
    elif "://" in raw:
        candidate = raw
        assumed = False
    else:
        if re.match(r"^(javascript|data|file|mailto):", raw, re.I):
            raise ValueError("http 또는 https 웹 주소만 확인할 수 있어요.")
        candidate = "https://" + raw
        assumed = True

    try:
        parts = urlsplit(candidate)

        if parts.scheme.lower() not in {"http", "https"}:
            raise ValueError("http 또는 https 웹 주소만 확인할 수 있어요.")

        hostname = parts.hostname
        port = parts.port

        if not hostname:
            raise ValueError("사이트 주소를 찾을 수 없어요.")

        host = hostname.rstrip(".").encode("idna").decode("ascii").lower()

    except (ValueError, UnicodeError):
        raise ValueError("주소 형식이 올바르지 않아요. 호스트명과 포트 번호를 확인해 주세요.")

    try:
        ipaddress.ip_address(host)
        is_ip = True
    except ValueError:
        is_ip = False

    if not is_ip:
        labels = host.split(".")

        if len(labels) < 2 or len(host) > 253:
            raise ValueError("example.com처럼 전체 도메인 주소를 입력해 주세요.")

        for label in labels:
            if not re.fullmatch(
                r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?",
                label,
            ):
                raise ValueError("도메인 이름의 형식이 올바르지 않아요.")

    findings = []

    if parts.username is not None or parts.password is not None:
        findings.append(
            (
                "주소에 사용자 정보(@ 앞부분)가 있어요.",
                "@ 앞의 익숙한 이름이 실제 사이트 주소는 아닐 수 있어요. "
                "아래에 표시한 호스트명을 확인하세요.",
            )
        )

    if host in SHORTENERS:
        findings.append(
            (
                "등록된 단축 URL 서비스 주소예요.",
                "이 문자열만으로 최종 연결 사이트를 알 수 없어요. "
                "단축 주소라는 사실만으로 악성이라고 판단하지는 않아요.",
            )
        )

    path = unquote(parts.path).lower()

    if re.search(r"\.apk(?:$|[;/])", path):
        findings.append(
            (
                "경로에 APK 확장자가 있어요.",
                "안드로이드 앱 설치 파일을 가리킬 수 있어요. "
                "파일 내용이나 악성 여부를 검사한 결과는 아니에요.",
            )
        )

    if is_ip:
        findings.append(
            (
                "도메인 이름 대신 IP 주소를 사용해요.",
                "숫자 주소만으로 운영 기관을 알아보기 어려워요. "
                "정상 서비스에서도 IP 주소를 사용할 수 있어요.",
            )
        )

    if any(label.startswith("xn--") for label in host.split(".")):
        findings.append(
            (
                "국제화 도메인이 포함돼 있어요.",
                "한글 등 여러 언어의 도메인을 나타내는 방식이에요. "
                "다른 주소와 글자 모양이 비슷한지도 확인해 보세요.",
            )
        )

    if parts.scheme.lower() == "http":
        findings.append(
            (
                "HTTP 주소예요.",
                "HTTPS 연결을 요청하는 주소가 아니에요. "
                "반대로 HTTPS라고 해서 사이트의 신뢰성이 보장되지는 않아요.",
            )
        )

    if port is not None and port not in {80, 443}:
        findings.append(
            (
                "일반적인 웹 포트와 다른 번호가 있어요.",
                "정상적인 개발·서비스 목적일 수도 있으므로 "
                "포트 번호만으로 악성이라고 판단하지 않아요.",
            )
        )

    return {
        "host": host,
        "scheme": parts.scheme,
        "assumed": assumed,
        "findings": findings,
    }


st.title("🔗 잠깐! · 의심 URL 확인")
st.write("주소를 붙여넣으면 살펴볼 특징을 설명해 드려요.")
st.caption("입력 주소에 접속하거나 파일을 내려받지 않습니다.")

with st.form("url_check_form"):
    raw_url = st.text_input(
        "확인할 URL",
        placeholder="https://example.com",
        max_chars=2049,
    )
    submitted = st.form_submit_button("주소 특징 확인", type="primary")

if submitted:
    try:
        result = analyze_url(raw_url)

    except ValueError as error:
        st.warning(str(error))

    else:
        st.subheader("주소에서 읽은 실제 호스트명")

        # 클릭 가능한 링크 대신 일반 코드로 표시합니다.
        st.code(result["host"], language=None)

        if result["assumed"]:
            st.caption(
                "프로토콜이 없어 분석할 때만 https://를 붙였어요. "
                "실제 HTTPS 지원 여부를 확인한 것은 아닙니다."
            )

        findings = result["findings"]

        if findings:
            st.warning(f"확인할 특징이 {len(findings)}개 있어요.")

            for title, description in findings:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.write(description)

        else:
            st.info(
                "현재 검사 규칙에 해당하는 특징을 찾지 못했어요. "
                "안전한 사이트라는 뜻은 아닙니다."
            )

        st.write(
            "문자 속 주소와 별개로, 평소 이용하던 앱이나 "
            "직접 확인한 공식 경로에서 관련 내용을 확인해 보세요."
        )

st.divider()

with st.expander("검사할 수 있는 것과 없는 것"):
    st.write("확인하는 것: 주소 형식, 호스트명, 일부 단축 도메인, APK 경로 등")
    st.write(
        "확인하지 않는 것: 실제 사이트 내용, 최종 이동 주소, "
        "악성코드, 발신자의 신원, 사기 여부"
    )
    st.write(
        ".com, .co.kr 같은 끝부분만으로 안전성을 판단하지 않습니다. "
        "HTTPS도 안전 인증 판정은 아닙니다."
    )

with st.expander("연습용 주소"):
    st.caption("아래 주소들은 문자열 분석 연습용입니다. 접속할 필요가 없어요.")
    st.code(
        "https://example.com\n"
        "http://example.com\n"
        "https://example.com/download/check.apk\n"
        "https://familiar.example@other.example",
        language=None,
    )
