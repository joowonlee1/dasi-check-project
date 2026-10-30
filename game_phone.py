"""방탈출 가상 문자 알림과 번호 복사 UI. 게임 자료와 판정은 변경하지 않습니다."""
import json
import streamlit as st
import streamlit.components.v1 as components

_PHONE_JS = r'''
(()=>{
const payload=__PAYLOAD__;
// 통화 화면(사기범 목소리 연출) 함수: voice_ui.CALL_JS
const jkCall=__CALLJS__;
let W;try{W=parent;if(!W.document) return;}catch(e){return;}
const D=W.document, key=String(payload.session);
// APP: 이 스크립트가 실행된 앱 화면. 배포된 앱에서는 바깥 틀(W)과 달라서, 효과음·숨은 입력칸·버튼 연결은 APP에서 찾아요.
const APP=window;
let state=W.__dotoriPhone;
if(!state||state.session!==key){
 if(state&&state.remove)state.remove();
 state=W.__dotoriPhone={session:key,seen:new Set(),messages:[],open:false};
}
state.messages=payload.messages;state.dial=payload.dial||null;
try{APP.__dotoriPhone=state;}catch(e){}  // 앱 화면의 버튼(나의 폰에서 전화 걸기·폰 지우기)도 같은 폰을 찾게 해요.
if(!state.root||!state.root.isConnected){
 state.open=false;
 const root=D.createElement('div');root.id='dotori-phone-ui';root.setAttribute('translate','no');root.setAttribute('lang','ko');root.className='notranslate';
 root.innerHTML='<style>#dotori-phone-ui{font-family:Pretendard Variable,Pretendard,system-ui,sans-serif;color:#17212b}#dotori-phone-ui button{font:inherit;cursor:pointer;border-radius:12px;min-height:44px;padding:10px 16px;font-weight:800}#dotori-phone-launch{position:fixed;right:22px;bottom:96px;z-index:999990;background:#fff4c9;color:#173f35;border:3px solid #b88720;font-size:22px!important;min-height:76px!important;padding:18px 30px!important;border-radius:22px!important;box-shadow:0 4px 18px #0005}#dotori-phone-launch{padding-left:108px!important}#dotori-phone-launch::before{content:"";position:absolute;left:10px;bottom:4px;width:90px;height:102px;background:url(__BTNIMG__) no-repeat center bottom/contain;pointer-events:none}#dotori-phone-cover{position:fixed;inset:0;background:#0009;z-index:999999;display:none;align-items:center;justify-content:center;padding:18px;overscroll-behavior:contain}#dotori-phone-panel{background:#fffdf5;border-radius:22px;border:3px solid #d8be77;width:min(680px,100%);max-height:88dvh;overflow:auto;padding:22px;box-sizing:border-box}#dotori-phone-panel h2{font-size:1.5rem;margin:0 0 18px}#dotori-phone-thread{background:#e9eef2;border-radius:14px;overflow:hidden;border:1px solid #d6dde2}#dotori-phone-list{padding:12px;max-height:48dvh;overflow:auto}#dotori-phone-from{display:flex;align-items:center;gap:10px;background:#fff;border-bottom:1px solid #d6dde2;padding:10px 14px;font-weight:800;color:#17212b}#dotori-phone-from .av{width:38px;height:38px;border-radius:50%;background:#cfd8dc;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}#dotori-phone-from small{display:block;color:#b42318;font-size:.85rem;font-weight:800}#dotori-phone-list article{background:#fff;border-radius:4px 16px 16px 16px;padding:10px 14px;margin:10px 40px 2px 0;overflow-wrap:anywhere;box-shadow:0 1px 2px #0002}#dotori-phone-list article.new{border:2px solid #b42318;animation:dp-in .35s ease-out}#dotori-phone-list small{display:block;color:#5b6770;font-size:.82rem;margin:0 0 6px 4px}#dotori-phone-list p{font-size:1.15rem;line-height:1.6;margin:0}@keyframes dp-in{from{transform:translateY(8px);opacity:0}to{transform:none;opacity:1}}@keyframes dp-shake{0%,100%{transform:translateX(0)}20%,60%{transform:translateX(-5px)}40%,80%{transform:translateX(5px)}}#dotori-phone-launch.ring{animation:dp-shake .5s ease-in-out 3}@keyframes dp-alarm{0%,100%{transform:rotate(0) scale(1)}10%{transform:rotate(-14deg) scale(1.15)}20%{transform:rotate(12deg) scale(1.15)}30%{transform:rotate(-12deg) scale(1.15)}40%{transform:rotate(10deg) scale(1.12)}50%{transform:rotate(-8deg) scale(1.1)}60%{transform:rotate(6deg) scale(1.06)}70%{transform:rotate(0) scale(1)}}@keyframes dp-glow{0%,100%{box-shadow:0 0 0 0 #dc262699,0 4px 18px #0005}50%{box-shadow:0 0 0 14px #dc262600,0 4px 18px #0005}}#dotori-phone-ui .alarm{animation:dp-alarm .9s ease-in-out 4,dp-glow 1.2s ease-out 3.6s infinite;background:#ffe1e1!important;border-color:#dc2626!important}#dotori-phone-close{background:#20483f;color:white;border:0;width:100%;margin-top:12px}#dotori-phone-tabs{display:flex;gap:8px;margin:-6px 0 12px}#dotori-phone-tabs button{flex:1;background:#eef2f0;border:2px solid #cfd8d3;color:#20483f}#dotori-phone-tabs button.on{background:#20483f;color:#fff;border-color:#20483f}#dotori-dial-input{width:100%;box-sizing:border-box;font:800 1.6rem ui-monospace,Consolas,monospace;letter-spacing:.06em;text-align:center;padding:12px;border:3px solid #20483f;border-radius:14px;background:#fff}#dotori-dial-chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}#dotori-dial-chips button{background:#fff4c9;border:2px solid #d8be77;color:#5b4300;min-height:38px;padding:6px 12px}#dotori-dial-pad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}#dotori-dial-pad button{background:#fff;border:2px solid #d6dde2;font-size:1.35rem;min-height:52px}#dotori-dial-go{width:100%;background:#16a34a;color:#fff;border:0;font-size:1.25rem!important;min-height:58px!important}#dotori-dial-status{margin:8px 0;font-weight:800;color:#b42318;min-height:1.2em}#dotori-dial-log article{background:#fff;border:2px solid #d6dde2;border-radius:14px;padding:10px 14px;margin:8px 0;line-height:1.6}#dotori-dial-log b{display:block}#dotori-dial-log em{font-style:normal;color:#5b6770;font-size:.9rem}@media(max-width:600px){#dotori-phone-launch{right:12px;bottom:92px;max-width:calc(100vw - 24px);font-size:21px!important;min-height:62px!important;padding:12px 18px!important}#dotori-phone-launch{padding-left:76px!important}#dotori-phone-launch::before{width:62px;height:72px;left:8px}#dotori-phone-panel{padding:16px}}</style><div id="dotori-phone-box"><button id="dotori-phone-launch" type="button">📱 나의 폰</button><style>#dotori-phone-pocket{position:fixed;right:24px;bottom:184px;z-index:999990;background:#fff!important;color:#5b4300!important;border:2px solid #b88720!important;border-radius:999px!important;min-height:44px!important;padding:8px 18px!important;font-size:17px!important;font-weight:800!important;box-shadow:0 2px 8px #0003}#dotori-phone-tab{display:none;position:fixed;right:0;bottom:266px;z-index:999990;width:96px;height:96px;min-height:96px!important;box-sizing:border-box;padding:0!important;align-items:center;justify-content:center;background:#fff4c9!important;border:3px solid #b88720!important;border-right:0!important;border-radius:22px 0 0 22px!important;font-size:42px!important;box-shadow:0 4px 14px #0004}#dotori-phone-tab[data-new]::after{content:attr(data-new);position:absolute;top:-8px;left:-8px;background:#b42318;color:#fff;border-radius:999px;min-width:22px;height:22px;font-size:13px;font-weight:900;display:flex;align-items:center;justify-content:center}#dotori-phone-ui.pocket #dotori-phone-launch,#dotori-phone-ui.pocket #dotori-phone-pocket{display:none!important}#dotori-phone-ui.pocket #dotori-phone-tab{display:flex}@media(max-width:600px){#dotori-phone-pocket{right:14px;bottom:160px}}</style><button id="dotori-phone-pocket" type="button" title="폰을 주머니에 넣어 화면을 가리지 않게 해요">👖 넣기 ⌄</button></div><style>#dotori-phone-box{position:fixed;right:22px;bottom:64px;z-index:999990;display:flex;flex-direction:column;border:3px solid #b88720;border-radius:22px;background:#fff4c9;box-shadow:0 4px 18px #0005;max-width:calc(100vw - 24px)}#dotori-phone-box #dotori-phone-launch{position:relative!important;right:auto!important;bottom:auto!important;border:0!important;border-radius:19px!important;box-shadow:none!important;max-width:none}#dotori-phone-box #dotori-phone-pocket{position:absolute!important;top:-17px;right:14px;bottom:auto!important;border:2px solid #fff!important;border-radius:999px!important;box-shadow:0 2px 8px #0005!important;background:#B45309!important;color:#fff!important;font-weight:900!important;min-height:32px!important;padding:3px 12px!important;font-size:14px!important;z-index:2}#dotori-phone-box #dotori-phone-pocket:hover{background:#92400E!important}#dotori-phone-ui.pocket #dotori-phone-box{display:none!important}body:has(#dotori-phone-ui:not(.pocket)) #dotori-helper{bottom:212px!important}@media(max-width:600px){#dotori-phone-box{right:12px;bottom:56px}}</style><button id="dotori-phone-tab" type="button" aria-label="주머니에서 폰 꺼내기" title="주머니에서 폰 꺼내기">📱</button><div id="dotori-phone-cover"><section id="dotori-phone-panel" role="dialog" aria-modal="true" aria-labelledby="dotori-phone-title" tabindex="-1"><h2 id="dotori-phone-title">📱 나의 폰 · 문자</h2><div id="dotori-phone-tabs"><button type="button" data-tab="sms">💬 문자</button><button type="button" data-tab="call">📞 전화</button></div><div id="dotori-phone-sms"><div id="dotori-phone-thread"><div id="dotori-phone-from"><span class="av">👤</span><div>010-6620-1184<small>⚠️ 저장되지 않은 번호</small></div></div><div id="dotori-phone-list"></div></div></div><div id="dotori-phone-call" style="display:none"><input id="dotori-dial-input" inputmode="tel" maxlength="16" placeholder="010-0000-0000" autocomplete="off"><div id="dotori-dial-chips"></div><div id="dotori-dial-pad"></div><button type="button" id="dotori-dial-go">📞 전화 걸기</button><div id="dotori-dial-status" role="status"></div><div id="dotori-dial-log"></div></div><button type="button" id="dotori-phone-close">확인하고 닫기</button></section></div>';
 D.body.appendChild(root);state.root=root;
 const cover=root.querySelector('#dotori-phone-cover'), panel=root.querySelector('#dotori-phone-panel'), list=root.querySelector('#dotori-phone-list'),launch=root.querySelector('#dotori-phone-launch'),close=root.querySelector('#dotori-phone-close');
 const tabs=root.querySelectorAll('#dotori-phone-tabs button'),smsBox=root.querySelector('#dotori-phone-sms'),callBox=root.querySelector('#dotori-phone-call'),title=root.querySelector('#dotori-phone-title');
 const dialInput=root.querySelector('#dotori-dial-input'),chips=root.querySelector('#dotori-dial-chips'),pad=root.querySelector('#dotori-dial-pad'),goBtn=root.querySelector('#dotori-dial-go'),status=root.querySelector('#dotori-dial-status'),log=root.querySelector('#dotori-dial-log');
 state.tab=state.tab||'sms';
 state.setTab=(k)=>{state.tab=(k==='call'&&state.dial)?'call':'sms';smsBox.style.display=state.tab==='sms'?'':'none';callBox.style.display=state.tab==='call'?'':'none';tabs.forEach(b=>b.classList.toggle('on',b.dataset.tab===state.tab));root.querySelector('#dotori-phone-tabs').style.display=state.dial?'flex':'none';title.textContent='📱 나의 폰 · '+(state.tab==='call'?'전화':'문자');};
 tabs.forEach(b=>b.onclick=()=>{state.setTab(b.dataset.tab);if(state.tab==='call')dialInput.focus({preventScroll:true});});
 ['1','2','3','4','5','6','7','8','9','-','0','⌫'].forEach(k=>{const b=D.createElement('button');b.type='button';b.textContent=k;b.onclick=()=>{dialInput.value=k==='⌫'?dialInput.value.slice(0,-1):(dialInput.value+k).slice(0,16);};pad.appendChild(b);});
 // 전화 걸기: 화면 뒤에 숨겨 둔 Streamlit 입력칸에 번호를 넣고 버튼을 눌러, 게임 판정(파이썬)으로 보내요.
 goBtn.onclick=()=>{const v=dialInput.value.trim();if(!v){status.textContent='번호를 입력해 주세요.';return;}
  // 배포된 앱은 바깥 틀(iframe) 안에서 돌아서, 숨은 입력칸은 이 스크립트가 실행된 앱 문서(APP)에 있어요.
  const box=APP.document.querySelector('.st-key-phone_dial_bridge')||D.querySelector('.st-key-phone_dial_bridge'),inp=box&&box.querySelector('input'),btn=box&&box.querySelector('button');
  if(!inp||!btn){status.textContent='지금은 전화를 걸 수 없어요. 게임 화면에서 다시 시도해 주세요.';return;}
  const view=inp.ownerDocument.defaultView;Object.getOwnPropertyDescriptor(view.HTMLInputElement.prototype,'value').set.call(inp,v);inp.dispatchEvent(new view.Event('input',{bubbles:true}));
  status.textContent='📞 연결 중…';state.tab='call';state.awaitDial=true;W.setTimeout(()=>btn.click(),120);dialInput.value='';};
 dialInput.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();goBtn.click();}});
 state.drawCall=()=>{const d=state.dial;if(!d)return;chips.replaceChildren();
  if(d.numbers&&d.numbers.length){const cap=D.createElement('small');cap.textContent='증거에서 찾은 번호 (누르면 입력돼요 · 정답 표시 아님): ';cap.style.width='100%';chips.appendChild(cap);d.numbers.forEach(n=>{const b=D.createElement('button');b.type='button';b.textContent=n;b.onclick=()=>{dialInput.value=n;};chips.appendChild(b);});}
  status.textContent=d.note||'';log.replaceChildren();
  (d.calls||[]).slice().reverse().forEach(c=>{const a=D.createElement('article'),h=D.createElement('b'),s=D.createElement('em'),body=D.createElement('div');h.textContent=c.title;s.textContent=c.name+' · '+c.number+' · '+c.status;body.innerHTML='';(c.lines||[]).forEach(l=>{const p=D.createElement('div');p.textContent=l[0]+': '+l[1];body.appendChild(p);});const n=D.createElement('div');n.textContent=c.note;n.style.color='#5b6770';body.appendChild(n);const rp=D.createElement('button');rp.type='button';rp.textContent='🔊 통화 다시 듣기';rp.style.cssText='margin-top:8px;background:#eef2ff;border:2px solid #6366f1;color:#3730a3;min-height:40px;padding:6px 12px';rp.onclick=()=>state.playCall(c);a.append(h,s,body,rp);log.appendChild(a);});};
 state.playCall=(c)=>{try{jkCall(D,W,APP.__jamkkanSound||W.__jamkkanSound||null,{name:c.name,number:c.number,avatar:c.avatar||'👤',lines:c.voice||c.lines.map(l=>[l[0],l[1],'']),pitch:payload.pitch||{},verdict:c.verdict||'',safe:!!c.safe,danger:!!c.danger,status:c.status});}catch(e){}};
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
  state.drawCall();state.setTab(state.tab);
 };
 state.show=()=>{
  state.focus=D.activeElement;state.draw();state.open=true;cover.style.display='flex';close.focus({preventScroll:true});
 };
 state.hide=()=>{
 // 닫으면 다음에 열 때는 문자 탭부터 보여요(전화는 ‘나의 폰에서 전화 걸기’로 바로 열려요)
  state.open=false;state.tab='sms';cover.style.display='none';
  for(const m of state.messages)state.seen.add(m.id);
  launch.textContent=state.messages.length?'📱 나의 폰 · 받은 문자 '+state.messages.length:'📱 나의 폰 · 새 문자 없음';
  if(state.focus&&state.focus.isConnected)state.focus.focus({preventScroll:true});
 };
 launch.onclick=()=>{launch.classList.remove('alarm');state.show();};
 // 폰 주머니에 넣기: 큰 버튼을 접어 화면 오른쪽 끝의 작은 손잡이로 바꿔요. 손잡이를 누르면 다시 꺼내요.
 const pocketBtn=root.querySelector('#dotori-phone-pocket'),tab=root.querySelector('#dotori-phone-tab');
 pocketBtn.onclick=()=>{state.pocket=true;root.classList.add('pocket');};
 tab.onclick=()=>{state.pocket=false;root.classList.remove('pocket');tab.classList.remove('alarm');tab.removeAttribute('data-new');};
 if(state.pocket)root.classList.add('pocket');
 // 깡지 도우미와 겹치지 않게: 앱 화면(부모 창)에 직접 감시 코드를 심어, 이 칸이 다시 그려져도 계속 동작해요.
 if(!W.__dpLiftInstalled){W.__dpLiftInstalled=1;const sc=D.createElement('script');sc.textContent="setInterval(function(){try{var h=document.getElementById('dotori-helper'),ui=document.getElementById('dotori-phone-ui'),box=document.getElementById('dotori-phone-box');if(!h)return;if(!ui||!box||ui.classList.contains('pocket')||!box.offsetParent){h.style.removeProperty('bottom');return;}var t=box.getBoundingClientRect().top;if(t>0)h.style.setProperty('bottom',(Math.ceil(innerHeight-t)+28)+'px','important');}catch(e){}},400);";D.head.appendChild(sc);}
 state.openCall=()=>{state.tab='call';launch.classList.remove('alarm');state.show();dialInput.focus({preventScroll:true});};close.onclick=()=>state.hide();
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
 // 주머니에 넣어 둔 상태면 손잡이에 새 문자 수를 띄우고 흔들어요.
 if(state.pocket){const tb=state.root.querySelector('#dotori-phone-tab');tb.setAttribute('data-new',fresh.length);tb.classList.remove('alarm');void tb.offsetWidth;tb.classList.add('alarm');}
 phoneButton.innerHTML='📱 나의 폰 <span style="display:inline-block;background:#b42318;color:white;border-radius:8px;padding:3px 8px;margin-left:5px">새 문자 '+fresh.length+'</span>';
 // 힌트를 본 직후(pop=false)에는 창을 저절로 열지 않고, 버튼 흔들림·새 문자 표시만 해요.
 // 새 문자 알림음: 효과음 장치의 다른 소리에 끊기지 않게 직접 울려요(사이드바에서 효과음을 끄면 울리지 않아요).
 const ringTone=(loud)=>{try{
  const h=APP.__jamkkanSound||W.__jamkkanSound;if(!h||!h.want)return;
  const go=()=>{const c=h.ctx;if(!c||c.state!=='running')return;const vol=Math.max(.08,(h.volume||.6)*.5),t0=c.currentTime+.25;
   // 문자 도착: 휴대폰 문자 알림처럼 '띠리링 띠리링~ 띠링!' (약 1.6초)
   // 힌트 직후 경보: '삐뽀삐뽀' 경보음을 두 번 (약 2.2초)
   const notes=loud?[988,740,988,740,988,740,0,988,740,988,740,988,740]:[1319,1568,2093,0,1319,1568,2093,0,0,2093,2637];
   const step=loud?.16:.13,len=loud?.15:.12;
   notes.forEach((f,k)=>{if(!f)return;const at=t0+k*step;
    [['square',1],['triangle',.7]].forEach(([type,mul])=>{const o=c.createOscillator(),g=c.createGain();
     o.type=type;o.frequency.setValueAtTime(f*(type==='triangle'?.5:1),at);
     g.gain.setValueAtTime(.0001,at);g.gain.linearRampToValueAtTime(vol*mul*(type==='square'?.45:1),at+.01);g.gain.exponentialRampToValueAtTime(.0001,at+len);
     o.connect(g);g.connect(c.destination);o.start(at);o.stop(at+len+.02);});});};
  if(h.ctx&&h.ctx.state==='running')go();else if(h.activate)h.activate().then(go).catch(()=>{});
 }catch(e){}};
 // 화면 위쪽 가운데에 '새 문자' 알림 띠를 잠깐 띄워요.
 const banner=D.createElement('div');
 banner.textContent='📩 새 문자 '+fresh.length+'개가 왔어요! ‘📱 나의 폰’을 눌러 확인하세요';
 banner.style.cssText='position:fixed;top:70px;left:50%;transform:translateX(-50%);z-index:999995;background:#B42318;color:#fff;font:800 18px Pretendard Variable,Pretendard,system-ui,sans-serif;padding:14px 22px;border-radius:16px;box-shadow:0 8px 24px #0006;max-width:calc(100vw - 32px);text-align:center;transition:opacity .5s';
 D.body.appendChild(banner);W.setTimeout(()=>{banner.style.opacity='0';},3500);W.setTimeout(()=>banner.remove(),4100);
 if(!state.open&&payload.pop){state.tab='sms';state.show();ringTone(false);}
 else if(state.open){state.draw();ringTone(false);}
 else{
  // 창을 열지 않을 때는 버튼을 크게 흔들고 빨갛게 깜빡이며 알람 소리로 알려요(누르면 멈춰요).
  phoneButton.classList.remove('alarm');void phoneButton.offsetWidth;phoneButton.classList.add('alarm');
  ringTone(true);
 }
}else if(state.open){state.draw();}else{state.drawCall&&state.drawCall();}
// 방금 건 전화(새 통화 기록)가 생기면 통화 화면을 열고 목소리로 들려줘요. 처음 그릴 때 이미 있던 기록은 다시 틀지 않아요.
const calls=(state.dial&&state.dial.calls)||[];
if(!state.spoken){state.spoken=new Set(calls.map(c=>c.title));}
else{const nw=calls.filter(c=>!state.spoken.has(c.title));nw.forEach(c=>state.spoken.add(c.title));if(nw.length&&state.awaitDial)state.playCall(nw[nw.length-1]);}
state.awaitDial=false;
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
  // 다른 번호를 복사하면 앞서 복사한 버튼은 다시 '📋 복사'로 돌아가요.
  root.querySelectorAll('.number-row button').forEach(other=>{if(other!==button)other.textContent='📋 복사';});
  button.textContent=ok?'✓ 복사됨':'복사 실패';
  row.querySelector('.status').textContent=ok?'':'번호를 길게 눌러 직접 복사해 주세요.';
 };
 const status=document.createElement('span');status.className='status';status.setAttribute('role','status');
 row.append(value,button,status);root.appendChild(row);
});
'''

def _btn_img(name):
    """버튼에 붙일 깡지 그림(data URL). 그림이 없으면 빈 그림이라 글자만 보여요."""
    import base64
    from pathlib import Path
    try:
        return "data:image/png;base64," + base64.b64encode((Path(__file__).resolve().parent / "assets" / name).read_bytes()).decode("ascii")
    except OSError:
        return "data:,"


def show_phone(session, messages, sender, clock_text, pop=True, dial=None, pitch=None):
    # dial: '전화' 탭에 보여 줄 내용 {numbers, calls, note}. 없으면 문자만 보여요.
    # pitch: 통화 목소리 높이·빠르기 {누가: [높이, 빠르기]}
    from voice_ui import CALL_JS
    payload={"session":session,"pop":bool(pop),"dial":dial,"pitch":pitch or {},"messages":[{"id":str(at)+"|"+text,"sender":sender,"time":clock_text(at),"text":text} for at,text,*_ in messages]}
    source=_PHONE_JS.replace("__CALLJS__",CALL_JS).replace("__BTNIMG__",_btn_img("btn_phone.png")).replace("__PAYLOAD__",json.dumps(payload,ensure_ascii=False).replace("<","\\u003c"))
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
body{margin:0;font:16px Pretendard Variable,Pretendard,system-ui;color:#20483f}
.number-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:6px 0;padding:6px;background:#f2f6f3;border-radius:10px}
.number-row>span:first-child{font-weight:700;user-select:all}
button{min-height:44px;padding:8px 12px;background:#20483f;color:white;border:2px solid #20483f;border-radius:8px;font:700 15px Pretendard Variable,Pretendard,system-ui;cursor:pointer}
.status{font-size:13px}
</style><div id="numbers"></div><script>"""+source+"</script></html>",height=len(numbers)*78+12,scrolling=True)

def clear_phone():
    # 매번 내용이 달라야 브라우저가 다시 실행해요(같은 내용이면 이전 것을 재사용해서 지우기가 안 될 수 있어요).
    st.session_state["_phone_clear_n"] = st.session_state.get("_phone_clear_n", 0) + 1
    components.html("<script>try{const t=parent.__jkTension;if(t&&t.remove)t.remove();}catch(e){}try{const s=parent.__dotoriPhone;if(s&&s.remove)s.remove();"
                    "const r=parent.document.getElementById('dotori-phone-ui');if(r)r.remove();}catch(e){}</script>"
                    f"<!-- {st.session_state['_phone_clear_n']} -->", height=0)


_TENSION_JS = r'''
(()=>{
// 남은 시간 긴장 연출: 5분 이하면 화면 가장자리가 빨갛게 숨 쉬듯 깜빡이고 심장 박동 소리가 나요. 1분 이하면 더 빨라져요.
const P=__PAYLOAD__;const A=window,D=A.document;
let T=A.__jkTension;
if(T&&T.session!==P.session){T.remove();T=null;}
if(!T){
 T=A.__jkTension={session:P.session,deadline:0};
 const el=D.createElement('div');el.id='jk-tension';
 el.innerHTML='<style>#jk-tension .v{position:fixed;inset:0;pointer-events:none;z-index:999980;box-shadow:inset 0 0 90px 22px rgba(220,38,38,.55);opacity:0;transition:opacity .4s}'
  +'#jk-tension .v.on{animation:jkt-beat var(--b,1.1s) ease-out infinite}'
  +'#jk-tension .tag{position:fixed;left:50%;top:72px;transform:translateX(-50%);z-index:999981;pointer-events:none;background:#B91C1C;color:#fff;font:900 16px Pretendard Variable,Pretendard,system-ui,sans-serif;padding:7px 16px;border-radius:999px;box-shadow:0 6px 18px #0005;display:none}'
  +'@keyframes jkt-beat{0%{opacity:.25}12%{opacity:1}24%{opacity:.45}36%{opacity:.9}70%,100%{opacity:.2}}'
  +'@media (prefers-reduced-motion:reduce){#jk-tension .v.on{animation:none;opacity:.6}}</style><div class="v"></div><div class="tag"></div>';
 D.body.appendChild(el);
 const v=el.querySelector('.v'),tag=el.querySelector('.tag');
 const beat=(fast)=>{try{const H=A.__jamkkanSound;if(!H||!H.want||!H.ctx||H.ctx.state!=='running'||(H.volume||0)<=0)return;
  const c=H.ctx,vol=Math.max(.06,(H.volume||.6)*(fast?.75:.55));
  [[0,62],[.2,52]].forEach(([off,f])=>{const o=c.createOscillator(),g=c.createGain(),at=c.currentTime+off;o.type='sine';o.frequency.setValueAtTime(f*1.6,at);o.frequency.exponentialRampToValueAtTime(f,at+.12);
   g.gain.setValueAtTime(.0001,at);g.gain.linearRampToValueAtTime(vol,at+.015);g.gain.exponentialRampToValueAtTime(.0001,at+.22);o.connect(g);g.connect(c.destination);o.start(at);o.stop(at+.25);});}catch(e){}};
 let last=0;const path=A.location.pathname;
 T.tick=()=>{
  const left=(T.deadline-Date.now())/1000;
  if(A.location.pathname!==path||left<=0||!D.querySelector('.st-key-escape_tension_anchor')){T.remove();return;}
  const on=left<=300,fast=left<=60;
  v.classList.toggle('on',on);v.style.setProperty('--b',fast?'.6s':'1.1s');
  tag.style.display=on?'block':'none';
  if(on){const m=Math.floor(left/60),s=Math.floor(left%60);tag.textContent=(fast?'🚨 1분도 안 남았어요! ':'💓 서두르세요! 남은 시간 ')+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');}
  const gap=fast?600:1100;if(on&&Date.now()-last>=gap){last=Date.now();beat(fast);}
 };
 T.timer=A.setInterval(()=>T.tick(),100);
 T.remove=()=>{A.clearInterval(T.timer);el.remove();if(A.__jkTension===T)A.__jkTension=null;};
}
T.deadline=Date.now()+P.left*1000;
})();
'''


def tension(session, seconds_left):
    """방탈출 남은 시간 긴장 연출을 깔아 둬요(앱 화면에서 스스로 1초마다 남은 시간을 계산해요)."""
    payload = {"session": str(session), "left": max(0.0, float(seconds_left))}
    source = _TENSION_JS.replace("__PAYLOAD__", json.dumps(payload))
    # 눈에 보이지 않는 장치라 화면에 빈칸이 생기지 않게 자리를 차지하지 않도록 해요.
    with st.container(key="escape_tension_anchor"):
        st.markdown("<style>.st-key-escape_tension_anchor{position:absolute!important;width:1px;height:0!important;overflow:hidden}</style>", unsafe_allow_html=True)
        st.session_state["_tension_n"] = st.session_state.get("_tension_n", 0) + 1
        components.html("<script>const d=parent.document;const s=d.createElement('script');s.textContent="
                        + json.dumps(source).replace("<", "\\u003c") + ";d.head.appendChild(s);s.remove();</script>"
                        f"<!-- {st.session_state['_tension_n']} -->", height=0)
