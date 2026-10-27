"""방탈출 가상 문자 알림과 번호 복사 UI. 게임 자료와 판정은 변경하지 않습니다."""
import json
import streamlit as st
import streamlit.components.v1 as components

_PHONE_JS = r'''
(()=>{
const payload=__PAYLOAD__;
let W;try{W=parent;if(!W.document) return;}catch(e){return;}
const D=W.document, key=String(payload.session);
let state=W.__dotoriPhone;
if(!state||state.session!==key){
 if(state&&state.remove)state.remove();
 state=W.__dotoriPhone={session:key,seen:new Set(),messages:[],open:false};
}
state.messages=payload.messages;
if(!state.root||!state.root.isConnected){
 state.open=false;
 const root=D.createElement('div');root.id='dotori-phone-ui';root.setAttribute('translate','no');root.setAttribute('lang','ko');root.className='notranslate';
 root.innerHTML='<style>#dotori-phone-ui{font-family:system-ui,sans-serif;color:#17212b}#dotori-phone-ui button{font:inherit;cursor:pointer;border-radius:12px;min-height:44px;padding:10px 16px;font-weight:800}#dotori-phone-launch{position:fixed;right:22px;bottom:96px;z-index:999990;background:#fff4c9;color:#173f35;border:3px solid #b88720;font-size:22px!important;min-height:62px!important;padding:14px 24px!important;border-radius:18px!important;box-shadow:0 4px 18px #0005}#dotori-phone-cover{position:fixed;inset:0;background:#0009;z-index:999999;display:none;align-items:center;justify-content:center;padding:18px;overscroll-behavior:contain}#dotori-phone-panel{background:#fffdf5;border-radius:22px;border:3px solid #d8be77;width:min(680px,100%);max-height:88dvh;overflow:auto;padding:22px;box-sizing:border-box}#dotori-phone-panel h2{font-size:1.5rem;margin:0 0 18px}#dotori-phone-list{background:#e9eef2;border-radius:14px;padding:12px;max-height:52dvh;overflow:auto}#dotori-phone-from{font-weight:800;margin:-6px 0 10px;color:#b42318}#dotori-phone-list article{background:#fff;border-radius:4px 16px 16px 16px;padding:10px 14px;margin:10px 40px 2px 0;overflow-wrap:anywhere;box-shadow:0 1px 2px #0002}#dotori-phone-list article.new{border:2px solid #b42318;animation:dp-in .35s ease-out}#dotori-phone-list small{display:block;color:#5b6770;font-size:.82rem;margin:0 0 6px 4px}#dotori-phone-list p{font-size:1.15rem;line-height:1.6;margin:0}@keyframes dp-in{from{transform:translateY(8px);opacity:0}to{transform:none;opacity:1}}@keyframes dp-shake{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-5px)}40%,80%{transform:translateX(5px)}}#dotori-phone-launch.ring{animation:dp-shake .5s ease-in-out 3}#dotori-phone-close{background:#20483f;color:white;border:0;width:100%}@media(max-width:600px){#dotori-phone-launch{right:12px;bottom:92px;max-width:calc(100vw - 24px);font-size:19px!important;min-height:54px!important;padding:10px 16px!important}#dotori-phone-panel{padding:16px}}</style><button id="dotori-phone-launch" type="button">📱 나의 폰</button><div id="dotori-phone-cover"><section id="dotori-phone-panel" role="dialog" aria-modal="true" aria-labelledby="dotori-phone-title" tabindex="-1"><h2 id="dotori-phone-title">📱 나의 폰 · 문자</h2><div id="dotori-phone-from">010-6620-1184 · 저장되지 않은 번호</div><div id="dotori-phone-list"></div><button type="button" id="dotori-phone-close">확인하고 닫기</button></section></div>';
 D.body.appendChild(root);state.root=root;
 const cover=root.querySelector('#dotori-phone-cover'), panel=root.querySelector('#dotori-phone-panel'), list=root.querySelector('#dotori-phone-list'),launch=root.querySelector('#dotori-phone-launch'),close=root.querySelector('#dotori-phone-close');
 state.draw=()=>{
  list.replaceChildren();
  if(!state.messages.length){const p=D.createElement('p');p.textContent='아직 도착한 문자가 없어요.';list.appendChild(p);}
  // 메신저처럼 오래된 문자가 위, 새 문자가 아래로 계속 쌓여요.
  for(const m of state.messages){
   const card=D.createElement('article'),body=D.createElement('p'),when=D.createElement('small');
   body.textContent=m.text;when.textContent=m.time;
   if(state.fresh&&state.fresh.has(m.id))card.className='new';
   card.append(body);list.append(card,when);
  }
  list.scrollTop=list.scrollHeight;
 };
 state.show=()=>{
  state.focus=D.activeElement;state.draw();state.open=true;cover.style.display='flex';close.focus({preventScroll:true});
 };
 state.hide=()=>{
  state.open=false;cover.style.display='none';
  for(const m of state.messages)state.seen.add(m.id);
  launch.textContent=state.messages.length?'📱 나의 폰 · 받은 문자 '+state.messages.length:'📱 나의 폰 · 새 문자 없음';
  if(state.focus&&state.focus.isConnected)state.focus.focus({preventScroll:true});
 };
 launch.onclick=()=>state.show();close.onclick=()=>state.hide();
 cover.addEventListener('keydown',e=>{
  if(e.key==='Escape'){e.preventDefault();state.hide();}
  if(e.key==='Tab'){e.preventDefault();close.focus();}
 });
 const originalPath=W.location.pathname;
 // 방탈출 게임 화면(자리표 game_phone_anchor)이 사라지면 '나의 폰'도 바로 없애요.
 // 다른 페이지로 가거나, 방탈출 안에서 시작 안내로 돌아가면 다른 화면에 남지 않아요.
 // 방탈출 페이지에 있는 동안은 계속 떠 있고, 다른 페이지로 가면 바로 없어져요.
 // (게임이 끝나거나 시간이 다 되면 app.py의 clear_phone()이 없애요.)
 const observer=new W.MutationObserver(()=>{if(W.location.pathname!==originalPath)state.remove();});
 observer.observe(D,{childList:true,subtree:true});
 const timer=W.setInterval(()=>{if(W.location.pathname!==originalPath)state.remove();},800);
 state.remove=()=>{observer.disconnect();W.clearInterval(timer);state.open=false;root.remove();};  // 읽은 문자 기록(seen)은 남겨서, 다시 들어와도 같은 문자로 또 알리지 않아요.
}
const fresh=state.messages.filter(m=>!state.seen.has(m.id));
const phoneButton=state.root.querySelector('#dotori-phone-launch');
phoneButton.textContent=state.messages.length?'📱 나의 폰 · 받은 문자 '+state.messages.length:'📱 나의 폰 · 새 문자 없음';
if(fresh.length){
 // 확인 전 재실행돼도 같은 문자를 반복 알림하지 않습니다.
 state.fresh=new Set(fresh.map(m=>m.id));
 fresh.forEach(m=>state.seen.add(m.id));
 phoneButton.classList.remove('ring');void phoneButton.offsetWidth;phoneButton.classList.add('ring');
 phoneButton.innerHTML='📱 나의 폰 <span style="display:inline-block;background:#b42318;color:white;border-radius:8px;padding:3px 8px;margin-left:5px">새 문자 '+fresh.length+'</span>';
 if(!state.open)state.show();else state.draw();
 const h=W.__jamkkanSound;
 if(h&&h.want)h.play('message');
}else if(state.open){state.draw();}
})();
'''
_COPY_JS = r'''
const phones=__PHONES__;
const root=document.getElementById('numbers');
phones.forEach(phone=>{
 const row=document.createElement('div');row.className='number-row';
 const value=document.createElement('span');value.textContent=phone;value.tabIndex=0;
 const button=document.createElement('button');button.type='button';button.textContent='📋 복사';button.setAttribute('aria-label',phone+' 복사');
 button.onclick=async()=>{
  let ok=false;
  try{await navigator.clipboard.writeText(phone);ok=true;}catch(e){
   const input=document.createElement('textarea');input.value=phone;document.body.appendChild(input);input.select();
   try{ok=document.execCommand('copy');}catch(e){}input.remove();
  }
  button.textContent=ok?'✓ 복사됨':'복사 실패';
  row.querySelector('.status').textContent=ok?'':'번호를 길게 눌러 직접 복사해 주세요.';
 };
 const status=document.createElement('span');status.className='status';status.setAttribute('role','status');
 row.append(value,button,status);root.appendChild(row);
});
'''

def show_phone(session, messages, sender, clock_text):
    payload={"session":session,"messages":[{"id":str(at)+"|"+text,"sender":sender,"time":clock_text(at),"text":text} for at,text,*_ in messages]}
    source=_PHONE_JS.replace("__PAYLOAD__",json.dumps(payload,ensure_ascii=False).replace("<","\\u003c"))
    with st.container(key="game_phone_anchor"):
        # 부모 문서에서 실행해 iframe이 교체돼도 버튼 콜백이 살아 있도록 합니다.
        script_json=json.dumps(source,ensure_ascii=False).replace("<","\\u003c")
        # 매번 내용이 조금씩 달라야 다시 실행돼요. 그래야 폰이 사라졌을 때 다음 화면에서 다시 나타나요.
        st.session_state["_phone_draw_n"] = st.session_state.get("_phone_draw_n", 0) + 1
        components.html("<script>const d=parent.document;const s=d.createElement('script');s.textContent="+script_json+";d.head.appendChild(s);s.remove();</script>"
                        f"<!-- {st.session_state['_phone_draw_n']} -->", height=0)

def copy_numbers(numbers):
    source=_COPY_JS.replace("__PHONES__",json.dumps(numbers,ensure_ascii=False).replace("<","\\u003c"))
    if not numbers:
        st.caption("번호가 있는 자료를 증거 보관함에 넣으면 여기에 표시돼요.")
        return
    components.html("""<!doctype html><html lang="ko"><meta charset="utf-8"><style>
body{margin:0;font:16px system-ui;color:#20483f}
.number-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:6px 0;padding:6px;background:#f2f6f3;border-radius:10px}
.number-row>span:first-child{font-weight:700;user-select:all}
button{min-height:44px;padding:8px 12px;background:#20483f;color:white;border:2px solid #20483f;border-radius:8px;font:700 15px system-ui;cursor:pointer}
.status{font-size:13px}
</style><div id="numbers"></div><script>"""+source+"</script></html>",height=len(numbers)*78+12,scrolling=True)

def clear_phone():
    # 매번 내용이 달라야 브라우저가 다시 실행해요(같은 내용이면 이전 것을 재사용해서 지우기가 안 될 수 있어요).
    st.session_state["_phone_clear_n"] = st.session_state.get("_phone_clear_n", 0) + 1
    components.html("<script>try{const s=parent.__dotoriPhone;if(s&&s.remove)s.remove();"
                    "const r=parent.document.getElementById('dotori-phone-ui');if(r)r.remove();}catch(e){}</script>"
                    f"<!-- {st.session_state['_phone_clear_n']} -->", height=0)
