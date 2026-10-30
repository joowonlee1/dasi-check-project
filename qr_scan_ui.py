"""🔲 연습용 QR 퀴즈: QR 속 글자만 읽어 '어디로 데려가는지'를 보여 줘요(주소에 접속하지 않아요).

- QR 만들기는 zxing-cpp 라이브러리를 써요.
"""
import io
import ipaddress
from html import escape
from urllib.parse import urlsplit

import streamlit as st
import dotori_data as dd

# 교육용 예약 도메인으로 만든 가상 주소입니다. 실제 주소로 접속하지 않습니다.
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
    """주소 공개 → 독립적인 기준과 비교 → 행동 선택. QR 외형을 채점하지 않습니다."""
    with st.container(border=True, key="qr_scan_box"):
        st.markdown('''<style>
        .st-key-qr_scan_box{background:#F3F8F5;padding:20px!important;}
        .st-key-qr_scan_box button{height:auto!important;min-height:48px!important;white-space:normal!important;padding:12px 18px!important;}
        .st-key-qr_scan_box button p{line-height:1.6!important;overflow-wrap:anywhere;}
        .st-key-qr_scan_box [data-testid=stMarkdownContainer] p{line-height:1.7;}
        .st-key-qr_scan_box [data-testid=stImage] img{border:1px solid #CBD5E1;border-radius:12px;}
        .st-key-qr_scan_box [data-testid=stCode]{margin:10px 0;}
        .st-key-qr_scan_box [data-testid=stAlert]{margin:12px 0;}
        </style>''', unsafe_allow_html=True)
        st.subheader("🔲 QR 속 주소, 확인하고 행동하기")
        st.write("QR 모양이나 안내문 제목만으로 안전 여부를 알 수 없어요. 주소를 읽고, 별도로 확인한 공식 정보와 비교해 보세요.")
        st.caption("교육용 가상 상황입니다. 아래 주소로 접속하거나 결제하지 않아요.")
        selected = st.radio("연습할 안내문", ["안내문 A · 주차요금 납부 요청", "안내문 B · 행사 안내"], key="qr_case_v2")
        i = 0 if selected.startswith("안내문 A") else 1
        text = list(PRACTICE.values())[i]
        read_key = f"qr_read_v2_{i}"
        result_key = f"qr_result_v2_{i}"
        st.markdown("**① QR 속 주소 읽기**")
        try:
            st.image(_qr_png(text), width=140)
        except Exception:
            st.caption("QR 그림을 만들지 못했어요. 아래 버튼으로 동일한 연습 주소를 확인할 수 있어요.")
        if st.button("🔎 주소만 읽기 · 사이트에 접속하지 않아요", key=f"qr_read_btn_v2_{i}", width="stretch"):
            st.session_state[read_key] = True
        if not st.session_state.get(read_key):
            return
        st.code(text, language=None, wrap_lines=True)
        st.markdown("**② 별도로 확인한 공식 정보와 비교하기**")
        st.info("가상 상황에서 내가 직접 찾아 확인한 도토리시 공식 누리집의 호스트 이름은 www.example.com이에요. 안내문에 적힌 연락처를 통해 확인한 정보가 아니에요.")
        st.caption("호스트는 주소에서 실제 연결할 서버 이름이에요. ‘@’가 있으면 그 뒤의 호스트를 확인하세요. 이름이 비슷하다는 이유만으로 같다고 판단하지 마세요.")
        with st.form(f"qr_compare_form_v2_{i}"):
            evidence = st.radio("주소를 비교한 결과는?", [
                "실제 호스트가 공식 안내의 호스트와 다르다",
                "호스트는 같지만, 이 요청이 실제 공지인지까지는 확인하지 못했다",
                "제목이나 로고가 공식처럼 보이므로 안전하다",
            ], index=None, key=f"qr_evidence_v2_{i}")
            st.markdown("**③ 다음 행동 선택하기**")
            action = st.radio("이제 어떻게 할까요?", [
                "QR 이용을 멈추고, 별도로 찾은 공식 경로에서 납부 요청을 확인한다",
                "QR로 바로 진행하지 않고, 공식 누리집에 직접 들어가 같은 행사 공지를 찾는다",
                "주소가 그럴듯하니 QR에서 바로 결제하거나 개인정보를 입력한다",
            ], index=None, key=f"qr_action_v2_{i}")
            submitted = st.form_submit_button("비교 근거와 행동 확인", width="stretch")
        if submitted:
            if evidence is None or action is None:
                st.warning("주소 비교 결과와 다음 행동을 모두 선택해 주세요.")
                st.session_state.pop(result_key, None)
            else:
                evidence_ok = evidence.startswith("실제 호스트") if i == 0 else evidence.startswith("호스트는 같지만")
                action_ok = action.startswith("QR 이용을 멈추고") if i == 0 else action.startswith("QR로 바로 진행하지")
                st.session_state[result_key] = (evidence_ok, action_ok)
                if evidence_ok and action_ok:
                    dd.achieve("qr_scan")
        result = st.session_state.get(result_key)
        if result is not None:
            if all(result):
                st.success("주소의 근거와 다음 확인 행동을 연결했어요.")
            else:
                st.warning("마지막으로 제출한 답변을 다시 살펴보세요. " + ("호스트 비교를 확인해 주세요. " if not result[0] else "") + ("요청 내용을 공식 경로에서 확인하는 행동을 골라 주세요." if not result[1] else ""))
            if i == 0:
                st.write("**실제 호스트는 login-secure.example.net**이에요. @ 앞의 주차 관련 글자는 공식 목적지를 증명하지 않아요. 기준 호스트와 다르므로 이용을 멈추고 공식 경로에서 납부 사실을 확인해요.")
            else:
                st.write("**호스트 www.example.com은 기준과 같아요.** 하지만 주소만으로 행사 내용·개인정보 요청까지 안전하다고 보장할 수 없어요. 직접 찾은 공식 누리집에서 해당 공지를 다시 확인해요.")
            st.caption("이 활동은 주소를 비교하는 연습이에요. 실제 사이트의 운영 상태나 악성 여부를 검사한 결과가 아니에요.")
        with st.expander("주소 구성도 더 살펴보기"):
            st.write("‘의심 URL 확인’에서는 주소의 구성과 주의할 특징을 더 살펴볼 수 있어요.")
            _to_url_page(text)
            st.page_link("pages/4_URL_확인.py", label="의심 URL 확인으로 이동", icon="🔗", width="stretch")


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
