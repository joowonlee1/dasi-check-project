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
        return bool(game.get("checks") or game.get("answers") or game.get("done"))
    return False

@contextmanager
def intro(number, route=False, suffix=""):
    key = ("route_" if route else "intro_") + number + suffix
    with st.container(key=key):
        if is_playing(number):
            st.markdown(f"<style>.st-key-{key} {{display:none!important}}</style>", unsafe_allow_html=True)
        yield

# 게임 화면(iframe) 안에서 쓸 깡지(작게 줄여 전송량을 줄여요). 게임마다 다른 깡지를 써요.
BRIDGE_MASCOTS = {"10": ("sneaker", "hooray", "think"), "11": ("postman", "hooray", "think"), "12": ("puzzle", "hooray", "detective")}


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
  style.textContent=active?'.st-key-route___NUMBER__,[class*="st-key-intro___NUMBER__"]{display:none!important}':'';
 }catch(e){}
}
// 결과 큰 창: 앱 화면 가운데에 띄워요. 창 안의 모양은 게임마다 따로 만들어 넘겨요(세계관이 달라요).
function jkOverlay(inner, then){
 try{
  const D=parent.document; const old=D.getElementById('jk-bigpop'); if(old) old.remove();
  const w=D.createElement('div'); w.id='jk-bigpop';
  w.style.cssText='position:fixed;inset:0;z-index:999998;background:rgba(15,23,42,.55);display:flex;align-items:center;justify-content:center;padding:16px;font-family:system-ui,sans-serif';
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
    return html_text.replace("<script>", "<script>"+script.replace("__NUMBER__", number), 1)
