"""큐싱 노노그램: 숫자 단서로 칸을 칠해 사기단이 붙인 가짜 QR 스티커 그림을 복원하는 퍼즐.

- 1단계 5×5(스마트폰), 2단계 8×8(자물쇠), 3단계 10×10(QR 코드 모양)
- 세 그림 모두 '한 줄씩 따져 보기'만으로 끝까지 풀리고, 답이 하나뿐인지 프로그램으로 확인했습니다(찍기 불필요).
- 마지막에 노노그램 단서가 런 길이 부호화(RLE)와 같은 원리라는 것을 공개합니다.
모든 장소·스티커·주소는 교육용 가상 내용입니다.
"""
from play_ui import intro, bridge
import json
from investigation_ui import attach

import streamlit as st
import dotori_data as dd
from mascot_ui import show_key_question, show_mascot
from nonogram_component_ui import create_nonogram_component

with intro("12", suffix=""):
    st.title("🧩 큐싱 노노그램")
    show_key_question("숫자 단서로 칸을 칠해 **찢긴 QR 스티커**를 복원하세요. 그림을 복원한 뒤 **출처·목적지·요구를 조사**하세요.", "🧩")
    show_mascot("puzzle", "숫자는 ‘연달아 칠한 칸 수’예요. 줄마다 따져 보면 찍지 않아도 끝까지 풀려요!", width=100)

    st.info("이번 활동은 ‘그림 복원’과 ‘안전성 판단’을 구별하는 연습이에요. 숫자로 그림을 정확히 복원해도 QR의 목적지가 안전하다는 뜻은 아니에요.")
    with st.expander("그림을 숫자로 표현하는 RLE 먼저 알아보기", expanded=True):
        st.markdown("**RLE(런 길이 부호화)**는 같은 값이 연속되는 길이를 적는 방법이에요. "
                    "예: **■■■□□■■ → 검정부터 3, 2, 2**. 시작 색과 빈칸 길이까지 알면 원래 줄을 복원할 수 있어요.")
        st.markdown("노노그램 단서 **3, 2**는 칠한 구간만 알려 줘요. 빈칸 길이가 빠져 있어서 "
                    "가로·세로 단서를 함께 비교해야 해요. 일반 RLE와 정보량이 같지는 않아요.")
        st.caption("복원하는 것은 교육용 그림이며, 실제 QR 데이터를 해독하는 과정은 아니에요.")

DATA = {
    "stages": [
        {
            "name": "증거 조각 ①",
            "title": "📱 스마트폰",
            "pic": ["#####", "#...#", "#...#", "#####", "##.##"],
            "story": "주차장 바닥에서 찢긴 스티커 조각을 찾았어요. 조각에 남은 숫자로 그림을 복원해 봐요.",
            "lesson": "사람들은 주차 요금을 내려고 휴대폰으로 정산기의 QR 코드를 찍었어요. QR을 읽으면 주소가 표시되거나 앱 설정에 따라 연결될 수 있어요. 링크를 열기 전 목적지와 이용하려던 서비스를 확인해야 해요.",
        },
        {
            "name": "증거 조각 ②",
            "title": "🔒 자물쇠",
            "pic": ["..####..", ".##..##.", ".#....#.", "########", "###..###", "###..###", "########", "########"],
            "story": "두 번째 조각은 QR을 찍은 사람들이 본 결제 화면에 있던 그림이에요.",
            "lesson": "가짜 결제 화면 주소창에도 자물쇠가 떠 있었어요. 자물쇠는 ‘주고받는 내용이 암호화됐다’는 뜻이지 ‘믿을 만한 사이트’라는 뜻은 아니에요. 가짜 사이트에도 자물쇠는 뜰 수 있어요.",
        },
        {
            "name": "증거 조각 ③",
            "title": "🔳 QR 코드",
            "pic": ["###.##.###", "#.#..#.#.#", "###..#.###", "....#.....", "#####.##..", ".#.#.####.", "....#..#.#", "###.##.##.", "#.#.##..#.", "###....#.#"],
            "story": "마지막 조각이에요. 정산기에서 발견된 스티커 모양이에요. 복원 후 안내의 출처와 요구를 확인해야 해요.",
            "lesson": "이렇게 QR 코드로 가짜 사이트에 접속하게 만드는 수법을 ‘큐싱(QR + 피싱)’이라고 해요.",
        },
    ],
    # 3단계 비교용: 같은 모양 틀(모서리 네모 3개)을 가진 '진짜' QR 그림
    "real_qr": ["###.##.###", "#.#.##.#.#", "###.##.###", "..........", ".#.####...", ".##....#..", ".....###..", "###..#....", "#.#..#.###", "###..##.#."],
}

HTML = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;background:#FFFEFA;color:#20483F;font:16px/1.6 'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
button{font:inherit;cursor:pointer;border:0;border-radius:12px;padding:10px 14px;background:#E4F0EA;color:#173D35;font-weight:800;min-height:44px;transition:transform .15s,background .15s}
button:hover:not(:disabled){transform:translateY(-2px);background:#D7E8DF}
button:active:not(:disabled){transform:scale(.95)}
button:disabled{opacity:.45;cursor:default}
button:focus-visible{outline:3px solid #FF7A45;outline-offset:2px}
.go{background:linear-gradient(135deg,#FF7A45,#FFB347);color:#fff;box-shadow:0 5px 14px #FF7A4540}
.go:hover:not(:disabled){background:linear-gradient(135deg,#F06A35,#FFA337)}
main.wrap{max-width:980px;margin:auto;padding:6px 4px 14px}
@keyframes pop{0%{transform:scale(.6);opacity:0}65%{transform:scale(1.05);opacity:1}100%{transform:scale(1)}}
@keyframes rise{0%{transform:translateY(10px);opacity:0}100%{transform:none;opacity:1}}
@keyframes stamp{0%{transform:scale(3) rotate(-18deg);opacity:0}60%{transform:scale(.9) rotate(-12deg);opacity:1}100%{transform:scale(1) rotate(-8deg);opacity:1}}
@keyframes burst{0%{transform:translate(0,0) scale(.3);opacity:1}100%{transform:translate(var(--x),var(--y)) scale(1.2);opacity:0}}
@keyframes flash{0%,100%{box-shadow:inset 0 0 0 0 #E5484D}50%{box-shadow:inset 0 0 0 4px #E5484D}}
@keyframes glow{0%,100%{box-shadow:inset 0 0 0 3px #FF7A45}50%{box-shadow:inset 0 0 0 3px #FFD3BD}}
@keyframes wave{0%{transform:scale(.4)}60%{transform:scale(1.15)}100%{transform:scale(1)}}
.hero{background:linear-gradient(135deg,#1E5B4F,#2E8B75)!important;color:#fff;border-radius:18px;padding:10px 16px;text-align:center;animation:pop .5s ease-out both}
.boardwrap{background:linear-gradient(rgba(255,255,255,.15),rgba(255,255,255,.15)),url(__SCENEIMG__) center/cover;border-radius:20px;padding:18px 10px!important;box-shadow:inset 0 0 0 2px #D7E2DD}
.hero b{display:block;font-size:1.4rem;font-weight:900;word-break:keep-all}.hero span{opacity:.92;font-weight:600;word-break:keep-all}
.box{background:#fff;border:1.5px solid #D7E2DD;border-radius:18px;padding:14px 16px;margin:10px 0;word-break:keep-all;animation:rise .4s ease-out both}
.box h3{margin:0 0 8px;font-size:1.12rem}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0}@media (max-width:980px){.steps{grid-template-columns:repeat(2,1fr)}}
.step{background:#F4F8F6;border:1.5px solid #D7E2DD;border-radius:16px;padding:12px;text-align:center;word-break:keep-all}
.step .ic{font-size:34px}.step b.h{display:block;font-size:1.02rem;margin:2px 0}.step p{margin:0;font-size:.9rem;color:#33524A;line-height:1.5}
.exs{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:8px}
.ex{background:#F9FBF8;border:1.5px dashed #BFD4CA;border-radius:14px;padding:10px;font-size:.9rem;line-height:1.5}
.ex b{display:block;margin-bottom:4px}
.strip{display:flex;align-items:center;gap:3px;margin:4px 0;flex-wrap:wrap}
.strip .n{font-weight:900;min-width:44px;color:#B4471B;font-size:.9rem}
.strip i{display:inline-block;width:22px;height:22px;border:1.5px solid #9DBFB2;border-radius:4px;background:#fff;font-style:normal;text-align:center;line-height:19px;font-size:.8rem;color:#B42318}
.strip i.f{background:#20483F;border-color:#20483F}
.strip i.m{background:#FFE7D6;border-color:#FF7A45}
.strip i.x::after{content:'✕'}
.stages{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0}
.stages button{display:flex;flex-direction:column;align-items:center;gap:2px;background:#fff;border:2px solid #C9DCD3;padding:8px 6px}
.stages button.on,.stages button.on:hover:not(:disabled){background:#20483F;color:#fff;border-color:#20483F;box-shadow:0 0 0 4px #FF7A4555}
.stages small{font-weight:700;font-size:.8rem;opacity:.9}
.story{background:#FFF8E6;border:2px solid #F2D58A;border-radius:14px;padding:8px 12px;font-weight:700;margin:8px 0;word-break:keep-all}
.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
.mode{display:flex;border-radius:14px;overflow:hidden;border:2px solid #20483F}
.mode button{border-radius:0;background:#fff;min-width:110px}
.mode button.on,.mode button.on:hover:not(:disabled){background:#20483F;color:#fff}
.boardwrap{overflow-x:auto;padding:4px 0 8px;display:flex;justify-content:center}
table.board{border-collapse:collapse;touch-action:none;user-select:none;-webkit-user-select:none;background:rgba(255,255,255,.94);box-shadow:0 0 0 12px rgba(255,255,255,.94),0 10px 24px 10px rgba(0,0,0,.28);border-radius:4px;margin:12px;transform:rotate(-1deg)}
.board td{padding:0}
.board .cc{vertical-align:bottom;text-align:center;font-weight:900;font-size:var(--fs);line-height:1.15;padding:0 0 4px;color:#20483F;width:var(--cs)}
.board .rc{text-align:right;font-weight:900;font-size:var(--fs);padding:0 6px 0 0;white-space:nowrap;color:#20483F;letter-spacing:.06em}
.board .cc.ok,.board .rc.ok{color:#A8B8B1}
.board .cc.cur,.board .rc.cur{color:#B4471B}
.cell{width:var(--cs);height:var(--cs);border:1px solid #B9CCC3;background:#fff;cursor:pointer;position:relative;transition:background .08s}
.cell.f{background:#20483F}
.cell.x::after{content:'✕';position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#C2410C;font-weight:900;font-size:calc(var(--cs) * .55)}
.cell.b5r{border-right:2.5px solid #20483F}.cell.b5b{border-bottom:2.5px solid #20483F}
.cell.wrong{animation:flash .5s ease-in-out 3}
.cell.hint{animation:glow .7s ease-in-out 3}
.cell.hl{background:#F0F7F3}.cell.f.hl{background:#2A5A4F}
.solved .cell{cursor:default}
.solved .cell.f{background:#20483F;animation:wave .45s ease-out both}
.solved .cell.x::after{content:''}
.toast{min-height:1.4em;font-weight:800;color:#B4471B;margin:6px 0;text-align:center;word-break:keep-all}
.row{display:flex;gap:8px;flex-wrap:wrap}.row>button{flex:1}
.progress{font-weight:800;font-size:.92rem;color:#33524A}
.result{position:relative;overflow:hidden;border-radius:22px;padding:18px 14px;text-align:center;margin:12px 0;word-break:keep-all;background:linear-gradient(135deg,#FFF1C2,#D9F2E6)}
.result.fx{animation:pop .55s ease-out both}
.result .big{font-size:52px}.result b.t{display:block;font-size:1.35rem;font-weight:900}
.stars{font-size:2rem;letter-spacing:4px}.fx .stars i{display:inline-block;font-style:normal;animation:pop .4s ease-out both}
.stamp{display:inline-block;margin-top:8px;border:5px solid #16815F;color:#16815F;border-radius:12px;padding:3px 16px;font-size:1.5rem;font-weight:900;transform:rotate(-8deg);background:rgba(255,255,255,.6)}
.fx .stamp{animation:stamp .5s .5s ease-out both}
.spark{position:absolute;left:50%;top:40%;font-size:24px;opacity:0;pointer-events:none}
.fx .spark{animation:burst 1.1s ease-out both}
.lesson{background:#fff;border:2px solid #C9DCD3;border-radius:14px;padding:10px 12px;margin:10px auto 0;max-width:640px;text-align:left;font-weight:600;line-height:1.65}
.twoqr{display:flex;justify-content:center;gap:18px;flex-wrap:wrap;margin:10px 0}
.twoqr figure{margin:0;text-align:center;font-weight:800;font-size:.92rem}
.mini{display:grid;gap:1px;background:#fff;padding:6px;border-radius:8px;border:1.5px solid #C9DCD3;margin:0 auto 4px}
.mini span{width:11px;height:11px;background:#fff}.mini span.f{background:#111}
.rle{font-family:'Courier New',monospace;font-weight:800;background:#1E2B28;color:#D6F5E8;border-radius:12px;padding:10px 12px;white-space:pre-wrap;word-break:break-all;font-size:.9rem;margin:8px 0}
.rle .k{color:#FFB385}
.ctable{width:100%;border-collapse:collapse;margin:8px 0;font-size:.92rem}
.ctable th,.ctable td{border:1px solid #D7E2DD;padding:6px;text-align:center}
.ctable th{background:#E4F0EA}
.others{background:#F0F7FF;border:2px solid #B8D4F0;border-radius:14px;padding:8px 12px;margin:10px auto 0;max-width:640px;text-align:left;font-weight:700;font-size:.92rem;line-height:1.6;color:#1E3A5F;word-break:keep-all}
.still .hero,.still .box,.still .story{animation:none!important}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:720px){.steps{grid-template-columns:1fr}.step{display:flex;gap:10px;align-items:center;text-align:left}.step .ic{font-size:28px}.exs{grid-template-columns:1fr}}
@media (max-width:480px){.hero b{font-size:1.2rem}.stages small{font-size:.72rem}.mode button{min-width:0;padding:10px 10px}}
</style></head><body>
<main class="wrap" id="app"></main>
<script>
const D = __DATA__;
const IQ_THEME = 'lab';
// 증거 복원실 감식 보드(코르크판) 모양의 큰 창 (큐싱 노노그램 전용)
function boardPop(o, then){
  jkOverlay(`<div class="jk-panel" style="background:#C8A06A;background-image:radial-gradient(#B8905A 1px,transparent 1.5px);background-size:9px 9px;border:10px solid #7C5A34;border-radius:14px;padding:18px;box-shadow:0 20px 50px #0007">
   <div style="position:relative;background:#FFFDF5;border-radius:4px;padding:18px 18px 14px;box-shadow:0 6px 14px #0003;transform:rotate(-.8deg)">
    <span style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);font-size:1.6rem">📌</span>
    <div style="font-size:.85rem;font-weight:900;color:#92400E;letter-spacing:.08em">🅿️ 도토리 공영주차장 · 증거 복원실 ${o.tag?'· '+o.tag:''}</div>
    <div style="display:flex;gap:14px;align-items:center;margin-top:8px">${jkImg(o.mascot,145)}
     <div style="flex:1"><div style="font-size:1.4rem;font-weight:900;color:#3F2A12">${o.title}</div>
     <div style="margin-top:6px;line-height:1.7;color:#1F2937">${o.body}</div></div></div>
    ${o.extra||''}
    <button data-close style="margin-top:14px;width:100%;min-height:50px;border:0;border-radius:10px;background:#7C5A34;color:#FFF7E6;font:800 1.05rem Pretendard Variable,Pretendard,system-ui;cursor:pointer">${o.button||'확인했어요 ▶'}</button></div></div>`, then);
}

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const SOL = D.stages.map(s => s.pic.map(row => row.split('').map(ch => ch === '#' ? 1 : 0)));
function rle(line){ const out = []; let c = 0; for (const v of line) { if (v === 1) c++; else if (c) { out.push(c); c = 0; } } if (c) out.push(c); return out; }
const CLUES = SOL.map(g => ({rows: g.map(r => rle(r)), cols: g[0].map((_, c) => rle(g.map(r => r[c])))}));
const blank = () => SOL.map(g => g.map(r => r.map(() => 0)));
const G = {screen: 'intro', stage: 0, mode: 1, grid: blank(), solved: [false, false, false], hints: [0, 0, 0], checks: [0, 0, 0], stars: [0, 0, 0], justSolved: false};
let fresh = true;

function render(){
  setPlayActive(G.screen !== 'intro');
  const app = $('app'); app.classList.toggle('still', !fresh); fresh = false;
  if (G.screen === 'intro') return renderIntro();
  if (G.screen === 'final') return renderFinal();
  renderPlay();
}

function strip(clue, cells){ return `<div class="strip"><span class="n">${clue}</span>${cells.split('').map(ch => `<i class="${ch === '#' ? 'f' : ch === '?' ? 'm' : ch === 'x' ? 'x' : ''}"></i>`).join('')}</div>`; }

function renderIntro(){
  $('app').innerHTML = `
  <section class="hero"><span>🅿️ 도토리 공영주차장 · 증거 복원실</span><b>찢긴 QR 스티커, 숫자만으로 복원하라!</b><span>정산기에 덧붙은 수상한 스티커의 조각 데이터를 확보했어요.</span></section>
  <div class="steps">
    <div class="step"><div class="ic">🔢</div><div><b class="h">① 단서 읽기</b><p>줄 옆 숫자는 <b>연달아 칠한 칸 수</b>예요. ‘3 1’이면 3칸 묶음, 빈칸 하나 이상, 1칸 묶음.</p></div></div>
    <div class="step"><div class="ic">✏️</div><div><b class="h">② 칠하고 ✕ 치기</b><p>확실한 칸은 칠하고, 확실히 빈칸은 ✕로 표시해요. 누른 채 끌면 여러 칸을 한 번에!</p></div></div>
    <div class="step"><div class="ic">🖼️</div><div><b class="h">③ 그림 복원</b><p>모든 줄의 숫자를 맞추면 숨은 그림이 나타나고 수법이 공개돼요.</p></div></div>
    <div class="step"><div class="ic">🔍</div><div><b class="h">④ 사실 조사</b><p>그림을 복원하면 <b>그 QR을 써도 되는지</b> 자료를 읽고 판단해요. 조사를 마쳐야 다음 조각이 열려요.</p></div></div>
  </div>
  <section class="box"><h3>🔍 예시로 감 잡기 (5칸짜리 줄)</h3>
    <div class="exs">
      <div class="ex"><b>① 숫자가 줄 길이와 같으면</b>${strip('5', '#####')}5칸 줄에 ‘5’ → 전부 칠해요.</div>
      <div class="ex"><b>② 0이면</b>${strip('0', 'xxxxx')}칠할 칸이 없어요 → 전부 ✕.</div>
      <div class="ex"><b>③ 겹치는 칸 찾기 (핵심 기술!)</b>${strip('3 · 왼쪽', '###..')}${strip('3 · 오른쪽', '..###')}${strip('→ 확정', '..?..')}3칸 묶음을 끝까지 왼쪽·오른쪽으로 밀어 봐요. <b>어떻게 놓아도 겹치는 가운데 칸</b>은 반드시 칠해요.</div>
      <div class="ex"><b>④ 묶음 사이엔 빈칸</b>${strip('2 2', '##.##')}‘2 2’는 2칸 + 빈칸 + 2칸 = 딱 5칸이라 바로 확정!<br>숫자 합 + 묶음 사이 빈칸 수가 줄 길이와 같으면 한 가지뿐이에요.</div>
    </div>
    <p style="margin:10px 0 0">👉 가로줄에서 알아낸 칸이 세로줄의 실마리가 되고, 세로줄에서 알아낸 칸이 다시 가로줄의 실마리가 돼요. 이렇게 번갈아 따지면 <b>찍지 않고도</b> 끝까지 풀려요.</p>
  </section>
  <section class="box"><h3>⭐ 별 받는 법</h3>⭐ 그림 복원 · ⭐ 힌트 없이 · ⭐ ‘틀린 칸 검사’ 없이</section>
  <button class="go" style="width:100%;font-size:1.15rem;min-height:56px" onclick="startStage(0)">🧩 복원 시작하기</button>`;
}

// 복원실 안에서 바로 전 화면(시작 화면)으로 돌아가요. 칠한 칸과 기록은 그대로 남아요.
function backIntro(){ G.screen = 'intro'; fresh = true; render(); window.scrollTo(0, 0); }
function startStage(i){ if(i>0&&!iqState(i+2).done)return; G.screen = 'play'; G.stage = i; G.justSolved = false; fresh = true; render(); window.scrollTo(0, 0); }

function stageButtons(){
  return `<div class="stages">${D.stages.map((s, i) => {
    const locked = i > 0 && (!G.solved[i - 1] || !iqState(i+2).done);
    const st = G.solved[i] ? '⭐'.repeat(G.stars[i]) + '☆'.repeat(3 - G.stars[i]) : (locked ? '🔒' : `${SOL[i].length}×${SOL[i].length}`);
    return `<button class="${i === G.stage ? 'on' : ''}" ${locked ? 'disabled' : ''} onclick="startStage(${i})">${i + 1}단계 · ${esc(s.name)}<small>${st}</small></button>`;
  }).join('')}</div>`;
}

function boardHtml(st){
  const n = SOL[st].length, cl = CLUES[st], g = G.grid[st];
  const cs = n <= 5 ? 46 : n <= 8 ? 36 : 30;
  const maxCol = Math.max(...cl.cols.map(c => Math.max(1, c.length)));
  let h = `<table class="board ${G.solved[st] ? 'solved' : ''}" id="board" style="--cs:min(${cs}px, calc((100vw - 96px) / ${n}));--fs:${n <= 5 ? '1rem' : n <= 8 ? '.92rem' : '.82rem'}"><tr><td></td>`;
  cl.cols.forEach((c, ci) => { h += `<td class="cc" id="cc${ci}">${(c.length ? c : [0]).join('<br>')}</td>`; });
  h += '</tr>';
  for (let r = 0; r < n; r++) {
    h += `<tr><td class="rc" id="rc${r}">${(cl.rows[r].length ? cl.rows[r] : [0]).join(' ')}</td>`;
    for (let c = 0; c < n; c++) {
      const v = g[r][c];
      const b = (n >= 8 && c % 5 === 4 && c < n - 1 ? ' b5r' : '') + (n >= 8 && r % 5 === 4 && r < n - 1 ? ' b5b' : '');
      const delay = G.solved[st] && G.justSolved ? ` style="animation-delay:${(r + c) * .035}s"` : '';
      h += `<td class="cell${v === 1 ? ' f' : v === 2 ? ' x' : ''}${b}" data-r="${r}" data-c="${c}"${delay}></td>`;
    }
    h += '</tr>';
  }
  return h + '</table>';
}

function renderPlay(){
  const st = G.stage, s = D.stages[st];
  const n = SOL[st].length;
  $('app').innerHTML = `
  <button style="background:#fff;border:2px solid #20483F;color:#20483F;margin:0 0 8px" onclick="backIntro()">← 이전 화면으로</button>
  <section class="hero"><span>🅿️ 도토리 공영주차장 · 증거 복원실</span><b>${st + 1}단계 · ${esc(s.name)}</b><span>${n}×${n} 칸</span></section>
  ${stageButtons()}
  <div class="story">📜 ${esc(s.story)}</div>
  ${G.solved[st] ? resultHtml(st) : `
  <div class="tools"><div class="mode" role="group" aria-label="칠하기 방식">
    <button class="${G.mode === 1 ? 'on' : ''}" onclick="setMode(1)">■ 칠하기</button>
    <button class="${G.mode === 2 ? 'on' : ''}" onclick="setMode(2)">✕ 빈칸 표시</button></div>
    <span class="progress" id="prog"></span></div>`}
  <div class="boardwrap">${boardHtml(st)}</div>
  ${G.solved[st] ? '' : `<div class="toast" id="toast">💡 지금 방식: ${G.mode === 1 ? '■ 칠하기' : '✕ 빈칸 표시'} · 같은 칸을 한 번 더 누르면 지워져요.</div>
  <div class="row"><button onclick="hint()">🧭 힌트 (한 칸 알려 주기)</button><button onclick="checkWrong()">🔍 틀린 칸 검사</button><button onclick="clearBoard()">↺ 처음부터</button></div>`}`;
  bindBoard(); updateClues();
}

function setMode(m){ G.mode = m; render(); }

let painting = null;
function bindBoard(){
  const board = $('board'); if (!board || G.solved[G.stage]) return;
  const apply = (td) => {
    if (!td || !td.classList.contains('cell')) return;
    const r = +td.dataset.r, c = +td.dataset.c, g = G.grid[G.stage];
    if (g[r][c] === painting) return;
    g[r][c] = painting;
    td.classList.toggle('f', painting === 1); td.classList.toggle('x', painting === 2);
    td.classList.remove('wrong', 'hint');
  };
  board.addEventListener('pointerdown', e => {
    const td = e.target.closest('.cell'); if (!td) return;
    e.preventDefault();
    const cur = G.grid[G.stage][+td.dataset.r][+td.dataset.c];
    painting = cur === G.mode ? 0 : G.mode;
    apply(td);
  });
  board.addEventListener('pointermove', e => {
    const td = document.elementFromPoint(e.clientX, e.clientY);
    const cell = td && td.closest ? td.closest('.cell') : null;
    if (cell) highlight(+cell.dataset.r, +cell.dataset.c);
    if (painting === null) return;
    apply(cell);
  });
  board.addEventListener('pointerleave', () => highlight(-1, -1));
  window.onpointerup = () => { if (painting !== null) { painting = null; updateClues(); checkSolved(); } };
}

function highlight(r, c){
  document.querySelectorAll('.cell.hl').forEach(el => el.classList.remove('hl'));
  document.querySelectorAll('.cur').forEach(el => el.classList.remove('cur'));
  if (r < 0) return;
  document.querySelectorAll(`.cell[data-r="${r}"],.cell[data-c="${c}"]`).forEach(el => el.classList.add('hl'));
  const rc = $('rc' + r), cc = $('cc' + c); if (rc) rc.classList.add('cur'); if (cc) cc.classList.add('cur');
}

function updateClues(){
  const st = G.stage, g = G.grid[st], cl = CLUES[st], n = g.length;
  let done = 0;
  for (let r = 0; r < n; r++) { const ok = rle(g[r]).join() === cl.rows[r].join(); const el = $('rc' + r); if (el) el.classList.toggle('ok', ok); done += ok; }
  for (let c = 0; c < n; c++) { const ok = rle(g.map(row => row[c])).join() === cl.cols[c].join(); const el = $('cc' + c); if (el) el.classList.toggle('ok', ok); done += ok; }
  const p = $('prog'); if (p) p.textContent = `숫자를 맞춘 줄 ${done} / ${n * 2}`;
}

function checkSolved(){
  const st = G.stage, g = G.grid[st], sol = SOL[st];
  if (!g.every((row, r) => row.every((v, c) => (v === 1) === (sol[r][c] === 1)))) return;
  G.solved[st] = true; G.justSolved = true;
  G.stars[st] = Math.max(G.stars[st], 1 + (G.hints[st] === 0 ? 1 : 0) + (G.checks[st] === 0 ? 1 : 0));

  render();
  const box = document.querySelector('.result'); if (box) box.scrollIntoView({block: 'start', behavior: 'smooth'});
  G.justSolved = false;
  const s = D.stages[st];
  boardPop({mascot:'puzzle', tag:s.name, title:`🧩 ${esc(s.title)} 복원 완료!`, body:esc(s.lesson),
    // 큰 창은 게임 화면 밖이라 그림을 칸마다 직접 색칠해서 보여 줘요.
    extra:`<div style="display:flex;justify-content:center;margin-top:10px"><div style="display:grid;grid-template-columns:repeat(${s.pic.length},${s.pic.length>8?14:20}px);gap:2px;background:#fff;padding:8px;border:2px solid #3F2A12;border-radius:6px">${s.pic.join('').split('').map(ch=>`<i style="display:block;aspect-ratio:1;background:${ch==='#'?'#1F2937':'#F1F5F9'}"></i>`).join('')}</div></div>`,
    button:'이제 사실을 조사하러 가기 ▶'});
}

function hint(){
  const st = G.stage, g = G.grid[st], sol = SOL[st], n = g.length;
  const wrong = [], need = [];
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) {
    if (g[r][c] === 1 && !sol[r][c]) wrong.push([r, c, 2]);
    else if (g[r][c] === 2 && sol[r][c]) wrong.push([r, c, 1]);
    else if (g[r][c] === 0 && sol[r][c]) need.push([r, c, 1]);
  }
  const pick = wrong.length ? wrong[0] : need[Math.floor(Math.random() * need.length)];
  if (!pick) return;
  G.hints[st]++;
  const [r, c, v] = pick; g[r][c] = v;
  render();
  const td = document.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`); if (td) td.classList.add('hint');
  $('toast').textContent = wrong.length ? `🧭 ${r + 1}번째 줄 ${c + 1}번째 칸이 잘못돼서 고쳐 놨어요.` : `🧭 ${r + 1}번째 줄 ${c + 1}번째 칸은 칠하는 칸이에요.`;
  checkSolved();
}

function checkWrong(){
  const st = G.stage, g = G.grid[st], sol = SOL[st];
  G.checks[st]++;
  let cnt = 0;
  document.querySelectorAll('.cell').forEach(td => {
    const r = +td.dataset.r, c = +td.dataset.c, v = g[r][c];
    if ((v === 1 && !sol[r][c]) || (v === 2 && sol[r][c])) { td.classList.remove('wrong'); void td.offsetWidth; td.classList.add('wrong'); cnt++; }
  });
  $('toast').textContent = cnt ? `🔍 잘못 칠했거나 잘못 ✕ 친 칸이 ${cnt}개 있어요. 깜빡이는 칸을 확인해요.` : '🔍 지금까지 칠하고 ✕ 친 칸은 모두 맞아요!';
}

function clearBoard(){ const n = SOL[G.stage].length; G.grid[G.stage] = SOL[G.stage].map(r => r.map(() => 0)); render(); }

function miniQR(pic){ const n = pic.length; return `<div class="mini" style="grid-template-columns:repeat(${n},11px)">${pic.join('').split('').map(ch => `<span class="${ch === '#' ? 'f' : ''}"></span>`).join('')}</div>`; }

function resultHtml(st){
  if(!iqState(st+3).done)return `<section class="result"><h3>그림 복원 완료 · 이제 사실을 확인하세요</h3><p>그림만으로 안전성을 판정할 수 없어요.</p></section>`+iqHTML(st+3);
  const s = D.stages[st], stars = G.stars[st];
  const sp = ['✨', '⭐', '🧩', '🎉', '✨', '💫', '⭐', '🎉'].map((ic, k) => { const a = k * Math.PI / 4; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 140)}px;--y:${Math.round(Math.sin(a) * 100)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  const qr = st === 2 ? `<div class="twoqr"><figure>${miniQR(D.real_qr)}✅ 정산기의 진짜 QR</figure><figure>${miniQR(s.pic)}🚨 덧붙인 가짜 QR</figure></div>
    <div class="lesson">👀 두 QR 코드를 눈으로 구별할 수 있나요? <b>QR 코드는 사람이 읽을 수 없는 그림</b>이라, 진짜 위에 가짜를 붙여도 알아채기 어려워요.</div>` : '';
  const next = st < 2 ? `<button class="go" style="width:100%;margin-top:10px" onclick="startStage(${st + 1})">다음 조각 복원하기 ➡️</button>` : `<button class="go" style="width:100%;margin-top:10px" onclick="toFinal()">🏆 사건 정리 보기</button>`;
  return `<section class="result ${G.justSolved ? 'fx' : ''}"><div class="big">${s.title.split(' ')[0]}</div><b class="t">짠! ${esc(s.title)} 복원 완료</b>
    <div class="stars">${[0, 1, 2].map(k => `<i style="animation-delay:${.3 + k * .2}s">${k < stars ? '⭐' : '☆'}</i>`).join('')}</div>
    <div style="font-size:.88rem;color:#52616B">힌트 ${G.hints[st]}번 · 틀린 칸 검사 ${G.checks[st]}번</div>
    <span class="stamp">복원 완료!</span>${sp}
    <div class="lesson">🔎 ${esc(s.lesson)}</div>${qr}${othersHtml(st)}${next}</section>`;
}

function iqComplete(i){
 const st=i-3;
 G.stars[st]=1+(G.hints[st]===0?1:0)+(G.checks[st]===0?1:0);
 sendResult({game:'nono',type:'clear',stage:st,stars:G.stars[st],hints:G.hints[st]});render();
 boardPop({mascot:st===2?'hooray':'detective', tag:'감식 보고서', title:`🔎 ${esc(IQ_CASES[i].title.split('·')[0].trim())} 조사 완료`,
   body:esc(IQ_CASES[i].lesson)+`<br><b style="font-size:1.2rem">${'⭐'.repeat(G.stars[st])}${'☆'.repeat(3-G.stars[st])}</b>`,
   button: st<2 ? '다음 증거 조각으로 ▶' : '최종 결과 보기 ▶'});
}
function iqHintUsed(i){G.hints[i-3]++;}
function iqWrong(i){G.checks[i-3]++;}
function toFinal(){
 if(![3,4,5].every(i=>iqState(i).done))return;
  sendResult({game: 'nono', type: 'final', stars: G.stars.reduce((a, b) => a + b, 0), hints: G.hints.reduce((a, b) => a + b, 0)});
  G.screen = 'final'; fresh = true; render(); window.scrollTo(0, 0);
}
function othersHtml(st){
  const n = STATS[`s${st}_clear`] || 0;
  if (!n) return '<div class="others">🌍 아직 이 그림을 복원한 기록이 없어요. 첫 복원의 주인공이에요!</div>';
  return `<div class="others">🌍 지금까지 <b>${n}번</b> 이 그림이 복원됐어요. 힌트 없이 푼 비율 <b>${Math.round((STATS[`s${st}_nohint`] || 0) * 100 / n)}%</b> · 별 3개 <b>${Math.round((STATS[`s${st}_star3`] || 0) * 100 / n)}%</b></div>`;
}

function fullRle(line){ const out = []; let cur = line[0], c = 0; for (const v of line) { if (v === cur) c++; else { out.push(c); cur = v; c = 1; } } out.push(c); return {start: line[0], runs: out}; }

function renderFinal(){
  const total = G.stars.reduce((a, b) => a + b, 0);
  const title = total >= 9 ? '🏅 수석 증거 복원관' : total >= 6 ? '🔍 증거 복원관' : '🌱 새내기 복원관';
  const sp = ['✨', '⭐', '🧩', '🎉', '✨', '💫', '⭐', '🎉', '🔳', '✨'].map((ic, k) => { const a = k * Math.PI / 5; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 150)}px;--y:${Math.round(Math.sin(a) * 110)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  const ex = SOL[0][1], exFull = fullRle(ex);
  const rows = SOL.map((g, i) => {
    const runs = g.reduce((a, r) => a + fullRle(r).runs.length, 0), cells = g.length * g.length;
    return `<tr><td>${esc(D.stages[i].title)}</td><td>${cells}칸</td><td>${runs}개</td><td>${Math.round(runs / cells * 100)}%</td></tr>`;
  }).join('');
  $('app').innerHTML = `
  <section class="result fx"><div class="big">🏆</div><b class="t">${title}</b>
    <div class="stars">${'⭐'.repeat(total)}${'☆'.repeat(9 - total)}</div><div style="font-weight:800">별 ${total} / 9</div>
    <span class="stamp">사건 해결!</span>${sp}</section>
  <section class="box"><h3>🛡️ 큐싱(QR 피싱) 막는 4가지</h3>
    ① 정산기·전단지·포스터의 QR은 <b>스티커가 덧붙여져 있지 않은지</b> 먼저 살펴봐요.<br>
    ② QR을 찍으면 뜨는 <b>주소를 먼저 확인</b>하고, 공식 주소가 아니면 열지 않아요.<br>
    ③ QR로 열린 페이지가 <b>앱 설치·로그인·카드 정보</b>를 요구하면 멈춰요.<br>
    ④ 요금 결제는 QR 대신 <b>공식 앱이나 정산기 화면</b>에서 직접 해요.</section>
  <section class="box"><h3>💾 비밀 공개: 노노그램 단서는 ‘압축 데이터’였어요</h3>
    흑백 그림은 컴퓨터 안에서 칸마다 <b>1(칠함)과 0(빈칸)</b>으로 저장돼요. 이걸 <b>비트맵</b>이라고 해요.
    <div class="rle">스마트폰 2번째 줄   ${ex.map(v => v ? '■' : '□').join('')}
비트맵(0과 1)       ${ex.join('')}
런 길이 부호화(RLE) <span class="k">${exFull.start ? '■' : '□'}부터</span> ${exFull.runs.join(', ')}  ← 같은 색이 몇 칸 이어지는지
노노그램 단서       ${rle(ex).join(' ')}          ← RLE에서 ‘칠한 칸’ 길이만 남긴 것</div>
    같은 색이 이어지는 길이만 적는 방식을 <b>런 길이 부호화(RLE)</b>라고 해요. 노노그램 단서는 RLE에서 빈칸 길이를 지운 것이라, 그만큼 정보가 부족해서 <b>퍼즐</b>이 돼요. 빈칸 길이까지 적으면 퍼즐 없이 바로 복원돼요.
    <table class="ctable"><tr><th>그림</th><th>원래 칸 수</th><th>RLE 숫자 개수</th><th>비율</th></tr>${rows}</table>
    👉 자물쇠처럼 <b>같은 색이 길게 이어지는 그림</b>은 숫자가 크게 줄어들고, QR 코드처럼 <b>들쭉날쭉한 그림</b>은 덜 줄어요. 데이터의 모양에 따라 압축이 잘 되는 정도가 달라요.</section>
  <div class="row"><button onclick="startStage(0)">🔁 1단계부터 다시 풀기</button><button class="go" onclick="restart()">🔄 처음부터 다시</button></div>`;
}

function restart(){ iqReset(); Object.assign(G, {screen: 'intro', stage: 0, mode: 1, grid: blank(), solved: [false, false, false], hints: [0, 0, 0], checks: [0, 0, 0], stars: [0, 0, 0], justSolved: false}); fresh = true; render(); }

// ───── Streamlit 높이 맞추기 ─────
let lastHeight = 0;
function sendHost(type, payload = {}) { window.parent.postMessage({isStreamlitMessage: true, type, ...payload}, '*'); }
function resize(force = false){ const root = document.querySelector('main.wrap'); if (!root) return; const h = Math.ceil(root.getBoundingClientRect().height) + 16; if (force || h !== lastHeight) { sendHost('streamlit:setFrameHeight', {height: h}); lastHeight = h; } }
// 도토리시 통계: 파이썬이 보낸 다른 사람들의 기록(stats)을 받고, 게임 결과를 파이썬으로 보냅니다.
let STATS = {};
function sendResult(obj){ sendHost('streamlit:setComponentValue', {value: Object.assign({id: Date.now() + '-' + Math.random().toString(36).slice(2)}, obj), dataType: 'json'}); }
window.addEventListener('message', ev => { if (ev.source === window.parent && ev.data && ev.data.type === 'streamlit:render') { if (ev.data.args && ev.data.args.stats) STATS = ev.data.args.stats; requestAnimationFrame(() => resize(true)); } });
sendHost('streamlit:componentReady', {apiVersion: 1});
new ResizeObserver(() => requestAnimationFrame(resize)).observe(document.querySelector('main.wrap'));
window.addEventListener('load', resize); window.addEventListener('resize', resize);
render();
</script></body></html>
'''

import scene_ui
page = bridge(attach(HTML), "12").replace("__SCENEIMG__", scene_ui.data_url("scene_kiosk")).replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("<", "\\u003c"))
value = create_nonogram_component(page)(key="jamkkan_qr_nonogram_v1", default=None, stats=dd.stats("nono"))

# 결과를 익명 통계(+1)에 더하고, 시민증이 있으면 명예의 전당에 저장해요.
event = dd.take_event(value)
if event and event.get("type") == "clear" and event.get("stage") in (0, 1, 2):
    s, stars, hints = int(event["stage"]), int(event.get("stars", 0)), int(event.get("hints", 0))
    dd.record("nono", {f"s{s}_clear": 1, f"s{s}_nohint": 1 if hints == 0 else 0, f"s{s}_star3": 1 if stars == 3 else 0})
    dd.stamp("12")
    if hints == 0:
        dd.achieve("nono_nohint")  # 업적: 힌트 없이 복원
elif event and event.get("type") == "final":
    stars, hints = max(0, min(9, int(event.get("stars", 0)))), max(0, int(event.get("hints", 0)))
    dd.record("nono", {"finals": 1})
    dd.note_mine("nono", f"별 {stars}/9 · 힌트 {hints}번")
    st.session_state["nono_hall"] = dd.save_hall(
        "nono", {"stars": stars, "hints": hints},
        lambda old, new: (new["stars"], -new["hints"]) > (old.get("stars", 0), -old.get("hints", 10**6)),
    )
dd.show_hall_note(st.session_state.get("nono_hall"))

# 📷 진짜 QR 비춰 보기: 웹캠 사진 속 QR을 읽어 목적지만 보여 줘요(접속하지 않아요).
from qr_scan_ui import show_qr_scanner
show_qr_scanner()

with st.expander("🧠 이 페이지 속 알고리즘 (정보 과목 연계)"):
    st.markdown(
        "- **비트맵과 2차원 배열**: 그림은 칸마다 1(칠함)·0(빈칸)을 담은 2차원 배열로 저장돼요.\n"
        "- **런 길이 부호화(RLE)**: 노노그램 단서는 같은 색이 이어지는 길이를 적는 압축 방식에서 나왔어요. 마지막 화면에서 그림마다 얼마나 줄어드는지 비교해요.\n"
        "- **제약 전파**: 가로줄에서 확정한 칸이 세로줄의 실마리가 되는 과정을 반복하는 방식이에요. 세 퍼즐 모두 이 방법만으로 끝까지 풀리고 답이 하나뿐인지 프로그램으로 확인했어요."
    )
