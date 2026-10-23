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


def show_mascot(pose, message="", width=130):
    description = POSES[pose][5]
    try:
        encoded = _pose_data(pose)
    except Exception:
        # 이미지 누락만으로 학습 기능이 멈추지 않게 합니다.
        if message:
            st.caption(message)
        return
    width = max(64, min(int(width), 240))
    text = html.escape(message)
    label = html.escape(description, quote=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;'
        f'background:#FFFFFF;border:1px solid #E4E9DD;border-radius:20px;'
        f'padding:8px 14px;margin:4px 0 10px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="{label}" '
        f'style="width:{width}px;max-width:100%;height:auto;flex-shrink:0;">'
        f'<div style="flex:1;min-width:100px;color:#24443B;font-size:1.05rem;'
        f'font-weight:700;line-height:1.75;word-break:keep-all;">{text}</div></div>',
        unsafe_allow_html=True,
    )


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
