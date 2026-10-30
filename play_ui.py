"""게임 안내의 표시 시점만 제어합니다. 게임 판정에는 관여하지 않습니다."""
from contextlib import contextmanager
import streamlit as st

def is_playing(number):
    s = st.session_state
    if number == "01": return bool(s.get("grandma_v3", {}).get("started"))
    if number == "02":
        chat = s.get("jamkkan_chat_realistic_v1", {})
        return bool(chat.get("pending") or any(m.get("role") == "user" for m in chat.get("messages", [])))
    if number == "03":
        return bool(s.get("escape_game")) and s.get("room_next_section", s.get("room_section")) == "🗝️ 게임 진행"
    if number == "08": return bool(s.get("coping_v1_started") or s.get("coping_v1_result"))
    if number == "09": return s.get("mafia_v1", {}).get("phase", "setup") != "setup"
    if number == "14":
        game = s.get("notice_verify_v3", {})
        return bool(game.get("entered", False))
    return False

@contextmanager
def intro(number, route=False, suffix=""):
    key = ("route_" if route else "intro_") + number + suffix
    with st.container(key=key):
        if is_playing(number):
            st.markdown(f"<style>.st-key-{key},div:has(> .st-key-{key}) {{display:none!important}}</style>", unsafe_allow_html=True)
        yield

# 게임 화면(iframe) 안에서 쓸 깡지(작게 줄여 전송량을 줄여요). 게임마다 다른 깡지를 써요.
BRIDGE_MASCOTS = {"06": ("trophy", "hooray", "news"), "10": ("sneaker", "hooray", "think"), "11": ("postman", "hooray", "think"), "12": ("puzzle", "hooray", "detective")}


def _mascot_urls(number):
    import base64
    import io
    import json
    out = {}
    try:
        from PIL import Image
        from mascot_ui import _pose_data
        for name in BRIDGE_MASCOTS.get(number, ()):
            with Image.open(io.BytesIO(base64.b64decode(_pose_data(name)))) as im:
                im = im.copy()
            im.thumbnail((260, 260))
            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
            out[name] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        pass  # 그림이 없어도 게임은 그대로 돼요(큰 창에 깡지만 빠져요).
    return json.dumps(out)


def bridge(html_text, number):
    # iframe 안의 시작/다시보기 동작이 서버 재실행 없이 바깥 안내도 접게 합니다.
    script = """
function setPlayActive(active){
 try{
  const doc=parent.document, id='play-intro-__NUMBER__';
  let style=doc.getElementById(id);
  if(!style){style=doc.createElement('style');style.id=id;doc.head.appendChild(style);}
  style.textContent=active?'.st-key-route___NUMBER__,[class*="st-key-intro___NUMBER__"],div:has(> .st-key-route___NUMBER__),div:has(> [class*="st-key-intro___NUMBER__"]){display:none!important}':'';
 }catch(e){}
}
// 결과 큰 창: 앱 화면 가운데에 띄워요. 창 안의 모양은 게임마다 따로 만들어 넘겨요(세계관이 달라요).
function jkOverlay(inner, then){
 try{
  const D=parent.document; const old=D.getElementById('jk-bigpop'); if(old) old.remove();
  const w=D.createElement('div'); w.id='jk-bigpop';
  w.style.cssText='position:fixed;inset:0;z-index:999998;background:rgba(15,23,42,.55);display:flex;align-items:center;justify-content:center;padding:16px;font-family:Pretendard Variable,Pretendard,system-ui,sans-serif';
  w.innerHTML='<style>@keyframes jkpop{from{transform:scale(.85) translateY(10px);opacity:0}to{transform:none;opacity:1}}#jk-bigpop .jk-panel{animation:jkpop .35s ease-out;max-width:640px;width:100%;max-height:88vh;overflow:auto}</style>'+inner;
  const close=()=>{w.remove(); if(then) then();};
  w.querySelectorAll('[data-close]').forEach(b=>b.onclick=close);
  w.addEventListener('click',e=>{if(e.target===w) close();});
  D.addEventListener('keydown',function esc(e){if(e.key==='Escape'&&D.getElementById('jk-bigpop')){close();D.removeEventListener('keydown',esc);}});
  D.body.appendChild(w); const b=w.querySelector('[data-close]'); if(b) b.focus();
 }catch(e){ if(then) then(); }
}
const JK_MASCOT=__MASCOTS__;
function jkImg(name,size){return JK_MASCOT[name]?'<img src="'+JK_MASCOT[name]+'" alt="" style="width:'+(size||120)+'px;flex:0 0 '+(size||120)+'px;height:auto">':'';}
"""
    script = script.replace("__MASCOTS__", _mascot_urls(number))
    # 게임 시작 화면 공통 틀: 핵심 3칸 카드(.jk-k3) + 자세히 보기 접기 상자(.jk-more)
    k3_css = ("<style>.jk-k3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:10px 0}"
              ".jk-k3>div{position:relative;background:#fff;border:2px solid #D7E2DD;border-radius:16px;padding:10px 12px;word-break:keep-all}"
              ".jk-k3>div.key{border-color:#F59E0B;background:#FFF8EC}"
              ".jk-k3 .t{display:flex;align-items:center;gap:6px;font-weight:900;font-size:1.02rem;color:#1F3A33}"
              ".jk-k3 .t i{font-style:normal;display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:#20483F;color:#fff;font-size:.8rem;flex:0 0 auto}"
              ".jk-k3 .t em{font-style:normal;font-size:1.3rem}"
              ".jk-k3 p{margin:4px 0 0;font-size:.9rem;line-height:1.5;color:#334155}"
              "details.jk-more{margin:10px 0 0;border:2px dashed #C9DCD3;border-radius:14px;background:#FAFCFB}"
              "details.jk-more>summary{cursor:pointer;font-weight:900;font-size:1.05rem;padding:10px 14px;color:#20483F;list-style:none}"
              "details.jk-more>summary::-webkit-details-marker{display:none}"
              "details.jk-more>summary::after{content:' ▾';color:#94A3B8}details.jk-more[open]>summary::after{content:' ▴'}"
              "details.jk-more>.in{padding:0 12px 12px}"
              "@media (max-width:640px){.jk-k3{grid-template-columns:1fr}}</style>")
    if "</head>" in html_text:
        html_text = html_text.replace("</head>", k3_css + "</head>", 1)
    return html_text.replace("<script>", "<script>"+script.replace("__NUMBER__", number), 1)
