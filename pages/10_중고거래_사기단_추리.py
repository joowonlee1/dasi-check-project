"""중고거래 사기단 추리: 압수한 사기단 메모를 해독해 단서를 얻고, 논리 표로 진짜 판매자를 찾는 퍼즐.

- 메모 1: 전치 암호(칸 수를 맞춰 다시 배열)
- 메모 2: 숫자 밀기 암호(시저 암호)
- 메모 3: 2진수
- 논리 표: 단서 10개를 모두 써야 답이 하나로 정해지도록 설계했습니다.
모든 인물·닉네임·메모는 교육용 가상 내용입니다.
"""
import json

import streamlit as st
import dotori_data as dd
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
    # 추리 표에서 막혔을 때 한 단계씩 보여 주는 힌트(정답 표를 바로 알려 주지 않음)
    "steps": [
        "먼저 ‘누가 무엇’이 바로 적힌 단서 4개를 표에 ⭕로 옮겨요: 동네이웃=앱 채팅, 새상품만=문자, 운동화왕=상품권, 급처분해요=9만 원.",
        "‘전화 = 19만 원’과 ‘신분증 사진 = 가장 비쌈(19만 원)’을 이어 보세요. 전화로 연락한 판매자와 신분증 사진을 요구한 판매자는 같은 사람이에요.",
        "남은 연락 방식은 외부 메신저·전화·오픈채팅이고, 남은 사람은 한정판러·급처분해요·운동화왕이에요. 상품권을 요구한 운동화왕은 전화(신분증)도, 외부 메신저(가짜 링크, 메모 1)도 아니에요.",
        "운동화왕이 오픈채팅이면 메모 3에 따라 가격이 정해져요. 급처분해요는 9만 원이라 19만 원인 전화가 될 수 없어요.",
        "마지막으로 앱 안전결제와 선입금 이체 중 누가 무엇인지 정해요. ‘앱 안전결제 판매자는 문자로 연락하지 않았다’와 메모 2를 써 보세요.",
    ],
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
.hero{background:linear-gradient(135deg,#EAF6F0,#F4FAF6);border:1.5px solid #CFE6DA;color:#3E4A46;border-radius:22px;padding:16px;text-align:center;animation:pop .5s ease-out both}
.hero b{display:block;font-size:1.4rem;font-weight:900;word-break:keep-all;color:#0F766E}.hero span{font-weight:600;word-break:keep-all}
.sellhead{font-weight:900;margin:10px 2px 0;color:#20483F}
.sellers div small{display:block;font-size:.7rem;color:#B4471B;font-weight:800}
.prices{background:#FFF4D6;border:2px solid #E2C98A;border-radius:14px;padding:8px 12px;margin:8px 0;font-weight:800;color:#6B4A1E;word-break:keep-all}
.prices span{display:inline-block;background:#fff;border:1.5px solid #E2C98A;border-radius:999px;padding:1px 10px;margin:2px 3px;font-family:'Courier New',monospace}
.ansin{font:inherit;font-size:1.3rem;font-weight:900;width:110px;padding:6px 10px;border:2px solid #9DBFB2;border-radius:10px;text-align:center}
.autochk{display:flex;align-items:center;gap:12px;margin-top:8px;font-weight:800;font-size:1.05rem;cursor:pointer}
.autochk input{width:26px;height:26px;accent-color:#0F766E;cursor:pointer;flex-shrink:0}
.legend{font-size:.88rem;font-weight:700;color:#6B4A1E;margin:0 2px 4px}
.clue .src{display:block;font-size:.75rem;color:#B4471B;font-weight:900}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.ai{background:#F5F3FF;border:2px solid #C4B5FD;border-radius:16px;padding:12px 14px;margin:10px 0}
.ai h4{margin:0 0 6px;color:#3730A3}
.ai .ask{display:flex;gap:8px;flex-wrap:wrap}
.ai input{flex:1;min-width:200px;font:inherit;padding:8px 12px;border:2px solid #C4B5FD;border-radius:10px}
.ai .qa{background:#fff;border-radius:12px;padding:8px 12px;margin:6px 0;word-break:keep-all}
.ai .qa b{color:#3730A3}
.bigcheck{width:100%;min-height:58px;font-size:1.15rem}
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
.optlabel{font-weight:800;color:#B4471B;margin:8px 0 2px;font-size:.95rem}
.opts{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 8px}
.opts button{background:#fff;border:2px solid #9DBFB2;min-width:64px}
.opts button:hover:not(:disabled){background:#F0F7F3;border-color:#20483F}
.opts button.on,.opts button.on:hover:not(:disabled){background:#20483F;color:#fff;border-color:#20483F;box-shadow:0 0 0 4px #FF7A4555;transform:translateY(-2px)}
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
.ex{background:#fff;border:2px solid #D7E2DD;border-radius:18px;padding:14px;margin:10px 0;animation:pop .45s ease-out both}
.ex h3{margin:0 0 6px}
.exrow{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.exbox{background:#F7FAF8;border:1.5px solid #D7E2DD;border-radius:14px;padding:10px;text-align:center;word-break:keep-all;animation:pop .45s ease-out both}
.exbox:nth-child(2){animation-delay:.15s}.exbox:nth-child(3){animation-delay:.3s}
.exbox p{margin:6px 0 0;font-size:.86rem;line-height:1.5}
.extag{display:inline-block;background:#20483F;color:#fff;border-radius:999px;padding:2px 10px;font-size:.78rem;font-weight:800;margin-bottom:6px}
.mini{border-collapse:collapse;margin:4px auto;table-layout:auto;width:auto}
.mini th,.mini td{border:1.5px solid #D7E2DD;padding:3px 7px;font-size:.85rem;font-weight:800;text-align:center;background:#fff}
.mini th{background:#EDF4F1}
.mini td.o{background:#D7F2E3}.mini td.x{background:#FFF1F1}.mini td.new{outline:3px solid #FF7A45;outline-offset:-3px}
.code.sm{font-size:1rem;padding:4px 8px}
.tips{background:#FFFBEA;border:2px solid #F1D98A;border-radius:14px;padding:10px 14px;margin:10px 0;word-break:keep-all}
.tips ol{margin:4px 0 0;padding-left:22px}.tips li{margin:3px 0}
.step{background:#EEF2FF;border:2px solid #A5B4FC;border-radius:12px;padding:8px 12px;margin:6px 0;font-weight:700;word-break:keep-all;animation:pop .35s ease-out both}
.others{background:#F0F7FF;border:2px solid #B8D4F0;border-radius:14px;padding:8px 12px;margin:10px auto 0;max-width:640px;text-align:left;font-weight:700;font-size:.92rem;line-height:1.6;color:#1E3A5F;word-break:keep-all}
.still .hero,.still .sellers div,.still .story,.still .ex,.still .exbox,.still .memo,.still .tgrid span,.still .digits span,.still .got,.still .hint,.still .step:not(:last-of-type){animation:none!important}
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
@media (max-width:560px){.exrow{grid-template-columns:1fr}.sellers,.pick{grid-template-columns:repeat(5,1fr);gap:4px}.sellers div,.pick button{font-size:.68rem}.pick button em,.sellers div em{font-size:22px}.tabs button{font-size:.85rem;padding:8px 4px}.code{font-size:1.05rem}.digits span{width:36px;height:46px;font-size:1.3rem}.lamp{width:50px}}
</style></head><body><main class="wrap" id="app"></main>
<script>
const D = __DATA__;
const KINDS = ['c', 'r', 'p'];
const G = {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0,
  k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, auto: true, pick: null, gridChecked: false, done: false, bad: {}, stepHint: 0};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let toastMsg = '';
let fresh = true;  // 탭을 처음 열 때만 튀어나오는 효과를 보여 줍니다.

function cluesOpen(){ return G.solved.filter(Boolean).length; }

function render(){
  const app = $('app');
  if (G.done) return;
  app.classList.toggle('still', !fresh); fresh = false;
  app.innerHTML = `
  <section class="hero"><span>🔐 추리 퍼즐 · 메모 해독 → 논리 표 → 지목</span><b>한정판 운동화, 진짜 판매자는 누구?</b>
  <span>정가 18만 원짜리 운동화를 사려는데 판매자 5명이 연락해 왔어요.</span></section>
  <div class="sellhead">🛍️ 연락해 온 판매자 5명 (중고거래 앱 닉네임)</div>
  <div class="sellers">${D.sellers.map((s, i) => `<div style="animation-delay:${i * .07}s"><em style="animation-delay:${i * .3}s">${D.emoji[i]}</em><small>판매자 ${i + 1}</small>${esc(s)}</div>`).join('')}</div>
  <div class="prices">💰 판매자들이 부른 가격(가격표): ${D.attrs.p.values.map(v => `<span>${esc(v)}</span>`).join('')} · 누가 얼마를 불렀는지는 단서로 찾아요.</div>
  <div class="chips"><span class="hot">📜 해독한 메모 ${cluesOpen()} / 3</span><span>🔎 쓸 수 있는 단서 ${D.base.length + cluesOpen()} / ${D.base.length + 3}</span><span>💡 힌트 ${G.hints.filter(Boolean).length + G.stepHint}번</span></div>
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
function go(t){ G.tab = t; fresh = true; render(); }
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
  ${memoExample()}

  <section class="memo ${G.solved[0] ? 'done' : ''}" id="m0"><span class="tag">${G.solved[0] ? '해독 완료 ✔' : '메모 1 · 자리 바꾸기'}</span>
    <h3>📜 메모 1 · 글자 순서가 뒤섞인 메모</h3>
    <div class="code">${esc(m1.cipher)}</div>
    <p style="margin:6px 0">사기단은 문장을 <b>몇 칸짜리 줄</b>에 가로로 쓴 뒤, <b>세로로</b> 읽어 옮겨 적었어요. 칸 수를 맞히면 문장이 돼요.</p>
    ${G.solved[0] ? '' : `<div class="optlabel">👆 칸 수를 눌러 바꿔 보세요 · 지금 고른 칸: <b>${G.k}칸</b></div>
    <div class="opts">${m1.options.map(k => `<button class="${k === G.k ? 'on' : ''}" onclick="G.k=${k};render()">${k === G.k ? '✔ ' : ''}${k}칸</button>`).join('')}</div>
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
    <div class="prices">💰 가격표에 있는 금액은 <span>90000</span><span>120000</span><span>140000</span><span>160000</span><span>190000</span>뿐이에요. 되돌린 숫자가 이 중 하나가 되어야 해요.</div>
    ${G.solved[1] ? `<div class="got">🔓 새 단서: ${esc(D.cipher_clues[1])}</div>` : `<div class="row"><button class="ok" onclick="check2()">이 숫자로 해독 완료!</button><button onclick="hint(1)">💡 힌트</button></div>`}
    ${G.hints[1] && !G.solved[1] ? '<div class="hint">💡 맨 앞 4가 1이 되려면 몇 칸 되돌려야 할까요? (4 → 3 → 2 → 1)</div>' : ''}
  </section>

  <section class="memo ${G.solved[2] ? 'done' : ''}" id="m2"><span class="tag">${G.solved[2] ? '해독 완료 ✔' : '메모 3 · 0과 1'}</span>
    <h3>📜 메모 3 · 0과 1로만 적힌 메모</h3>
    <p style="margin:4px 0">${esc(m3.before)}<span class="code">${esc(m3.bits)}</span></p>
    <p style="margin:6px 0">2진수예요. 각 자리는 왼쪽부터 <b>16 · 8 · 4 · 2 · 1</b>을 뜻해요. 메모의 숫자를 보고 <b>어느 자리에 1이 있는지 직접 찾아</b> 전구를 켠 뒤, <b>합을 직접 계산</b>해서 적어 보세요.</p>
    <div class="lamps">${[16, 8, 4, 2, 1].map((v, i) => `<div class="lamp ${G.lamps[i] ? 'on' : ''}" role="button" tabindex="0" onclick="lamp(${i})" onkeydown="if(event.key==='Enter')lamp(${i})"><div class="v">${v}</div><div class="bit">?</div>${G.lamps[i] ? '💡' : '⚫'}</div>`).join('')}</div>
    <div class="sum">켠 전구 ${G.lamps.filter(Boolean).length}개 · 합은 직접 더해 보세요</div>
    ${G.solved[2] ? `<div class="got">🔓 새 단서: ${esc(D.cipher_clues[2])}</div>` : `<div class="row" style="align-items:center"><span style="font-weight:800">가격 =</span><input class="ansin" type="number" min="0" max="31" value="${esc(G.m3val || '')}" oninput="G.m3val=this.value" aria-label="2진수를 바꾼 값"><span style="font-weight:800">만 원</span><button class="ok" onclick="check3()">해독 완료!</button><button onclick="hint(2)">💡 힌트</button></div>`}
    ${G.hints[2] && !G.solved[2] ? '<div class="hint">💡 01110을 한 자리씩 16 · 8 · 4 · 2 · 1 아래에 맞춰 써 보세요. 1이 있는 자리의 값만 더해요.</div>' : ''}
  </section>
  ${cluesOpen() === 3 ? `<button class="go" style="width:100%" onclick="go('grid')">🧩 단서 3개 확보! 추리 표로 가기 ▶</button>` : ''}`;
}
function memoExample(){
  return `<section class="ex"><h3>👀 먼저 예시로 볼까요? 암호 3가지 푸는 법</h3>
  <div class="exrow">
    <div class="exbox"><span class="extag">자리 바꾸기</span><br>
      원래 문장 <b>가나다라마바</b>를 <b>3칸</b> 줄에 가로로 쓰면
      <table class="mini"><tr><td>가</td><td>나</td><td>다</td></tr><tr><td>라</td><td>마</td><td>바</td></tr></table>
      세로로 읽어 적은 암호는 <span class="code sm">가라나마다바</span>
      <p>👉 거꾸로, 암호를 <b>3칸</b>에 세로로 채우고 <b>가로로 읽으면</b> 원래 문장!</p></div>
    <div class="exbox"><span class="extag">숫자 밀기</span><br>
      <span class="code sm">1234</span> 를 <b>2칸 앞으로</b> 밀면 <span class="code sm">3456</span>
      <p>👉 암호 <b>3456</b>을 <b>2칸 되돌리면</b> 1234!<br>9 다음은 0으로 돌아가요 (8을 3칸 밀면 1).</p></div>
    <div class="exbox"><span class="extag">2진수</span><br>
      자리마다 <b>16 · 8 · 4 · 2 · 1</b><br><span class="code sm">00101</span>
      <p>👉 1이 있는 자리만 더해요: <b>4 + 1 = 5</b></p></div>
  </div></section>`;
}
function gridExample(){
  return `<section class="ex"><h3>👀 먼저 예시로 볼까요? 추리 표 채우는 법 (3명 × 색깔)</h3>
  <p style="margin:0 0 8px;word-break:keep-all">단서 ① <b>B는 파랑이다.</b> &nbsp; 단서 ② <b>A는 빨강이 아니다.</b></p>
  <div class="exrow">
    <div class="exbox"><span class="extag">1. 바로 정해지는 단서</span>
      <table class="mini"><tr><th></th><th>빨강</th><th>파랑</th><th>노랑</th></tr>
      <tr><th>A</th><td></td><td class="x new">❌</td><td></td></tr>
      <tr><th>B</th><td class="x new">❌</td><td class="o new">⭕</td><td class="x new">❌</td></tr>
      <tr><th>C</th><td></td><td class="x new">❌</td><td></td></tr></table>
      <p>단서 ①로 B-파랑 ⭕. 한 사람은 색 하나, 한 색은 한 사람뿐이라 같은 줄·같은 칸은 ❌</p></div>
    <div class="exbox"><span class="extag">2. ‘아니다’ 단서</span>
      <table class="mini"><tr><th></th><th>빨강</th><th>파랑</th><th>노랑</th></tr>
      <tr><th>A</th><td class="x new">❌</td><td class="x">❌</td><td></td></tr>
      <tr><th>B</th><td class="x">❌</td><td class="o">⭕</td><td class="x">❌</td></tr>
      <tr><th>C</th><td></td><td class="x">❌</td><td></td></tr></table>
      <p>단서 ②로 A-빨강 ❌</p></div>
    <div class="exbox"><span class="extag">3. 하나 남으면 ⭕</span>
      <table class="mini"><tr><th></th><th>빨강</th><th>파랑</th><th>노랑</th></tr>
      <tr><th>A</th><td class="x">❌</td><td class="x">❌</td><td class="o new">⭕</td></tr>
      <tr><th>B</th><td class="x">❌</td><td class="o">⭕</td><td class="x">❌</td></tr>
      <tr><th>C</th><td class="o new">⭕</td><td class="x">❌</td><td class="x new">❌</td></tr></table>
      <p>A 줄에 남은 칸은 노랑뿐 → ⭕. 그러면 C는 빨강!</p></div>
  </div>
  <div class="tips"><b>🧭 진짜 문제에서는 이렇게 해요</b><ol>
    <li><b>‘누가 무엇’이 바로 적힌 단서</b>부터 ⭕로 옮겨요.</li>
    <li><b>두 단서를 이어 붙여요.</b> 예: ‘전화 = 19만 원’ + ‘신분증 = 19만 원’ → 전화한 사람이 신분증을 요구했어요.</li>
    <li>한 줄에 <b>남은 칸이 하나</b>면 그게 ⭕예요.</li>
    <li>‘아니다’ 단서는 ❌로 표시해요.</li></ol></div></section>`;
}
function hint(i){ G.hints[i] = true; render(); }
function lamp(i){ G.lamps[i] = G.lamps[i] ? 0 : 1; render(); }
function unlock(i){ G.solved[i] = true; toastMsg = '🔓 해독 성공! 추리 표에 새 단서가 열렸어요.'; render(); }
function check1(){ if (G.k === D.memo1.answer) unlock(0); else { G.wrongMemo++; toast('아직 문장이 안 돼요. 다른 칸 수로 해 보세요.', $('m0')); } }
function check2(){ if (G.shift === D.memo2.shift) unlock(1); else { G.wrongMemo++; toast('가격표에 없는 금액이에요. 되돌리는 칸 수를 바꿔 보세요.', $('m1')); } }
function check3(){
  // 전구는 계산을 돕는 도구일 뿐이고, 직접 계산한 값이 맞아야 해독돼요.
  const ok = parseInt(G.m3val, 10) === D.memo3.answer;
  if (ok) { G.lamps = D.memo3.bits.split('').map(Number); unlock(2); }
  else { G.wrongMemo++; toast('값이 달라요. 1이 적힌 자리를 다시 찾고, 그 자리 값만 더해 보세요.', $('m2')); }
}

// ───── ② 추리 표 ─────
function cellKey(kind, s, v){ return kind + '|' + s + '|' + v; }
function gridTab(){
  const clueHtml = D.base.map((t, i) => clueBtn('b' + i, t, false, false))
    .concat(D.cipher_clues.map((t, i) => clueBtn('m' + i, G.solved[i] ? t : `🔒 메모 ${i + 1}을 해독하면 열려요`, !G.solved[i], true))).join('');
  $('body').innerHTML = `
  <div class="story">👆 칸을 누를 때마다 <b>빈칸 → ❌ 아님 → ⭕ 맞음</b>으로 바뀌어요. 단서를 하나씩 읽고 표에 표시해 보세요. 다 쓴 단서는 눌러서 지워 두면 편해요.
  <label class="autochk"><input type="checkbox" ${G.auto ? 'checked' : ''} onchange="G.auto=this.checked"> ⭕를 표시하면 같은 줄·같은 칸의 나머지를 자동으로 ❌</label></div>
  ${gridExample()}
  <h3 style="margin:8px 2px">🔎 단서 (${D.base.length + cluesOpen()} / ${D.base.length + 3})</h3>
  <div class="legend">흰색 = 처음부터 알고 있던 단서 · <span style="background:#FFFBEA;border:1.5px solid #E6D9A8;border-radius:6px;padding:0 6px">노란색</span> = 📜 메모를 해독해서 얻은 단서(3개)</div>
  <div class="clues">${clueHtml}</div>
  <div class="tools"><button onclick="resetGrid()">↺ 표 지우기</button></div>
  <div class="grids">${KINDS.map(gridHtml).join('')}</div>
  <button class="ok bigcheck" onclick="checkGrid()">✅ 표 채점하기 (⭕ 15개를 모두 채우면)</button>
  ${aiBox()}
  ${cluesOpen() < 3 ? '<div class="hint">💡 단서 7개만으로는 답이 하나로 안 정해져요. 메모를 해독해서 단서를 더 모아요!</div>' : ''}`;
}
function clueBtn(id, text, locked, memo){
  const src = memo ? `<span class="src">📜 메모 ${+id.slice(1) + 1}에서 나온 단서</span>` : '';
  return `<button class="clue ${locked ? 'lock' : ''} ${memo ? 'memo' : ''} ${G.used[id] ? 'used' : ''}" ${locked ? 'disabled' : `onclick="G.used['${id}']=!G.used['${id}'];render()"`}><span>${src}${esc(text)}</span></button>`;
}
// ───── 🤖 AI에게 물어보기 (정해진 힌트 대신, 내가 궁금한 걸 5번까지) ─────
let AI = {answers: [], left: 5, wait: false};
function aiBox(){
  const qa = AI.answers.map((x, i) => `<div class="qa"><b>🙋 질문 ${i + 1}:</b> ${esc(x.q)}<br><b>🤖</b> ${esc(x.a)}</div>`).join('');
  const can = AI.left > 0 && !AI.wait;
  return `<section class="ai"><h4>🤖 막혔어요! AI에게 물어보기 (남은 횟수 ${AI.left} / 5)</h4>
  <div style="font-size:.88rem;margin-bottom:6px;word-break:keep-all">정해진 힌트 대신, <b>내가 진짜 궁금한 것</b>을 물어보세요. 예: “운동화왕은 왜 전화가 아니에요?”, “다음에 어떤 단서를 쓰면 좋을까요?” AI는 정답을 바로 알려 주지 않고 생각할 방향을 알려 줘요. 이름·전화번호 같은 개인정보는 적지 마세요.</div>
  ${qa}
  ${AI.wait ? '<div class="qa">🤖 생각하는 중이에요…</div>' : ''}
  <div class="ask"><input id="aiq" maxlength="120" placeholder="${can ? '궁금한 점을 적어 주세요' : (AI.left ? '답을 기다리는 중…' : '질문 5번을 모두 썼어요')}" value="${esc(G.aiDraft || '')}" oninput="G.aiDraft=this.value" ${can ? '' : 'disabled'} onkeydown="if(event.key==='Enter')ask()">
  <button class="ok" onclick="ask()" ${can ? '' : 'disabled'}>물어보기</button></div></section>`;
}
function snapshot(){
  const marks = Object.entries(G.grid).filter(([, v]) => v === 2).map(([k]) => k.split('|').slice(1).join('='));
  return {solved: G.solved, marks};
}
function ask(){
  const q = (G.aiDraft || '').trim();
  if (!q) { toast('궁금한 점을 먼저 적어 주세요.'); return; }
  if (/\d{6,}/.test(q.replace(/[\s-]/g, ''))) { toast('🔒 긴 숫자는 개인정보일 수 있어서 보내지 않았어요.'); return; }
  AI.wait = true; G.stepHint++; G.aiDraft = '';
  sendResult({type: 'ask', question: q.slice(0, 120), state: snapshot()});
  render();
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
  const stars = 1 + (allMemo && G.gridChecked ? 1 : 0) + (G.hints.every(h => !h) && G.stepHint === 0 && G.wrongPick === 0 ? 1 : 0);
  const hintsUsed = G.hints.filter(Boolean).length + G.stepHint;
  sendResult({game: 'memo', type: 'finish', stars, hints: hintsUsed, wrong: G.wrongPick});
  const plays = STATS.plays || 0;
  const others = plays ? `<div class="others">🌍 지금까지 <b>${plays}번</b> 사기단이 검거됐어요. 별 3개 <b>${Math.round((STATS.star3 || 0) * 100 / plays)}%</b> · 한 번에 진짜를 지목한 비율 <b>${Math.round((STATS.first_pick || 0) * 100 / plays)}%</b></div>`
    : '<div class="others">🌍 아직 모인 기록이 없어요. 첫 검거의 주인공이에요!</div>';
  const sp = ['✨', '⭐', '🎉', '💫', '✨', '⭐', '🎉', '✨'].map((ic, k) => { const a = k * Math.PI / 4; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 140)}px;--y:${Math.round(Math.sin(a) * 110)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  $('app').innerHTML = `
  <section class="result win"><div class="big">🏡</div><b>진짜 판매자는 ‘동네이웃’이었어요!</b>
  <div class="stars">${[0, 1, 2].map(k => `<i style="animation-delay:${.3 + k * .2}s">${k < stars ? '⭐' : '☆'}</i>`).join('')}</div>
  <span class="stamp">사기단 검거!</span>${sp}</section>
  <p style="text-align:center;font-size:.9rem;color:#52616B">⭐ 정답 · ⭐ 메모 3장 해독 + 표 완성 · ⭐ 힌트 없이 한 번에 지목</p>
  ${others}
  <h3>📢 판매자별 수법 공개</h3>
  <div class="tact">${D.sellers.map((s, i) => `<div class="${s === D.real ? 'real' : ''}" style="animation-delay:${i * .08}s"><b>${D.emoji[i]} ${esc(s)} · ${esc(D.solution[s].join(' · '))}</b>${esc(D.tactics[s])}</div>`).join('')}</div>
  <section class="story" style="margin-top:12px"><b>🛡️ 중고거래 사기 막는 4가지</b><br>
  ① 판매자가 <b>앱 밖(외부 메신저·문자·오픈채팅)</b>으로 가자고 하면 멈춰요.<br>
  ② 결제는 <b>앱 안의 안전결제</b>로만. 받은 결제 링크는 누르지 말고 앱에서 직접 열어요.<br>
  ③ 시세보다 <b>너무 싼 가격</b>은 미끼일 수 있어요.<br>
  ④ <b>신분증 사진·상품권 결제</b> 요구는 거절해요.</section>
  <button class="go" style="width:100%" onclick="restart()">🔄 처음부터 다시</button>`;
}
function restart(){ fresh = true; Object.assign(G, {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0, k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, pick: null, gridChecked: false, done: false, bad: {}, stepHint: 0, m3val: '', aiDraft: ''}); sendResult({type: 'ai_reset'}); render(); }

// ───── Streamlit 높이 맞추기 ─────
let lastHeight = 0;
function sendHost(type, payload = {}) { window.parent.postMessage({isStreamlitMessage: true, type, ...payload}, '*'); }
function resize(force = false){ const root = document.querySelector('main.wrap'); if (!root) return; const h = Math.ceil(root.getBoundingClientRect().height) + 16; if (force || h !== lastHeight) { sendHost('streamlit:setFrameHeight', {height: h}); lastHeight = h; } }
// 도토리시 통계: 파이썬이 보낸 다른 사람들의 기록(stats)을 받고, 게임 결과를 파이썬으로 보냅니다.
let STATS = {};
function sendResult(obj){ sendHost('streamlit:setComponentValue', {value: Object.assign({id: Date.now() + '-' + Math.random().toString(36).slice(2)}, obj), dataType: 'json'}); }
window.addEventListener('message', ev => { if (ev.source === window.parent && ev.data && ev.data.type === 'streamlit:render') { const a = ev.data.args || {}; if (a.stats) STATS = a.stats;
  if (a.ai) { const before = AI.answers.length; AI.answers = a.ai.answers || []; AI.left = a.ai.left; G.stepHint = AI.answers.length + (AI.wait && AI.answers.length === before ? 1 : 0);
    if (AI.answers.length > before) AI.wait = false; if (G.tab === 'grid' && !G.done) render(); }
  requestAnimationFrame(() => resize(true)); } });
sendHost('streamlit:componentReady', {apiVersion: 1});
new ResizeObserver(() => requestAnimationFrame(resize)).observe(document.querySelector('main.wrap'));
window.addEventListener('load', resize); window.addEventListener('resize', resize);
render();
</script></body></html>
'''

AI_KEY = "memo_ai_answers"
AI_MAX = 5
AI_RULES = (
    "너는 고등학생이 푸는 논리 퍼즐(중고거래 판매자 5명 × 연락 방식·요구한 것·가격)을 돕는 친절한 도우미야. "
    "학생의 질문에 쉬운 해요체로 2~4문장만 답해. 정답 표 전체나 진짜 판매자가 누구인지는 절대 직접 말하지 마. "
    "대신 어떤 단서를 어떻게 이어 보면 되는지, 학생이 표시한 ⭕ 중 다시 볼 줄이 있는지 정도로 생각할 방향을 알려 줘. "
    "아직 해독하지 않은 메모의 단서 내용은 말하지 말고 '메모를 해독해 보라'고 해. "
    "퍼즐과 관계없는 질문이면 퍼즐에 대해 물어봐 달라고 짧게 답해. 개인정보를 묻거나 요구하지 마."
)


def ask_ai(question, snap):
    """AI(Gemini)에게 학생 질문을 보내 힌트를 받아요. 연결이 안 되면 준비해 둔 힌트를 대신 보여 줘요."""
    solved = list((snap or {}).get("solved") or [False] * 3)[:3]
    marks = [str(m)[:40] for m in (snap or {}).get("marks", [])][:15]
    clues = DATA["base"] + [c for c, ok in zip(DATA["cipher_clues"], solved) if ok]
    secret = "; ".join(f"{name}: {' / '.join(vals)}" for name, vals in DATA["solution"].items())
    prompt = (
        "[퍼즐 단서 - 학생이 볼 수 있는 것]\n" + "\n".join(clues)
        + f"\n[해독한 메모 수] {sum(map(bool, solved))} / 3"
        + "\n[학생이 표에 ⭕로 표시한 칸] " + (", ".join(marks) or "없음")
        + "\n[정답 - 학생에게 직접 말하지 말 것] " + secret
        + "\n[학생 질문] " + question
    )
    try:
        from google import genai
        from google.genai import types

        key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if not key:
            raise RuntimeError("missing_key")
        client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=30000))
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", contents=prompt,
            config=types.GenerateContentConfig(system_instruction=AI_RULES, max_output_tokens=600),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("empty")
        return text[:600]
    except Exception:
        used = len(st.session_state.get(AI_KEY, []))
        return "(AI 연결이 어려워서 준비해 둔 힌트를 대신 보여 줘요) " + DATA["steps"][min(used, len(DATA["steps"]) - 1)]


answers = st.session_state.setdefault(AI_KEY, [])
page = HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("<", "\\u003c"))
value = create_puzzle_component(page)(key="jamkkan_memo_puzzle_v1", default=None, stats=dd.stats("memo"),
                                      ai={"answers": answers, "left": AI_MAX - len(answers)})

# 결과를 익명 통계(+1)에 더하고, 시민증이 있으면 명예의 전당에 저장해요.
event = dd.take_event(value)
if event and event.get("type") == "ask":
    if len(answers) < AI_MAX:
        question = str(event.get("question", ""))[:120]
        with st.spinner("🤖 AI가 생각하고 있어요…"):
            answers.append({"q": question, "a": ask_ai(question, event.get("state"))})
    st.rerun()
elif event and event.get("type") == "ai_reset":
    st.session_state[AI_KEY] = []
    st.rerun()
elif event and event.get("type") == "finish":
    stars, hints, wrong = max(1, min(3, int(event.get("stars", 1)))), max(0, int(event.get("hints", 0))), max(0, int(event.get("wrong", 0)))
    dd.record("memo", {"plays": 1, f"star{stars}": 1, "first_pick": 1 if wrong == 0 else 0})
    dd.note_mine("memo", f"별 {stars}/3 · 힌트 {hints}번 · 잘못 지목 {wrong}번")
    dd.stamp("10")
    st.session_state["memo_hall"] = dd.save_hall(
        "memo", {"stars": stars, "hints": hints, "wrong": wrong},
        lambda old, new: (new["stars"], -new["hints"], -new["wrong"]) > (old.get("stars", 0), -old.get("hints", 10**6), -old.get("wrong", 10**6)),
    )
dd.show_hall_note(st.session_state.get("memo_hall"))

with st.expander("🧠 이 페이지 속 알고리즘 (정보 과목 연계)"):
    st.markdown(
        "- **AI 힌트**: 정해진 힌트 대신 내가 궁금한 걸 AI(Gemini)에게 5번까지 물어볼 수 있어요. 질문 글과 표에 표시한 ⭕만 보내고, 이름 같은 개인정보는 보내지 않아요.\n"
        "- **암호화와 복호화**: 메모 1은 글자 자리를 바꾸는 전치 암호, 메모 2는 숫자를 같은 칸만큼 미는 시저 암호예요. 열쇠(칸 수)를 알면 거꾸로 풀 수 있어요.\n"
        "- **2진수**: 메모 3의 01110은 각 자리가 16·8·4·2·1을 뜻해서 8 + 4 + 2 = 14가 돼요.\n"
        "- **제약 조건과 완전 탐색**: 논리 표는 가능한 172만 8천 가지 경우를 모두 검사해서, 단서 10개를 다 쓰면 답이 딱 하나만 남도록 만들었어요."
    )
st.caption("교육용 가상 이야기입니다. 실제 거래 앱·판매자와 관계없으며, 진행은 새로고침하면 초기화됩니다.")
