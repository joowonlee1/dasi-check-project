import ipaddress
import re
import unicodedata
import idna
import tldextract
from urllib.parse import urlsplit, unquote

import streamlit as st
from mascot_ui import show_key_question, show_mascot
import dotori_data as dd


# 이 목록은 모든 단축 주소 서비스를 포함하지 않습니다.
SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "url.kr",
    "vo.la",
    "me2.do",
    "abr.ge",
    "han.gl",
    "buly.kr",
    "c11.kr",
    "naver.me",
    "is.gd",
    "t.ly",
    "ow.ly",
    "cutt.ly",
    "rebrand.ly",
    "shorturl.at",
}

# 피싱 주소에 자주 끼워 넣는 익숙한 이름과, 그 이름의 대표적인 공식 주소입니다.
# (화면에 보일 이름, 주소 속 영문 이름, 문자 속 한글 이름, 대표 공식 주소)
# 모든 공식 주소를 담은 목록은 아니에요.
BRANDS = [
    ("카카오", ("kakao", "kakaobank", "kakaopay"), ("카카오",), {"kakao.com", "kakaocorp.com", "kakaobank.com", "kakaopay.com"}),
    ("네이버", ("naver",), ("네이버",), {"naver.com", "naver.me"}),
    ("토스", ("toss", "tossbank"), ("토스",), {"toss.im", "tossbank.com"}),
    ("쿠팡", ("coupang",), ("쿠팡",), {"coupang.com"}),
    ("G마켓", ("gmarket",), ("G마켓", "지마켓", "g마켓"), {"gmarket.co.kr"}),
    ("11번가", ("11st",), ("11번가",), {"11st.co.kr"}),
    ("옥션", ("auction",), ("옥션",), {"auction.co.kr"}),
    ("우체국", ("epost", "koreapost"), ("우체국",), {"epost.go.kr", "koreapost.go.kr"}),
    ("경찰청", ("police",), ("경찰",), {"police.go.kr"}),
    ("검찰청", ("spo", "prosecutor"), ("검찰",), {"spo.go.kr"}),
    ("금융감독원", ("fss",), ("금융감독원", "금감원"), {"fss.or.kr"}),
    ("KB국민은행", ("kbstar", "kbbank"), ("국민은행", "KB국민"), {"kbstar.com"}),
    ("신한", ("shinhan",), ("신한",), {"shinhan.com", "shinhancard.com"}),
    ("우리은행", ("woori", "wooribank"), ("우리은행", "우리카드"), {"wooribank.com", "wooricard.com"}),
    ("하나은행", ("hanabank", "kebhana"), ("하나은행",), {"kebhana.com", "hanabank.com"}),
    ("농협", ("nonghyup", "nhbank"), ("농협",), {"nonghyup.com", "nhbank.com"}),
    ("IBK기업은행", ("ibk",), ("기업은행",), {"ibk.co.kr"}),
    ("CJ대한통운", ("cjlogistics",), ("대한통운",), {"cjlogistics.com"}),
    ("삼성", ("samsung",), ("삼성",), {"samsung.com", "samsungcard.com"}),
    ("애플", ("apple", "icloud"), ("애플",), {"apple.com", "icloud.com"}),
    ("구글", ("google", "gmail"), ("구글",), {"google.com", "google.co.kr", "gmail.com"}),
]

OFFICIAL_DOMAINS = set().union(*(official for _, _, _, official in BRANDS))

# 피싱 주소가 믿음을 주려고 자주 넣는 단어입니다. 공식 사이트에도 쓰일 수 있어요.
LURE_WORDS = (
    "login", "signin", "verify", "secure", "security", "account",
    "update", "auth", "confirm", "wallet", "otp", "cert",
)

# 설치된 라이브러리의 PSL 스냅샷만 사용합니다. 외부 조회/디스크 캐시 없음.
EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None,
                              include_psl_private_domains=True)


def registered_domain(host):
    item = EXTRACT(host)
    return f"{item.domain}.{item.suffix}" if item.domain and item.suffix else None


def analyze_url(raw):
    """주소 문자열만 분석합니다. 네트워크 요청은 하지 않습니다."""
    if any(unicodedata.category(c) in {"Cc", "Cf"} for c in raw):
        raise ValueError("제어 문자나 보이지 않는 문자가 포함돼 있어요. 주소를 다시 확인하세요.")
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
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw) and not re.match(r"^[^/?#]+\.[^/?#:]+:[0-9]+(?:[/?#]|$)", raw):
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

        hostname = hostname.removesuffix(".")
        if "%" in hostname or parts.netloc.endswith(":"):
            raise ValueError("모호한 호스트 또는 빈 포트")
        try:
            host = str(ipaddress.ip_address(hostname))
        except ValueError:
            host = idna.encode(hostname, uts46=True, std3_rules=True).decode("ascii").lower()
        if port == 0:
            raise ValueError("포트 0은 지원하지 않음")

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

    if not is_ip and re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*", host):
        raise ValueError("축약·16진수 등 특수 숫자 주소는 브라우저마다 해석이 달라 여기서는 분석하지 않아요.")

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

    owner = None if is_ip else registered_domain(host)

    if owner:
        tokens = set(re.split(r"[.-]", host))
        joined = host.replace("-", "")   # cj-logistics처럼 하이픈을 넣은 이름도 찾아요.

        for name, keywords, _, official in BRANDS:
            if owner not in official and any(
                keyword in tokens or (len(keyword) >= 5 and keyword in joined)
                for keyword in keywords
            ):
                findings.append(
                    (
                        f"{name} 이름이 들어 있지만, 진짜 주인은 {owner}예요.",
                        f"{name}의 대표 공식 주소는 {', '.join(sorted(official))}인데, 이 주소의 주인은 달라요. "
                        "주소 앞부분에는 누구나 익숙한 이름을 붙일 수 있어서, 공식 주소처럼 보이게 만든 것일 수 있어요. "
                        "(이 앱의 공식 주소 목록에 없는 진짜 주소일 수도 있어요.)",
                    )
                )
                break

        words = sorted(
            word for word in LURE_WORDS
            if word in host or word in path
        )

        if words:
            findings.append(
                (
                    f"로그인·인증을 떠올리게 하는 단어가 있어요 ({', '.join(words)}).",
                    "공식 사이트에도 쓰이는 단어지만, 피싱 주소가 믿음을 주려고 "
                    "자주 넣는 단어예요. 위의 진짜 주인 주소와 함께 확인하세요.",
                )
            )

        extra = host[: -len(owner)].rstrip(".")

        if extra.count(".") >= 2:
            findings.append(
                (
                    "진짜 주인 앞에 붙은 이름이 여러 겹이에요.",
                    "정상 사이트도 앞에 이름을 여러 개 붙이기도 해요. "
                    "오른쪽 끝의 진짜 주인 주소를 먼저 보세요.",
                )
            )

    ext = None if is_ip else EXTRACT(host)
    if not is_ip and not owner:
        findings.append(("진짜 주인 주소를 찾지 못했어요.",
                         "목록에 없는 끝부분 또는 접미사만 있는 주소예요. 존재 여부나 안전성은 판단할 수 없어요."))
    if ext and ext.is_private:
        findings.append(("누구나 사이트를 만들 수 있는 호스팅 주소예요.", "호스팅 회사 주소 안에 개인이 만든 사이트예요. 호스팅 회사가 운영하는 사이트라는 뜻이 아니에요."))
    return {
        "suffix": ext.suffix if ext else "",
        "subdomain": ext.subdomain if ext else "",
        "unicode_host": host if is_ip else idna.decode(host),
        "port": port,
        "path": parts.path,
        "query": parts.query,
        "fragment": parts.fragment,
        "userinfo": parts.username is not None,
        "host": host,
        "owner": owner,
        "scheme": parts.scheme,
        "assumed": assumed,
        "findings": findings,
    }


# ─────────────────────────────────────
# 문자 전체 확인
# ─────────────────────────────────────

# 문자 속 주소를 찾습니다. https://로 시작하지 않는 주소(abc.kr/xyz)도 찾아요.
URL_PATTERN = re.compile(
    r"https?://[^\s<>\"'()]+|(?<![\w@.:-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?::[0-9]+)?(?:[/?#][^\s<>\"'()]*)?",
    re.IGNORECASE,
)

# 문자 내용에서 살펴볼 신호입니다. 하나만으로 피싱이라고 판단하지 않아요.
MESSAGE_SIGNS = [
    (
        "서두르게 하는 말이 있어요",
        ("오늘까지", "지금 바로", "즉시", "긴급", "24시간", "당일", "기한", "마감", "소멸", "만료"),
        "기한을 짧게 주면 확인할 시간 없이 누르게 돼요. 정상 광고에도 쓰이는 말이라, "
        "서두르지 말고 직접 확인할 시간을 가지세요.",
    ),
    (
        "불이익을 말하는 표현이 있어요",
        ("정지", "차단", "미납", "연체", "체포", "벌금", "압류", "고소", "반송", "보류"),
        "겁을 주면 판단이 흐려져요. 실제 기관이나 회사도 이런 안내를 하지만, "
        "문자 속 링크 대신 공식 앱이나 대표번호로 확인하세요.",
    ),
    (
        "민감한 정보나 행동을 요구하는 말이 있어요",
        ("인증번호", "비밀번호", "계좌", "송금", "입금", "설치", "카드번호", "신분증", "원격"),
        "이 단어가 있다는 이유만으로 사기라고 단정할 수는 없어요. "
        "요구에 응하기 전에 평소 사용하던 앱이나 별도로 확인한 공식 연락처에서 확인하세요.",
    ),
    (
        "가족·지인을 떠올리게 하는 말이 있어요",
        ("엄마", "아빠", "폰 고장", "액정", "임시폰", "번호 바뀌", "청첩장", "부고"),
        "가족이나 지인인 척하는 문자일 수 있어요. 원래 저장된 번호로 전화해 직접 확인하세요.",
    ),
    (
        "해외에서 보낸 문자로 표시돼 있어요",
        ("국제발신", "국외발신", "해외발신"),
        "국내 회사나 기관을 말하는데 해외에서 보낸 문자라면 더 조심해서 확인하세요.",
    ),
]


def find_urls(text):
    urls = []

    for match in URL_PATTERN.findall(text):
        url = match.rstrip(".,!)}〉」』'\"")
        if url.endswith("]") and "[" not in url:
            url = url[:-1]

        if url and url not in urls:
            urls.append(url)

    return urls[:5]


def analyze_message(text):
    """문자 전체에서 주소와 내용의 신호를 찾습니다. 네트워크 요청은 하지 않습니다."""
    text = text.strip()

    if not text:
        raise ValueError("문자 내용을 먼저 붙여넣어 주세요.")

    if len(text) > 3000:
        raise ValueError("문자가 너무 길어요. 3,000자 이하로 붙여넣어 주세요.")

    links = []

    for url in find_urls(text):
        try:
            links.append((url, analyze_url(url), None))
        except ValueError as error:
            links.append((url, None, str(error)))

    signs = []
    lowered = text.lower()

    for title, words, description in MESSAGE_SIGNS:
        found = [word for word in words if word.lower() in lowered]

        if found:
            signs.append((f"{title} ({', '.join(found[:4])})", description))

    # 문자에서 말하는 회사와 링크의 진짜 주인이 같은지 봅니다.
    for name, _, korean_names, official in BRANDS:
        if not any(word.lower() in lowered for word in korean_names):
            continue

        for url, result, _ in links:
            if result and result["owner"] and result["owner"] not in official:
                signs.append(
                    (
                        f"문자에서는 ‘{name}’이라고 하는데, 링크의 진짜 주인은 {result['owner']}예요.",
                        "단축 주소이거나 다른 회사 주소라서, 링크만 보고는 정말 "
                        f"{name}에서 보낸 것인지 알 수 없어요. 링크를 누르지 말고 "
                        f"{name} 앱이나 직접 검색한 공식 사이트({', '.join(sorted(official))})에서 "
                        "같은 내용이 있는지 확인하세요.",
                    )
                )
                break

    if "(광고)" in text and "수신거부" in text:
        signs.append(
            (
                "(광고)와 수신거부 문구가 있어요.",
                "광고 형식의 문구가 포함돼 있어요. 법적 요건 충족 여부는 검사하지 않아요. 다만 사기 문자도 이 형식을 흉내 낼 수 있어서, "
                "표기만으로 진짜라고 판단할 수는 없어요.",
            )
        )

    return {"links": links, "signs": signs}


def show_structure(result):
    # 전문 용어 대신 쉬운 말로 쓰고, 처음에는 접어 둬요. (궁금한 사람만 펼쳐 보기)
    with st.expander("🔎 주소를 부분별로 자세히 보기"):
        rows = [
            {"부분": "통신 방식", "값": result["scheme"], "뜻": "https여도 진짜 기관이라는 보증은 아니에요"},
            {"부분": "서버 이름(호스트)", "값": result["host"], "뜻": "실제로 접속하는 서버의 전체 이름"},
        ]
        if result["unicode_host"] != result["host"]:
            rows.append({"부분": "한글 등으로 풀어 쓴 이름", "값": result["unicode_host"], "뜻": "xn--로 시작하는 주소를 글자로 바꾼 모습"})
        rows += [
            {"부분": "진짜 주인", "값": result["owner"] or "찾지 못함", "뜻": "주소 끝에서 찾은 이름. 이것이 아는 회사 주소와 같은지 보세요"},
            {"부분": "앞에 붙은 이름", "값": result["subdomain"] or "없음", "뜻": "주인이 마음대로 붙일 수 있는 이름"},
            {"부분": "끝부분", "값": result["suffix"] or "없음", "뜻": ".com, .co.kr 같은 공통 끝부분"},
            {"부분": "포트", "값": str(result["port"] if result["port"] is not None else (443 if result["scheme"] == "https" else 80)), "뜻": "적지 않으면 기본 번호를 써요"},
            {"부분": "경로", "값": result["path"] or "/", "뜻": "사이트 안의 어느 페이지인지"},
            {"부분": "쿼리(? 뒤)", "값": result["query"] or "없음", "뜻": "서버로 보내는 값. 개인정보를 넣지 마세요"},
            {"부분": "프래그먼트(# 뒤)", "값": result["fragment"] or "없음", "뜻": "페이지 안의 위치. 서버로 보내지 않아요"},
            {"부분": "사용자 정보(@ 앞)", "값": "있음 (내용 숨김)" if result["userinfo"] else "없음", "뜻": "@ 앞부분은 주소가 아니에요"},
        ]
        for row in rows:  # 주소가 눌리는 링크로 바뀌지 않게 글자(코드)로 보여 줘요
            row["값"] = f"`{row['값']}`"
        st.table(rows)


st.title("🔗 잠깐! · 의심 URL 확인")
show_mascot("link", "누르기 전에 주소부터 살펴봐요. 검사 결과가 안전을 보장하지는 않아요.")
show_key_question("누르기 전에 **주소부터** 확인해요. 붙여넣으면 살펴볼 특징을 설명해 드려요.", "🔗")
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
        dd.stamp("04")

        # ① 가장 중요한 것 하나: 이 주소의 진짜 주인
        st.subheader("🏠 이 주소의 진짜 주인")
        st.code(result["owner"] or result["host"], language=None)  # 누를 수 없게 글자로만 보여 줘요
        st.caption("주소 맨 끝에서 찾은 이름이에요. 그 앞에 붙은 이름은 누구나 마음대로 붙일 수 있어요. "
                   "이 이름이 내가 아는 회사의 공식 주소와 같은지 먼저 보세요. "
                   "주소 모양으로 나눈 결과라서, 실제 등록 여부·소유자·기관의 신원을 확인한 결과는 아니에요.")

        # ② 확인할 점
        findings = result["findings"]
        if findings:
            st.markdown(f"#### ⚠️ 확인할 점 {len(findings)}개")
            for title, description in findings:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.write(description)
        else:
            st.info("검사 규칙에 걸리는 특징은 없었어요. 그래도 안전하다는 뜻은 아니에요.")

        # ③ 그래서 어떻게 하면 되는지
        st.success("**이렇게 하세요** · 문자 속 링크는 누르지 말고, 평소 쓰던 앱이나 직접 검색한 공식 사이트에서 확인하세요.")

        # ④ 궁금한 사람만 펼쳐 보는 자세한 내용
        show_structure(result)
        if result["assumed"]:
            st.caption("프로토콜이 없어 분석할 때만 https://를 붙였어요. 실제 HTTPS 지원 여부를 확인한 것은 아닙니다.")
        st.write("문자 속 주소와 별개로, 평소 이용하던 앱이나 직접 확인한 공식 경로에서 관련 내용을 확인해 보세요.")

st.divider()

st.subheader("📩 문자 전체를 붙여넣어 확인하기")
st.write(
    "받은 문자를 통째로 붙여넣으면, 인식할 수 있는 링크를 최대 5개 살펴보고 "
    "문자 내용에서 확인할 신호도 함께 알려 드려요."
)
st.caption(
    "입력 내용은 앱 서버에서 처리합니다. 이 검사 기능은 별도 저장·외부 조회를 하지 않고 링크에도 접속하지 않습니다. "
    "내 이름·계좌번호 같은 개인정보는 지우고 붙여넣어 주세요."
)

with st.form("message_check_form"):
    raw_message = st.text_area(
        "받은 문자 내용",
        placeholder="예) [○○택배] 주소 불일치로 배송이 보류되었습니다. 주소 확인: https://...",
        height=180,
        max_chars=3000,
    )
    message_submitted = st.form_submit_button("문자 확인", type="primary")

if message_submitted:
    try:
        report = analyze_message(raw_message)

    except ValueError as error:
        st.warning(str(error))

    else:
        dd.stamp("04")
        links = report["links"]
        signs = report["signs"]

        st.markdown(f"#### 🔗 문자 속 링크 {len(links)}개")

        if not links:
            st.info(
                "문자에서 링크를 찾지 못했어요. 링크가 없어도 전화를 걸게 하거나 "
                "답장을 유도하는 사기 문자가 있으니 내용도 함께 살펴보세요."
            )

        for url, result, error in links:
            with st.container(border=True):
                st.code(url, language=None)

                if error:
                    st.caption(f"이 주소는 분석하지 못했어요. ({error})")
                    continue

                if result["owner"]:
                    st.markdown(f"**🏠 진짜 주인: `{result['owner']}`**")

                if result["findings"]:
                    for title, description in result["findings"]:
                        st.markdown(f"- **{title}** {description}")
                else:
                    st.caption(
                        "현재 검사 규칙에 해당하는 특징을 찾지 못했어요. "
                        "안전한 사이트라는 뜻은 아닙니다."
                    )

        st.markdown(f"#### 📝 문자 내용에서 살펴볼 신호 {len(signs)}개")

        if signs:
            for title, description in signs:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.write(description)
        else:
            st.info(
                "현재 규칙에 해당하는 신호를 찾지 못했어요. "
                "진짜 문자라는 뜻은 아닙니다."
            )

        st.success(
            "**가장 확실한 방법** · 문자 속 링크는 누르지 말고, 평소 쓰던 앱을 직접 열거나 "
            "직접 검색한 공식 사이트·대표번호에서 같은 내용이 있는지 확인하세요."
        )

st.divider()

with st.expander("검사할 수 있는 것과 없는 것"):
    st.write(
        "확인하는 것: 주소 형식, 호스트명, 도메인 경계, 익숙한 이름 끼워 넣기, "
        "로그인·인증 단어, 일부 단축 도메인, APK 경로 등"
    )
    st.write(
        "문자 전체 확인에서 더 보는 것: 문자 속 링크 찾기, 문자에서 말하는 회사와 "
        "링크 도메인과 참고 목록의 일치 여부, 서두르게 하는 말, 불이익 표현, 민감한 요구, 가족 사칭 표현, 국제발신 표시"
    )
    st.write(
        "익숙한 이름 비교는 일부 기관·회사의 대표 공식 주소만 담고 있어요. "
        "목록에 없는 공식 주소가 있을 수 있어요."
    )
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
        "https://familiar.example@other.example\n"
        "https://kakaobank.login-check.example/verify\n"
        "https://www.epost.go.kr.delivery.example/track",
        language=None,
    )


with st.expander("📚 URL 원리 공부 · 먼저 알아둘 세 가지"):
    st.code("https://news.example.com:443/notice?id=7#details", language=None)
    st.write("① 호스트는 news.example.com이고, 경로는 /notice예요. 경로·쿼리에 기관 이름이 있어도 그 기관의 사이트라는 뜻은 아니에요.")
    st.write("② 진짜 주인은 주소 맨 끝에서 찾아요. 그 앞에 붙은 이름은 누구나 마음대로 붙일 수 있어요.")
    st.write("③ HTTPS는 암호화된 연결을 요청하는 방식이에요. 사이트가 사기인지, 발신자가 누구인지를 보증하지 않아요.")
    st.caption("이 도구는 제한된 HTTP(S) 주소 분석기예요. 브라우저의 모든 주소 해석을 그대로 따라 하지는 않아요.")
    st.markdown("참고: [Python URL 분석 문서](https://docs.python.org/3/library/urllib.parse.html#url-parsing-security)")
