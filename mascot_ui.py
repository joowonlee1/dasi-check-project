"""공통 마스코트 표시. 원본 시트에서 CSS로 동작 영역만 보여줍니다."""
import base64
import html
from functools import lru_cache
from pathlib import Path
import streamlit as st

POSES = {
    "stop": ("mascot_four.png", 2, 2, 0, 0, 728, 544, "손바닥을 들고 잠깐 멈추라고 안내하는 캐릭터"),
    "suspicious": ("mascot_four.png", 2, 2, 1, 0, 728, 544, "의심스러운 문자를 살펴보는 캐릭터"),
    "detective": ("mascot_four.png", 2, 2, 0, 1, 728, 544, "돋보기로 증거를 조사하는 캐릭터"),
    "escape": ("mascot_four.png", 2, 2, 1, 1, 728, 544, "열쇠를 들고 탈출을 축하하는 캐릭터"),
    "welcome": ("mascot_six.png", 3, 2, 0, 0, 512, 512, "반갑게 손을 흔드는 캐릭터"),
    "phone": ("mascot_six.png", 3, 2, 1, 0, 512, 512, "전화로 확인하는 캐릭터"),
    "shield": ("mascot_six.png", 3, 2, 2, 0, 512, 512, "방패로 수상한 링크를 막는 캐릭터"),
    "hint": ("mascot_six.png", 3, 2, 0, 1, 512, 512, "전구와 함께 힌트를 알려주는 캐릭터"),
    "retry": ("mascot_six.png", 3, 2, 1, 1, 512, 512, "다시 도전을 응원하는 캐릭터"),
    "trophy": ("mascot_six.png", 3, 2, 2, 1, 512, 512, "트로피를 들고 축하하는 캐릭터"),
}

@lru_cache(maxsize=2)
def _image_data(filename):
    path = Path(__file__).resolve().parent / "assets" / filename
    return base64.b64encode(path.read_bytes()).decode("ascii")

def show_mascot(pose, message="", width=130):
    filename, columns, rows, col, row, cell_w, cell_h, description = POSES[pose]
    try:
        encoded = _image_data(filename)
    except OSError:
        # 이미지 누락만으로 학습 기능이 멈추지 않게 합니다.
        if message:
            st.caption(message)
        return
    width = max(64, min(int(width), 240))
    x = col * 100 / (columns - 1)
    y = row * 100 / (rows - 1)
    text = html.escape(message)
    label = html.escape(description, quote=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;'
        f'background:#FFFFFF;border:1px solid #E4E9DD;border-radius:20px;'
        f'padding:12px 16px;margin:8px 0 18px;">'
        f'<div role="img" aria-label="{label}" style="width:{width}px;'
        f'max-width:100%;flex-shrink:0;aspect-ratio:{cell_w}/{cell_h};'
        f'background-image:url(data:image/png;base64,{encoded});'
        f'background-size:{columns*100}% {rows*100}%;'
        f'background-position:{x}% {y}%;background-repeat:no-repeat;"></div>'
        f'<div style="flex:1;min-width:100px;color:#24443B;font-size:1.05rem;'
        f'font-weight:700;line-height:1.75;word-break:keep-all;">{text}</div></div>',
        unsafe_allow_html=True,
    )
