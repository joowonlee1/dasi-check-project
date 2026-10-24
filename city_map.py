"""도토리시 지도: 섬 모양 지형(강·광장·철길·길) 위에 장소 핀을 제 위치에 찍어 보여 줘요.

그림(지형)은 SVG를 파이썬으로 만들어 <img> 하나로 넣고, 핀과 동네 이름은 HTML로 위에 얹어요.
그래서 화면 폭이 달라져도 핀이 같은 자리에 있고, 글씨는 항상 또렷해요. (Streamlit이 없어도 동작해요.)
"""
import base64
import html
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
    "13": (78, 82, "통계청"),
}

# 동네 이름표: 동네 이름 -> (가로 %, 세로 %, 아이콘)
MAP_TOWNS = {
    "상수리동": (16, 12, "🌳"),
    "떡갈나무동": (37, 12, "🍂"),
    "개암골": (60, 12, "🌰"),
    "도토리역 앞": (83, 12, "🚉"),
    "다람쥐동": (18, 58, "🐿️"),
    "중앙동": (45, 58, "⛲"),
    "시청로": (78, 56, "🏛️"),
}


def _river_y(x):
    """강 가운데선의 대략적인 높이(나무를 강 위에 심지 않으려고 써요)."""
    import math
    return 295 + 22 * math.sin(x / 95.0)


def _svg():
    island = ("M 95,112 C 70,62 200,42 330,52 C 450,32 600,36 700,82 C 772,112 778,200 762,282 "
              "C 790,382 742,520 640,552 C 520,590 380,566 260,574 C 140,586 50,526 60,424 "
              "C 30,332 112,302 72,232 C 50,180 102,160 95,112 Z")
    pins = [(x * MAP_W / 100, y * MAP_H / 100) for x, y, _ in MAP_PINS.values()]
    rnd = random.Random(7)
    trees = []
    tries = 0
    while len(trees) < 46 and tries < 4000:
        tries += 1
        x, y = rnd.uniform(90, 750), rnd.uniform(75, 545)
        # 섬 안쪽(타원 근사)만, 핀·강·광장·길과 겹치지 않게
        if ((x - 410) / 330) ** 2 + ((y - 310) / 245) ** 2 > 0.86:
            continue
        if any(abs(x - px) < 62 and abs(y - py) < 52 for px, py in pins):
            continue
        if abs(y - _river_y(x)) < 34:
            continue
        if ((x - 360) / 95) ** 2 + ((y - 414) / 62) ** 2 < 1:
            continue
        if 540 < x < 780 and 420 < y < 456:
            continue
        if 722 < x < 750 and 90 < y < 260:
            continue
        if any(abs(x - tx) < 24 and abs(y - ty) < 24 for tx, ty, _ in trees):
            continue
        trees.append((x, y, rnd.choice((8, 9, 10, 11))))
    tree_svg = "".join(
        f'<circle cx="{x:.0f}" cy="{y + 3:.0f}" r="{r}" fill="#3F7F3B" opacity=".55"/>'
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#5FA050"/>'
        f'<circle cx="{x - 3:.0f}" cy="{y - 3:.0f}" r="{r * 0.4:.1f}" fill="#8CCB74" opacity=".8"/>'
        for x, y, r in trees)
    waves = "".join(
        f'<path d="M {x},{y} q 12,-8 24,0 t 24,0" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".55"/>'
        for x, y in ((18, 40), (700, 24), (24, 560), (726, 574), (410, 18), (150, 592), (580, 590), (30, 200), (770, 430)))
    river = "M -10,300 C 110,270 160,330 250,300 S 380,252 470,288 S 600,332 690,288 S 770,262 810,276"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MAP_W} {MAP_H}" preserveAspectRatio="none">'
        f'<rect width="{MAP_W}" height="{MAP_H}" fill="#CFEAF6"/>{waves}'
        f'<path d="{island}" fill="#F2DFA8" stroke="#E2C98A" stroke-width="4"/>'
        f'<g transform="translate(400 310) scale(.93) translate(-400 -310)">'
        f'<path d="{island}" fill="#86C06A"/>'
        f'<ellipse cx="250" cy="150" rx="210" ry="86" fill="#A9D98E" opacity=".65"/>'
        f'<ellipse cx="610" cy="470" rx="170" ry="70" fill="#9ACF7E" opacity=".55"/></g>'
        f'<path d="{river}" fill="none" stroke="#8ECDEB" stroke-width="34" stroke-linecap="round"/>'
        f'<path d="{river}" fill="none" stroke="#B9E3F5" stroke-width="20" stroke-linecap="round"/>'
        f'<ellipse cx="520" cy="96" rx="38" ry="18" fill="#B9E3F5" stroke="#8ECDEB" stroke-width="5"/>'
        f'<g fill="#C99A5B" stroke="#8A5A2B" stroke-width="3">'
        f'<rect x="236" y="282" width="30" height="36" rx="4" transform="rotate(-8 251 300)"/>'
        f'<rect x="456" y="268" width="30" height="40" rx="4" transform="rotate(10 471 288)"/></g>'
        f'<path d="M 735,92 L 735,262" stroke="#8A8F94" stroke-width="7" fill="none"/>'
        f'<path d="M 735,92 L 735,262" stroke="#F4F4F2" stroke-width="3" stroke-dasharray="6 8" fill="none"/>'
        f'<path d="M 560,438 L 700,438" stroke="#F6EBC8" stroke-width="22" stroke-linecap="round" fill="none"/>'
        f'<path d="M 566,438 L 694,438" stroke="#E2C98A" stroke-width="3" stroke-dasharray="10 10" fill="none"/>'
        f'<ellipse cx="360" cy="414" rx="70" ry="42" fill="#F0E3B8" stroke="#E2C98A" stroke-width="4"/>'
        f'<circle cx="360" cy="414" r="13" fill="#B9E3F5" stroke="#8ECDEB" stroke-width="4"/>'
        f'<g fill="none" stroke="#F5E9C7" stroke-width="12" stroke-linecap="round">'
        '<path d="M130 185H660 M160 185V255 M300 175V280 M480 175V265 M650 185V250"/>'
        '<path d="M160 390V480H625V370 M160 430H650 M360 350V500 M480 340V490"/></g>'
        '<g fill="#FFF5DD" stroke="#A8865D" stroke-width="2">'
        '<path d="M180 135h28v26h-28z M340 130h32v28h-32z M570 135h30v26h-30z"/>'
        '<path d="M210 365h30v24h-30z M430 460h30v24h-30z M580 365h30v24h-30z"/></g>'
        '<g fill="#B97855"><path d="M176 135l18-16 18 16z M336 130l20-16 20 16z M566 135l19-15 19 15z"/>'
        '<path d="M206 365l19-15 19 15z M426 460l19-15 19 15z M576 365l19-15 19 15z"/></g>'
        f'{tree_svg}</svg>' 
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
        ".cmap .cpin.on i{border-color:#B42318;background:#FFF8E6;}"
        ".cmap .cpin.on i::after{content:\"🏅\";position:absolute;right:-9px;top:-11px;font-size:.8rem;}"
        ".cmap-legend{display:none;}"
        "@media (max-width:640px){"
        ".cmap{aspect-ratio:4/3;}"
        ".cmap .cpin b{display:none;}"
        ".cmap .cpin i{width:30px;height:30px;font-size:.95rem;}"
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
