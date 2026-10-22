"""중고거래 사기단 추리: 압수한 사기단 메모를 해독해 단서를 얻고, 논리 표로 진짜 판매자를 찾는 퍼즐.

- 메모 1: 전치 암호(칸 수를 맞춰 다시 배열)
- 메모 2: 숫자 밀기 암호(시저 암호)
- 메모 3: 2진수
- 논리 표: 단서 10개를 모두 써야 답이 하나로 정해지도록 설계했습니다.
모든 인물·닉네임·메모는 교육용 가상 내용입니다.
"""
import json

import streamlit as st
from mascot_ui import show_key_question, show_mascot
from puzzle_component_ui import create_puzzle_component

st.title("🔐 중고거래 사기단 추리")
show_key_question("판매자 5명 중 **진짜는 단 1명**. 사기단 메모를 **해독**하고, 단서로 **진짜 판매자**를 찾아내세요.", "🔐")
show_mascot("detective", "메모를 하나 풀 때마다 결정적인 단서가 나와요. 단서를 모두 모아야 범인이 가려져요!", width=100)

DATA = {
    "sellers": ["한정판러", "급처분해요", "새상품만", "운동화왕", "동네이웃"],
    "emoji": ["👟", "⚡", "📦", "👑", "🏡"],
    "attrs": {
        "c": {"name": "연락 방식", "values": ["앱 채팅", "외부 메신저", "문자", "전화", "오픈채팅"]},
        "r": {"name": "요구한 것", "values": ["앱 안전결제", "가짜 결제 링크", "선입금 이체", "신분증 사진", "상품권"]},
        "p": {"name": "가격", "values": ["9만 원", "12만 원", "14만 원", "16만 원", "19만 원"]},
    },
    # 정답(검증: 단서 10개를 모두 쓰면 172만 8천 가지 경우 중 이 답 하나만 남음)
    "solution": {
        "한정판러": ["전화", "신분증 사진", "19만 원"],
        "급처분해요": ["외부 메신저", "가짜 결제 링크", "9만 원"],
        "새상품만": ["문자", "선입금 이체", "12만 원"],
        "운동화왕": ["오픈채팅", "상품권", "14만 원"],
        "동네이웃": ["앱 채팅", "앱 안전결제", "16만 원"],
    },
    "real": "동네이웃",
    "base": [
        "🏡 동네이웃은 앱 채팅으로 연락했다.",
        "⚡ 가장 싼 9만 원짜리는 급처분해요의 물건이다.",
        "🪪 신분증 사진을 요구한 판매자가 가장 비싸게 불렀다.",
        "📦 새상품만은 문자로 연락했다.",
        "👑 운동화왕은 상품권으로 결제해 달라고 했다.",
        "📞 전화로 연락한 판매자는 19만 원을 불렀다.",
        "🛡️ 앱 안전결제를 쓴 판매자는 문자로 연락하지 않았다.",
    ],
    "cipher_clues": [
        "📜 외부 메신저로 옮기자고 한 판매자가 가짜 결제 링크를 보냈다.",
        "📜 선입금 이체를 요구한 판매자의 가격은 12만 원이다.",
        "📜 오픈채팅으로 연락한 판매자의 가격은 14만 원이다.",
    ],
    # 메모 1: 4칸으로 가로로 쓴 문장을 세로로 읽어 만든 전치 암호
    "memo1": {"cipher": "외저자자결를부로던가제보메옮판가링냈신기매짜크다", "answer": 4, "options": [2, 3, 4, 6, 8]},
    # 메모 2: 숫자마다 3칸씩 앞으로 민 시저 암호 (120000 → 453333)
    "memo2": {"before": "선입금 이체를 요구한 판매자의 가격: ", "cipher": "453333", "after": "원", "shift": 3},
    # 메모 3: 2진수 01110 = 14
    "memo3": {"before": "오픈채팅 판매자의 가격(만 원): ", "bits": "01110", "answer": 14},
    "tactics": {
        "한정판러": "📞 전화로 친근하게 다가와 ‘본인 확인’이라며 신분증 사진을 요구했어요. 신분증 사진은 명의 도용에 쓰일 수 있어요. 가격도 정가(18만 원)보다 비쌌죠.",
        "급처분해요": "⚡ 정가의 절반인 9만 원으로 눈길을 끈 뒤, 외부 메신저로 옮겨 ‘안전결제’처럼 보이는 가짜 결제 링크를 보냈어요.",
        "새상품만": "📦 문자로 연락해 앱 밖에서 계좌로 먼저 돈을 보내라고 했어요. 앱 밖 거래는 보호를 받기 어려워요.",
        "운동화왕": "👑 오픈채팅으로 연락해 상품권 핀번호로 결제해 달라고 했어요. 상품권은 돌려받기 어려워 사기에 자주 쓰여요.",
        "동네이웃": "🏡 앱 채팅으로만 대화하고, 앱 안의 안전결제를 이용했어요. 가격(16만 원)도 시세에 맞았어요.",
    },
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
.ok{background:#0F766E;color:#fff}.ok:hover:not(:disabled){background:#0B655B}
main.wrap{max-width:980px;margin:auto;padding:6px 4px 14px}
.hero{background:linear-gradient(135deg,#1F5F55,#2E8B78);color:#fff;border-radius:22px;padding:18px;text-align:center;animation:pop .5s ease-out both}
.hero b{display:block;font-size:1.4rem;font-weight:900;word-break:keep-all}.hero span{opacity:.92;font-weight:600;word-break:keep-all}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.chips span{background:#EDF4F1;border-radius:999px;padding:5px 12px;font-weight:800;font-size:.9rem}
.chips .hot{background:#FFF1E6;color:#B4471B}
.tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}
.tabs button{background:#F1F5F2;border:2px solid #CBDAD2;min-height:52px}
.tabs button.on{background:#20483F;color:#fff;border-color:#20483F}
.story{background:#fff;border:1.5px solid #D7E2DD;border-radius:18px;padding:14px 16px;margin:10px 0;word-break:keep-all;animation:pop .45s ease-out both}
.sellers{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:8px 0}
.sellers div{background:#F4F8F6;border-radius:14px;padding:8px 4px;text-align:center;font-weight:800;font-size:.85rem;animation:pop .45s ease-out both}
.sellers div em{display:block;font-style:normal;font-size:26px;animation:bob 2.4s ease-in-out infinite}
.memo{position:relative;background:repeating-linear-gradient(#FFFDF4,#FFFDF4 31px,#EFE6C8 32px);border:2px solid #E6D9A8;border-radius:16px;padding:16px 16px 14px;margin:12px 0;box-shadow:0 6px 16px #8a6d1e18;animation:pop .45s ease-out both}
.memo.done{border-color:#0F766E;background:#F0F7F3}
.memo h3{margin:0 0 6px;font-size:1.1rem}
.memo .tag{position:absolute;top:-12px;right:14px;background:#B4471B;color:#fff;border-radius:999px;padding:2px 10px;font-size:.78rem;font-weight:900;transform:rotate(4deg)}
.memo.done .tag{background:#0F766E}
.code{font-family:'Courier New',monospace;font-weight:900;font-size:1.35rem;letter-spacing:.12em;background:#3B2F1E;color:#FFE9A8;border-radius:10px;padding:8px 12px;display:inline-block;word-break:break-all;margin:4px 0}
.opts{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.opts button.on{background:#20483F;color:#fff}
.tgrid{display:grid;gap:4px;margin:8px 0}
.tgrid span{background:#fff;border:1.5px solid #E6D9A8;border-radius:8px;text-align:center;font-weight:900;padding:6px 0;font-size:1.05rem;animation:flip .35s ease-out both}
.read{background:#fff;border:2px dashed #C9B97A;border-radius:12px;padding:8px 12px;font-weight:800;word-break:break-all;margin:6px 0}
.read.good{border:2px solid #0F766E;background:#E6F4EC;color:#0F5E4F}
.digits{display:flex;gap:6px;margin:8px 0;flex-wrap:wrap}
.digits span{width:42px;height:52px;border-radius:10px;background:#3B2F1E;color:#FFE9A8;display:flex;align-items:center;justify-content:center;font-family:'Courier New',monospace;font-size:1.6rem;font-weight:900;animation:flip .3s ease-out both}
.stepper{display:flex;align-items:center;gap:10px;margin:6px 0;flex-wrap:wrap}
.stepper b{font-size:1.3rem;min-width:2ch;text-align:center}
.lamps{display:flex;gap:8px;margin:8px 0;flex-wrap:wrap}
.lamp{width:58px;border-radius:12px;background:#F1EBDA;border:2px solid #E6D9A8;padding:6px 0;text-align:center;font-weight:900;cursor:pointer;transition:transform .15s}
.lamp:hover{transform:translateY(-2px)}
.lamp .v{font-size:.8rem;color:#7A6A3A}.lamp .bit{font-size:1.5rem;font-family:'Courier New',monospace}
.lamp.on{background:#FFE08A;border-color:#E3A400;box-shadow:0 0 0 4px #FFE08A66;animation:boing .4s}
.sum{font-weight:900;font-size:1.1rem}
.hint{background:#EEF2FF;border:2px solid #A5B4FC;border-radius:12px;padding:8px 12px;margin:8px 0;font-weight:700;word-break:keep-all;animation:pop .35s ease-out both}
.got{background:#E6F4EC;border:2px solid #0F766E;border-radius:12px;padding:10px 12px;font-weight:800;margin-top:8px;word-break:keep-all;animation:pop .5s ease-out both}
.toast{min-height:1.5em;font-weight:800;color:#B4471B;margin:6px 0;word-break:keep-all}
.shake{animation:shake .45s}
.clues{display:grid;gap:6px;margin:8px 0}
.clue{display:flex;gap:8px;align-items:flex-start;background:#fff;border:1.5px solid #D7E2DD;border-radius:12px;padding:8px 10px;cursor:pointer;word-break:keep-all;text-align:left;font-weight:700;font-size:.95rem;width:100%}
.clue.used{opacity:.5;text-decoration:line-through}
.clue.lock{background:#F4F4F0;color:#8A8F87;cursor:default}
.clue.memo{border-color:#E6D9A8;background:#FFFBEA}
.grids{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin:10px 0}
.g{background:#fff;border:1.5px solid #D7E2DD;border-radius:16px;padding:10px;overflow-x:auto}
.g h4{margin:0 0 6px}
table{border-collapse:collapse;width:100%;table-layout:fixed}
th:first-child{width:32%}
th{font-size:.72rem;font-weight:800;color:#33524A;padding:3px 2px;word-break:keep-all;line-height:1.2}
td.n{font-size:.8rem;font-weight:800;white-space:nowrap;padding-right:4px}
td.c{padding:2px}
td.c button{width:100%;min-height:36px;padding:0;border-radius:8px;background:#F4F8F6;border:1.5px solid #D7E2DD;font-size:1rem}
td.c button.x{background:#FFF1F1;border-color:#F3B4B0}
td.c button.o{background:#D7F2E3;border-color:#0F766E;animation:boing .35s}
td.c button.bad{outline:3px solid #E5484D}
.row{display:flex;gap:10px;flex-wrap:wrap}.row button{flex:1}
.pick{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0}
.pick button{display:flex;flex-direction:column;align-items:center;padding:12px 4px;border:2px solid #D7E2DD;background:#fff}
.pick button em{font-style:normal;font-size:30px}
.pick button.on{border-color:#FF7A45;background:#FFF6EE;transform:translateY(-3px)}
.result{position:relative;overflow:hidden;border-radius:24px;padding:24px 18px;text-align:center;margin:10px 0}
.result.win{background:linear-gradient(135deg,#FFF1C2,#FFD6A5);animation:pop .6s ease-out both}
.result .big{font-size:64px;animation:bob 1.6s .8s ease-in-out infinite}
.result b{display:block;font-size:1.5rem;font-weight:900;word-break:keep-all}
.stamp{display:inline-block;margin-top:10px;border:5px solid #D7263D;color:#D7263D;border-radius:12px;padding:3px 16px;font-size:1.7rem;font-weight:900;transform:rotate(-10deg);animation:stamp .5s .4s ease-out both;background:#ffffffa0}
.stars{font-size:40px;letter-spacing:6px}.stars i{display:inline-block;font-style:normal;animation:starpop .45s ease-out both}
.spark{position:absolute;left:50%;top:38%;font-size:24px;animation:burst 1.1s .45s ease-out both;pointer-events:none}
.tact{display:grid;gap:8px}
.tact div{background:#fff;border:1.5px solid #D7E2DD;border-radius:14px;padding:10px 12px;word-break:keep-all;animation:pop .45s ease-out both}
.tact div.real{border:2.5px solid #0F766E;background:#EEF8F2}
.tact b{display:block}
.drum{text-align:center;font-size:1.4rem;font-weight:900;padding:36px 0}
.drum div{font-size:64px;animation:bob .45s ease-in-out infinite}
@keyframes pop{0%{transform:scale(.6);opacity:0}65%{transform:scale(1.04);opacity:1}100%{transform:scale(1)}}
@keyframes bob{50%{transform:translateY(-7px)}}
@keyframes boing{0%{transform:scale(1)}30%{transform:scale(1.12,.9)}60%{transform:scale(.94,1.06)}100%{transform:scale(1)}}
@keyframes flip{0%{transform:rotateX(90deg);opacity:0}100%{transform:none;opacity:1}}
@keyframes shake{0%,100%{transform:translateX(0)}25%,75%{transform:translateX(-8px)}50%{transform:translateX(8px)}}
@keyframes stamp{0%{transform:scale(3) rotate(-18deg);opacity:0}60%{transform:scale(.9) rotate(-10deg);opacity:1}100%{transform:scale(1) rotate(-10deg)}}
@keyframes starpop{0%{transform:scale(0) rotate(-40deg)}70%{transform:scale(1.3)}100%{transform:scale(1)}}
@keyframes burst{0%{transform:translate(0,0) scale(.3);opacity:1}100%{transform:translate(var(--x),var(--y)) scale(1.2);opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:560px){.sellers,.pick{grid-template-columns:repeat(5,1fr);gap:4px}.sellers div,.pick button{font-size:.68rem}.pick button em,.sellers div em{font-size:22px}.tabs button{font-size:.85rem;padding:8px 4px}.code{font-size:1.05rem}.digits span{width:36px;height:46px;font-size:1.3rem}.lamp{width:50px}}
</style></head><body><main class="wrap" id="app"></main>
<script>
const D = __DATA__;
const KINDS = ['c', 'r', 'p'];
const G = {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0,
  k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, auto: true, pick: null, gridChecked: false, done: false, bad: {}};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let toastMsg = '';

function cluesOpen(){ return G.solved.filter(Boolean).length; }

function render(){
  const app = $('app');
  if (G.done) return;
  app.innerHTML = `
  <section class="hero"><span>🔐 추리 퍼즐 · 메모 해독 → 논리 표 → 지목</span><b>한정판 운동화, 진짜 판매자는 누구?</b>
  <span>정가 18만 원짜리 운동화를 사려는데 판매자 5명이 연락해 왔어요.</span></section>
  <div class="sellers">${D.sellers.map((s, i) => `<div style="animation-delay:${i * .07}s"><em style="animation-delay:${i * .3}s">${D.emoji[i]}</em>${esc(s)}</div>`).join('')}</div>
  <div class="chips"><span class="hot">📜 해독한 메모 ${cluesOpen()} / 3</span><span>🔎 쓸 수 있는 단서 ${D.base.length + cluesOpen()} / ${D.base.length + 3}</span><span>💡 힌트 ${G.hints.filter(Boolean).length}번</span></div>
  <div class="tabs">
    <button class="${G.tab === 'memo' ? 'on' : ''}" onclick="go('memo')">① 📜 메모 해독</button>
    <button class="${G.tab === 'grid' ? 'on' : ''}" onclick="go('grid')">② 🧩 추리 표</button>
    <button class="${G.tab === 'pick' ? 'on' : ''}" onclick="go('pick')">③ 🏁 진짜 지목</button>
  </div>
  <div id="body"></div>
  <div class="toast" id="toast" aria-live="polite">${esc(toastMsg)}</div>`;
  toastMsg = '';
  if (G.tab === 'memo') memoTab(); else if (G.tab === 'grid') gridTab(); else pickTab();
}
function go(t){ G.tab = t; render(); }
function toast(t, el){ const x = $('toast'); if (x) x.textContent = t; if (el) { el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); } }

// ───── ① 메모 해독 ─────
function decodeColumns(ct, k){ const r = ct.length / k, cols = []; for (let i = 0; i < k; i++) cols.push(ct.slice(i * r, (i + 1) * r)); let out = ''; for (let i = 0; i < r; i++) for (let c = 0; c < k; c++) out += cols[c][i]; return {out, cols, r}; }
function shiftBack(s, n){ return s.replace(/\d/g, d => String((+d - n + 100) % 10)); }

function memoTab(){
  const m1 = D.memo1, m2 = D.memo2, m3 = D.memo3;
  const {out, cols, r} = decodeColumns(m1.cipher, G.k);
  let gridHtml = '';
  for (let i = 0; i < r; i++) for (let c = 0; c < G.k; c++) gridHtml += `<span style="animation-delay:${(i * G.k + c) * .015}s">${cols[c][i]}</span>`;
  const dec2 = shiftBack(m2.cipher, G.shift);
  const sum = G.lamps.reduce((a, v, i) => a + (v ? [16, 8, 4, 2, 1][i] : 0), 0);
  $('body').innerHTML = `
  <div class="story">🚓 경찰 사이버수사대가 중고거래 사기단에게서 <b>작업 메모 3장</b>을 압수했어요. 메모는 암호로 적혀 있어요. 하나씩 풀면 <b>추리 표에 쓸 단서</b>가 열려요.</div>

  <section class="memo ${G.solved[0] ? 'done' : ''}" id="m0"><span class="tag">${G.solved[0] ? '해독 완료 ✔' : '메모 1 · 자리 바꾸기'}</span>
    <h3>📜 메모 1 · 글자 순서가 뒤섞인 메모</h3>
    <div class="code">${esc(m1.cipher)}</div>
    <p style="margin:6px 0">사기단은 문장을 <b>몇 칸짜리 줄</b>에 가로로 쓴 뒤, <b>세로로</b> 읽어 옮겨 적었어요. 칸 수를 맞히면 문장이 돼요.</p>
    ${G.solved[0] ? '' : `<div class="opts">${m1.options.map(k => `<button class="${k === G.k ? 'on' : ''}" onclick="G.k=${k};render()">${k}칸</button>`).join('')}</div>
    <div class="tgrid" style="grid-template-columns:repeat(${G.k},1fr);max-width:${G.k * 52}px">${gridHtml}</div>`}
    <div class="read ${G.solved[0] ? 'good' : ''}">가로로 읽으면 → ${esc(G.solved[0] ? decodeColumns(m1.cipher, m1.answer).out : out)}</div>
    ${G.solved[0] ? `<div class="got">🔓 새 단서: ${esc(D.cipher_clues[0])}</div>` : `<div class="row"><button class="ok" onclick="check1()">이 칸 수로 해독 완료!</button><button onclick="hint(0)">💡 힌트</button></div>`}
    ${G.hints[0] && !G.solved[0] ? '<div class="hint">💡 메모 귀퉁이에 ■■■■ 네모 4개가 그려져 있어요.</div>' : ''}
  </section>

  <section class="memo ${G.solved[1] ? 'done' : ''}" id="m1"><span class="tag">${G.solved[1] ? '해독 완료 ✔' : '메모 2 · 숫자 밀기'}</span>
    <h3>📜 메모 2 · 숫자가 이상한 메모</h3>
    <p style="margin:4px 0">${esc(m2.before)}<span class="code">${esc(m2.cipher)}</span>${esc(m2.after)}</p>
    <p style="margin:6px 0">사기단은 숫자를 <b>모두 같은 칸 수만큼 앞으로</b> 밀어 적었어요(9 다음은 0). 몇 칸 되돌려야 가격표의 금액이 될까요?</p>
    ${G.solved[1] ? '' : `<div class="stepper"><button onclick="G.shift=(G.shift+9)%10;render()">◀</button><b>${G.shift}</b><button onclick="G.shift=(G.shift+1)%10;render()">▶</button><span>칸 되돌리기</span></div>`}
    <div class="digits">${(G.solved[1] ? shiftBack(m2.cipher, m2.shift) : dec2).split('').map((d, i) => `<span style="animation-delay:${i * .04}s">${d}</span>`).join('')}<span style="background:none;color:#20483F;width:auto">원</span></div>
    <p style="font-size:.85rem;color:#52616B;margin:2px 0">가격표: 90000 · 120000 · 140000 · 160000 · 190000</p>
    ${G.solved[1] ? `<div class="got">🔓 새 단서: ${esc(D.cipher_clues[1])}</div>` : `<div class="row"><button class="ok" onclick="check2()">이 숫자로 해독 완료!</button><button onclick="hint(1)">💡 힌트</button></div>`}
    ${G.hints[1] && !G.solved[1] ? '<div class="hint">💡 맨 앞 4가 1이 되려면 몇 칸 되돌려야 할까요? (4 → 3 → 2 → 1)</div>' : ''}
  </section>

  <section class="memo ${G.solved[2] ? 'done' : ''}" id="m2"><span class="tag">${G.solved[2] ? '해독 완료 ✔' : '메모 3 · 0과 1'}</span>
    <h3>📜 메모 3 · 0과 1로만 적힌 메모</h3>
    <p style="margin:4px 0">${esc(m3.before)}<span class="code">${esc(m3.bits)}</span></p>
    <p style="margin:6px 0">2진수예요. 각 자리는 왼쪽부터 <b>16 · 8 · 4 · 2 · 1</b>을 뜻해요. <b>1이 적힌 자리의 전구를 켜서</b> 더해 보세요.</p>
    <div class="lamps">${[16, 8, 4, 2, 1].map((v, i) => `<div class="lamp ${G.lamps[i] ? 'on' : ''}" role="button" tabindex="0" onclick="lamp(${i})" onkeydown="if(event.key==='Enter')lamp(${i})"><div class="v">${v}</div><div class="bit">${m3.bits[i]}</div>${G.lamps[i] ? '💡' : '⚫'}</div>`).join('')}</div>
    <div class="sum">켠 전구의 합: ${sum} (만 원)</div>
    ${G.solved[2] ? `<div class="got">🔓 새 단서: ${esc(D.cipher_clues[2])}</div>` : `<div class="row"><button class="ok" onclick="check3()">이 합으로 해독 완료!</button><button onclick="hint(2)">💡 힌트</button></div>`}
    ${G.hints[2] && !G.solved[2] ? '<div class="hint">💡 01110에서 1은 가운데 세 자리예요. 8 + 4 + 2 = ?</div>' : ''}
  </section>
  ${cluesOpen() === 3 ? `<button class="go" style="width:100%" onclick="go('grid')">🧩 단서 3개 확보! 추리 표로 가기 ▶</button>` : ''}`;
}
function hint(i){ G.hints[i] = true; render(); }
function lamp(i){ G.lamps[i] = G.lamps[i] ? 0 : 1; render(); }
function unlock(i){ G.solved[i] = true; toastMsg = '🔓 해독 성공! 추리 표에 새 단서가 열렸어요.'; render(); }
function check1(){ if (G.k === D.memo1.answer) unlock(0); else { G.wrongMemo++; toast('아직 문장이 안 돼요. 다른 칸 수로 해 보세요.', $('m0')); } }
function check2(){ if (G.shift === D.memo2.shift) unlock(1); else { G.wrongMemo++; toast('가격표에 없는 금액이에요. 되돌리는 칸 수를 바꿔 보세요.', $('m1')); } }
function check3(){
  const ok = G.lamps.every((v, i) => v === +D.memo3.bits[i]);
  if (ok) unlock(2); else { G.wrongMemo++; toast('1이 적힌 자리의 전구만 켜야 해요.', $('m2')); }
}

// ───── ② 추리 표 ─────
function cellKey(kind, s, v){ return kind + '|' + s + '|' + v; }
function gridTab(){
  const clueHtml = D.base.map((t, i) => clueBtn('b' + i, t, false, false))
    .concat(D.cipher_clues.map((t, i) => clueBtn('m' + i, G.solved[i] ? t : `🔒 메모 ${i + 1}을 해독하면 열려요`, !G.solved[i], true))).join('');
  $('body').innerHTML = `
  <div class="story">👆 칸을 누를 때마다 <b>빈칸 → ❌ 아님 → ⭕ 맞음</b>으로 바뀌어요. 단서를 하나씩 읽고 표에 표시해 보세요. 다 쓴 단서는 눌러서 지워 두면 편해요.
  <label style="display:block;margin-top:6px;font-weight:700"><input type="checkbox" ${G.auto ? 'checked' : ''} onchange="G.auto=this.checked"> ⭕를 표시하면 같은 줄·같은 칸의 나머지를 자동으로 ❌</label></div>
  <h3 style="margin:8px 2px">🔎 단서 (${D.base.length + cluesOpen()} / ${D.base.length + 3})</h3>
  <div class="clues">${clueHtml}</div>
  <div class="grids">${KINDS.map(gridHtml).join('')}</div>
  <div class="row"><button onclick="resetGrid()">↺ 표 지우기</button><button class="ok" onclick="checkGrid()">표 채점하기 (⭕ 15개를 모두 채우면)</button></div>
  ${cluesOpen() < 3 ? '<div class="hint">💡 단서 7개만으로는 답이 하나로 안 정해져요. 메모를 해독해서 단서를 더 모아요!</div>' : ''}`;
}
function clueBtn(id, text, locked, memo){
  return `<button class="clue ${locked ? 'lock' : ''} ${memo ? 'memo' : ''} ${G.used[id] ? 'used' : ''}" ${locked ? 'disabled' : `onclick="G.used['${id}']=!G.used['${id}'];render()"`}>${esc(text)}</button>`;
}
function gridHtml(kind){
  const a = D.attrs[kind];
  let h = `<div class="g"><h4>판매자 × ${esc(a.name)}</h4><table><tr><th></th>${a.values.map(v => `<th>${esc(v)}</th>`).join('')}</tr>`;
  D.sellers.forEach((s, si) => {
    h += `<tr><td class="n">${D.emoji[si]} ${esc(s)}</td>`;
    a.values.forEach(v => {
      const st = G.grid[cellKey(kind, s, v)] || 0, k = cellKey(kind, s, v);
      h += `<td class="c"><button class="${st === 1 ? 'x' : st === 2 ? 'o' : ''} ${G.bad[k] ? 'bad' : ''}" aria-label="${esc(s)} ${esc(v)}" onclick="cell('${kind}','${esc(s)}','${esc(v)}')">${st === 1 ? '❌' : st === 2 ? '⭕' : ''}</button></td>`;
    });
    h += '</tr>';
  });
  return h + '</table></div>';
}
function cell(kind, s, v){
  const k = cellKey(kind, s, v), st = ((G.grid[k] || 0) + 1) % 3;
  G.grid[k] = st; G.bad = {};
  if (st === 2 && G.auto) {
    D.attrs[kind].values.forEach(v2 => { if (v2 !== v && !G.grid[cellKey(kind, s, v2)]) G.grid[cellKey(kind, s, v2)] = 1; });
    D.sellers.forEach(s2 => { if (s2 !== s && !G.grid[cellKey(kind, s2, v)]) G.grid[cellKey(kind, s2, v)] = 1; });
  }
  render();
}
function resetGrid(){ G.grid = {}; G.bad = {}; render(); }
function checkGrid(){
  const os = Object.entries(G.grid).filter(([, v]) => v === 2).map(([k]) => k);
  if (os.length < 15) { toast(`⭕가 ${os.length}개예요. 판매자마다 연락 방식·요구·가격을 하나씩, 모두 15개를 채워요.`); return; }
  G.bad = {};
  let wrong = 0;
  os.forEach(k => { const [kind, s, v] = k.split('|'); if (D.solution[s][KINDS.indexOf(kind)] !== v) { G.bad[k] = 1; wrong++; } });
  if (!wrong) { G.gridChecked = true; toastMsg = '🎉 표 완성! 모든 칸이 맞았어요. 이제 진짜 판매자를 지목해요!'; G.tab = 'pick'; render(); }
  else { toastMsg = `❌ 빨간 테두리 칸 ${wrong}개가 틀렸어요. 단서를 다시 확인해요.`; render(); }
}

// ───── ③ 진짜 지목 ─────
function pickTab(){
  $('body').innerHTML = `
  <div class="story">🏁 진짜 판매자라고 생각하는 사람을 골라요. <b>앱 밖으로 나가자고 하지 않고, 안전하게 거래하는 판매자</b>는 누구였을까요?</div>
  <div class="pick" id="pk">${D.sellers.map((s, i) => `<button class="${G.pick === s ? 'on' : ''}" onclick="G.pick='${esc(s)}';render()"><em>${D.emoji[i]}</em>${esc(s)}</button>`).join('')}</div>
  <button class="go" style="width:100%" ${G.pick ? '' : 'disabled'} onclick="answer()">🔍 이 판매자가 진짜예요!</button>
  ${G.gridChecked ? '' : '<p style="font-size:.88rem;color:#52616B">표를 다 채우지 않아도 지목할 수 있어요. 대신 표까지 완성하면 별을 더 받아요.</p>'}`;
}
function answer(){
  if (G.pick !== D.real) { G.wrongPick++; toast(`${G.pick}의 요구를 다시 떠올려 봐요. 표를 확인하고 다시 골라요!`, $('pk')); return; }
  G.done = true;
  const box = $('app');
  const steps = [['🥁', '두구두구…'], ['🔎', '거래 기록을 대조하는 중…'], ['🎉', '진짜 판매자 발견!']];
  let i = 0;
  const tick = () => { if (i < steps.length) { box.innerHTML = `<div class="drum"><div>${steps[i][0]}</div>${steps[i][1]}</div>`; i++; setTimeout(tick, 600); } else final(); };
  tick();
  try { if (window.frameElement) window.frameElement.scrollIntoView({behavior: 'smooth', block: 'start'}); } catch (e) {}
}
function final(){
  const allMemo = G.solved.every(Boolean);
  const stars = 1 + (allMemo && G.gridChecked ? 1 : 0) + (G.hints.every(h => !h) && G.wrongPick === 0 ? 1 : 0);
  const sp = ['✨', '⭐', '🎉', '💫', '✨', '⭐', '🎉', '✨'].map((ic, k) => { const a = k * Math.PI / 4; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 140)}px;--y:${Math.round(Math.sin(a) * 110)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  $('app').innerHTML = `
  <section class="result win"><div class="big">🏡</div><b>진짜 판매자는 ‘동네이웃’이었어요!</b>
  <div class="stars">${[0, 1, 2].map(k => `<i style="animation-delay:${.3 + k * .2}s">${k < stars ? '⭐' : '☆'}</i>`).join('')}</div>
  <span class="stamp">사기단 검거!</span>${sp}</section>
  <p style="text-align:center;font-size:.9rem;color:#52616B">⭐ 정답 · ⭐ 메모 3장 해독 + 표 완성 · ⭐ 힌트 없이 한 번에 지목</p>
  <h3>📢 판매자별 수법 공개</h3>
  <div class="tact">${D.sellers.map((s, i) => `<div class="${s === D.real ? 'real' : ''}" style="animation-delay:${i * .08}s"><b>${D.emoji[i]} ${esc(s)} · ${esc(D.solution[s].join(' · '))}</b>${esc(D.tactics[s])}</div>`).join('')}</div>
  <section class="story" style="margin-top:12px"><b>🛡️ 중고거래 사기 막는 4가지</b><br>
  ① 판매자가 <b>앱 밖(외부 메신저·문자·오픈채팅)</b>으로 가자고 하면 멈춰요.<br>
  ② 결제는 <b>앱 안의 안전결제</b>로만. 받은 결제 링크는 누르지 말고 앱에서 직접 열어요.<br>
  ③ 시세보다 <b>너무 싼 가격</b>은 미끼일 수 있어요.<br>
  ④ <b>신분증 사진·상품권 결제</b> 요구는 거절해요.</section>
  <button class="go" style="width:100%" onclick="restart()">🔄 처음부터 다시</button>`;
}
function restart(){ Object.assign(G, {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0, k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, pick: null, gridChecked: false, done: false, bad: {}}); render(); }

// ───── Streamlit 높이 맞추기 ─────
let lastHeight = 0;
function sendHost(type, payload = {}) { window.parent.postMessage({isStreamlitMessage: true, type, ...payload}, '*'); }
function resize(force = false){ const root = document.querySelector('main.wrap'); if (!root) return; const h = Math.ceil(root.getBoundingClientRect().height) + 16; if (force || h !== lastHeight) { sendHost('streamlit:setFrameHeight', {height: h}); lastHeight = h; } }
window.addEventListener('message', ev => { if (ev.source === window.parent && ev.data && ev.data.type === 'streamlit:render') requestAnimationFrame(() => resize(true)); });
sendHost('streamlit:componentReady', {apiVersion: 1});
new ResizeObserver(() => requestAnimationFrame(resize)).observe(document.querySelector('main.wrap'));
window.addEventListener('load', resize); window.addEventListener('resize', resize);
render();
</script></body></html>
'''

page = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("<", "\\u003c"))
create_puzzle_component(page)(key="jamkkan_memo_puzzle_v1", default=None)

with st.expander("🧠 이 페이지 속 알고리즘 (정보 과목 연계)"):
    st.markdown(
        "- **암호화와 복호화**: 메모 1은 글자 자리를 바꾸는 전치 암호, 메모 2는 숫자를 같은 칸만큼 미는 시저 암호예요. 열쇠(칸 수)를 알면 거꾸로 풀 수 있어요.\n"
        "- **2진수**: 메모 3의 01110은 각 자리가 16·8·4·2·1을 뜻해서 8 + 4 + 2 = 14가 돼요.\n"
        "- **제약 조건과 완전 탐색**: 논리 표는 가능한 172만 8천 가지 경우를 모두 검사해서, 단서 10개를 다 쓰면 답이 딱 하나만 남도록 만들었어요."
    )
st.caption("교육용 가상 이야기입니다. 실제 거래 앱·판매자와 관계없으며, 진행은 새로고침하면 초기화됩니다.")
