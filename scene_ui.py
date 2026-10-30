"""장소 그림 위에 게임 진행 상황을 올려 보여 주는 '장면 보드'.

게임 시작 화면 맨 위에 자리(st.empty)를 먼저 잡아 두고, 게임 결과(이벤트)를 처리한 뒤 그 자리에 그려요.
그래서 게임을 하는 동안 그림이 바로바로 바뀌어요. 그림은 static 폴더의 scene_*.jpg예요.
"""
import html
from pathlib import Path

import streamlit as st

_CSS = (
    "<style>.sb{position:relative;border-radius:20px;overflow:hidden;border:3px solid #E2C98A;container-type:inline-size;"
    "box-shadow:0 6px 16px rgba(60,40,10,.15);margin:2px 0 10px;background-size:cover;background-position:center}"
    ".sb>*{position:absolute}"
    ".sb .sb-place{left:1.6%;bottom:4%;background:rgba(255,253,240,.95);border:.25cqw solid #C9A86A;border-radius:999px;padding:.3cqw 1.4cqw;"
    "font-weight:900;color:#5B3A12;font-size:1.7cqw;white-space:nowrap}"
    ".sb .sb-status{right:1.6%;top:4%;background:rgba(32,72,63,.94);color:#fff;border:.25cqw solid #F6D55C;border-radius:1.4cqw;padding:.5cqw 1.4cqw;"
    "font-weight:900;font-size:1.7cqw;max-width:46%;line-height:1.35;word-break:keep-all}"
    ".sb.stat-left .sb-status{right:auto;left:1.6%;max-width:23%}.sb.place-right .sb-place{left:auto;right:1.6%}"
    ".sb .sb-status small{display:block;font-weight:700;color:#FDE68A;font-size:1.35cqw}"
    "@keyframes sb-bob{0%,100%{translate:0 0}50%{translate:0 -.6cqw}}"
    "@keyframes sb-pop{0%{transform:translate(-50%,-50%) scale(2) rotate(-20deg);opacity:0}100%{transform:translate(-50%,-50%) scale(1) rotate(-10deg);opacity:1}}"
    "@media (prefers-reduced-motion:reduce){.sb *{animation:none!important}}</style>"
)


def ready(name):
    return (Path(__file__).resolve().parent / "static" / f"{name}.jpg").exists()


def board(name, place, inner, ratio, status="", pos="center", cls=""):
    """그림 + 장소 이름표 + 오른쪽 위 진행 상황 + 그 위에 얹을 표시(inner)."""
    return (
        _CSS + f'<div class="sb {cls}" style="background-image:url(app/static/{name}.jpg);aspect-ratio:{ratio};background-position:{pos}">'
        + inner
        + f'<span class="sb-place">📍 {html.escape(place)}</span>'
        + (f'<span class="sb-status">{status}</span>' if status else "")
        + "</div>"
    )


# ───── 중고거래 사기단 추리: 천막 5개 = 판매자 5명 ─────
MARKET_X = [12.4, 33.8, 51.6, 69.4, 87.6]


def market(sellers, emoji, real, finished):
    css = ("<style>.mk-tag{transform:translate(-50%,0);top:4%;background:#FFFDF5;border:.25cqw solid #8A5A2B;border-radius:1cqw;padding:.3cqw .9cqw;"
           "font-weight:900;font-size:1.55cqw;color:#5B3A12;white-space:nowrap;box-shadow:0 .3cqw 0 rgba(0,0,0,.15)}"
           ".mk-q{transform:translate(-50%,-50%);top:52%;font-size:3.4cqw;font-weight:900;color:#fff;background:rgba(15,23,42,.55);border-radius:50%;"
           "width:6cqw;aspect-ratio:1;display:flex;align-items:center;justify-content:center;animation:sb-bob 2s ease-in-out infinite}"
           ".mk-tape{transform:translate(-50%,-50%) rotate(-12deg);top:50%;width:17%;background:repeating-linear-gradient(45deg,#FACC15 0 1.2cqw,#111827 1.2cqw 2.4cqw);"
           "color:#fff;font-weight:900;font-size:1.6cqw;text-align:center;padding:.5cqw 0;text-shadow:0 0 .4cqw #000;box-shadow:0 .4cqw .8cqw rgba(0,0,0,.35);animation:sb-pop .5s ease-out both}"
           ".mk-tape b{background:#B91C1C;border-radius:.6cqw;padding:.1cqw .8cqw;text-shadow:none}"
           ".mk-real{transform:translate(-50%,-50%);top:50%;background:#16A34A;color:#fff;border:.35cqw solid #fff;border-radius:1.4cqw;padding:.6cqw 1.2cqw;"
           "font-weight:900;font-size:1.8cqw;white-space:nowrap;box-shadow:0 0 0 .6cqw rgba(22,163,74,.35),0 0 3cqw rgba(250,204,21,.8);animation:sb-bob 1.6s ease-in-out infinite}</style>")
    marks = []
    for i, (name, x) in enumerate(zip(sellers, MARKET_X)):
        marks.append(f'<span class="mk-tag" style="left:{x}%">{emoji[i]} {html.escape(name)}</span>')
        if not finished:
            marks.append(f'<span class="mk-q" style="left:{x}%;animation-delay:{i * .2}s">?</span>')
        elif name == real:
            marks.append(f'<span class="mk-real" style="left:{x}%">✅ 진짜 판매자</span>')
        else:
            marks.append(f'<span class="mk-tape" style="left:{x}%;animation-delay:{i * .12}s"><b>🚨 검거</b></span>')
    status = ("🎉 사기단 4명 검거 완료!<small>진짜 판매자만 남았어요</small>" if finished
              else "🕵️ 진짜 판매자는 단 1명<small>거래 기록을 조사해 찾아내요</small>")
    return css + board("scene_market", "개암골 · 도토리 중고마켓", "".join(marks), "759/314", status)


# ───── 큐싱 노노그램: 정산기의 찢긴 QR 스티커 ─────
_QR = ["1111111", "1000001", "1011101", "1011101", "1011101", "1000001", "1111111"]


def kiosk(cleared, final):
    n = len(cleared)
    cells = []
    for r, row in enumerate(_QR):
        for c, v in enumerate(row):
            piece = (c * 3) // 7  # 세로 3조각
            shown = piece in cleared or final
            color = "#111827" if v == "1" else "#FFFFFF"
            cells.append(f'<i style="background:{color if shown else "transparent"}"></i>')
    css = ("<style>.kq{left:31%;top:46.4%;transform:translate(-50%,-50%) rotate(-8deg);width:11%;aspect-ratio:1;background:#FFFDF5;border:.3cqw solid #D6C7A1;"
           "padding:.6cqw;display:grid;grid-template-columns:repeat(7,1fr);gap:0;box-shadow:0 .4cqw .8cqw rgba(0,0,0,.35);clip-path:polygon(0 0,100% 0,100% 82%,84% 100%,0 100%)}"
           ".kq i{display:block;aspect-ratio:1}"
           ".kq.empty{background:repeating-linear-gradient(45deg,#FFFDF5 0 .6cqw,#F1E7CC .6cqw 1.2cqw)}"
           ".kq-warn{left:31%;top:77%;transform:translate(-50%,0);background:#DC2626;color:#fff;border-radius:999px;padding:.3cqw 1.2cqw;font-weight:900;font-size:1.5cqw;white-space:nowrap;animation:sb-bob 1.6s ease-in-out infinite}"
           ".kq-pieces{left:31%;top:12%;transform:translate(-50%,0);background:rgba(255,253,240,.95);border:.25cqw solid #8A5A2B;border-radius:999px;padding:.3cqw 1cqw;font-weight:900;font-size:1.45cqw;color:#5B3A12;white-space:nowrap}</style>")
    inner = (f'<span class="kq{" empty" if not n and not final else ""}">' + "".join(cells) + "</span>"
             + f'<span class="kq-pieces">🧩 복원한 조각 {3 if final else n}/3</span>'
             + ('<span class="kq-warn">⚠️ 출처를 모르는 QR</span>' if (n or final) else ""))
    status = ("🔍 그림은 복원했어요!<small>이제 누가 붙였는지·어디로 가는지 조사해요</small>" if final or n == 3
              else "🧩 찢긴 QR 스티커 발견<small>노노그램을 풀어 조각을 복원해요</small>")
    return css + board("scene_kiosk", "중앙동 · 도토리 공영주차장", inner, "481/250", status, "center 45%")


# ───── 피싱 필터 만들기: 우체국 컨베이어 ─────
def post(last):
    """last: 마지막 실행 결과 {stage, clear, wrong}"""
    lamp = "#9CA3AF"
    status = "📮 필터를 만들고 실행해 보세요<small>진짜 문자는 통과, 가짜 문자는 차단</small>"
    if last:
        wrong = len(last.get("wrong", []))
        lamp = "#22C55E" if last.get("clear") else "#EF4444"
        status = (f"✅ {last['stage'] + 1}단계 통과!<small>모든 문자를 바르게 분류했어요</small>" if last.get("clear")
                  else f"🚨 {last['stage'] + 1}단계 · 잘못 분류 {wrong}통<small>규칙을 고쳐 다시 실행해요</small>")
    css = ("<style>.pl{left:44%;top:19.5%;transform:translate(-50%,-50%);width:6%;aspect-ratio:1;border-radius:50%;border:.4cqw solid #fff;"
           f"background:{lamp};box-shadow:0 0 3cqw {lamp},0 0 0 .4cqw rgba(0,0,0,.2);animation:pl-blink 1s ease-in-out infinite}}"
           "@keyframes pl-blink{50%{opacity:.55}}"
           ".pe{top:76%;font-size:3cqw;animation:pe-move 6s linear infinite;filter:drop-shadow(0 .3cqw .3cqw rgba(0,0,0,.3))}"
           "@keyframes pe-move{0%{left:-6%}100%{left:100%}}</style>")
    envs = "".join(f'<span class="pe" style="animation-delay:{-k * 1.5}s">{e}</span>' for k, e in enumerate(("✉️", "💬", "✉️", "💬")))
    return css + board("scene_post", "시청로 · 도토리 우체국 문자 필터실", '<span class="pl"></span>' + envs, "409/220", status, "center 60%")


# ───── 가짜뉴스 확산 막기: 광장에 퍼지는 소문 ─────
_BUBBLES = [(28, 42), (72, 40), (16, 22), (58, 62), (38, 16), (46, 60), (12, 56), (88, 58), (50, 32)]


def plaza(last_pct, stars_total):
    """last_pct: 마지막 단계에서 지킨 비율(%) 또는 None"""
    left = len(_BUBBLES) if last_pct is None else round(len(_BUBBLES) * (100 - last_pct) / 100)
    css = ("<style>.pb{transform:translate(-50%,-50%);background:#fff;border:.3cqw solid #DC2626;border-radius:2cqw;padding:.4cqw 1cqw;font-weight:900;font-size:1.45cqw;color:#B91C1C;white-space:nowrap;"
           "box-shadow:0 .3cqw .6cqw rgba(0,0,0,.2);animation:pb-spread 3.2s ease-out infinite}"
           ".pb::after{content:'';position:absolute;left:20%;bottom:-1.1cqw;border:.6cqw solid transparent;border-top-color:#DC2626}"
           ".pb.gone{animation:none;opacity:0}"
           "@keyframes pb-spread{0%{left:50%;top:60%;opacity:0;scale:.3}25%{opacity:1}100%{opacity:1;scale:1}}"
           ".ps{transform:translate(-50%,-50%);font-size:4.4cqw;filter:drop-shadow(0 .3cqw .3cqw rgba(0,0,0,.3));animation:sb-bob 2s ease-in-out infinite}</style>")
    marks = []
    for k, (x, y) in enumerate(_BUBBLES):
        gone = k >= left
        if gone:
            marks.append(f'<span class="ps" style="left:{x}%;top:{y}%">🛡️</span>')
        else:
            word = ("💰 지원금 준대!", "🔗 이 링크 눌러", "😱 오늘까지래", "📢 다들 공유해", "💸 선착순!")[k % 5]
            marks.append(f'<span class="pb" style="left:{x}%;top:{y}%;animation-delay:{k * .25}s">{word}</span>')
    status = ("📣 광장에 가짜 소문이 퍼지는 중!<small>아래 게임에서 주민을 지키면 말풍선이 🛡️ 방패로 바뀌어요</small>" if last_pct is None
              else f"🛡️ 지난 단계 {last_pct}% 지킴<small>모은 별 {stars_total}개 · 막은 소문은 방패로 바뀌어요</small>")
    return css + board("scene_plaza", "중앙동 · 도토리 광장", "".join(marks), "611/230", status, "center 55%")


# ───── 할머니 폰 지키기 시작 화면: 소파의 할머니와 울리는 휴대폰 ─────
def grandma_cover(face_html):
    css = ("<style>.gc-face{left:50%;top:50%;transform:translate(-50%,-50%);width:16%}"
           ".gc-face img,.gc-face svg{width:100%!important;height:auto!important;margin:0!important;border-radius:50%!important;border:.4cqw solid #fff!important;box-shadow:0 0 0 .3cqw #F2B6C6,0 .5cqw 1cqw rgba(0,0,0,.25)!important;aspect-ratio:1;object-fit:cover}"
           ".gc-phone{left:61%;top:60%;transform:translate(-50%,-50%);font-size:3.6cqw;animation:gc-buzz .5s ease-in-out infinite}"
           ".gc-ring{left:61%;top:60%;width:6cqw;aspect-ratio:1;border-radius:50%;border:.3cqw solid #DC2626;transform:translate(-50%,-50%);animation:gc-ring 1.4s ease-out infinite}"
           "@keyframes gc-buzz{0%,100%{rotate:0deg}25%{rotate:-14deg}75%{rotate:14deg}}"
           "@keyframes gc-ring{0%{scale:.6;opacity:1}100%{scale:2;opacity:0}}"
           ".gc-say{left:63%;top:22%;background:#fff;border:.3cqw solid #20483F;border-radius:1.6cqw 1.6cqw 1.6cqw .3cqw;padding:.6cqw 1.3cqw;font-weight:900;font-size:1.6cqw;color:#20483F;white-space:nowrap}"
           ".gc-noti{left:2%;top:6%;width:30%;display:flex;flex-direction:column;gap:.6cqw}"
           ".gc-noti span{position:static;display:block;background:rgba(255,255,255,.96);border-left:.6cqw solid #DC2626;border-radius:1cqw;padding:.5cqw 1cqw;font-size:1.3cqw;font-weight:800;color:#1F2937;box-shadow:0 .3cqw .8cqw rgba(0,0,0,.2);opacity:0;animation:gc-in .5s ease-out forwards}"
           ".gc-noti span:nth-child(1){border-left-color:#16A34A}"
           "@keyframes gc-in{from{opacity:0;translate:-1cqw 0}to{opacity:1;translate:0 0}}</style>")
    inner = (f'<span class="gc-face">{face_html}</span><span class="gc-ring"></span><span class="gc-phone">📱</span>'
             '<span class="gc-say">어머, 또 연락이 왔네?</span>'
             '<span class="gc-noti"><span style="animation-delay:.3s">💳 [○○은행] 승인 12,800원</span>'
             '<span style="animation-delay:1.2s">📞 발신 표시: 서울중앙지검</span>'
             '<span style="animation-delay:2.1s">💬 링크 눌러서 앱부터 설치하세요</span></span>')
    status = "👵 할머니 폰이 계속 울려요<small>진짜 연락과 사기를 가려 할머니를 도와요</small>"
    return css + board("scene_grandma", "상수리동 · 할머니 댁 거실", inner, "754/314", status)


# ───── 가짜 안내서 감별소 시작 화면: 문마다 붙은 안내서 ─────
def hallway_cover(kj_url):
    css = ("<style>.hc-paper{transform:translate(-50%,-50%) rotate(-4deg);top:38%;width:7.5%;aspect-ratio:3/4;background:#FFFDF5;border:.2cqw solid #D6C7A1;border-radius:.4cqw;"
           "display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.3cqw;font-size:2.6cqw;box-shadow:0 .4cqw .8cqw rgba(0,0,0,.3);animation:sb-bob 2.4s ease-in-out infinite}"
           ".hc-paper b{font-size:1.1cqw;color:#B91C1C}"
           ".hc-plate{transform:translate(-50%,0);top:6%;background:#FFF8E1;border:.25cqw solid #8A5A2B;border-radius:.8cqw;padding:.1cqw 1cqw;font-weight:900;font-size:1.7cqw;color:#5B3A12}"
           ".hc-kj{left:1%;bottom:0;width:15%;display:flex;align-items:flex-end}"
           ".hc-kj img{width:100%!important;height:auto!important;margin:0!important;filter:drop-shadow(0 .4cqw .4cqw rgba(0,0,0,.3))}"
           ".hc-say{left:14%;bottom:24%;background:#fff;border:.3cqw solid #20483F;border-radius:1.6cqw 1.6cqw 1.6cqw .3cqw;padding:.6cqw 1.3cqw;font-weight:900;font-size:1.5cqw;color:#20483F;white-space:nowrap}</style>")
    papers = "".join(f'<span class="hc-plate" style="left:{x}%">{d}</span><span class="hc-paper" style="left:{x}%;animation-delay:{k * .3}s">📮<b>진짜?</b></span>'
                     for k, (x, d) in enumerate(zip((33.0, 56.5, 79.5), ("101호", "102호", "103호"))))
    kj = f'<span class="hc-kj"><img src="{kj_url}" alt="깡지"></span>' if kj_url else ""
    inner = papers + kj + '<span class="hc-say">문마다 우편물 안내서가 붙었어요! 진짜일까?</span>'
    status = "📮 안내서 3장 도착<small>적힌 번호로 전화하기 전에 문을 하나씩 감별해요</small>"
    return css + board("scene_hallway", "다람쥐동 · 다람쥐아파트 복도", inner, "758/330", status, cls="stat-left place-right")
