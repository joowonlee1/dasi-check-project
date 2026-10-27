"""할머니 얼굴 표정: assets/grandma_faces.png(표정 14개가 2줄로 그려진 그림)에서 표정 하나씩 잘라 보여 줘요.
그림 파일이 없으면, 아래에 숫자로 그린 할머니 얼굴(SVG)을 대신 보여 줘요.
"""
import base64
import io
from functools import lru_cache
from pathlib import Path

SHEET = Path(__file__).resolve().parent / "assets" / "grandma_faces.png"
BG = (251, 247, 237)  # 그림 바탕색(잘라 낸 뒤 정사각형으로 채울 때 써요)

# 표정마다 그림에서 잘라 낼 영역(x0, y0, x1, y1). 하트·땀·물음표 같은 꾸밈까지 잘리지 않게 측정했어요.
FACE_BOXES = {"grateful": (26, 187, 237, 419), "relieved": (241, 182, 462, 420), "shocked": (468, 177, 688, 419), "angry": (688, 186, 889, 422), "hurt": (890, 181, 1097, 419), "huffy": (1097, 183, 1302, 417), "tired": (1312, 177, 1519, 412), "annoyed": (29, 555, 239, 796), "calm": (243, 566, 465, 806), "down": (467, 567, 668, 795), "terrified": (681, 569, 891, 800), "anxious": (895, 571, 1099, 802), "puzzled": (1109, 565, 1310, 795), "neutral": (1315, 573, 1515, 799)}


@lru_cache(maxsize=32)
def _face_png(name):
    """표정 하나를 잘라 정사각형 PNG(base64)로 만들어요. 한 번 만든 건 다시 써요."""
    from PIL import Image

    box = FACE_BOXES[name]
    with Image.open(SHEET) as sheet:
        part = sheet.convert("RGB").crop(box)
    side = max(part.size)
    square = Image.new("RGB", (side, side), BG)
    square.paste(part, ((side - part.width) // 2, (side - part.height) // 2))
    square = square.resize((320, 320))
    buffer = io.BytesIO()
    square.save(buffer, format="PNG", optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def face_img(name, size=200):
    """할머니 표정 그림(<img>). 그림 파일이 없으면 숫자로 그린 얼굴로 대신해요."""
    name = name if name in FACE_BOXES else "neutral"
    try:
        data = _face_png(name)
    except Exception:
        return face_svg(name, size, drawn=True)
    return (f'<img src="data:image/png;base64,{data}" alt="할머니 표정" '
            f'style="width:{int(size)}px;height:{int(size)}px;border-radius:22px;display:block;">')

# 표정 이름: (눈썹, 눈, 입, 덧붙임들)
FACES = {
    "grateful": ("soft", "happy", "smile", ("tear", "blush")),   # 고마워하며 안심
    "relieved": ("soft", "closed", "smile", ("blush",)),         # 한숨 돌림
    "shocked":  ("up", "wide", "o", ("sweat",)),                 # 깜짝 놀람
    "angry":    ("angry", "dot", "frown", ("vein",)),            # 화남
    "hurt":     ("sad", "dot", "frown", ("tear",)),              # 서운하고 겁남
    "huffy":    ("angry", "side", "flat", ("puff",)),            # 언짢음
    "tired":    ("sad", "half", "wave", ("puff",)),              # 지침
    "annoyed":  ("flat", "half", "flat", ()),                    # 불편함
    "calm":     ("soft", "dot", "smile", ("blush",)),            # 편안함
    "down":     ("sad", "dot", "frown", ()),                     # 시무룩
    "terrified": ("up", "wide", "wave", ("sweat", "sweat2")),    # 완전히 겁먹음
    "anxious":  ("sad", "dot", "wave", ("sweat",)),              # 불안함
    "puzzled":  ("tilt", "dot", "flat", ("q",)),                 # 긴가민가
    "neutral":  ("flat", "dot", "flat", ()),                     # 조금 이상하다고 느낌
}


def _brows(kind):
    shapes = {
        "soft": "M52 66 Q62 61 72 65 M108 65 Q118 61 128 66",
        "up": "M52 60 Q62 52 72 58 M108 58 Q118 52 128 60",
        "angry": "M52 62 L73 70 M128 62 L107 70",
        "sad": "M52 70 L72 62 M108 62 L128 70",
        "flat": "M53 66 H72 M108 66 H127",
        "tilt": "M52 63 Q62 58 72 63 M108 68 H127",
    }
    return f'<path d="{shapes[kind]}" stroke="#8B8B8B" stroke-width="4.5" stroke-linecap="round" fill="none"/>'


def _eyes(kind):
    if kind == "happy":
        return '<path d="M55 86 Q63 77 71 86 M109 86 Q117 77 125 86" stroke="#2B2B2B" stroke-width="4" stroke-linecap="round" fill="none"/>'
    if kind == "closed":
        return '<path d="M55 84 Q63 90 71 84 M109 84 Q117 90 125 84" stroke="#2B2B2B" stroke-width="4" stroke-linecap="round" fill="none"/>'
    if kind == "wide":
        return ('<circle cx="63" cy="84" r="9" fill="#fff" stroke="#2B2B2B" stroke-width="2.5"/><circle cx="63" cy="84" r="3.5" fill="#2B2B2B"/>'
                '<circle cx="117" cy="84" r="9" fill="#fff" stroke="#2B2B2B" stroke-width="2.5"/><circle cx="117" cy="84" r="3.5" fill="#2B2B2B"/>')
    if kind == "half":
        return ('<path d="M55 82 H71 M109 82 H125" stroke="#2B2B2B" stroke-width="3.5" stroke-linecap="round"/>'
                '<path d="M57 82 Q63 89 69 82 M111 82 Q117 89 123 82" fill="#2B2B2B"/>')
    if kind == "side":
        return '<circle cx="67" cy="84" r="4.5" fill="#2B2B2B"/><circle cx="121" cy="84" r="4.5" fill="#2B2B2B"/>'
    return '<circle cx="63" cy="84" r="5" fill="#2B2B2B"/><circle cx="117" cy="84" r="5" fill="#2B2B2B"/>'


def _mouth(kind):
    shapes = {
        "smile": '<path d="M76 118 Q90 132 104 118" stroke="#8C3B2E" stroke-width="4.5" stroke-linecap="round" fill="none"/>',
        "frown": '<path d="M76 127 Q90 115 104 127" stroke="#8C3B2E" stroke-width="4.5" stroke-linecap="round" fill="none"/>',
        "flat": '<path d="M79 122 H101" stroke="#8C3B2E" stroke-width="4.5" stroke-linecap="round"/>',
        "o": '<ellipse cx="90" cy="123" rx="8" ry="10" fill="#8C3B2E"/>',
        "wave": '<path d="M76 123 q5 -5 10 0 t10 0 t8 0" stroke="#8C3B2E" stroke-width="4" stroke-linecap="round" fill="none"/>',
    }
    return shapes[kind]


def _extras(items):
    out = []
    for item in items:
        if item == "tear":
            out.append('<path d="M56 94 q-5 10 0 14 q5 -4 0 -14z M124 94 q-5 10 0 14 q5 -4 0 -14z" fill="#7CC4F2"/>')
        elif item == "blush":
            out.append('<ellipse cx="52" cy="104" rx="10" ry="6" fill="#F4A6A6" opacity=".7"/><ellipse cx="128" cy="104" rx="10" ry="6" fill="#F4A6A6" opacity=".7"/>')
        elif item == "sweat":
            out.append('<path d="M140 50 q-7 12 0 17 q7 -5 0 -17z" fill="#7CC4F2" stroke="#4A9BD1" stroke-width="1.5"/>')
        elif item == "sweat2":
            out.append('<path d="M38 58 q-6 10 0 14 q6 -4 0 -14z" fill="#7CC4F2" stroke="#4A9BD1" stroke-width="1.5"/>')
        elif item == "vein":
            out.append('<path d="M132 40 l8 8 m0 -8 l-8 8 M136 36 v4 M136 52 v4" stroke="#E5484D" stroke-width="3.5" stroke-linecap="round"/>')
        elif item == "puff":
            out.append('<g fill="#E8EEF2" stroke="#B8C4CC" stroke-width="1.5"><circle cx="116" cy="134" r="5"/><circle cx="126" cy="131" r="6"/><circle cx="137" cy="133" r="5"/></g>')
        elif item == "q":
            out.append('<text x="140" y="56" font-size="30" font-weight="900" fill="#8A5A00" font-family="sans-serif">?</text>')
    return "".join(out)


def face_svg(name, size=110, drawn=False):
    """표정 이름으로 할머니 얼굴을 만들어요. 기본은 그림 파일(face_img), drawn=True면 숫자로 그린 SVG예요."""
    if not drawn:
        return face_img(name, size)
    brow, eye, mouth, extras = FACES.get(name, FACES["neutral"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 170" width="{size}" height="{size * 170 // 180}" '
        f'role="img" aria-label="할머니 얼굴">'
        # 쪽진 머리(뒤쪽 쪽) · 얼굴 · 머리카락
        '<circle cx="90" cy="20" r="16" fill="#D9D9D9" stroke="#A9A9A9" stroke-width="2"/>'
        '<path d="M80 14 h20" stroke="#B07A3A" stroke-width="4" stroke-linecap="round"/>'
        '<ellipse cx="90" cy="92" rx="62" ry="64" fill="#FFE2C4" stroke="#D9A882" stroke-width="2.5"/>'
        '<path d="M30 80 Q28 34 90 30 Q152 34 150 80 Q138 52 112 48 Q90 58 68 48 Q42 52 30 80z" fill="#E3E3E3" stroke="#B5B5B5" stroke-width="2"/>'
        '<path d="M40 62 Q50 48 66 46 M140 62 Q130 48 114 46" stroke="#C7C7C7" stroke-width="2" fill="none"/>'
        # 귀
        '<ellipse cx="28" cy="94" rx="7" ry="11" fill="#FFD7B0" stroke="#D9A882" stroke-width="2"/>'
        '<ellipse cx="152" cy="94" rx="7" ry="11" fill="#FFD7B0" stroke="#D9A882" stroke-width="2"/>'
        + _brows(brow) + _eyes(eye) +
        # 동그란 안경
        '<circle cx="63" cy="84" r="16" fill="none" stroke="#9A6B3F" stroke-width="3"/>'
        '<circle cx="117" cy="84" r="16" fill="none" stroke="#9A6B3F" stroke-width="3"/>'
        '<path d="M79 84 Q90 78 101 84" stroke="#9A6B3F" stroke-width="3" fill="none"/>'
        # 주름 · 코
        '<path d="M44 96 q4 3 8 1 M128 97 q4 2 8 -1 M78 142 q12 5 24 0" stroke="#E0B08E" stroke-width="2" fill="none" stroke-linecap="round"/>'
        '<path d="M90 92 q-4 10 2 13" stroke="#D9A882" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        + _mouth(mouth) + _extras(extras) +
        '</svg>'
    )
