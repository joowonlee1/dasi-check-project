"""공통 마스코트 표시. 원본 시트에서 포즈마다 실제 그림이 있는 영역만 잘라 보여줍니다."""
import base64
import html
import io
import re
from functools import lru_cache
from pathlib import Path
import streamlit as st

# 포즈: (파일, 실제 그림 영역 x1, y1, x2, y2, 설명)
# 칸을 똑같이 나누면 칸 밖으로 나온 손·방패·소품이 잘려서, 그림이 있는 영역을 직접 측정했습니다.
POSES = {
    "stop": ("mascot_four.png", 64, 71, 672, 523, "손바닥을 들고 잠깐 멈추라고 안내하는 캐릭터"),
    "suspicious": ("mascot_four.png", 815, 114, 1300, 523, "의심스러운 문자를 살펴보는 캐릭터"),
    "detective": ("mascot_four.png", 168, 601, 633, 1005, "돋보기로 증거를 조사하는 캐릭터"),
    "escape": ("mascot_four.png", 758, 568, 1417, 1000, "열쇠를 들고 탈출을 축하하는 캐릭터"),
    "welcome": ("mascot_six.png", 12, 92, 503, 483, "반갑게 손을 흔드는 캐릭터"),
    "phone": ("mascot_six.png", 542, 91, 973, 501, "전화로 확인하는 캐릭터"),
    "shield": ("mascot_six.png", 1000, 108, 1531, 485, "방패로 수상한 링크를 막는 캐릭터"),
    "hint": ("mascot_six.png", 17, 505, 524, 947, "전구와 함께 힌트를 알려주는 캐릭터"),
    "retry": ("mascot_six.png", 579, 564, 970, 951, "다시 도전을 응원하는 캐릭터"),
    "trophy": ("mascot_six.png", 1012, 559, 1512, 947, "트로피를 들고 축하하는 캐릭터"),
}
PAD = 14  # 테두리 선이 가장자리에 붙지 않도록 남기는 여백(px)


@lru_cache(maxsize=16)
def _pose_data(pose):
    """포즈 영역만 잘라 PNG(base64)로 돌려줍니다. 한 번 만든 결과는 재사용합니다."""
    from PIL import Image  # Streamlit 설치 시 함께 설치되는 라이브러리

    filename, x1, y1, x2, y2, _ = POSES[pose]
    path = Path(__file__).resolve().parent / "assets" / filename
    with Image.open(path) as image:
        w, h = image.size
        box = (max(0, x1 - PAD), max(0, y1 - PAD), min(w, x2 + PAD), min(h, y2 + PAD))
        part = image.convert("RGBA").crop(box)
    part.thumbnail((480, 480))  # 화면 표시용으로 줄여 전송량을 줄입니다.
    buffer = io.BytesIO()
    part.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def show_mascot(pose, message="", width=96):
    description = POSES[pose][5]
    try:
        encoded = _pose_data(pose)
    except Exception:
        # 이미지 누락만으로 학습 기능이 멈추지 않게 합니다.
        if message:
            st.caption(message)
        return
    width = max(56, min(int(width), 130))  # 깡지가 눈에 잘 띄되 화면을 너무 차지하지 않게 상한을 둬요
    text = html.escape(message)
    label = html.escape(description, quote=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;'
        f'background:#FFFFFF;border:1px solid #E4E9DD;border-radius:20px;'
        f'padding:4px 12px;margin:2px 0 6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="{label}" '
        f'style="width:{width}px;max-width:100%;height:auto;flex-shrink:0;">'
        f'<div style="flex:1;min-width:100px;color:#24443B;font-size:1.05rem;'
        f'font-weight:700;line-height:1.5;word-break:keep-all;">{text}</div></div>',
        unsafe_allow_html=True,
    )


def mascot_img(pose, width=200):
    """깡지 그림만 크게 보여 줄 때 쓰는 <img> 태그(홈 첫 화면 등). 그림이 없으면 빈 글자."""
    try:
        encoded = _pose_data(pose)
    except Exception:
        return ""
    label = html.escape(POSES[pose][5], quote=True)
    return (f'<img src="data:image/png;base64,{encoded}" alt="{label}" '
            f'style="width:{int(width)}px;max-width:100%;height:auto;display:block;margin:0 auto;">')


def show_key_question(text, icon="💡"):
    """페이지의 핵심 질문·문장을 눈에 띄는 상자로 보여 줍니다. **굵게** 표시를 쓸 수 있어요."""
    body = re.sub(r"\*\*(.+?)\*\*", r'<b style="color:#B4471B;">\1</b>', html.escape(text))
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#FFF4E8,#EAF6F1);border-left:8px solid #FF7A45;'
        f'border-radius:18px;padding:12px 18px;margin:4px 0 10px;box-shadow:0 4px 14px rgba(32,72,63,.08);">'
        f'<div style="font-size:1.25rem;font-weight:900;color:#20483F;line-height:1.55;word-break:keep-all;">'
        f'{icon} {body}</div></div>',
        unsafe_allow_html=True,
    )


# 깡지 증명사진(배경색과 표정이 조금씩 다른 4장). 사이드바와 시민증 페이지에서 함께 써요.
ID_PHOTOS = ["ggangji_citizen_photo.png", "ggangji_blue.png", "ggangji_pink.png", "ggangji_cream.png"]


@st.cache_data(show_spinner=False)
def id_photo(filename):
    """증명사진에서 얼굴부터 어깨 맨 위까지만 잘라 작게 줄인 뒤 PNG(base64)로 돌려줘요."""
    from PIL import Image

    path = Path(__file__).resolve().parent / "assets" / filename
    with Image.open(path) as image:
        w, h = image.size
        # 원본(1086×1448) 기준 얼굴 양옆 빈 곳과 몸통을 덜어 내는 비율이에요.
        box = (int(w * 0.037), int(h * 0.207), int(w * 0.963), int(h * 0.822))
        part = image.convert("RGB").crop(box).resize((240, 212))
    buffer = io.BytesIO()
    part.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()


# ───────── 통통 튀는 시작 화면 ─────────
# 게임 시작 화면을 다른 게임(마피아·가짜뉴스)처럼 큰 배너와 색깔 카드로 보여 주는 공통 도구예요.
HERO_CSS = """<style>
@keyframes jk-pop {0%{transform:scale(.85);opacity:0} 70%{transform:scale(1.03);opacity:1} 100%{transform:scale(1)}}
@keyframes jk-bounce {0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)}}
.jk-hero {background:linear-gradient(135deg,var(--a,#EAF6F0),var(--b,#F4FAF6));border:1.5px solid var(--line,#CFE6DA);
  border-radius:20px;padding:12px 16px;color:#3E4A46;text-align:center;animation:jk-pop .6s ease-out both;margin:6px 0 12px;}
.jk-hero b {display:block;font-size:1.35rem;font-weight:900;margin:2px 0;word-break:keep-all;color:var(--ink,#0F766E);}
.jk-hero span {font-weight:600;word-break:keep-all;}
.jk-tiles {display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px;margin:4px 0 10px;}
.jk-tile {border-radius:14px;padding:8px 10px;border:1px solid rgba(0,0,0,.06);text-align:left;
  display:grid;grid-template-columns:34px 1fr;column-gap:8px;align-items:center;animation:jk-pop .5s ease-out both;word-break:keep-all;}
.jk-tile div {font-size:26px;grid-row:span 2;text-align:center;animation:jk-bounce 2.4s ease-in-out infinite;}
.jk-tile b {display:block;color:#1E2F2B;font-size:.95rem;}
.jk-tile small {color:#3E5751;font-size:.82rem;line-height:1.4;display:block;}
.jk-hero.sm {padding:12px 16px;border-radius:20px;margin:2px 0 8px;} .jk-hero.sm b {font-size:1.3rem;margin:2px 0;}
@media (max-width:640px) {.jk-hero b {font-size:1.3rem;} .jk-tiles {grid-template-columns:repeat(2,1fr);}}
@media (prefers-reduced-motion: reduce) {.jk-hero, .jk-tile, .jk-tile div {animation:none !important;}}
</style>"""
# 연한 색 카드(눈이 편한 파스텔 톤)
TILE_COLORS = ["#FDECEC", "#FFFBE6", "#EAF6F0", "#EEF4FF", "#F5EEFB", "#FFF3E8"]


# 연한 배너 색 세트: (배경1, 배경2, 테두리, 제목 글씨)
HERO_TONES = {
    "pink": ("#FDECEC", "#FFF6F3", "#F6CACA", "#B42318"),
    "cream": ("#FFFBE6", "#FFF8EC", "#F1DFA6", "#8A5A00"),
    "mint": ("#EAF6F0", "#F4FAF6", "#CFE6DA", "#0F766E"),
    "sky": ("#EEF4FF", "#F6F9FF", "#CCDDF5", "#1E4E8C"),
}


def show_hero(tag, title, sub, tone="mint", small=False):
    """게임 시작 화면의 배너(연한 색). small=True면 높이를 줄인 작은 배너예요."""
    a, b, line, ink = HERO_TONES.get(tone, HERO_TONES["mint"])
    st.markdown(
        HERO_CSS + f'<div class="jk-hero{" sm" if small else ""}" style="--a:{a};--b:{b};--line:{line};--ink:{ink}">'
        f"<span>{html.escape(tag)}</span><b>{html.escape(title)}</b><span>{html.escape(sub)}</span></div>",
        unsafe_allow_html=True,
    )


def show_tiles(tiles):
    """(아이콘, 제목, 설명) 카드들을 색깔별로 통통 튀게 보여 줘요."""
    st.markdown(
        HERO_CSS + '<div class="jk-tiles">' + "".join(
            f'<div class="jk-tile" style="background:{TILE_COLORS[i % len(TILE_COLORS)]};animation-delay:{i * .08:.2f}s">'
            f'<div style="animation-delay:{i * .3:.1f}s">{icon}</div><b>{html.escape(title)}</b>'
            f"<small>{html.escape(text)}</small></div>"
            for i, (icon, title, text) in enumerate(tiles)
        ) + "</div>",
        unsafe_allow_html=True,
    )
