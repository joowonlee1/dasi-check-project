from play_ui import intro, bridge
from notice_inquiry import DATA as INQUIRY
"""안내서 3건의 주장과 별도 공식 확인 결과를 대조하는 교육용 가상 활동."""
import streamlit as st
import dotori_data as dd
from card_ui import show_result_card
from sound_effects import queue_effect
from mascot_ui import show_key_question, mascot_img

KEY = "notice_verify_v3"
CASES = [
 {"door":"101호", "claim":"오늘 14:25 등기 방문. 부재중이어서 내일 다시 방문합니다.",
  "looks":"종이가 구겨지고 테이프로 붙어 있어요.", "reference":"A-102",
  "official":"별도로 연 도토리 우체국 공식 조회에서 A-102의 수취 주소가 101호이고, 오늘 14:25 부재중 방문과 다음 날 재방문이 기록돼 있어요. 공식 고객센터도 이 안내 내용을 확인했어요.",
  "answer":"안내 내용 정상 확인",
  "reason":"수취 주소·방문 시각·후속 절차가 별도로 확인한 기록과 일치한다.",
  "options":["종이가 구겨졌지만 기관 로고가 있으므로 정상이다.","수취 주소·방문 시각·후속 절차가 별도로 확인한 기록과 일치한다.","실제 우편물이 하나라도 있으면 모든 추가 요구가 안전하다."],
  "lesson":"종이 상태만으로 위조라고 단정하지 않아요. 이 사례에서는 안내 내용까지 공식 경로로 따로 확인했기 때문에 정상으로 판단했어요."},
 {"door":"102호", "claim":"등기가 도착했습니다. 재배달하려면 이 QR에서 계정 비밀번호와 문자 인증번호를 입력하세요.",
  "looks":"깨끗한 종이이며 흔적 없이 떨어져요. 실제 등기번호가 적혀 있어요.", "reference":"A-205",
  "official":"별도로 연 공식 조회에 A-205 등기는 실제로 있어요. 하지만 공식 고객센터는 해당 QR과 비밀번호·인증번호 입력 요구를 자신들이 보낸 것이 아니라고 확인했어요. 정식 재배달 절차도 따로 안내했어요.",
  "answer":"안내 내용 위조 확인",
  "reason":"실제 등기는 있지만, 기관이 이 안내의 추가 요구를 명시적으로 부인했다.",
  "options":["종이가 깨끗하고 접착 흔적이 없으므로 정상이다.","실제 등기는 있지만, 기관이 이 안내의 추가 요구를 명시적으로 부인했다.","등기번호가 조회되므로 QR의 목적지도 검증됐다."],
  "lesson":"실제 등기번호를 베껴 쓸 수도 있어요. 우편물 존재와 안내서의 추가 요구가 정당한지는 별도로 확인해야 해요."},
 {"door":"103호", "claim":"오늘 등기 방문. 부재중이므로 연락 바랍니다.",
  "looks":"접착 흔적이 남아 있어요. 사진에서는 방문 시각 일부가 흐려요.", "reference":"A-309",
  "official":"공식 조회 시스템이 점검 중이라 기록을 확인할 수 없어요. 별도로 연락한 공식 고객센터도 지금은 방문 여부를 확정하지 못했고, 복구 후 재확인하거나 창구에서 확인하도록 안내했어요.",
  "answer":"판단 보류",
  "reason":"조회 실패는 위조 증거가 아니며, 현재 확인된 정보만으로는 결론을 낼 수 없다.",
  "options":["조회되지 않으니 무조건 위조다.","접착 흔적이 있으므로 위조가 확정됐다.","조회 실패는 위조 증거가 아니며, 현재 확인된 정보만으로는 결론을 낼 수 없다."],
  "lesson":"모르는 것을 안다고 단정하지 않는 것도 판단이에요. 안내서 속 경로로 이동하지 말고 내가 직접 찾은 공식 경로에서 따로 다시 확인해요."}
]
ROUTES = ["안내서에 적힌 번호나 QR로 확인", "안내서와 별도로 찾은 공식 홈페이지·고객센터에서 확인"]
VERDICTS = ["안내 내용 정상 확인","안내 내용 위조 확인","판단 보류"]
def fresh():
    return {"i":0,"checks":{},"answers":{},"recorded":False,"done":False,"attempts":{}}
S=st.session_state.setdefault(KEY,fresh())
with intro("14", suffix=""):
    st.title("📬 가짜 안내서 감별소")
    show_key_question("안내서의 주장과 **별도로 확인한 기록**을 대조해요. 근거가 부족하면 **판단을 보류**할 수 있어요.","📬")
    # 이 게임은 시작 이야기가 없어서 짧은 이야기 상자를 넣었어요.
    st.markdown(
        '<div style="display:flex;gap:12px;align-items:flex-start;background:#FFF8E7;border:2.5px solid #F1C96B;'
        'border-radius:16px;padding:12px 16px;margin:.4rem 0 .8rem;line-height:1.7;word-break:keep-all">'
        '<span style="font-size:1.8rem;line-height:1">📖</span><div><b style="color:#8A5A00;font-size:1.05rem">이야기</b><br>'
        '다람쥐아파트 101·102·103호 문에 등기 안내서가 붙었어요. 진짜 안내도, 가짜 안내도, 아직 알 수 없는 안내도 있어요. '
        '공식 경로로 직접 확인한 기록과 대조해 ‘정상·위조·판단 보류’ 중 하나로 감별해 주세요.</div></div>',
        unsafe_allow_html=True)
    # 시작 전 설명: 안내서에 무엇이 적혀 있고, 무엇으로 확인하고, 어떻게 판정하는지 미리 알려 줘요.
    st.markdown("""<div style="border:2.5px solid #C7D2FE;background:#F5F7FF;border-radius:16px;padding:14px 16px;margin:.2rem 0 .8rem;line-height:1.7;word-break:keep-all">
<b style="font-size:1.1rem;color:#1E3A8A">🧭 시작하기 전에 · 이렇게 감별해요</b>
<div class="nv-how" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px">
<div style="background:#fff;border-radius:12px;padding:10px 12px;border:1.5px solid #E0E7FF"><b>① 안내서 읽기</b><br>
<b>🔖 참조번호</b>는 안내서에 적힌 <b>등기번호</b>예요. 공식 조회에서 이 번호로 우편물을 찾아 <b>주소·방문 시각이 안내서와 같은지</b> 맞춰 봐요.<br>
<b>👀 겉모습</b>(구겨짐·테이프·흐린 글씨)은 참고만 해요. 겉모습만으로는 진짜·가짜를 정할 수 없어요.</div>
<div style="background:#fff;border-radius:12px;padding:10px 12px;border:1.5px solid #E0E7FF"><b>② 확인 경로 고르기</b><br>
안내서에 적힌 <b>번호·QR</b>로 물어보면, 안내서를 만든 사람에게 묻는 셈이라 확인이 안 돼요.<br>
<b>안내서와 상관없이 내가 직접 찾은 공식 홈페이지·고객센터</b>로 확인해야 기록으로 인정돼요.</div>
<div style="background:#fff;border-radius:12px;padding:10px 12px;border:1.5px solid #E0E7FF"><b>③ 확인 기록 모으기</b><br>
📦 <b>등기 조회</b>: 그 번호의 우편물이 진짜 있는지, 주소·시각이 맞는지<br>
📞 <b>정식 절차</b>: 안내서가 시킨 일(QR 입력 등)을 기관이 정말 요구하는지<br>
🕒 <b>조회 범위</b>: 조회가 제대로 끝났는지, 최신 기록인지</div>
<div style="background:#fff;border-radius:12px;padding:10px 12px;border:1.5px solid #E0E7FF"><b>④ 판정 도장 찍기</b><br>
<b style="color:#15803D">정상 확인</b> · 기록이 안내서와 모두 맞아요<br>
<b style="color:#B91C1C">위조</b> · 기관이 안내서의 요구를 부인했어요 (우편물이 진짜 있어도 위조일 수 있어요!)<br>
<b style="color:#B45309">판단 보류</b> · 조회가 안 돼서 아직 알 수 없어요<br>
판정·이유·근거 기록·다음 행동을 함께 골라 제출해요.</div>
</div>
<style>@media (max-width:1100px){.nv-how{grid-template-columns:repeat(2,1fr)!important}}@media (max-width:640px){.nv-how{grid-template-columns:1fr!important}}</style>
<div style="margin-top:8px;font-size:.95rem;color:#374151">🚪 101호 → 102호 → 103호, 안내서 3장을 차례로 감별해요. <b>처음 제출에서 맞힌 개수</b>가 점수예요. 필요한 기록을 다 모은 뒤에 제출하세요.</div>
</div>""", unsafe_allow_html=True)
    st.caption("모든 기관·등기번호·응답은 교육용 가상 자료예요. 실제 웹사이트 접속이나 전화 연결은 하지 않아요.")


# ───────── 그림으로 보여 주기(판정 로직은 그대로) ─────────
from html import escape as _esc

STAMP = {"안내 내용 정상 확인": ("정상 확인", "#15803D"), "안내 내용 위조 확인": ("위조", "#B91C1C"), "판단 보류": ("판단 보류", "#B45309")}
Q_ICON = {"delivery": "📦", "procedure": "📞", "status": "🕒", "surface": "🔍", "printed": "☎️"}
# 안내서 종이 모양: 겉모습 설명에 맞춰 1번은 구겨지고 테이프, 2번은 깨끗하고 QR, 3번은 접착 흔적과 흐린 시각
PAPER = [
    {"rot": -2.5, "bg": "repeating-linear-gradient(115deg,#FFFDF6 0 22px,#F3EEDF 22px 24px,#FFFDF6 24px 47px)", "tape": True, "qr": False, "blur": False},
    {"rot": 0, "bg": "#FFFFFF", "tape": False, "qr": True, "blur": False},
    {"rot": 1.5, "bg": "#FFFCF2", "tape": False, "qr": False, "blur": True},
]
NV_CSS = """<style>
@keyframes nv-stamp{0%{transform:scale(2.4) rotate(-20deg);opacity:0}60%{transform:scale(.92) rotate(-12deg);opacity:1}100%{transform:scale(1) rotate(-12deg);opacity:1}}
@keyframes nv-in{from{transform:translateY(-10px);opacity:0}to{transform:none;opacity:1}}
.nv-doors{display:flex;gap:10px;margin:.3rem 0 .8rem}
.nv-doors div{flex:1;text-align:center;border-radius:12px;padding:8px 4px;font-weight:800;border:2px solid #E5E7EB;background:#F9FAFB;color:#6B7280}
.nv-doors .now{border-color:#B45309;background:#FFF7ED;color:#9A3412}.nv-doors .ok{border-color:#16A34A;background:#F0FDF4;color:#166534}
.nv-scene{display:flex;justify-content:center;align-items:flex-end;gap:22px;flex-wrap:wrap;background:linear-gradient(#EDE7DB,#E2D9C8);border-radius:18px;padding:18px 14px 0;margin-bottom:.6rem}.nv-clues{flex:1 1 280px;max-width:420px;align-self:center;margin:0 0 16px;display:flex;flex-direction:column;gap:10px}.nv-clues .t{font-weight:900;color:#374151;font-size:1.05rem}.nv-clue{border-radius:12px;padding:10px 14px;font-size:1.02rem;line-height:1.6;box-shadow:0 3px 8px #0002}@media (max-width:640px){.nv-clues{max-width:none;margin-bottom:12px}}
.nv-doorwrap{display:flex;flex-direction:column;align-items:center;width:min(100%,440px)}.nv-door{position:relative;width:100%;box-sizing:border-box;background:linear-gradient(90deg,#7B5134,#9C6A43 45%,#8A5C3B);border:12px solid #4A2F1D;border-bottom:0;border-radius:8px 8px 0 0;padding:14px 44px 18px 18px;box-shadow:inset 0 0 0 3px #5C3A23,0 6px 0 #3B2516}.nv-peep{position:absolute;top:12px;left:50%;transform:translateX(-50%);width:14px;height:14px;border-radius:50%;background:radial-gradient(#1F2937 35%,#C9A227 40%,#8B6B14 70%);box-shadow:0 1px 2px #0006}.nv-panel{border:3px solid #6B4429;border-radius:6px;box-shadow:inset 2px 2px 0 #B07D52,inset -2px -2px 0 #5A3920;padding:12px}.nv-panel.low{height:64px;margin-top:14px;background:linear-gradient(#8F603E,#7E5336)}.nv-handle{position:absolute;right:-4px;top:58%;width:44px;height:12px;border-radius:8px;background:linear-gradient(#F7D774,#B8860B);box-shadow:0 2px 3px #0005}.nv-handle::before{content:'';position:absolute;right:30px;top:-8px;width:22px;height:28px;border-radius:6px;background:linear-gradient(#E5C158,#A47A0E)}.nv-mat{width:78%;height:26px;margin-top:0;background:repeating-linear-gradient(90deg,#9B7B4E 0 6px,#8A6A40 6px 12px);border-radius:4px;color:#F5E6C8;font-weight:900;font-size:.8rem;letter-spacing:.2em;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 6px #0003}
.nv-plate{display:table;margin:14px auto 10px;background:linear-gradient(#F9E7B5,#D9B45A);color:#4A3420;font-weight:900;border-radius:6px;padding:3px 14px;box-shadow:0 2px 0 #0004;border:1px solid #A6802B}

.nv-paper{position:relative;color:#1F2937;border-radius:4px;padding:16px 16px 14px;box-shadow:0 6px 14px #0004;line-height:1.65;animation:nv-in .4s ease-out both}
.nv-paper h4{margin:0 0 6px;font-size:1.05rem;letter-spacing:.04em}
.nv-tape{position:absolute;top:-10px;width:70px;height:22px;background:#F4E7A9cc;border:1px solid #E2CF7A}
.nv-qr{display:grid;grid-template-columns:repeat(7,8px);gap:1px;margin-top:8px}.nv-qr i{width:8px;height:8px;background:#111}.nv-qr i.o{background:#fff}
.nv-stamp{position:absolute;right:10px;bottom:10px;border:4px solid currentColor;border-radius:10px;padding:4px 12px;font-weight:900;font-size:1.3rem;background:#ffffffcc;animation:nv-stamp .5s ease-out both}
.nv-rec{border-radius:14px;padding:10px 14px;margin:0 0 10px;border:2px solid;line-height:1.6}
.nv-rec b{display:block}.nv-rec small{font-weight:800;border-radius:999px;padding:1px 8px;margin-left:6px}
</style>"""

def _go_door(k):
    S["i"] = k

def door_strip(i):
    """문 3개를 버튼으로: 감별을 마친 문과 지금 문은 눌러서 오갈 수 있고, 아직 차례가 아닌 문은 잠겨 있어요."""
    reach = len(S["answers"])  # 지금까지 맞힌 수 = 새로 열 수 있는 문 번호
    st.markdown('<style>.st-key-nv_doors button{min-height:50px!important;border-radius:12px!important}'
                '.st-key-nv_doors button p{font-weight:900!important;font-size:1.02rem!important}</style>', unsafe_allow_html=True)
    with st.container(key="nv_doors"):
        cols = st.columns(len(CASES))
        for k, (col, c) in enumerate(zip(cols, CASES)):
            if k in S["answers"]:
                label = f"✅ {c['door']} · 감별 완료"
            elif k == i:
                label = f"🔍 {c['door']} · 감별 중"
            elif k <= reach:
                label = f"🚪 {c['door']}"
            else:
                label = f"🔒 {c['door']}"
            col.button(label, key=f"nv_door_{k}", width="stretch", type="primary" if k == i else "secondary",
                       disabled=k > reach, on_click=_go_door, args=(k,),
                       help=None if k <= reach else "앞 안내서를 감별하면 열려요.")
    if reach < len(CASES) - 1:
        st.caption("🔒 잠긴 문은 앞 안내서를 감별하면 열려요. 감별을 마친 문은 다시 눌러 볼 수 있어요.")

def door_scene(i, stamp=None, clues=False, say=None):
    case, look = CASES[i], PAPER[i]
    claim = _esc(case["claim"])
    extra = ""
    if look["blur"]:
        extra += '<div>방문 시각: <span style="filter:blur(3.5px)">14:25</span> <small style="color:#92400E">(사진에서 흐려요)</small></div>'
    if look["qr"]:
        pattern = "1111111100000110111011011101101110110000011111111"
        extra += '<div class="nv-qr">' + "".join(f'<i class="{"" if b == "1" else "o"}"></i>' for b in pattern) + "</div>"
    tape = ('<span class="nv-tape" style="left:10px;transform:rotate(-8deg)"></span>'
            '<span class="nv-tape" style="right:10px;transform:rotate(7deg)"></span>') if look["tape"] else ""
    if look["blur"]:
        tape = '<span class="nv-tape" style="left:40%;background:#00000010;border:1px dashed #9CA3AF"></span>'
    stamp_html = ""
    if stamp:
        label, color = STAMP[stamp]
        stamp_html = f'<span class="nv-stamp" style="color:{color}">{label}</span>'
    st.markdown(
        f'<div class="nv-scene"><div class="nv-doorwrap"><div class="nv-door"><span class="nv-peep"></span><span class="nv-plate">🏠 {case["door"]}</span>'
        f'<div class="nv-panel"><div class="nv-paper" style="transform:rotate({look["rot"]}deg);background:{look["bg"]}">{tape}'
        f'<h4>📮 등기 우편물 안내</h4><div>{claim}</div>{extra}'
        f'<div style="margin-top:6px;font-size:.9rem;color:#6B7280">참조번호 {case["reference"]}</div>{stamp_html}</div></div>'
        '<div class="nv-panel low"></div><span class="nv-handle"></span></div><div class="nv-mat">다람쥐아파트</div></div>'
        + (('<div class="nv-clues"><div class="t">🔎 안내서에서 보이는 단서</div>'
            f'<div class="nv-clue" style="background:#FFE08A;color:#6B4300"><b>🔖 참조번호(등기번호)</b><br>{case["reference"]}</div>'
            f'<div class="nv-clue" style="background:#EEF4FF;color:#1F3A68"><b>👀 겉모습</b><br>{_esc(case["looks"])}</div>'
            + (kkangji_say(say[0], say[1], 120) if say else '') + '</div>') if clues else '')
        + '</div>',
        unsafe_allow_html=True)

def record_card(q, text):
    official = q in ("delivery", "procedure", "status")
    color, bg, tag = ("#16A34A", "#F0FDF4", "공식 경로로 확인") if official else ("#9CA3AF", "#F9FAFB", "참고만 · 진위 확인 아님")
    st.markdown(
        f'<div class="nv-rec" style="border-color:{color};background:{bg}"><b>{Q_ICON.get(q, "📄")} {_esc(INQUIRY["questions"][q])}'
        f'<small style="background:{color};color:#fff">{tag}</small></b>{_esc(text)}</div>', unsafe_allow_html=True)


# ───────── 깡지와 함께: 말풍선 · 폰 화면 · 큰 창 ─────────
def kkangji_say(pose, text, width=110):
    """깡지가 말풍선으로 안내해요."""
    return (f'<div style="display:flex;align-items:center;gap:10px"><div style="flex:0 0 {int(width)}px">{mascot_img(pose, width)}</div>'
            f'<div style="flex:1;position:relative;background:#fff;border:2.5px solid #F1C96B;border-radius:16px;padding:10px 14px;'
            f'font-weight:800;color:#5B4300;line-height:1.55;word-break:keep-all;box-shadow:0 3px 8px #0001">{text}</div></div>')

def phone_screen(app, color, body_html, sub=""):
    """작은 휴대폰 화면 모양(공식 앱·통화 화면)."""
    return (f'<div style="width:100%;max-width:340px;margin:0 auto 14px;background:#111827;border-radius:38px;padding:12px;box-shadow:0 14px 30px #0005">'
            f'<div style="background:#F8FAFC;border-radius:28px;overflow:hidden">'
            f'<div style="height:22px;display:flex;justify-content:center;align-items:center"><span style="width:90px;height:6px;border-radius:9px;background:#CBD5E1"></span></div>'
            f'<div style="background:{color};color:#fff;padding:12px 16px;font-weight:900;font-size:1.05rem">{app}'
            + (f'<div style="font-size:.82rem;font-weight:700;opacity:.9">{sub}</div>' if sub else "") + '</div>'
            f'<div style="padding:14px 16px 18px;font-size:1.02rem;line-height:1.7;color:#111827;min-height:120px">{body_html}</div></div></div>')

TOOL_VIEW = {
    # q: (제목, 깡지 자세, 깡지 한마디, 화면 종류)
    "delivery": ("📱 도토리 우체국 공식 앱 · 등기 조회", "app", "내가 직접 연 공식 앱이야. 번호·주소·시각이 안내서와 같은지 봐!", "app"),
    "procedure": ("📞 도토리 우체국 고객센터", "headset", "공식 고객센터에 안내서의 요구가 진짜인지 물어봤어.", "call"),
    "status": ("🖥️ 공식 조회 · 조회 상태", "think", "조회가 끝까지 됐는지, 최신 기록인지도 꼭 봐야 해.", "app"),
    "printed": ("☎️ 안내서에 적힌 번호", "suspicious", "음… 이 번호는 안내서를 만든 사람이 받을 수도 있어. 참고만 하자.", "call"),
    "surface": ("🔍 돋보기로 살펴보기", "detective", "겉모습은 단서일 뿐, 진짜·가짜를 정해 주지는 않아.", "lens"),
}

@st.dialog("🧰 조사 결과", width="medium")
def tool_popup(i, kind, q):
    if kind == "trap":
        st.markdown(kkangji_say("stop", "잠깐! 안내서에 있는 QR로 확인하면, 안내서를 만든 사람에게 묻는 셈이야!", 170), unsafe_allow_html=True)
        st.markdown('<div style="margin-top:10px;background:#FEF2F2;border:3px solid #FCA5A5;border-radius:16px;padding:14px 18px;font-size:1.1rem;line-height:1.7;font-weight:700;color:#7F1D1D">'
                    '🚫 확인 실패 · 이 방법으로는 안내서가 진짜인지 알 수 없어요.<br>'
                    '👉 <b>🏛️ 내가 직접 찾은 공식 경로</b>의 도구로 같은 내용을 확인해 보세요.</div>', unsafe_allow_html=True)
    elif kind == "blocked":
        st.markdown(kkangji_say("think", "고객센터에 묻기 전에, 먼저 공식 조회에서 이 등기번호부터 찾아보자!", 170), unsafe_allow_html=True)
        st.info("📦 ‘공식 조회에서 등기번호·주소·방문 시각 찾기’를 먼저 눌러 주세요. 어떤 우편물인지 알아야 절차를 물을 수 있어요.")
    else:
        title, pose, line, view = TOOL_VIEW[q]
        text = _esc(INQUIRY["responses"][i][q])
        left, right = st.columns([1.05, 1], vertical_alignment="center", gap="small")
        with left:
            if view == "app":
                body = f'<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:14px;padding:10px 12px">🔎 조회 결과<br><b>{text}</b></div>'
                st.markdown(phone_screen(title, "#0F766E", body, "내가 직접 찾아 연 공식 경로"), unsafe_allow_html=True)
            elif view == "call":
                official = q == "procedure"
                body = (f'<div style="text-align:center;font-size:2.4rem">{"🏤" if official else "❓"}</div>'
                        f'<div style="text-align:center;color:#64748B;font-weight:800;margin-bottom:8px">통화 중 · 0{2 if official else 1}:1{4 if official else 8}</div>'
                        f'<div style="background:#fff;border-radius:4px 14px 14px 14px;padding:10px 12px;box-shadow:0 1px 3px #0002">{text}</div>')
                st.markdown(phone_screen(title, "#1E3A8A" if official else "#9A3412", body,
                                         "공식 경로로 확인" if official else "⚠️ 안내서 속 번호 · 진위 확인 아님"), unsafe_allow_html=True)
            else:
                st.markdown('<div style="width:min(100%,330px);aspect-ratio:1;margin:0 auto;border-radius:50%;border:14px solid #475569;'
                            'background:repeating-linear-gradient(115deg,#FFFDF6 0 22px,#F3EEDF 22px 24px);display:flex;align-items:center;justify-content:center;'
                            f'padding:34px;box-shadow:0 10px 24px #0004;text-align:center;font-size:1.05rem;line-height:1.6;font-weight:700">{text}</div>', unsafe_allow_html=True)
        with right:
            st.markdown(f'<div style="text-align:center">{mascot_img(pose, 190)}</div>'
                        f'<div style="background:#fff;border:2.5px solid #F1C96B;border-radius:16px;padding:10px 14px;margin-top:8px;'
                        f'font-weight:800;color:#5B4300;line-height:1.55;word-break:keep-all">💬 {line}</div>'
                        '<div style="margin-top:8px;background:#ECFDF3;border:2px solid #86EFAC;border-radius:12px;padding:8px 12px;'
                        'font-weight:800;color:#166534">📁 확인 기록 보관함에 넣었어요.</div>', unsafe_allow_html=True)
    if st.button("확인했어요 ▶", type="primary", width="stretch", key=f"nv_popup_ok_{i}"):
        st.rerun()

@st.dialog("🔏 판정 도장 쾅!", width="medium")
def stamp_popup(i):
    case = CASES[i]
    label, color = STAMP[case["answer"]]
    left, right = st.columns([1, 1.3], vertical_alignment="center")
    with left:
        st.markdown(f'<div style="text-align:center"><span style="display:inline-block;border:6px solid {color};color:{color};border-radius:16px;'
                    f'padding:10px 22px;font-size:2rem;font-weight:900;transform:rotate(-10deg);background:#fff;animation:nv-stamp .5s ease-out both">{label}</span></div>'
                    "<style>@keyframes nv-stamp{0%{transform:scale(2.4) rotate(-20deg);opacity:0}60%{transform:scale(.92) rotate(-12deg);opacity:1}100%{transform:scale(1) rotate(-10deg);opacity:1}}</style>",
                    unsafe_allow_html=True)
        st.markdown(mascot_img("hold" if case["answer"]=="판단 보류" else "stamp", 210), unsafe_allow_html=True)
    with right:
        st.markdown(f'<div style="font-size:1.25rem;font-weight:900;color:{color};margin-bottom:6px">다람쥐아파트 {case["door"]} 감별 완료!</div>'
                    f'<div style="font-size:1.08rem;line-height:1.75">{_esc(case["lesson"])}</div>'
                    f'<div style="margin-top:8px;color:#52616B">판단 근거: {_esc(case["reason"])}</div>', unsafe_allow_html=True)
    if st.button("다음으로 ▶", type="primary", width="stretch", key=f"nv_stamp_ok_{i}"):
        st.rerun()

def _back_notice():
    # 바로 전 화면으로: 2·3번 안내서에서는 앞 안내서로, 1번 안내서에서는 처음 화면으로 돌아가요.
    if S["i"]>0:
        S["i"]-=1
    else:
        st.session_state[KEY]=fresh()

if not S["done"]:
    i=S["i"]; case=CASES[i]
    # 감별 중에도 바로 전 화면으로 돌아갈 수 있어요.
    st.button("← 이전 화면으로", on_click=_back_notice, key="nv_quit",
              help="앞 안내서로 돌아가요. 1번 안내서에서는 처음 화면으로 돌아가요.")
    st.markdown(NV_CSS, unsafe_allow_html=True)
    door_strip(i)
    st.markdown(f'<div style="font-size:1.3rem;font-weight:900;margin:14px 0 8px">{i+1}/3 · 다람쥐아파트 {case["door"]} 문 앞</div>', unsafe_allow_html=True)
    # 문에 붙은 안내서를 그림으로 보여 줘요. 판정을 맞히면 그 위에 도장이 찍혀요.
    _checked=S["checks"].get(i,{})
    if i in S["answers"]:
        _say=("hooray","도장 쾅! 위의 문 버튼으로 다음 문에 가 보자!")
    elif not _checked:
        _say=("letter","이 안내서, 진짜일까? 아래 🧰 도구로 하나씩 확인해 보자!")
    else:
        _say=("think",f"기록 {len(_checked)}개 모음! 필요한 걸 다 모았으면 도장을 찍어 봐.")
    door_scene(i, case["answer"] if i in S["answers"] else None, clues=True, say=_say)

    checked=S["checks"].setdefault(i,{})
    flash=S.setdefault("flash",{})
    st.markdown('<div style="font-size:1.3rem;font-weight:900;margin:22px 0 8px">🧰 조사 도구함 · 도구를 골라 사실을 확인하세요</div>', unsafe_allow_html=True)
    st.markdown('<style>[class*="st-key-nv_tool_"] button{min-height:64px!important;border-radius:14px!important;text-align:left!important;justify-content:flex-start!important}'
                '[class*="st-key-nv_tool_"] button p{font-size:1rem!important;font-weight:800!important;line-height:1.45!important}'
                '.nv-group{font-weight:900;border-radius:10px;padding:6px 12px;margin:6px 0 6px}</style>', unsafe_allow_html=True)

    def use_tool(kind, q):
        # 판정에 쓰는 기록(checked)은 원래와 똑같은 규칙으로 쌓여요.
        if kind=="trap":
            flash[i]="⚠️ 안내서에 적힌 QR·번호로는 안내서 자체를 검증할 수 없어요. 안내서를 만든 사람에게 묻는 셈이니까요. 내가 직접 찾은 공식 경로로 같은 질문을 확인하세요."
            S["popup"]=(i,"trap",q)
        elif q=="procedure" and "delivery" not in checked:
            flash[i]="📦 먼저 공식 조회에서 등기번호·주소·방문 시각을 확인해야, 그 우편물의 절차를 고객센터에 물을 수 있어요."
            S["popup"]=(i,"blocked",q)
        else:
            S["popup"]=(i,kind,q)
            checked[q]=INQUIRY["responses"][i][q]
            flash.pop(i,None)
            if kind=="official":
                queue_effect("clue")

    tools=[
        ("📮 안내서에 적힌 방법", "#FEF2F2", "#B91C1C", [
            ("trap","delivery","📷 안내서 QR로 등기 조회하기"),
            ("plain","printed","☎️ 안내서에 적힌 번호로 문의하기")]),
        ("🏛️ 내가 직접 찾은 공식 경로", "#F0FDF4", "#166534", [
            ("official","delivery","📦 공식 조회에서 등기번호·주소·방문 시각 찾기"),
            ("official","procedure","📞 공식 고객센터에 안내서의 요구가 맞는지 묻기"),
            ("official","status","🕒 조회가 끝까지 됐는지·최신 기록인지 보기")]),
        ("🔍 눈으로 살피기", "#F8FAFC", "#334155", [
            ("plain","surface","🔍 돋보기로 종이·접착 흔적 살피기")]),
    ]
    for gname, gbg, gfg, items in tools:
        st.markdown(f'<div class="nv-group" style="background:{gbg};color:{gfg}">{gname}</div>', unsafe_allow_html=True)
        cols=st.columns(len(items))
        for col,(kind,q,label) in zip(cols,items):
            done = q in checked and kind!="trap"
            with col.container(key=f"nv_tool_{i}_{kind}_{q}"):
                st.button(("✓ " if done else "")+label, key=f"nv_toolbtn_{i}_{kind}_{q}", width="stretch",
                          disabled=done or i in S["answers"], on_click=use_tool, args=(kind,q))
    if flash.get(i):
        st.warning(flash[i])
    if S.get("popup") and S["popup"][0]==i:
        _pi,_pk,_pq=S.pop("popup")
        tool_popup(_pi,_pk,_pq)
    st.markdown(f'<div style="font-size:1.3rem;font-weight:900;margin:22px 0 8px">📁 확인 기록 보관함 · {len(checked)}개</div>', unsafe_allow_html=True)
    if checked:
        for q,text in checked.items():
            record_card(q, text)
    else:
        st.caption("아직 모은 기록이 없어요. 위의 도구를 눌러 확인해 보세요.")
    st.markdown('<div style="font-size:1.3rem;font-weight:900;margin:22px 0 8px">🔏 판정 도장 찍기</div>', unsafe_allow_html=True)
    st.markdown('<style>.st-key-nv_judge [data-testid=stRadio] [role=radiogroup]{gap:8px!important}'
                '.st-key-nv_judge [data-testid=stRadio]:first-of-type [role=radiogroup] label{border:2px solid #D6DDE2;border-radius:12px;padding:8px 14px;background:#fff;font-weight:800}'
                '.st-key-nv_judge [data-testid=stRadio]:first-of-type [role=radiogroup] label:has(input:checked){border-color:#20483F;background:#EAF6F0}</style>',
                unsafe_allow_html=True)
    with st.container(key="nv_judge"), st.form(f"nv_answer_{i}"):
        verdict=st.radio("현재 근거로 내릴 수 있는 판단",VERDICTS,index=None,horizontal=True)
        reason=st.radio("판단 이유",case["options"],index=None)
        evidence=st.multiselect("판단을 직접 뒷받침하는 확인 기록",list(checked),format_func=INQUIRY["questions"].get,placeholder="먼저 필요한 자료를 확인하세요")
        action=st.radio("다음 행동",INQUIRY["actions"],index=None)
        submitted=st.form_submit_button("근거를 연결해 판단 제출",disabled=i in S["answers"])
    if submitted:
        if verdict is None or reason is None or action is None or not evidence:
            st.warning("판단·이유·근거·다음 행동을 모두 선택하세요.")
        else:
            S["attempts"][i]=S["attempts"].get(i,0)+1
            needed=set(INQUIRY["required"][i])
            ok=(verdict==case["answer"] and reason==case["reason"] and set(evidence)==needed and needed.issubset(checked) and action==INQUIRY["actions"][i])
            if ok:
                S["answers"][i]={"ok":True,"first":S["attempts"][i]==1}
                S["stamp_pop"]=i
                queue_effect("correct")
                st.rerun()
            else:
                queue_effect("notice")
                st.markdown(kkangji_say("retry","괜찮아, 다시 해 보자! 기록 보관함을 한 번 더 살펴봐.",130), unsafe_allow_html=True)
                st.warning("아직 자료와 결론이 충분히 연결되지 않았어요. 같은 번호·주소·시각인지, 조회가 완료됐는지, 추가 요구까지 확인했는지 다시 살펴보세요.")
    if S.get("stamp_pop")==i and not S.get("popup"):
        S.pop("stamp_pop")
        stamp_popup(i)
    if i in S["answers"]:
        label, color = STAMP[case["answer"]]
        st.markdown(f'<div style="border:3px solid {color};border-radius:16px;padding:14px 18px;background:#fff;line-height:1.7">'
                    f'<b style="color:{color};font-size:1.25rem">🔏 {label} 도장 쾅!</b><br>{_esc(case["lesson"])}<br>'
                    f'<span style="color:#52616B">판단 근거: {_esc(case["reason"])}</span></div>', unsafe_allow_html=True)
        if st.button("다음 안내서" if i<2 else "결과 보기",type="primary"):
            if i<2:S["i"]+=1
            else:S["done"]=True
            st.rerun()
else:
    score=sum(a.get("first",False) for a in S["answers"].values())
    if not S["recorded"]:
        stats_ok=dd.record("notice",{"v3_plays":1,"v3_perfect":int(score==3),
                      **{f"v3_h{i}_ok":int(S["answers"][i].get("first",False)) for i in range(3)}})
        S["hall"]=dd.save_hall("notice",{"score":score,"total":3,"probes":sum(len(v) for v in S["checks"].values()),"version":3},
            lambda old,new: new["score"]/new["total"]>old.get("score",0)/max(old.get("total",5),1))
        S["recorded"]=True
        dd.note_mine("notice",f"조사 완료 3/3 · 첫 제출 정확도 {score}/3")
        if not stats_ok:
            st.warning("활동 결과의 통계 저장에 실패했어요. 화면의 결과는 확인할 수 있어요.")
    dd.stamp("14")
    st.subheader(f"조사 완료 3/3 · 첫 제출에서 맞힌 사례 {score}/3")
    dd.show_hall_note(S.get("hall"))
    st.markdown(NV_CSS, unsafe_allow_html=True)
    cols=st.columns(3)
    for k,col in enumerate(cols):
        with col:
            door_scene(k, CASES[k]["answer"])
    for case in CASES:
        with st.expander(f"{case['door']} · {case['answer']}",expanded=True):
            st.write(case["lesson"])
    st.info("현실에서는 안내서 속 연락처·QR 대신 별도로 확인한 공식 경로를 이용하세요. 조회가 안 되는 이유를 확인하고, 확인 전에는 안내서가 요구하는 결제나 정보 전달을 보류하세요.")
    me=dd.citizen()
    show_result_card({"color":"#9A3412","place":"다람쥐아파트 관리사무소","game":"가짜 안내서 감별소","emoji":"📬",
        "title":"따로 확인 완료","subtitle":f"첫 제출 정확도 {score}/3",
        "stats":[("첫 제출 정확도",f"{score}/3"),("사례 수","3")],
        "sections":[("확인 습관",["겉모습으로 단정하지 않기","우편물 존재와 추가 요구를 구분하기","근거가 부족하면 판단 보류"])],
        "nickname":me["nickname"] if me else "","mascot":"trophy" if score==3 else "retry"},
        "jamkkan_notice_card.png")
    if st.button("🔄 다른 방법으로 다시 도전"):
        st.session_state[KEY]=fresh()
        for k in list(st.session_state):
            if k.startswith(("nv_route_","nv_question_")): del st.session_state[k]
        st.rerun()
