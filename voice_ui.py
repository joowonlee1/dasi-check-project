"""사기범 목소리 통화 연출: 브라우저 음성 합성(Web Speech API)으로 지어낸 대사를 실제 목소리로 읽어 줘요.

- 키가 필요 없고, 소리는 사용자의 브라우저에서만 만들어져요(서버로 아무것도 보내지 않아요).
- 한국어 목소리가 없는 기기나 사이드바에서 효과음을 끈 경우에는 자막만 차례로 보여 줘요.
- 대사는 모두 교육용 가상 대사예요.
"""
import json
import streamlit as st
import streamlit.components.v1 as components

# 통화 화면을 그리고 대사를 읽는 함수. (D: 화면을 그릴 문서, SW: 목소리를 낼 창, H: 효과음 엔진, data: 통화 내용)
CALL_JS = r'''
(function(D,SW,H,data){
 try{const old=D.getElementById('jk-call');if(old){if(old.__stop)old.__stop();old.remove();}}catch(e){}
 const soundOn=()=>!!(H&&H.want&&(H.volume||0)>0);
 const want=soundOn();
 const synth=SW&&SW.speechSynthesis;
 const root=D.createElement('div');root.id='jk-call';root.setAttribute('translate','no');root.className='notranslate';
 root.innerHTML='<style>#jk-call{position:fixed;inset:0;z-index:1000002;background:rgba(8,15,25,.9);display:flex;align-items:center;justify-content:center;padding:16px;font-family:Pretendard Variable,Pretendard,system-ui,sans-serif}'
 +'#jk-call .cd{width:min(470px,100%);max-height:92dvh;overflow:auto;background:linear-gradient(180deg,#1e293b,#0b1220);color:#fff;border-radius:30px;padding:22px 20px 18px;text-align:center;box-shadow:0 20px 60px #000a;border:2px solid #334155;box-sizing:border-box}'
 +'#jk-call .stt{font-weight:800;color:#93c5fd;font-size:.95rem}#jk-call .av{width:92px;height:92px;border-radius:50%;margin:14px auto 8px;display:flex;align-items:center;justify-content:center;font-size:46px;background:#334155;box-shadow:0 0 0 0 #60a5fa88;animation:jkc-pulse 1.6s infinite}'
 +'#jk-call .nm{font-size:1.5rem;font-weight:900}#jk-call .no{color:#cbd5e1;font-size:.95rem;margin-top:2px}'
 +'#jk-call .wave{display:flex;gap:4px;justify-content:center;align-items:flex-end;height:26px;margin:12px 0 6px;opacity:.25;transition:opacity .2s}#jk-call .wave.on{opacity:1}#jk-call .wave i{width:5px;background:#60a5fa;border-radius:3px;height:6px}#jk-call .wave.on i{animation:jkc-bar .7s ease-in-out infinite}'
 +'#jk-call .wave i:nth-child(2){animation-delay:.1s!important}#jk-call .wave i:nth-child(3){animation-delay:.2s!important}#jk-call .wave i:nth-child(4){animation-delay:.3s!important}#jk-call .wave i:nth-child(5){animation-delay:.15s!important}#jk-call .wave i:nth-child(6){animation-delay:.25s!important}'
 +'#jk-call .sub{background:#f8fafc;color:#0f172a;border-radius:18px;padding:14px 16px;min-height:64px;text-align:left;font-size:1.18rem;line-height:1.6;font-weight:700;word-break:keep-all}#jk-call .sub b{display:inline-block;background:#1e3a8a;color:#fff;border-radius:999px;padding:1px 10px;font-size:.85rem;margin-right:6px;vertical-align:2px}'
 +'#jk-call .wn{display:none;margin:10px 0 0;background:#fee2e2;color:#991b1b;border:3px solid #dc2626;border-radius:14px;padding:10px 14px;font-weight:900;font-size:1.05rem;line-height:1.45;text-align:left;word-break:keep-all;text-wrap:balance;animation:jkc-shake .5s 2}#jk-call .wn.ok{background:#dcfce7;color:#14532d;border-color:#16a34a;animation:none}'
 +'#jk-call .hs{margin-top:10px;text-align:left;max-height:150px;overflow:auto}#jk-call .hs div{color:#cbd5e1;font-size:.92rem;line-height:1.5;padding:4px 2px;border-top:1px dashed #334155}#jk-call .hs div.w{color:#fca5a5}'
 +'#jk-call .nt{color:#94a3b8;font-size:.8rem;margin-top:8px}#jk-call .end{margin-top:14px;width:100%;min-height:56px;border:0;border-radius:999px;background:#dc2626;color:#fff;font:900 1.15rem Pretendard Variable,Pretendard,system-ui;cursor:pointer}#jk-call .end.done{background:#16a34a}'
 +'@keyframes jkc-pulse{0%{box-shadow:0 0 0 0 #60a5fa88}100%{box-shadow:0 0 0 22px #60a5fa00}}@keyframes jkc-bar{0%,100%{height:6px}50%{height:26px}}@keyframes jkc-shake{0%,100%{transform:translateX(0)}25%,75%{transform:translateX(-6px)}50%{transform:translateX(6px)}}'
 +'@media (prefers-reduced-motion:reduce){#jk-call *{animation:none!important}}</style>'
 +'<div class="cd" role="dialog" aria-modal="true" aria-label="통화 화면"><div class="stt">📞 <span class="st">연결 중…</span> · <span class="tm">00:00</span></div>'
 +'<div class="av"></div><div class="nm"></div><div class="no"></div><div class="wave"><i></i><i></i><i></i><i></i><i></i><i></i></div>'
 +'<div class="sub">…</div><div class="wn"></div><div class="hs"></div><div class="nt"></div><button type="button" class="end">📵 통화 끊기</button></div>';
 D.body.appendChild(root);
 const q=s=>root.querySelector(s),sub=q('.sub'),wn=q('.wn'),hs=q('.hs'),wave=q('.wave'),stt=q('.st'),tm=q('.tm'),end=q('.end'),nt=q('.nt');
 q('.av').textContent=data.avatar||'👤';q('.nm').textContent=data.name||'';q('.no').textContent=data.number||'';
 const retry=D.createElement('button');retry.type='button';retry.textContent='🔊 음성 재생하기';retry.className='end';retry.style.background='#2563eb';retry.hidden=true;end.before(retry);
 let alive=true,t0=null,elapsed=0,heard=false,completed=false,timers=[],currentUtterance=null,attempt=0;
 const pauseTime=()=>{if(t0!==null){elapsed+=Date.now()-t0;t0=null;}};
 const startTime=()=>{if(t0===null)t0=Date.now();};
 const retryLabel=()=>{retry.textContent=completed&&heard?"🔊 다시 듣기":heard?"🔊 이어 듣기":"🔊 음성 재생하기";};
 const later=(f,ms)=>{const id=SW.setTimeout(()=>{if(alive)f();},ms);timers.push(id);return id;};
 const clock=SW.setInterval(()=>{const s=Math.floor((elapsed+(t0===null?0:Date.now()-t0))/1000);tm.textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');},500);
 const stop=()=>{alive=false;attempt++;currentUtterance=null;SW.clearInterval(clock);timers.forEach(i=>SW.clearTimeout(i));try{synth&&synth.cancel();}catch(e){}};
 root.__stop=stop;
 const close=()=>{stop();root.remove();};
 end.onclick=close;root.addEventListener('keydown',e=>{if(e.key==='Escape')close();});end.focus({preventScroll:true});
 // 통화 연결음 '뚜르르'(효과음이 켜져 있을 때만)
 const ring=()=>{try{if(!want||!H.ctx||H.ctx.state!=='running')return;const c=H.ctx,v=Math.max(.05,(H.volume||.6)*.25);
  [0,1.25].forEach(off=>{[440,480].forEach(f=>{const o=c.createOscillator(),g=c.createGain(),at=c.currentTime+off;o.frequency.value=f;
   g.gain.setValueAtTime(.0001,at);g.gain.linearRampToValueAtTime(v,at+.03);g.gain.setValueAtTime(v,at+.9);g.gain.exponentialRampToValueAtTime(.0001,at+1);
   o.connect(g);g.connect(c.destination);o.start(at);o.stop(at+1.05);});});}catch(e){}};
 const KO=()=>{try{return (synth?synth.getVoices():[]).filter(v=>/^ko/i.test((v.lang||'').replace('_','-')));}catch(e){return [];}};const MALE=/injoon|hyunsu|bongjin|gookmin|jimin|male|남성/i,FEMALE=/sunhi|heami|yuna|seoyeon|female|여성|google/i;const score=v=>(/natural|neural|online/i.test(v.name)?6:0)+(/google/i.test(v.name)?3:0)+(v.localService===false?1:0);const pickVoice=(who)=>{const vs=KO().sort((a,b)=>score(b)-score(a));if(!vs.length)return null;const g=(data.gender||{})[who];if(g==='m'){const m=vs.find(v=>MALE.test(v.name));if(m)return m;}if(g==='f'){const f=vs.find(v=>FEMALE.test(v.name)&&!MALE.test(v.name));if(f)return f;}return vs[0];};
 const pitch=data.pitch||{};
 const lines=data.lines||[];
 let i=0,voice=null,speak=false;
 const finish=()=>{pauseTime();completed=true;retryLabel();retry.hidden=false;wave.classList.remove('on');stt.textContent=heard?'통화 종료':'자막 보기 완료';q('.av').style.animation='none';
  if(data.verdict){wn.textContent=data.verdict;wn.className='wn'+(data.safe?' ok':'');wn.style.display='block';}
  end.textContent='닫기';end.classList.add('done');};
 const next=(replay=false)=>{
  if(!alive)return;
  if(i>=lines.length){finish();return;}
  const [who,text,warn]=lines[i++];
  if(sub.dataset.has&&!replay){const h=D.createElement('div');h.textContent=sub.dataset.has;if(sub.dataset.w)h.className='w';hs.prepend(h);}
  sub.innerHTML='';const b=D.createElement('b');b.textContent=who;sub.append(b,D.createTextNode(text));sub.dataset.has=who+': '+text;sub.dataset.w=warn?'1':'';
  wn.style.display='none';
  if(warn){later(()=>{wn.textContent=warn;wn.className='wn';wn.style.display='block';try{H&&H.play&&want&&H.play('warn');}catch(e){}},Math.min(2200,300+text.length*45));}
  const token=++attempt;
  let moved=false,started=false;
  const fail=(message)=>{if(!alive||token!==attempt||moved)return;moved=true;attempt++;wave.classList.remove('on');pauseTime();stt.textContent=heard?'음성 재생 중단':'음성 준비 중';retryLabel();nt.style.display='block';nt.textContent=message+(heard?' 이어 듣기를 누르면 중단된 대사의 처음부터 재생해요.':' 음성 재생하기를 눌러 주세요.');retry.hidden=false;i--;currentUtterance=null;try{synth&&synth.cancel();}catch(e){}};
  const go=()=>{if(!alive||token!==attempt||moved)return;moved=true;currentUtterance=null;wave.classList.remove('on');later(()=>next(),warn?1500:600);};
  const guess=1600+text.length*190;
  if(speak){
   try{const u=new SW.SpeechSynthesisUtterance(text);currentUtterance=u;u.lang='ko-KR';const vv=pickVoice(who)||voice;if(vv)u.voice=vv;const p=pitch[who]||[1,1];const male=vv&&MALE.test(vv.name);u.pitch=(male&&(data.gender||{})[who]==='m')?1:p[0];u.rate=p[1];u.volume=Math.min(1,(H&&H.volume)||.8);
    u.onstart=()=>{if(alive&&token===attempt){started=true;heard=true;startTime();stt.textContent=data.status||'통화 중';wave.classList.add('on');}};u.onend=go;
    u.onerror=()=>fail('목소리를 재생하지 못했어요.');
    synth.speak(u);
    later(()=>{if(!started)fail('음성이 시작되지 않았어요.');},3500);
    later(()=>fail('음성 재생이 멈췄어요.'),Math.max(20000,guess+12000));
   }catch(e){fail('이 브라우저에서 음성을 시작하지 못했어요.');}
  }else{wave.classList.add('on');later(go,guess);}
 };
 retry.onclick=()=>{if(!alive)return;retryLabel();voice=pickVoice('');speak=!!(soundOn()&&synth&&typeof SW.SpeechSynthesisUtterance==='function');if(!speak){nt.style.display='block';nt.textContent=!soundOn()?'사이드바에서 효과음을 켜고 음량을 올린 뒤 다시 눌러 주세요.':'이 브라우저에서 음성 기능을 사용할 수 없어요. 다른 브라우저로 열어 주세요.';return;}if(completed){i=0;completed=false;heard=false;elapsed=0;t0=null;tm.textContent='00:00';hs.innerHTML='';delete sub.dataset.has;delete sub.dataset.w;end.textContent='📵 통화 끊기';end.classList.remove('done');q('.av').style.animation='';}retry.hidden=true;nt.style.display='none';stt.textContent='음성 준비 중';next(true);};

 const begin=()=>{voice=pickVoice('');speak=!!(soundOn()&&synth&&typeof SW.SpeechSynthesisUtterance==='function');
  stt.textContent=speak?'음성 준비 중':soundOn()?'음성 준비 중':'자막 재생 중';q('.av').style.background=data.safe?'#166534':(data.danger?'#7f1d1d':'#334155');
  if(soundOn()&&!speak){nt.style.display='block';nt.textContent='이 브라우저에서 음성 기능을 사용할 수 없어요. 자막으로 보여 드려요.';speak=false;startTime();stt.textContent='자막 재생 중';next();return;}
  if(!speak){startTime();nt.textContent='🔇 효과음이 꺼져 있어서 자막으로만 보여 줘요. (사이드바 🔊 효과음)';}
  else{nt.textContent='';nt.style.display='none';}
  next();};
 // 목소리 목록이 비어 있어도 lang=ko-KR로 기본 한국어 음성을 요청합니다.
 // iPad에서도 사용자 터치와 같은 호출 안에서 음성을 시작합니다.
 // 연결음·목소리 목록 타이머 뒤로 음성 시작을 미루지 않습니다.
 begin();

})
'''

_BUTTON_HTML = r'''<!doctype html><html lang="ko"><meta charset="utf-8"><style>
body{margin:0;font-family:Pretendard Variable,Pretendard,system-ui,sans-serif}
button{width:100%;height:52px;box-sizing:border-box;border-radius:14px;border:2px solid __BORDER__;background:__BG__;color:__FG__;font:800 1.08rem Pretendard Variable,Pretendard,system-ui;cursor:pointer;box-shadow:0 2px 0 __SHADOW__;display:flex;align-items:center;justify-content:center;gap:8px}
button:active{transform:translateY(1px);box-shadow:0 1px 0 __SHADOW__}
@keyframes ring{0%,100%{transform:rotate(0)}20%{transform:rotate(-14deg)}40%{transform:rotate(12deg)}60%{transform:rotate(-8deg)}80%{transform:rotate(6deg)}}
.ic{display:inline-block;animation:ring 1s ease-in-out infinite}
</style><button type="button" id="b"><span class="__ICCLASS__">__ICON__</span><span>__LABEL__</span></button><script>
const data=__DATA__;const play=__CALLJS__;
// 화면이 열릴 때 목록 로딩을 먼저 요청합니다. 실제 발화는 클릭 때만 합니다.
const preloadVoices=()=>{try{window.speechSynthesis?.getVoices();}catch(e){}};
preloadVoices();
try{window.speechSynthesis?.addEventListener('voiceschanged',preloadVoices);}catch(e){}
window.addEventListener('pagehide',()=>{try{window.speechSynthesis?.removeEventListener('voiceschanged',preloadVoices);}catch(e){}});

document.getElementById('b').onclick=()=>{let D=document,H=null;try{D=parent.document;H=parent.__jamkkanSound||null;}catch(e){}
 const go=()=>play(D,window,H,data);
 go(); /* 음성을 터치 이벤트 안에서 바로 시작해요. */};
</script></html>'''

_TONES = {
    "danger": ("#dc2626", "#fee2e2", "#7f1d1d", "#fca5a5"),
    "calm": ("#20483f", "#ecfdf5", "#14532d", "#86efac"),
}


def call_button(data, label, key, tone="danger", icon="📞"):
    """누르면 통화 화면이 열리고 대사를 목소리로 읽어 주는 버튼.
    data = {name, number, avatar, lines:[[누가, 대사, 경고문 또는 ""]], pitch:{누가:[높이, 빠르기]}, verdict, safe, danger}"""
    border, bg, fg, shadow = _TONES.get(tone, _TONES["danger"])
    html = (_BUTTON_HTML.replace("__BORDER__", border).replace("__BG__", bg).replace("__FG__", fg).replace("__SHADOW__", shadow)
            .replace("__LABEL__", label.replace("<", "&lt;"))
            .replace("__ICCLASS__", "ic" if icon == "📞" else "").replace("__ICON__", icon)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("<", "\\u003c"))
            .replace("__CALLJS__", CALL_JS))
    # key는 같은 버튼끼리 구분하려는 표시예요(같은 화면에 여러 번 그려져도 괜찮게 위젯 키로는 쓰지 않아요).
    components.html(html + f"<!-- {key} -->", height=54)
