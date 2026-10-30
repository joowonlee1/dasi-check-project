"""🔲 연습용 QR 퀴즈: QR 속 글자만 읽어 '어디로 데려가는지'를 보여 줘요(주소에 접속하지 않아요).

- QR 만들기는 zxing-cpp 라이브러리를 써요.
"""
import io
import ipaddress
from html import escape
from urllib.parse import urlsplit

import streamlit as st
import dotori_data as dd

# 연습용 가짜 QR(교육용 가상 주소: example.com은 예시용으로 비워 둔 주소라 실제 사이트가 아니에요)
PRACTICE = {
    "🅿️ 주차요금 스티커 (사기 예시)": "http://dotori-parking-pay.example.com@login-secure.example.net/pay?fine=40000",
    "🏛️ 도토리시 공식 안내 (정상 예시)": "https://www.example.com/dotori/notice",
}
SHORTENERS = {"bit.ly", "me2.do", "han.gl", "t.ly", "tinyurl.com", "url.kr", "vo.la", "buly.kr", "c11.kr", "gg.gg", "is.gd", "goo.gl", "naver.me"}
WORDS = ("login", "secure", "verify", "pay", "bank", "account", "update", "fine", "refund")


def _domain(host):
    try:
        import tldextract
        item = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)(host)
        return f"{item.domain}.{item.suffix}" if item.domain and item.suffix else host
    except Exception:
        return host


def _qr_png(text):
    import zxingcpp
    from PIL import Image
    image = Image.fromarray(__import__("numpy").array(zxingcpp.write_barcode_to_image(
        zxingcpp.create_barcode(text, zxingcpp.BarcodeFormat.QRCode), scale=10)))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def describe(text):
    """QR 속 글자가 무엇을 시키는지와, 주소라면 살펴볼 점을 정리해요."""
    low = text.strip().lower()
    if low.startswith("wifi:"):
        return "📶 와이파이 접속", "휴대폰을 이 와이파이에 연결하게 해요. 모르는 공용 와이파이는 정보가 새어 나갈 수 있어요.", [], None
    if low.startswith("tel:"):
        return "📞 전화 걸기", f"{text[4:]} 번호로 전화를 걸게 해요. 걸기 전에 공식 번호인지 직접 찾아 확인해요.", [], None
    if low.startswith(("smsto:", "sms:")):
        return "💬 문자 보내기", "미리 써 둔 문자를 보내게 해요. 유료 문자이거나 인증번호를 보내게 하는 수법일 수 있어요.", [], None
    if not low.startswith(("http://", "https://")):
        return "📝 글자", "주소가 아니라 글자만 들어 있어요.", [], None
    parts = urlsplit(text.strip())
    host = (parts.hostname or "").lower()
    domain = _domain(host)
    flags = []
    if "@" in parts.netloc:
        flags.append("주소 안에 ‘@’가 있어요. ‘@’ 앞부분은 장식이고, 진짜 목적지는 ‘@’ 뒤예요.")
    if parts.scheme == "http":
        flags.append("‘https’가 아니라 ‘http’예요. 주고받는 내용이 암호화되지 않아요.")
    try:
        ipaddress.ip_address(host)
        flags.append("이름 대신 숫자(IP 주소)로 된 주소예요. 공식 기관은 보통 이렇게 안내하지 않아요.")
    except ValueError:
        pass
    if domain in SHORTENERS:
        flags.append("단축 주소예요. 진짜 목적지가 가려져 있어요.")
    if "xn--" in host:
        flags.append("다른 나라 글자로 비슷하게 꾸민 주소(퓨니코드)일 수 있어요.")
    if host.count(".") >= 3:
        flags.append("점(.)으로 나뉜 부분이 많아요. 진짜 주인 이름은 맨 뒤쪽이에요.")
    hit = [w for w in WORDS if w in text.lower()]
    if hit:
        flags.append("‘" + "’, ‘".join(hit) + "’ 같은 말로 로그인·결제를 서두르게 할 수 있어요.")
    return "🌐 인터넷 주소", f"이 QR은 ‘{domain}’(이)라는 사이트로 데려가요.", flags, {"주소": text, "통신 방식": parts.scheme, "진짜 주인(도메인)": domain, "경로": parts.path or "/"}


def _to_url_page(text):
    st.session_state["url_check_input"] = text


def show_qr_scanner():
    # 연습용 QR 2장: 먼저 "찍어도 될까?"를 내가 판단하고, 그다음 QR 속 주소를 열어 맞았는지 확인해요.
    with st.container(border=True, key="qr_scan_box"):
        st.markdown(
            "<style>.st-key-qr_scan_box{background:linear-gradient(135deg,#EFF6FF,#F0FDF4)}"
            ".st-key-qr_scan_box [data-testid=stImage] img{border-radius:10px;border:2px solid #CBD5E1}"
            "[class*=st-key-qr_card_]{background:#fff;border:2px solid #BFDBFE;border-radius:16px;padding:10px 12px;gap:6px!important}"
            "[class*=st-key-qr_card_] button{min-height:44px!important;height:44px;border:2px solid #BFDBFE!important;background:#fff!important;border-radius:12px!important}"
            "[class*=st-key-qr_card_] button p{font-weight:800!important;font-size:1rem!important;color:#1E3A8A!important}"
            "[class*=st-key-qr_card_] button:hover{border-color:#3B82F6!important;background:#EFF6FF!important}"
            ".st-key-qr_scan_box [data-testid=stPageLink] a{background:#fff;border:2px solid #93C5FD;border-radius:12px;justify-content:center;padding:6px 10px}"
            ".st-key-qr_scan_box [data-testid=stPageLink] a p,.st-key-qr_scan_box [data-testid=stPageLink] a span{color:#1E3A8A!important;font-weight:800!important;opacity:1!important}"
            "</style>"
            '<div style="font-size:1.3rem;font-weight:900;color:#1E3A8A">🔲 이 QR, 찍어도 될까?</div>'
            '<div style="color:#475569;font-size:.92rem;word-break:keep-all;margin:2px 0 4px">QR마다 <b>먼저 내 판단</b>을 고르면, QR 속 주소를 열어(접속은 안 해요) 맞았는지 알려 줘요. '
            '가상 주소라 휴대폰으로 찍어도 열리지 않아요.</div>',
            unsafe_allow_html=True,
        )
        guesses = st.session_state.setdefault("qr_guess", {})
        cards = st.columns(len(PRACTICE), gap="small")
        for i, (col, (label, text)) in enumerate(zip(cards, PRACTICE.items())):
            with col, st.container(key=f"qr_card_{i}"):
                try:
                    png = _qr_png(text)
                except Exception:
                    st.caption("연습용 QR을 만들지 못했어요.")
                    continue
                # 이름표에서 정답(사기/정상) 표시는 빼고 장소만 보여 줘요. 정답은 판단한 뒤에 공개해요.
                place = label.split(" (")[0]
                pic, info = st.columns([1, 1.7], vertical_alignment="center", gap="small")
                with pic:
                    st.image(png, width=104)
                with info:
                    st.markdown(f'<div style="font-weight:900;color:#1E3A8A;font-size:1.05rem;word-break:keep-all">{escape(place)}</div>',
                                unsafe_allow_html=True)
                    if i in guesses:
                        right = guesses[i] == (_answer(label) == "scam")
                        st.markdown(f'<div style="font-weight:900;color:{"#166534" if right else "#B91C1C"}">'
                                    f'{"⭕ 정답!" if right else "❌ 아쉬워요"} · {"🚫 사기 QR" if "사기" in label else "✅ 정상 QR"}</div>',
                                    unsafe_allow_html=True)
                    b1, b2 = st.columns(2, gap="small")
                    if b1.button("✅ 괜찮아", key=f"qr_ok_{i}", width="stretch"):
                        guesses[i] = False
                        st.session_state["qr_demo_text"] = text
                        st.session_state["qr_demo_i"] = i
                        st.rerun()
                    if b2.button("🚫 수상해", key=f"qr_bad_{i}", width="stretch"):
                        guesses[i] = True
                        st.session_state["qr_demo_text"] = text
                        st.session_state["qr_demo_i"] = i
                        st.rerun()
        if st.session_state.get("qr_demo_text"):
            _show_results([st.session_state["qr_demo_text"]])


def _answer(label):
    return "scam" if "사기" in label else "ok"


def _show_results(texts):
    dd.achieve("qr_scan")
    for text in texts[:2]:
        kind, summary, flags, table = describe(text)
        danger = bool(flags)
        color, bg = ("#B91C1C", "#FEF2F2") if danger else ("#166534", "#F0FDF4")
        items = "".join(f"<li>{escape(f)}</li>" for f in flags)
        st.markdown(
            f'<div style="border:3px solid {color};background:{bg};border-radius:18px;padding:14px 16px;margin:8px 0;animation:jkq .5s ease-out">'
            '<style>@keyframes jkq{from{transform:scale(.96);opacity:0}to{transform:none;opacity:1}}</style>'
            f'<div style="font-weight:900;color:{color};font-size:1.15rem">🔎 QR을 읽었어요 · {escape(kind)}</div>'
            f'<div style="font-size:1.08rem;font-weight:700;margin:6px 0;word-break:keep-all">{escape(summary)}</div>'
            f'<div style="font-family:ui-monospace,Consolas,monospace;background:#fff;border-radius:10px;padding:8px 10px;overflow-wrap:anywhere">{escape(text)}</div>'
            + (f'<div style="margin-top:8px;font-weight:900;color:{color}">⚠️ 살펴볼 점 {len(flags)}가지</div><ul style="margin:4px 0 0;line-height:1.7;columns:2 260px;column-gap:28px">{items}</ul>' if flags
               else '<div style="margin-top:8px;font-weight:800;color:#166534">눈에 띄는 위험 신호는 없어요. 그래도 안전하다는 뜻은 아니니, 공식 앱·누리집에서 직접 찾아 확인해요.</div>')
            + "<div style='margin-top:8px;color:#475569;font-size:.9rem'>🔒 이 주소에 접속하지 않았어요. 글자만 살펴본 결과예요.</div></div>",
            unsafe_allow_html=True,
        )
        if table:
            st.page_link("pages/4_URL_확인.py", label="‘의심 URL 확인’에서 이 주소를 부분별로 더 자세히 보기", icon="🔗", width="stretch")
            _to_url_page(text)
