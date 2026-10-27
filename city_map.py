"""도토리시 지도: 섬 모양 지형(강·다리·광장·철길·길·건물) 위에 장소 핀을 제 위치에 찍어 보여 줘요.

그림(지형)은 SVG를 파이썬으로 만들어 <img> 하나로 넣고, 핀과 동네 이름은 HTML로 위에 얹어요.
그래서 화면 폭이 달라져도 핀이 같은 자리에 있고, 글씨는 항상 또렷해요. (Streamlit이 없어도 동작해요.)
"""
import base64
import html
import math
import random
from functools import lru_cache

MAP_W, MAP_H = 800, 600

# 번호: (가로 %, 세로 %, 지도에 쓰는 짧은 이름)  ※ 번호는 app.py의 PLACES와 같아요.
MAP_PINS = {
    "01": (16, 31, "할머니 댁"),
    "09": (37, 29, "3반 단톡방"),
    "10": (60, 29, "중고마켓"),
    "04": (83, 31, "사이버 검문소"),
    "03": (20, 69, "민서네 집"),
    "14": (25, 81, "관리사무소"),
    "06": (45, 69, "도토리 광장"),
    "07": (38, 83, "시민안전센터"),
    "12": (56, 85, "공영주차장"),
    "02": (68, 64, "대화 연습실"),
    "05": (82, 62, "시립도서관"),
    "08": (78, 74, "시민 등록소"),
    "11": (68, 87, "우체국 필터실"),
    "13": (82, 88, "통계청"),  # 시민 등록소와 겹치지 않게 아래·왼쪽으로 옮겼어요.
}

# 동네 이름표: 동네 이름 -> (가로 %, 세로 %, 아이콘)
MAP_TOWNS = {
    "상수리동": (16, 12, "🌳"),
    "떡갈나무동": (37, 12, "🍂"),
    "개암골": (60, 12, "🌰"),
    "도토리역 앞": (83, 12, "🚉"),
    "다람쥐동": (18, 58, "🐿️"),
    "중앙동": (45, 58, "⛲"),
    "시청로": (73, 55, "🏛️"),
}

# 길(선분). 그리기와 '나무 안 심을 곳' 계산에 같이 써요.
_ROADS = [
    ((130, 185), (731, 185)), ((160, 185), (160, 480)), ((300, 175), (300, 345)), ((300, 345), (360, 345)),
    ((480, 175), (480, 340)), ((650, 185), (650, 250)), ((160, 480), (625, 480)), ((625, 370), (625, 480)),
    ((160, 430), (650, 430)), ((360, 350), (360, 500)), ((480, 340), (480, 490)), ((560, 438), (700, 438)),
]
_BRIDGE_X = (160, 300, 480)

# 건물·연못 같은 고정 물체의 자리(x0, y0, x1, y1): 나무와 풀이 피해 가요.
_BLOCKS = [
    (176, 118, 212, 164), (350, 112, 404, 160), (566, 122, 608, 166), (200, 190, 236, 226),
    (206, 348, 244, 392), (420, 436, 464, 478), (576, 348, 614, 392), (96, 222, 146, 250),
    (108, 450, 152, 496), (388, 486, 508, 538), (518, 82, 604, 122), (686, 92, 730, 168),
    (286, 392, 434, 458),
]

_RIVER = [((-10, 300), (110, 270), (160, 330), (250, 300)), ((250, 300), (340, 270), (380, 252), (470, 288)),
          ((470, 288), (560, 324), (600, 332), (690, 288)), ((690, 288), (780, 244), (770, 262), (810, 276))]


@lru_cache(maxsize=1)
def _river_pts():
    pts = []
    for p0, p1, p2, p3 in _RIVER:
        for i in range(201):
            t = i / 200
            u = 1 - t
            pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return pts


def _river_y(x):
    """강 가운데선의 높이(다리를 정확한 자리에 놓고 나무를 강 위에 심지 않으려고 써요)."""
    return min(_river_pts(), key=lambda p: abs(p[0] - x))[1]


def _seg_dist(x, y, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def _free(x, y, pins, margin=12, pin_box=(62, 52)):
    """이 자리가 비어 있는지(핀·길·강·건물·광장·이름표와 안 겹치는지) 확인해요."""
    if ((x - 410) / 330) ** 2 + ((y - 310) / 245) ** 2 > 0.86:
        return False
    if any(abs(x - px) < pin_box[0] and abs(y - py) < pin_box[1] for px, py in pins):
        return False
    if abs(y - _river_y(x)) < 36 or ((x - 360) / 95) ** 2 + ((y - 414) / 62) ** 2 < 1:
        return False
    if any(_seg_dist(x, y, a, b) < 14 + margin / 2 for a, b in _ROADS):
        return False
    if any(x0 - margin < x < x1 + margin and y0 - margin < y < y1 + margin for x0, y0, x1, y1 in _BLOCKS):
        return False
    if any(abs(x - tx * MAP_W / 100) < 56 and abs(y - ty * MAP_H / 100) < 20 for tx, ty, _ in MAP_TOWNS.values()):
        return False
    return not (722 < x < 750 and 80 < y < 270)


def _house(x, y, w=30, h=24, wall="#FFF5DD", roof="#B97855"):
    return (f'<ellipse cx="{x + w / 2}" cy="{y + h + 2}" rx="{w * .62}" ry="3.5" fill="#2F4A2E" opacity=".18"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{wall}" stroke="#A8865D" stroke-width="2"/>'
            f'<path d="M{x - 4} {y}L{x + w / 2} {y - 16}L{x + w + 4} {y}Z" fill="{roof}" stroke="#8A5A3B" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="{x + w - 9}" y="{y - 14}" width="5" height="9" fill="#9C6B4A"/>'
            f'<rect x="{x + w / 2 - 4}" y="{y + h - 11}" width="8" height="11" fill="#8A5A2B"/>'
            f'<rect x="{x + 4}" y="{y + 6}" width="6" height="6" fill="#BFE3F5"/>'
            f'<rect x="{x + w - 10}" y="{y + 6}" width="6" height="6" fill="#BFE3F5"/>')


def _bridge(x):
    y = _river_y(x)
    planks = "".join(f'<path d="M{x - 17} {y + k:.0f}H{x + 17}" stroke="#A97B42" stroke-width="2"/>' for k in range(-24, 28, 8))
    return (f'<rect x="{x - 17}" y="{y - 30:.0f}" width="34" height="60" rx="3" fill="#C99A5B" stroke="#8A5A2B" stroke-width="3"/>'
            f'{planks}<path d="M{x - 17} {y - 30:.0f}V{y + 30:.0f}M{x + 17} {y - 30:.0f}V{y + 30:.0f}" stroke="#6B4423" stroke-width="4"/>')


def _tree(x, y, r, kind):
    shadow = f'<ellipse cx="{x:.0f}" cy="{y + r:.0f}" rx="{r * 1.1:.0f}" ry="{r * .4:.0f}" fill="#2F4A2E" opacity=".25"/>'
    if kind == 0:  # 소나무
        return (shadow + f'<rect x="{x - 1.5:.0f}" y="{y + r - 4:.0f}" width="3" height="6" fill="#8A5A2B"/>'
                f'<path d="M{x:.0f} {y - r - 6:.0f}L{x + r:.0f} {y + 2:.0f}H{x - r:.0f}Z" fill="#3F7F3B"/>'
                f'<path d="M{x:.0f} {y - r + 2:.0f}L{x + r * 1.1:.0f} {y + r - 2:.0f}H{x - r * 1.1:.0f}Z" fill="#4E9444"/>')
    out = (shadow + f'<circle cx="{x:.0f}" cy="{y + 3:.0f}" r="{r}" fill="#3F7F3B" opacity=".55"/>'
           f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#5FA050"/>'
           f'<circle cx="{x - 3:.0f}" cy="{y - 3:.0f}" r="{r * .4:.1f}" fill="#8CCB74" opacity=".8"/>')
    if kind == 2:  # 열매 나무(도토리시니까 도토리!)
        out += "".join(f'<circle cx="{x + dx:.0f}" cy="{y + dy:.0f}" r="2" fill="#B5651D"/>' for dx, dy in ((-4, 2), (3, -3), (4, 4)))
    return out


@lru_cache(maxsize=1)
def _svg():
    island = ("M 95,112 C 70,62 200,42 330,52 C 450,32 600,36 700,82 C 772,112 778,200 762,282 "
              "C 790,382 742,520 640,552 C 520,590 380,566 260,574 C 140,586 50,526 60,424 "
              "C 30,332 112,302 72,232 C 50,180 102,160 95,112 Z")
    pins = [(x * MAP_W / 100, y * MAP_H / 100) for x, y, _ in MAP_PINS.values()]
    rnd = random.Random(7)

    trees = []
    for _ in range(5000):
        if len(trees) >= 52:
            break
        x, y = rnd.uniform(90, 750), rnd.uniform(75, 545)
        if _free(x, y, pins) and not any(abs(x - tx) < 26 and abs(y - ty) < 26 for tx, ty, _, _ in trees):
            trees.append((x, y, rnd.choice((8, 9, 10, 11)), rnd.choice((0, 1, 1, 2))))
    tree_svg = "".join(_tree(*t) for t in sorted(trees, key=lambda t: t[1]))

    tufts, flowers = [], []
    for _ in range(4000):
        x, y = rnd.uniform(90, 750), rnd.uniform(75, 545)
        if _free(x, y, pins, margin=4, pin_box=(46, 40)):
            (tufts if len(tufts) < 80 else flowers).append((x, y))
        if len(flowers) >= 30:
            break
    tuft_svg = "".join(f'<path d="M{x:.0f} {y:.0f}l-3 -6M{x:.0f} {y:.0f}v-7M{x:.0f} {y:.0f}l3 -6" stroke="#5E9A4A" stroke-width="1.6" stroke-linecap="round" fill="none"/>'
                       for x, y in tufts)
    flower_svg = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.6" fill="{rnd.choice(("#F29BB8", "#FFD84D", "#FFFFFF", "#FF9F6B"))}"/>'
                         f'<circle cx="{x:.0f}" cy="{y:.0f}" r=".9" fill="#B5651D"/>' for x, y in flowers)

    waves = "".join(f'<path d="M {x},{y} q 12,-8 24,0 t 24,0" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".6"/>'
                    for x, y in ((18, 40), (700, 24), (24, 560), (700, 590), (410, 18), (150, 592), (580, 592), (30, 200), (772, 430), (30, 470)))
    river = "M -10,300 C 110,270 160,330 250,300 S 380,252 470,288 S 600,332 690,288 S 770,262 810,276"
    reeds = "".join(
        f'<path d="M{x} {_river_y(x) + s * 26:.0f}v-12M{x + 4} {_river_y(x) + s * 26:.0f}v-9" stroke="#5E9A4A" stroke-width="2"/>'
        f'<circle cx="{x}" cy="{_river_y(x) + s * 26 - 13:.0f}" r="2.4" fill="#8A5A2B"/>'
        for x, s in ((70, -1), (210, 1), (380, -1), (560, 1), (650, -1), (400, 1), (120, 1)))
    road_d = "".join(f"M{a[0]} {a[1]}L{b[0]} {b[1]}" for a, b in _ROADS)
    sleepers = "".join(f'<path d="M727 {y}h16" stroke="#8A5A2B" stroke-width="3"/>' for y in range(96, 262, 9))
    lot_lines = "".join(f'<path d="M{x} 490v14M{x} 522v14" stroke="#fff" stroke-width="2"/>' for x in range(402, 500, 14))
    cars = "".join(f'<rect x="{x}" y="{y}" width="10" height="13" rx="3" fill="{c}"/>'
                   for x, y, c in ((392, 491, "#E5484D"), (420, 491, "#3E7BD6"), (476, 523, "#F2B134"), (448, 523, "#4FA37C")))
    houses = (_house(180, 134, 28, 26, roof="#B97855") + _house(572, 138, 30, 24, roof="#C45B4A") + _house(204, 204, 26, 20, roof="#6F8FB8") +
              _house(210, 366, 30, 24, roof="#B97855") + _house(424, 452, 30, 24, roof="#C45B4A") + _house(580, 366, 30, 24, roof="#6F8FB8"))
    school = ('<rect x="352" y="130" width="50" height="28" fill="#FFE7B0" stroke="#A8865D" stroke-width="2"/>'
              '<path d="M348 130L377 114L406 130Z" fill="#C45B4A" stroke="#8A5A3B" stroke-width="2" stroke-linejoin="round"/>'
              '<rect x="371" y="142" width="12" height="16" fill="#8A5A2B"/>'
              + "".join(f'<rect x="{x}" y="136" width="7" height="7" fill="#BFE3F5"/>' for x in (357, 389)) +
              '<path d="M402 130V108" stroke="#6B4423" stroke-width="2"/><path d="M402 108h14l-4 5 4 5h-14z" fill="#E5484D"/>')
    apt = ('<rect x="112" y="452" width="34" height="42" fill="#E8DCC4" stroke="#A8865D" stroke-width="2"/>'
           + "".join(f'<rect x="{116 + c * 10}" y="{458 + r * 10}" width="6" height="6" fill="#BFE3F5"/>' for r in range(4) for c in range(3)) +
           '<rect x="124" y="484" width="10" height="10" fill="#8A5A2B"/>')
    garden = ('<rect x="98" y="224" width="46" height="24" rx="3" fill="#B98A5A" stroke="#8A5A2B" stroke-width="2"/>'
              + "".join(f'<path d="M100 {y}H142" stroke="#5E9A4A" stroke-width="3" stroke-dasharray="3 3"/>' for y in (231, 237, 243)))
    station = ('<ellipse cx="708" cy="164" rx="22" ry="4" fill="#2F4A2E" opacity=".18"/>'
               '<rect x="690" y="108" width="36" height="52" fill="#F4F1EA" stroke="#8A8F94" stroke-width="2"/>'
               '<path d="M686 108L708 92L730 108Z" fill="#3E7BD6" stroke="#27579F" stroke-width="2" stroke-linejoin="round"/>'
               '<circle cx="708" cy="120" r="6" fill="#fff" stroke="#6B4423" stroke-width="1.5"/><path d="M708 116v4h3" stroke="#6B4423" fill="none"/>'
               '<rect x="702" y="138" width="12" height="22" fill="#8A5A2B"/>')
    train = ('<rect x="730" y="194" width="14" height="22" rx="4" fill="#E5484D" stroke="#8C2A2E" stroke-width="1.5"/>'
             '<rect x="730" y="218" width="14" height="20" rx="3" fill="#F2B134" stroke="#9A6B12" stroke-width="1.5"/>'
             '<rect x="730" y="240" width="14" height="20" rx="3" fill="#F2B134" stroke="#9A6B12" stroke-width="1.5"/>'
             '<rect x="733" y="198" width="8" height="6" fill="#BFE3F5"/>')
    plaza = ('<ellipse cx="360" cy="414" rx="70" ry="42" fill="#F0E3B8" stroke="#E2C98A" stroke-width="4"/>'
             '<ellipse cx="360" cy="414" rx="58" ry="33" fill="none" stroke="#E2C98A" stroke-width="2" stroke-dasharray="5 6"/>'
             '<circle cx="360" cy="414" r="15" fill="#B9E3F5" stroke="#8ECDEB" stroke-width="4"/>'
             + "".join(f'<rect x="{x}" y="{y}" width="16" height="5" rx="2" fill="#B97855" stroke="#8A5A3B"/>' for x, y in ((344, 372), (344, 450)))
             + "".join(f'<path d="M{x} {y}v-12" stroke="#6B4423" stroke-width="2"/><circle cx="{x}" cy="{y - 13}" r="3.5" fill="#FFE066" stroke="#E2A93B"/>'
                       for x, y in ((296, 405), (424, 405), (296, 436), (424, 436))))
    pond = ('<ellipse cx="560" cy="102" rx="38" ry="18" fill="#B9E3F5" stroke="#8ECDEB" stroke-width="5"/>'
            '<circle cx="545" cy="106" r="5" fill="#6FB65A"/><circle cx="576" cy="98" r="4.5" fill="#6FB65A"/><circle cx="560" cy="108" r="3.5" fill="#6FB65A"/>'
            '<circle cx="572" cy="106" r="5" fill="#fff" stroke="#E5E5E5"/><circle cx="574" cy="105" r="3" fill="#FFD84D"/>'
            '<path d="M547 96q2 -4 5 0z" fill="#F2B134"/><circle cx="549" cy="97" r="3" fill="#FFF3B0"/>')
    compass = ('<circle cx="742" cy="566" r="20" fill="#fff" opacity=".85" stroke="#8A5A2B" stroke-width="2"/>'
               '<path d="M742 548L747 566L742 584L737 566Z" fill="#E5484D"/><path d="M724 566L742 561L760 566L742 571Z" fill="#8A5A2B" opacity=".7"/>'
               '<text x="742" y="545" font-size="11" font-weight="800" text-anchor="middle" fill="#8A5A2B" font-family="sans-serif">N</text>')
    boat = ('<path d="M762 506h28l-5 9h-18z" fill="#B97855" stroke="#8A5A3B" stroke-width="1.5"/><path d="M776 478V506" stroke="#6B4423" stroke-width="2"/>'
            '<path d="M778 480L792 502H778z" fill="#fff" stroke="#C7D3DA"/><path d="M774 484L764 502H774z" fill="#FFD84D"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MAP_W} {MAP_H}" preserveAspectRatio="none">'
        '<defs><linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D7F0FA"/><stop offset="1" stop-color="#BCE1F2"/></linearGradient></defs>'
        f'<rect width="{MAP_W}" height="{MAP_H}" fill="url(#w)"/>{waves}'
        f'<path d="{island}" fill="none" stroke="#EAF8FD" stroke-width="26" stroke-linejoin="round" opacity=".7"/>'
        f'<path d="{island}" transform="translate(0 7)" fill="#8FC3DA" opacity=".55"/>'
        f'<path d="{island}" fill="#F2DFA8" stroke="#E2C98A" stroke-width="4"/>'
        f'<g transform="translate(400 310) scale(.93) translate(-400 -310)"><path d="{island}" fill="#86C06A"/>'
        '<clipPath id="isl"><path d="' + island + '"/></clipPath><g clip-path="url(#isl)">'
        '<ellipse cx="250" cy="150" rx="210" ry="86" fill="#A9D98E" opacity=".65"/>'
        '<ellipse cx="610" cy="470" rx="170" ry="70" fill="#9ACF7E" opacity=".55"/>'
        '<ellipse cx="150" cy="330" rx="90" ry="40" fill="#7DB862" opacity=".35"/></g></g>'
        f'{tuft_svg}{flower_svg}'
        f'<path d="{river}" fill="none" stroke="#6DB6DA" stroke-width="42" stroke-linecap="round"/>'
        f'<path d="{river}" fill="none" stroke="#8ECDEB" stroke-width="34" stroke-linecap="round"/>'
        f'<path d="{river}" fill="none" stroke="#B9E3F5" stroke-width="20" stroke-linecap="round"/>'
        f'<path d="{river}" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="14 24" opacity=".7"/>{reeds}'
        f'<path d="{road_d}" stroke="#D9C58E" stroke-width="17" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
        f'<path d="{road_d}" stroke="#F7ECCB" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
        f'<path d="{road_d}" stroke="#E2C98A" stroke-width="2" stroke-dasharray="8 9" fill="none"/>'
        + "".join(_bridge(x) for x in _BRIDGE_X) + pond + plaza +
        f'<rect x="388" y="486" width="120" height="52" rx="8" fill="#DDD9CE" stroke="#B5B0A0" stroke-width="3"/>{lot_lines}{cars}'
        f'<path d="M735 92L735 262" stroke="#8A8F94" stroke-width="7" fill="none"/>{sleepers}'
        '<path d="M732 92V262M738 92V262" stroke="#C9CDD1" stroke-width="1.5"/>'
        f'{station}{train}'
        '<path d="M720 178V164" stroke="#6B4423" stroke-width="2"/><circle cx="720" cy="162" r="3.5" fill="#E5484D"/><circle cx="720" cy="170" r="3.5" fill="#F2B134"/>'
        f'{houses}{school}{apt}{garden}{tree_svg}{compass}{boat}</svg>'
    )


@lru_cache(maxsize=1)
def _svg_b64():
    return base64.b64encode(_svg().encode("utf-8")).decode("ascii")


def city_map_css():
    return (
        "<style>"
        ".cmap{position:relative;width:100%;max-width:820px;margin-inline:auto;aspect-ratio:4/3;border-radius:22px;overflow:hidden;border:2px solid #CDE3EE;background:#CFEAF6;margin:2px auto 6px;}"
        ".cmap-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:fill!important;display:block;margin:0!important;max-width:none!important;max-height:none!important;height:100%!important;width:100%!important;}"
        ".cmap .dlabel{position:absolute;transform:translate(-50%,-50%);font-size:.82rem;font-weight:900;color:#2F4A2E;"
        "background:rgba(255,255,255,.72);border-radius:999px;padding:1px 10px;white-space:nowrap;letter-spacing:-.02em;}"
        ".cmap .cpin{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:2px;}"
        ".cmap .cpin i{position:relative;font-style:normal;width:34px;height:34px;border-radius:50%;background:#fff;border:2.5px solid #8A5A2B;"
        "display:flex;align-items:center;justify-content:center;font-size:1.05rem;line-height:1;box-shadow:0 3px 0 rgba(60,40,10,.25);}"
        ".cmap .cpin b{font-size:.74rem;font-weight:800;color:#24443B;background:rgba(255,255,255,.93);border-radius:8px;padding:1px 6px;"
        "white-space:nowrap;line-height:1.35;box-shadow:0 1px 2px rgba(0,0,0,.12);}"
        # 도장 받은 장소: 금빛 테두리 + 빨간 체크 배지 (눈에 확 띄게)
        ".cmap .cpin.on{z-index:2;}"
        ".cmap .cpin.on i{border-color:#E0A100;background:#FFF3C4;box-shadow:0 0 0 4px rgba(245,179,1,.5),0 3px 0 rgba(60,40,10,.25);}"
        ".cmap .cpin.on i::after{content:'✓';position:absolute;right:-12px;top:-12px;width:21px;height:21px;border-radius:50%;"
        "background:#D92D20;color:#fff;border:2px solid #fff;font-size:.8rem;font-weight:900;font-style:normal;"
        "display:flex;align-items:center;justify-content:center;box-shadow:0 2px 5px rgba(0,0,0,.4);}"
        ".cmap .cpin.on b{background:#FFF3C4;color:#7A4B00;box-shadow:0 0 0 1.5px #E0A100;}"
        ".cmap-legend{display:none;}"
        "@media (max-width:640px){"
        ".cmap{aspect-ratio:4/3;}"
        ".cmap .cpin b{display:none;}"
        ".cmap .cpin i{width:30px;height:30px;font-size:.95rem;}"
        ".cmap .cpin.on i{box-shadow:0 0 0 3px rgba(245,179,1,.5),0 2px 0 rgba(60,40,10,.25);}"
        ".cmap .cpin.on i::after{width:16px;height:16px;right:-7px;top:-8px;font-size:.62rem;border-width:1.5px;}"
        ".cmap .dlabel{font-size:.62rem;padding:1px 6px;}"
        ".cmap .dlabel em{display:none;}"
        ".cmap-legend{display:grid;}"
        "}"
        "</style>"
    )


def city_map_html(got, places):
    """got: 도장을 받은 장소 번호 모음, places: app.py의 PLACES(번호 -> (아이콘, 동네, 장소, 소개))."""
    parts = [f'<div class="cmap" role="img" aria-label="도토리시 지도"><img class="cmap-bg" alt="" src="data:image/svg+xml;base64,{_svg_b64()}">']
    for name, (x, y, icon) in MAP_TOWNS.items():
        parts.append(f'<span class="dlabel" style="left:{x}%;top:{y}%;"><em style="font-style:normal;">{icon} </em>{html.escape(name)}</span>')
    for number, (x, y, short) in MAP_PINS.items():
        if number not in places:
            continue
        icon, town, place, _ = places[number]
        on = " on" if number in got else ""
        tip = html.escape(f"{town} · {place}")
        parts.append(
            f'<span class="cpin{on}" style="left:{x}%;top:{y}%;" title="{tip}"><i>{html.escape(icon)}</i><b>{html.escape(short)}</b></span>')
    parts.append("</div>")
    return "".join(parts)
