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
 const root=D.createElement('div');root.id='dotori-phone-ui';
 root.innerHTML='<style>#dotori-phone-ui{font-family:system-ui,sans-serif;color:#17212b}#dotori-phone-ui button{font:inherit;cursor:pointer;border-radius:12px;min-height:44px;padding:10px 16px;font-weight:800}#dotori-phone-launch{position:fixed;right:22px;bottom:26px;z-index:999990;background:#20483f;color:white;border:2px solid white;box-shadow:0 3px 14px #0004}#dotori-phone-cover{position:fixed;inset:0;background:#0009;z-index:999999;display:none;align-items:center;justify-content:center;padding:18px;overscroll-behavior:contain}#dotori-phone-panel{background:#fffdf5;border-radius:22px;border:3px solid #d8be77;width:min(680px,100%);max-height:88dvh;overflow:auto;padding:22px;box-sizing:border-box}#dotori-phone-panel h2{font-size:1.5rem;margin:0 0 18px}#dotori-phone-list article{background:#eef5f2;border-radius:12px;padding:16px;margin:12px 0;overflow-wrap:anywhere}#dotori-phone-list p{font-size:1.15rem;line-height:1.7;margin:8px 0}#dotori-phone-close{background:#20483f;color:white;border:0;width:100%}@media(max-width:600px){#dotori-phone-launch{right:12px;bottom:18px}#dotori-phone-panel{padding:16px}}</style><button id="dotori-phone-launch" type="button">📱 나의 폰</button><div id="dotori-phone-cover"><section id="dotori-phone-panel" role="dialog" aria-modal="true" aria-labelledby="dotori-phone-title" tabindex="-1"><h2 id="dotori-phone-title">📱 나의 폰</h2><div id="dotori-phone-list"></div><button type="button" id="dotori-phone-close">확인하고 닫기</button></section></div>';
 D.body.appendChild(root);state.root=root;
 const cover=root.querySelector('#dotori-phone-cover'), panel=root.querySelector('#dotori-phone-panel'), list=root.querySelector('#dotori-phone-list'),launch=root.querySelector('#dotori-phone-launch'),close=root.querySelector('#dotori-phone-close');
 state.draw=()=>{
  list.replaceChildren();
  if(!state.messages.length){const p=D.createElement('p');p.textContent='아직 도착한 문자가 없어요.';list.appendChild(p);}
  for(const m of [...state.messages].reverse()){
   const card=D.createElement('article'),head=D.createElement('strong'),body=D.createElement('p');
   head.textContent=m.sender+' · '+m.time;body.textContent=m.text;
   card.append(head,body);list.appendChild(card);
  }
 };
 state.show=()=>{
  state.focus=D.activeElement;state.draw();state.open=true;cover.style.display='flex';close.focus({preventScroll:true});
 };
 state.hide=()=>{
  state.open=false;cover.style.display='none';
  for(const m of state.messages)state.seen.add(m.id);
  launch.textContent='📱 나의 폰 ('+state.messages.length+')';
  if(state.focus&&state.focus.isConnected)state.focus.focus({preventScroll:true});
 };
 launch.onclick=()=>state.show();close.onclick=()=>state.hide();
 cover.addEventListener('keydown',e=>{
  if(e.key==='Escape'){e.preventDefault();state.hide();}
  if(e.key==='Tab'){e.preventDefault();close.focus();}
 });
 const originalPath=W.location.pathname;
 const observer=new W.MutationObserver(()=>{
  if(W.location.pathname!==originalPath){state.remove();}
 });
 observer.observe(D,{childList:true,subtree:true});
 state.remove=()=>{observer.disconnect();state.open=false;root.remove();};
}
const fresh=state.messages.filter(m=>!state.seen.has(m.id));
state.root.querySelector('#dotori-phone-launch').textContent='📱 나의 폰 ('+state.messages.length+')';
if(fresh.length){
 // 확인 전 재실행돼도 같은 문자를 반복 알림하지 않습니다.
 fresh.forEach(m=>state.seen.add(m.id));
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
        components.html("<script>"+source+"</script>",height=0)

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
    components.html("<script>try{const s=parent.__dotoriPhone;if(s&&s.remove)s.remove();}catch(e){}</script>",height=0)
