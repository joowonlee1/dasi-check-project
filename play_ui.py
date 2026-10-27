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
        game = s.get("notice_verify_v2", {})
        return bool(game.get("checks") or game.get("answers") or game.get("done"))
    return False

@contextmanager
def intro(number, route=False, suffix=""):
    key = ("route_" if route else "intro_") + number + suffix
    with st.container(key=key):
        if is_playing(number):
            st.markdown(f"<style>.st-key-{key} {{display:none!important}}</style>", unsafe_allow_html=True)
        yield

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
"""
    return html_text.replace("<script>", "<script>"+script.replace("__NUMBER__", number), 1)
