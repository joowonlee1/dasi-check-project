"""Optional sound layer; no changes to game rules or saved data.

소리는 브라우저 안(Web Audio)에서 숫자로 만들어요. 외부 소리 파일이 필요 없고,
사이드바의 '효과음' 스위치와 음량 슬라이더로 켜고 끌 수 있어요.

- render_sound_controls(): 사이드바에 켜기/끄기·음량·미리듣기를 그리고 소리 엔진을 한 번 깔아 둬요.
- queue_effect(kind) / flush_effect(): 파이썬 쪽에서 원하는 순간에 소리를 내고 싶을 때 써요.
- 버튼·선택·페이지 이동·정답/오답 알림·결과 카드 같은 화면 변화는 엔진이 알아서 감지해 소리를 내요.
"""
import json
import uuid
import streamlit as st
import streamlit.components.v1 as components

SOUND_ON = "sound_on"          # 효과음 스위치(켜짐/꺼짐)
SOUND_VOLUME = "sound_volume"  # 음량 0~100
DEFAULT_VOLUME = 60


def sound_enabled():
    """효과음이 켜져 있는지(처음 방문은 켜짐)."""
    return bool(st.session_state.get(SOUND_ON, True))


def sound_volume():
    """0.0~1.0 사이 음량."""
    try:
        return max(0.0, min(1.0, float(st.session_state.get(SOUND_VOLUME, DEFAULT_VOLUME)) / 100))
    except (TypeError, ValueError):
        return DEFAULT_VOLUME / 100


def queue_effect(kind="stamp"):
    st.session_state["_sound_event"] = {"id": uuid.uuid4().hex, "kind": kind}


def flush_effect():
    event = st.session_state.pop("_sound_event", None)
    if event and sound_enabled():
        components.html("<script>try{const h=parent.__jamkkanSound;const e=" + json.dumps(event) + ";if(h&&!h.events.has(e.id)){h.events.add(e.id);if(h.events.size>128)h.events.delete(h.events.values().next().value);h.play(e.kind);}}catch(e){}</script>", height=0)


def render_sound_controls():
    """사이드바용 효과음 켜기/끄기 + 음량 + 미리듣기. (with st.sidebar: 안에서 불러 주세요.)"""
    st.session_state.setdefault(SOUND_ON, True)
    st.session_state.setdefault(SOUND_VOLUME, DEFAULT_VOLUME)
    on = st.toggle("🔊 효과음", key=SOUND_ON, help="버튼을 누르거나 정답·오답이 나올 때 나는 소리예요. 끄면 조용해져요.")
    if on:
        st.slider("🎚️ 음량", 0, 100, key=SOUND_VOLUME, help="0이면 소리가 나지 않아요.")
        st.button("🔔 소리 들어보기", key="sound_preview", width="stretch")
    components.html(_engine(on, sound_volume()), height=0)


def _engine(enabled, volume):
    config = json.dumps({"enabled": bool(enabled), "volume": round(float(volume), 3)})
    return _HTML.replace("__CONFIG__", config)


_HTML = r'''<!doctype html><html lang="ko"><meta charset="utf-8"><body>
<script>
(()=>{
'use strict';
let W=window;try{if(parent&&parent.document)W=parent;}catch(e){}
const CONFIG=__CONFIG__;
// 소리 한 음: n(주파수, 길이(초), {t:파형, v:크기, to:끝 주파수, at:시작 시각(초)})
const n=(f,d,o)=>Object.assign({f:f,d:d,t:'sine',v:1,to:0,at:-1},o||{});
const PATTERNS={
 tap:[n(520,.05,{t:'triangle',to:760})],
 cell:[n(430,.03,{t:'square',v:.45})],
 toggle:[n(330,.04,{t:'square',v:.4}),n(660,.06,{t:'triangle'})],
 next:[n(0,.16,{t:'noise',v:.5,at:0}),n(380,.14,{t:'triangle',to:820,at:0})],
 back:[n(720,.1,{t:'triangle',to:400})],
 reset:[n(600,.06,{t:'triangle',to:420}),n(420,.08,{t:'triangle',to:300})],
 start:[n(523,.08,{t:'triangle'}),n(659,.08,{t:'triangle'}),n(784,.08,{t:'triangle'}),n(1047,.2,{t:'triangle'})],
 clue:[n(988,.05),n(1319,.05),n(1760,.05,{v:.8}),n(2093,.14,{v:.6})],
 confirm:[n(660,.05,{t:'square',v:.4}),n(880,.1,{t:'triangle'})],
 message:[n(740,.06,{t:'triangle'}),n(988,.1,{t:'triangle'})],
 correct:[n(784,.07,{t:'triangle'}),n(1175,.2,{t:'triangle'})],
 wrong:[n(220,.12,{t:'sawtooth',v:.4,to:180}),n(165,.2,{t:'sawtooth',v:.4,to:120})],
 notice:[n(392,.09,{t:'triangle'}),n(330,.09,{t:'triangle'}),n(262,.16,{t:'triangle'})],
 warn:[n(880,.08,{t:'square',v:.35}),n(660,.08,{t:'square',v:.35}),n(880,.08,{t:'square',v:.35}),n(660,.12,{t:'square',v:.35})],
 coin:[n(988,.07,{t:'square',v:.35}),n(1319,.3,{t:'square',v:.35})],
 unlock:[n(0,.03,{t:'noise',v:.6,at:0}),n(200,.05,{t:'square',v:.4,at:0}),n(784,.09,{t:'triangle',at:.08}),n(1175,.22,{t:'triangle',at:.17})],
 success:[n(523,.09,{t:'triangle'}),n(659,.09,{t:'triangle'}),n(784,.09,{t:'triangle'}),n(1047,.32,{t:'triangle'}),n(784,.32,{v:.5,at:.36}),n(659,.32,{v:.5,at:.36})],
 result:[n(392,.1,{t:'triangle'}),n(523,.1,{t:'triangle'}),n(659,.1,{t:'triangle'}),n(784,.12,{t:'triangle'}),n(1047,.45,{t:'triangle',at:.52}),n(784,.45,{v:.6,at:.52}),n(659,.45,{v:.6,at:.52}),n(523,.45,{v:.5,at:.52})],
 fanfare:[n(0,.5,{t:'noise',v:.35,at:0}),n(392,.09,{t:'square',v:.35,at:0}),n(392,.09,{t:'square',v:.35,at:.12}),n(392,.09,{t:'square',v:.35,at:.24}),n(523,.5,{t:'square',v:.4,at:.36}),n(659,.5,{t:'triangle',v:.6,at:.36}),n(784,.5,{t:'triangle',v:.5,at:.36}),n(698,.12,{t:'triangle',at:.9}),n(784,.12,{t:'triangle',at:1.04}),n(880,.12,{t:'triangle',at:1.18}),n(1047,.9,{t:'square',v:.4,at:1.32}),n(1319,.9,{t:'triangle',v:.6,at:1.32}),n(1568,.9,{t:'triangle',v:.5,at:1.32}),n(784,.9,{t:'sine',v:.6,at:1.32}),n(2093,.08,{v:.35,at:1.5}),n(2637,.08,{v:.3,at:1.62}),n(3136,.08,{v:.3,at:1.74}),n(2637,.08,{v:.3,at:1.86}),n(3520,.25,{v:.3,at:1.98}),n(0,.6,{t:'noise',v:.45,at:1.32})],
 fail:[n(392,.2,{t:'triangle',to:370}),n(370,.2,{t:'triangle',to:330}),n(330,.2,{t:'triangle',to:290}),n(262,.5,{t:'triangle',to:150})],
 stamp:[n(0,.06,{t:'noise',v:.9,at:0}),n(170,.1,{to:80,at:0}),n(1047,.12,{t:'triangle',at:.1}),n(1319,.26,{t:'triangle',at:.2})]
};
PATTERNS.preview=PATTERNS.success;
const PRIORITY={tap:0,cell:0,toggle:0,back:0,reset:0,next:1,start:1,clue:1,confirm:1,message:2,correct:2,notice:3,warn:3,coin:3,wrong:3,success:3,result:3,fail:3,fanfare:5,unlock:4,stamp:4,preview:4};
const CLICKABLE='button,[role="button"],input[type="radio"],input[type="checkbox"],summary,.cell[data-r],'
 +'label[data-testid="stRadioOption"],[data-testid="stToggle"] label,[data-testid="stCheckbox"] label,'
 +'a[data-testid="stPageLink-NavLink"],[data-testid="stSidebarNav"] a,[data-testid="stSidebarNavLink"]';
if(!W.__jamkkanSound){
 const H=W.__jamkkanSound={want:false,enabled:false,volume:.6,ctx:null,noise:null,last:0,voices:[],events:new Set(),docs:new WeakSet(),frames:new WeakSet(),seen:new WeakSet(),texts:new Map(),action:0,busyUntil:0,priority:0};
 H.stop=()=>{for(const o of H.voices){try{o.stop();}catch(e){}}H.voices=[];};
 H.noiseBuffer=()=>{
  if(H.noise&&H.noise.sampleRate===H.ctx.sampleRate)return H.noise;
  const len=Math.floor(H.ctx.sampleRate*.5),buf=H.ctx.createBuffer(1,len,H.ctx.sampleRate),d=buf.getChannelData(0);
  for(let i=0;i<len;i++)d[i]=Math.random()*2-1;H.noise=buf;return buf;
 };
 H.play=(kind,again)=>{try{
  if(!H.want||H.volume<=0)return;
  // 소리 장치가 멈춰 있으면(음량 조절·다른 소리 재생 뒤 등) 한 번 깨운 다음 다시 들려줘요.
  if(!H.ctx||H.ctx.state!=='running'){if(!again)H.activate().then(()=>H.play(kind,true)).catch(()=>{});return;}
  const notes=PATTERNS[kind]||PATTERNS.tap,now=Date.now(),priority=PRIORITY[kind]||0;
  if((now-H.last<65&&priority<=H.priority)||(now<H.busyUntil&&priority<H.priority))return;
  H.last=now;H.priority=priority;H.stop();
  const ctx=H.ctx,t0=ctx.currentTime+.01;let cursor=0,end=t0;
  for(const s of notes){
   const start=t0+(s.at>=0?s.at:cursor);
   if(s.at<0)cursor+=s.d+.03;
   const g=ctx.createGain();
   g.gain.setValueAtTime(.0001,start);
   g.gain.linearRampToValueAtTime(Math.max(.0002,H.volume*.30*s.v),start+.008);
   g.gain.exponentialRampToValueAtTime(.0001,start+s.d);
   let src;
   if(s.t==='noise'){
    src=ctx.createBufferSource();src.buffer=H.noiseBuffer();
    const f=ctx.createBiquadFilter();f.type='bandpass';f.frequency.value=1800;src.connect(f);f.connect(g);
   }else{
    src=ctx.createOscillator();src.type=s.t;src.frequency.setValueAtTime(s.f,start);
    if(s.to>0)src.frequency.exponentialRampToValueAtTime(s.to,start+s.d);
    src.connect(g);
   }
   g.connect(ctx.destination);src.start(start);src.stop(start+s.d+.02);
   src.onended=()=>{try{src.disconnect();g.disconnect();}catch(e){}H.voices=H.voices.filter(v=>v!==src);};
   H.voices.push(src);end=Math.max(end,start+s.d);
  }
  H.busyUntil=now+(end-ctx.currentTime)*1000;
 }catch(e){H.stop();}};
 H.activate=async()=>{
  const AC=W.AudioContext||W.webkitAudioContext;if(!AC)return;
  if(!H.ctx||H.ctx.state==='closed')H.ctx=new AC();
  if(H.ctx.state!=='running'){try{await H.ctx.resume();}catch(e){}}
  // 깨워도 계속 멈춰 있으면 소리 장치를 새로 만들어요(한 번 고장 나면 계속 안 들리던 문제).
  if(H.ctx.state!=='running'){try{H.ctx.close();}catch(e){}H.ctx=new AC();H.noise=null;try{await H.ctx.resume();}catch(e){}}
  H.enabled=H.ctx.state==='running';
 };
 H.configure=c=>{
  H.want=!!c.enabled;const v=Number(c.volume);H.volume=Number.isFinite(v)?Math.max(0,Math.min(1,v)):.6;
  if(!H.want){H.enabled=false;H.stop();return;}
  H.activate().catch(()=>{});
 };
 H.kindOf=el=>{
  if(el.matches('.cell[data-r]'))return 'cell';
  if(el.matches('input[type="checkbox"],[data-testid="stToggle"] label,[data-testid="stCheckbox"] label'))return 'toggle';
  if(el.matches('a[data-testid="stPageLink-NavLink"],[data-testid="stSidebarNav"] a,[data-testid="stSidebarNavLink"]'))return 'next';
  const text=(el.innerText||el.getAttribute('aria-label')||'').replace(/\s+/g,' ');
  if(/들어보기|미리듣기/.test(text))return 'preview';
  if(/시작|입장|출발|실행|도전/.test(text))return 'start';
  if(/힌트|단서|조사|열기|공개|펼치/.test(text))return 'clue';
  if(/정답|제출|확인|판정|검사|검거|지목|저장|보내기|전송|해제/.test(text))return 'confirm';
  if(/다음|계속|넘어|이동/.test(text))return 'next';
  if(/뒤로|돌아|닫기|취소|이전/.test(text))return 'back';
  if(/다시|처음|초기화|새로/.test(text))return 'reset';
  return 'tap';
 };
 H.attach=doc=>{
  if(!doc||doc.nodeType!==9||H.docs.has(doc))return;H.docs.add(doc);
  doc.addEventListener('click',e=>{
   const el=e.target.closest?e.target.closest(CLICKABLE):null;
   if(!el||el.disabled||el.getAttribute('aria-disabled')==='true')return;
   H.action=Date.now();const kind=H.kindOf(el);if(kind==='start')H.texts.clear();
   // 소리가 켜져 있는데 아직 브라우저가 소리를 막고 있으면, 이 누름을 계기로 풀고 바로 들려줘요.
   if(H.want&&(!H.ctx||H.ctx.state!=='running')){H.activate().then(()=>H.play(kind)).catch(()=>{});return;}
   H.play(kind);
  },true);
  doc.addEventListener('change',e=>{if(e.target.matches&&e.target.matches('select')){H.action=Date.now();H.play('tap');}},true);
  doc.addEventListener('keydown',e=>{
   if(e.repeat||!['Enter',' '].includes(e.key))return;
   const el=e.target.closest?e.target.closest('[role="button"]'):null;
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
    const signature=(doc.location?doc.location.pathname:'')+'|'+(el.className||'')+'|'+text;
    if(!text||H.seen.has(el))return;H.seen.add(el);
    if(H.texts.has(signature)||Date.now()-H.action>15000)return;
    H.texts.set(signature,true);if(H.texts.size>256)H.texts.delete(H.texts.keys().next().value);
    if(el.querySelector('[data-testid="stChatMessageAvatarAssistant"]'))H.play('message');
    else if(el.querySelector('[data-testid="stAlertContentSuccess"]'))H.play('correct');
    else if(el.querySelector('[data-testid="stAlertContentError"]'))H.play('wrong');
    else if(el.querySelector('[data-testid="stAlertContentWarning"]'))H.play('notice');
    else if(el.matches('.result'))H.play(el.classList.contains('lose')?'fail':'result');
    else if(el.matches('.zz-card,.mf-reveal'))H.play('result');
   });
   doc.querySelectorAll('iframe').forEach(frame=>{
    const connect=()=>{try{if(frame.contentDocument)H.attach(frame.contentDocument);}catch(e){}};
    if(!H.frames.has(frame)){H.frames.add(frame);frame.addEventListener('load',connect);}connect();
   });
  };
  new W.MutationObserver(()=>{if(!pending){pending=true;W.setTimeout(scan,120);}}).observe(doc,{childList:true,subtree:true});scan();
 };
 H.docs.add(document);H.attach(W.document);
}
const H=W.__jamkkanSound;H.docs.add(document);
H.configure(CONFIG);
})();
</script></body></html>'''
