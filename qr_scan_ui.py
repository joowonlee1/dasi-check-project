"""📷 웹캠으로 QR 비춰 보기: 사진 속 QR을 읽어 '어디로 데려가는지'만 보여 줘요.

- 주소에 접속하지 않아요. 글자만 읽고 생김새를 살펴봐요.
- 사진은 QR을 읽는 데만 쓰고 저장하지 않아요(서버 메모리에서 바로 버려요).
- QR 읽기는 zxing-cpp 라이브러리를 써요.
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


def read_qr(file):
    """사진에서 QR 글자를 읽어요. 못 찾으면 빈 목록."""
    import zxingcpp
    from PIL import Image, ImageOps
    image = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
    found = zxingcpp.read_barcodes(image)
    if not found:  # 좌우가 뒤집힌 웹캠 사진도 한 번 더 읽어 봐요.
        found = zxingcpp.read_barcodes(ImageOps.mirror(image))
    return [r.text for r in found if r.text]


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
    # 한 상자 안에: 왼쪽은 웹캠·결과, 오른쪽은 연습용 QR(작게 나란히). 빈 곳 없이 한눈에 보이게 배치해요.
    with st.container(border=True, key="qr_scan_box"):
        st.markdown(
            "<style>.st-key-qr_scan_box{background:linear-gradient(135deg,#EFF6FF,#F0FDF4)}"
            ".st-key-qr_scan_box [data-testid=stImage] img{border-radius:10px;border:2px solid #CBD5E1}</style>"
            '<div style="display:flex;align-items:center;gap:10px"><span style="font-size:2rem">📷</span><div>'
            '<div style="font-size:1.3rem;font-weight:900;color:#1E3A8A">진짜 QR 비춰 보기</div>'
            '<div style="color:#475569;font-size:.95rem;word-break:keep-all">휴대폰 화면이나 종이 속 QR을 웹캠에 비춰 찍으면, 주소에 들어가지 않고 '
            '<b>어디로 데려가는지만</b> 알려 줘요. 사진은 QR을 읽는 데만 쓰고 저장하지 않아요.</div></div></div>',
            unsafe_allow_html=True,
        )
        texts = _scan_area()
        st.markdown("**🖨️ 연습용 가짜 QR** · 휴대폰에 띄우거나 출력해서 비춰 보세요")
        cols = st.columns(len(PRACTICE))
        for i, (col, (label, text)) in enumerate(zip(cols, PRACTICE.items())):
            with col:
                try:
                    png = _qr_png(text)
                    st.image(png, caption=label, width=130)
                    if st.button("🔎 바로 검사", key=f"qr_try_{i}", type="primary", width="stretch",
                                 help="웹캠이 없어도 이 QR 속 주소를 바로 읽어 살펴봐요."):
                        st.session_state["qr_demo_text"] = text
                    with st.expander("QR 저장·인쇄하기"):
                        st.download_button("⬇️ QR 이미지 저장", png, file_name=("practice_qr_scam.png" if "사기" in label else "practice_qr_ok.png"),
                                           mime="image/png", key=f"qr_dl_{i}", width="stretch")
                except Exception:
                    st.caption("연습용 QR을 만들지 못했어요.")
        st.markdown('<div style="margin-top:6px;background:#FEF3C7;border-radius:10px;padding:6px 10px;font-size:.85rem;font-weight:700;color:#92400E;word-break:keep-all">'
                    '📵 연습용 QR은 <b>가상 주소</b>라 휴대폰 카메라로 찍어도 사이트가 열리지 않아요(일부러 그렇게 만들었어요). '
                    '‘🔎 바로 검사’를 누르거나 위의 웹캠에 비춰 보세요.</div>', unsafe_allow_html=True)
        if not texts and st.session_state.get("qr_demo_text"):
            texts = [st.session_state["qr_demo_text"]]
        # 결과는 두 칸 아래에 넓게 보여 줘요(오른쪽에 빈 곳이 생기지 않게).
        if texts:
            _show_results(texts)


def _scan_area():
    if not st.toggle("📷 웹캠 켜기", key="qr_cam_on", help="켜면 브라우저가 카메라 사용 허락을 물어봐요."):
        steps = (("1", "📷", "웹캠 켜기", "브라우저가 카메라 허락을 물어봐요"),
                 ("2", "🔲", "QR 비추고 찍기", "QR이 화면 가운데에 크게"),
                 ("3", "🔎", "목적지 확인", "주소에 들어가지 않고 글자만 살펴봐요"))
        st.markdown(
            '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:4px">'
            + "".join(f'<div style="background:#fff;border:2px solid #BFDBFE;border-radius:14px;padding:10px 8px;text-align:center">'
                      f'<div style="font-size:1.8rem">{icon}</div><div style="font-weight:900;color:#1E3A8A">{n}. {t}</div>'
                      f'<div style="font-size:.95rem;font-weight:600;color:#475569;word-break:keep-all;line-height:1.4">{d}</div></div>'
                      for n, icon, t, d in steps)
            + "</div>",
            unsafe_allow_html=True,
        )
        return None
    shot = st.camera_input("QR이 화면 가운데에 크게 오게 비추고 ‘사진 찍기’를 눌러요", key="qr_cam")
    if shot is None:
        return None
    try:
        texts = read_qr(shot)
    except Exception:
        st.error("사진을 읽지 못했어요. 다시 찍어 주세요.")
        return None
    if not texts:
        st.warning("QR을 찾지 못했어요. 더 가까이, 밝은 곳에서, 흔들리지 않게 찍어 주세요.")
        return None
    return texts


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
            st.page_link("pages/4_URL_확인.py", label="🔗 ‘의심 URL 확인’에서 이 주소 더 자세히 보기", icon="➡️")
            _to_url_page(text)
