"""Optional sound layer; no changes to game rules or saved data."""
import json
import uuid
import streamlit as st
import streamlit.components.v1 as components

def queue_effect(kind="stamp"):
    st.session_state["_sound_event"] = {"id": uuid.uuid4().hex, "kind": kind}

def flush_effect():
    event = st.session_state.pop("_sound_event", None)
    if event:
        components.html("<script>try{const h=parent.__jamkkanSound;const e=" + json.dumps(event) + ";if(h&&!h.events.has(e.id)){h.events.add(e.id);if(h.events.size>128)h.events.delete(h.events.values().next().value);h.play(e.kind);}}catch(e){}</script>", height=0)

def render_sound_controls():
    components.html(_HTML, height=110)

_HTML = r'''<!doctype html><html lang="ko"><meta charset="utf-8">
<style>body{margin:0;font:14px system-ui;color:#254c44}.bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:8px;background:#f0f6f2;border-radius:12px}button{border:0;border-radius:9px;background:#3d7068;color:white;padding:9px 12px;cursor:pointer}input{width:90px;vertical-align:middle}button{min-height:44px}label{white-space:nowrap}.bar{box-sizing:border-box}small{flex-basis:100%}small{font-size:12px}</style>
<div class="bar"><button id="toggle" aria-pressed="false">🔇 효과음 켜기</button><label>음량 <input id="volume" aria-label="효과음 음량" type="range" min="0" max="100" value="25"></label><small id="status" role="status"></small></div>
<script>
(()=>{
'use strict';
let W=window;try{if(parent.document)W=parent;}catch(e){}
const patterns={tap:[[650,.045]],cell:[[480,.035]],start:[[440,.09],[554,.09],[659,.13]],clue:[[880,.07],[1175,.12]],message:[[740,.06],[880,.09]],success:[[523,.09],[659,.09],[784,.15]],notice:[[330,.08],[294,.11]],stamp:[[1047,.12],[1319,.22]],result:[[523,.09],[659,.12]]};
if(!W.__jamkkanSound){
 const H=W.__jamkkanSound={enabled:false,volume:.25,ctx:null,last:0,voices:[],events:new Set(),docs:new WeakSet(),frames:new WeakSet(),seen:new WeakSet(),texts:new Map(),action:0,busyUntil:0,priority:0};
 try{const v=Number(W.localStorage.getItem('jamkkan-volume')??.25);if(Number.isFinite(v))H.volume=Math.max(0,Math.min(1,v));}catch(e){}
 H.stop=()=>{for(const o of H.voices){try{o.stop();}catch(e){}}H.voices=[];};
 H.play=kind=>{try{
  if(!H.enabled||!H.ctx||H.ctx.state!=='running'||H.volume<=0)return;
  const now=Date.now(),priority=({tap:0,cell:0,start:1,clue:1,message:2,notice:3,success:3,result:3,stamp:4})[kind]??0;
  if((now-H.last<65 && priority<=H.priority)||(now<H.busyUntil&&priority<H.priority))return;
  H.last=now;H.priority=priority;H.stop();
  let at=H.ctx.currentTime;
  for(const [hz,duration] of patterns[kind]||patterns.tap){
   const o=H.ctx.createOscillator(),g=H.ctx.createGain();o.type='sine';o.frequency.value=hz;
   g.gain.setValueAtTime(0,at);g.gain.linearRampToValueAtTime(H.volume*.20,at+.008);g.gain.exponentialRampToValueAtTime(.0001,at+duration);
   o.connect(g);g.connect(H.ctx.destination);o.start(at);o.stop(at+duration+.01);
   o.onended=()=>{o.disconnect();g.disconnect();H.voices=H.voices.filter(v=>v!==o);};H.voices.push(o);at+=duration+.035;
  }
  H.busyUntil=now+(at-H.ctx.currentTime)*1000;
 }catch(e){H.enabled=false;H.stop();}};
 H.activate=async()=>{const AC=W.AudioContext||W.webkitAudioContext;if(!AC)throw Error('unsupported');if(!H.ctx||H.ctx.state==='closed')H.ctx=new AC();await H.ctx.resume();H.enabled=H.ctx.state==='running';};
 H.classify=text=>/시작|입장|출발|실행/.test(text)?'start':/힌트|단서|조사|열기|공개/.test(text)?'clue':'tap';
 H.attach=doc=>{
  if(H.docs.has(doc))return;H.docs.add(doc);
  doc.addEventListener('click',e=>{
   const el=e.target.closest?.('button,[role="button"],input[type="radio"],input[type="checkbox"],summary,.cell[data-r]');
   if(!el||el.disabled||el.getAttribute('aria-disabled')==='true')return;
   if(H.enabled&&H.ctx?.state==='suspended')H.ctx.resume().catch(()=>{});
   H.action=Date.now();const kind=el.matches('.cell[data-r]')?'cell':H.classify(el.innerText||el.getAttribute('aria-label')||'');if(kind==='start')H.texts.clear();H.play(kind);
  },true);
  doc.addEventListener('change',e=>{if(e.target.matches('select')){H.action=Date.now();H.play('tap');}},true);
  doc.addEventListener('keydown',e=>{
   if(e.repeat||!['Enter',' '].includes(e.key))return;
   const el=e.target.closest?.('[role="button"]');
   if(el&&el.tagName!=='BUTTON'&&el.getAttribute('aria-disabled')!=='true'){H.action=Date.now();H.play('tap');}
  },true);
  doc.addEventListener('visibilitychange',()=>{if(doc.hidden)H.stop();});
  const selector='[data-testid="stAlert"],[data-testid="stChatMessage"],.result,.zz-card,.mf-reveal';
  doc.querySelectorAll(selector).forEach(el=>H.seen.add(el));
  let pending=false;
  const scan=()=>{
   pending=false;
   doc.querySelectorAll(selector).forEach(el=>{
    const text=(el.textContent||'').trim();
    const signature=(doc.location?.pathname||'')+'|'+(el.className||'')+'|'+text;
    if(!text||H.seen.has(el))return;H.seen.add(el);
    if(H.texts.has(signature)||Date.now()-H.action>15000)return;
    H.texts.set(signature,true);if(H.texts.size>256)H.texts.delete(H.texts.keys().next().value);
    if(el.querySelector('[data-testid="stChatMessageAvatarAssistant"]'))H.play('message');
    else if(el.querySelector('[data-testid="stAlertContentSuccess"]'))H.play('success');
    else if(el.querySelector('[data-testid="stAlertContentError"],[data-testid="stAlertContentWarning"]'))H.play('notice');
    else if(el.matches('.result,.zz-card,.mf-reveal'))H.play('result');
   });
   doc.querySelectorAll('iframe').forEach(frame=>{
    const connect=()=>{try{if(frame.contentDocument)H.attach(frame.contentDocument);}catch(e){}};
    if(!H.frames.has(frame)){H.frames.add(frame);frame.addEventListener('load',connect);}connect();
   });
  };
  new W.MutationObserver(()=>{if(!pending){pending=true;W.setTimeout(scan,120);}}).observe(doc.documentElement,{childList:true,subtree:true});scan();
 };
 H.docs.add(document);H.attach(W.document);
}
const H=W.__jamkkanSound;H.docs.add(document);
const button=document.getElementById('toggle'),volume=document.getElementById('volume'),status=document.getElementById('status');
const paint=()=>{button.textContent=H.enabled?'🔊 효과음 끄기':'🔇 효과음 켜기';button.setAttribute('aria-pressed',String(H.enabled));volume.value=Math.round(H.volume*100);status.textContent=H.enabled?'효과음 사용 중':'소리를 켠 뒤 이용해 주세요.';};
button.onclick=async()=>{if(H.enabled){H.enabled=false;H.stop();paint();return;}try{await H.activate();paint();if(H.enabled)H.play('start');else status.textContent='한 번 더 눌러 주세요.';}catch(e){status.textContent='이 브라우저에서 소리를 시작하지 못했어요.';}};
volume.oninput=()=>{H.volume=Number(volume.value)/100;if(!H.volume)H.stop();try{W.localStorage.setItem('jamkkan-volume',String(H.volume));}catch(e){}};
volume.onchange=()=>H.play('tap');paint();
const fit=()=>{try{if(window.frameElement)window.frameElement.style.height=(document.body.scrollHeight+8)+'px';}catch(e){}};
new ResizeObserver(fit).observe(document.querySelector('.bar'));fit();

})();
</script></html>'''
