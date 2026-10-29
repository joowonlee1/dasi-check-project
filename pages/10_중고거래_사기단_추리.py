from play_ui import intro, bridge
"""거래 기록 세 묶음의 근거를 연결한 뒤 기존 논리 표로 판매자를 찾는 교육용 게임."""
import json
from investigation_ui import attach

import streamlit as st
import dotori_data as dd
from mascot_ui import show_key_question, show_mascot
from puzzle_component_ui import create_puzzle_component

with intro("10", suffix=""):
    st.title("🔐 중고거래 사기단 추리")
    show_key_question("판매자 5명 중 **진짜는 단 1명**. 거래 기록을 **비교**하고, 단서로 **진짜 판매자**를 찾아내세요.", "🔐")
    show_mascot("sneaker", "거래 기록을 연결할 때마다 새 단서가 나와요. 단서를 모두 모아야 범인이 가려져요!", width=100)

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
    # 조사 1: 4칸으로 가로로 쓴 문장을 세로로 읽어 만든 전치 암호
    "memo1": {"cipher": "외저자자결를부로던가제보메옮판가링냈신기매짜크다", "answer": 4, "options": [2, 3, 4, 6, 8]},
    # 조사 2: 숫자마다 3칸씩 앞으로 민 시저 암호 (120000 → 453333)
    "memo2": {"before": "선입금 이체를 요구한 판매자의 가격: ", "cipher": "453333", "after": "원", "shift": 3},
    # 조사 3: 2진수 01110 = 14
    "memo3": {"before": "오픈채팅 판매자의 가격(만 원): ", "bits": "01110", "answer": 14},
    # 추리 표에서 막혔을 때 한 단계씩 보여 주는 힌트(정답 표를 바로 알려 주지 않음)
    "steps": [
        "먼저 ‘누가 무엇’이 바로 적힌 단서 4개를 표에 ⭕로 옮겨요: 동네이웃=앱 채팅, 새상품만=문자, 운동화왕=상품권, 급처분해요=9만 원.",
        "‘전화 = 19만 원’과 ‘신분증 사진 = 가장 비쌈(19만 원)’을 이어 보세요. 전화로 연락한 판매자와 신분증 사진을 요구한 판매자는 같은 사람이에요.",
        "남은 연락 방식은 외부 메신저·전화·오픈채팅이고, 남은 사람은 한정판러·급처분해요·운동화왕이에요. 상품권을 요구한 운동화왕은 전화(신분증)도, 외부 메신저(가짜 링크, 조사 1)도 아니에요.",
        "운동화왕이 오픈채팅이면 조사 3에 따라 가격이 정해져요. 급처분해요는 9만 원이라 19만 원인 전화가 될 수 없어요.",
        "마지막으로 앱 안전결제와 선입금 이체 중 누가 무엇인지 정해요. ‘앱 안전결제 판매자는 문자로 연락하지 않았다’와 조사 2를 써 보세요.",
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
.clues{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:8px 0}.clues .clue{margin:0!important;min-height:52px;align-items:center}@media (max-width:640px){.clues{grid-template-columns:1fr}}
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
 .toast,.msg-toast{font-size:1.2rem!important;font-weight:900!important;padding:18px!important;line-height:1.6!important;}
</style></head><body><main class="wrap" id="app"></main>
<script>
const D = __DATA__;
const IQ_THEME = 'market';
// 도토리마켓 앱 화면 모양의 큰 창 (중고거래 추리 전용)
function marketPop(o, then){
  jkOverlay(`<div class="jk-panel" style="background:#1F2937;border-radius:34px;padding:12px;box-shadow:0 20px 50px #0007;max-width:560px">
   <div style="background:#FFF7ED;border-radius:26px;overflow:hidden">
    <div style="background:${o.bar||'#F97316'};color:#fff;padding:12px 18px;font-weight:900;font-size:1.05rem;display:flex;justify-content:space-between"><span>🛍️ 도토리마켓</span><span>${o.tag||''}</span></div>
    <div style="padding:16px 18px;display:flex;gap:14px;align-items:center">${jkImg(o.mascot,150)}
     <div style="flex:1"><div style="font-size:1.35rem;font-weight:900;color:#7C2D12;line-height:1.35">${o.title}</div>
     <div style="margin-top:8px;background:#fff;border-radius:4px 16px 16px 16px;padding:10px 12px;box-shadow:0 1px 3px #0002;font-size:1.02rem;line-height:1.7;color:#1F2937">${o.body}</div></div></div>
    ${o.extra||''}
    <div style="padding:0 18px 18px"><button data-close style="width:100%;min-height:52px;border:0;border-radius:14px;background:${o.bar||'#F97316'};color:#fff;font:800 1.1rem system-ui;cursor:pointer">${o.button||'확인했어요 ▶'}</button></div>
   </div></div>`, then);
}

const KINDS = ['c', 'r', 'p'];
const G = {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0,
  k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, auto: true, pick: null, gridChecked: false, done: false, bad: {}, stepHint: 0};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let toastMsg = '';
let fresh = true;  // 탭을 처음 열 때만 튀어나오는 효과를 보여 줍니다.

function cluesOpen(){ return G.solved.filter(Boolean).length; }

let hasInteracted=false;
document.addEventListener('click',e=>{if(e.target.closest('button')){hasInteracted=true;setPlayActive(true);}},true);
function render(){
  setPlayActive(hasInteracted);
  const app = $('app');
  if (G.done) return;
  app.classList.toggle('still', !fresh); fresh = false;
  app.innerHTML = `
  <section class="hero"><span>🔐 추리 퍼즐 · 거래 기록 조사 → 논리 표 → 지목</span><b>한정판 운동화, 진짜 판매자는 누구?</b>
  <span>정가 18만 원짜리 운동화를 사려는데 판매자 5명이 연락해 왔어요. 나머지 4명은 저마다 다른 수법을 쓰는 사기단이에요.</span></section>
  <div class="sellhead">🛍️ 연락해 온 판매자 5명 (중고거래 앱 닉네임)</div>
  <div class="sellers">${D.sellers.map((s, i) => `<div style="animation-delay:${i * .07}s"><em style="animation-delay:${i * .3}s">${D.emoji[i]}</em><small>판매자 ${i + 1}</small>${esc(s)}</div>`).join('')}</div>
  <div class="prices">💰 판매자들이 부른 가격(가격표): ${D.attrs.p.values.map(v => `<span>${esc(v)}</span>`).join('')} · 누가 얼마를 불렀는지는 단서로 찾아요.</div>
  <div class="chips"><span class="hot">📜 검증한 거래 기록 ${cluesOpen()} / 3</span><span>🔎 쓸 수 있는 단서 ${D.base.length + cluesOpen()} / ${D.base.length + 3}</span><span>💡 사용한 힌트 ${G.hints.filter(Boolean).length + G.stepHint}번</span></div>
  <button style="background:#fff;border:2px solid #20483F;color:#20483F;margin:0 0 8px" onclick="goBack()">← 이전 화면으로</button>
  <div class="tabs">
    <button class="${G.tab === 'memo' ? 'on' : ''}" onclick="go('memo')">① 📜 거래 기록 조사</button>
    <button class="${G.tab === 'grid' ? 'on' : ''}" onclick="go('grid')">② 🧩 추리 표</button>
    <button class="${G.tab === 'pick' ? 'on' : ''}" onclick="go('pick')">③ 🏁 진짜 지목</button>
  </div>
  <div id="body"></div>
  <div class="toast" id="toast" aria-live="polite">${esc(toastMsg)}</div>`;
  toastMsg = '';
  if (G.tab === 'memo') memoTab(); else if (G.tab === 'grid') gridTab(); else pickTab();
}
function go(t){ G.tab = t; fresh = true; render(); }
// 바로 전 화면으로: 추리 표 → 거래 기록, 지목 → 추리 표, 거래 기록 → 바깥의 게임 설명 화면. 진행은 그대로 남아요.
function goBack(){ const order = ['memo', 'grid', 'pick'], k = order.indexOf(G.tab);
  if (k > 0) { go(order[k - 1]); return; }
  hasInteracted = false; setPlayActive(false); try { window.parent.scrollTo({top: 0, behavior: 'smooth'}); } catch (e) {} }
function toast(t, el){ const x = $('toast'); if (x) x.textContent = t; if (el) { el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); } }

// ───── ① 거래 기록 조사 ─────
function decodeColumns(ct, k){ const r = ct.length / k, cols = []; for (let i = 0; i < k; i++) cols.push(ct.slice(i * r, (i + 1) * r)); let out = ''; for (let i = 0; i < r; i++) for (let c = 0; c < k; c++) out += cols[c][i]; return {out, cols, r}; }
function shiftBack(s, n){ return s.replace(/\d/g, d => String((+d - n + 100) % 10)); }

function memoTab(){
 $('body').innerHTML='<div class="story" style="border:2.5px solid #F1DFA6;background:#FFFBEB"><b style="font-size:1.08rem">🧭 시작하기 전에 · 이렇게 풀어요</b><p style="margin:.4rem 0 .2rem">거래 기록은 <b>누구의 거래인지 이름을 가려 둔</b> 조사 자료예요. 대신 판매자마다 <b>익명 판매자 가·나·다·라</b> 이름표를 붙여 두었어요. <b>위의 판매자 1~5와는 다른 이름표</b>라서, 누가 누구인지는 추리 표로 찾아야 해요. (예: <b style="border:2px solid #60A5FA;background:#DBEAFE;color:#1E40AF;padding:0 7px;border-radius:999px">🕵️ 익명 판매자 가</b> 거래라고 적힌 자료들은 모두 같은 판매자와의 거래 이야기)</p><ol style="margin:.3rem 0 .2rem 1.2rem;padding:0;line-height:1.7"><li><b>자료 버튼</b>을 눌러 하나씩 읽어요. 앞 자료를 읽어야 열리는 자료도 있어요. 실제 조사처럼 <b>시간 순서대로</b> 따라가야 무엇이 바뀌었는지 보이거든요.</li><li><b>같은 익명 판매자의 자료</b>끼리 이어요. 다른 익명 판매자의 자료나 판매자의 말만 있는 자료는 헷갈리라고 넣은 자료일 수 있어요.</li><li>이어 보니 알게 된 사실을 <b>결론</b>에서 고르고, 그 결론을 직접 뒷받침하는 <b>자료에 체크</b>해서 제출해요.</li><li>세 거래를 모두 풀면 단서 세 개가 생겨요. 그 단서로 <b>추리 표</b>를 채워 진짜 판매자를 찾아요.</li></ol><small style="color:#6B5A2E">💡 막히면 ‘비교할 지점 힌트’를 눌러 보세요. 정답 자료를 처음부터 다 보여 주지는 않아요.</small></div>'+[0,1,2].map(i=>iqHTML(i)).join('')+(cluesOpen()===3?`<button onclick="go('grid')">추리 표로 이동</button>`:'');
}
function iqComplete(i){unlock(i);}
function iqHintUsed(i){G.hints[i]=true;}
function iqWrong(i){G.wrongMemo++;}
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
function unlock(i){ G.solved[i] = true; render();  // 조사 완료 소식은 도토리마켓 큰 창으로만 알려요(맨 아래 글자는 띄우지 않아요)
  const n = G.solved.filter(Boolean).length;
  marketPop({mascot:'sneaker', tag:'거래 기록 조사 완료', title:`🔓 단서 확보! (${n}/3)`,
    body: esc(IQ_CASES[i].lesson) + '<br><b>추리 표에 새 단서가 열렸어요.</b>',
    button: n === 3 ? '🧩 추리 표로 가기 ▶' : '다음 거래 기록 조사하기 ▶'}, n === 3 ? () => go('grid') : null); }
function check1(){ if (G.k === D.memo1.answer) unlock(0); else { G.wrongMemo++; toast('아직 문장이 안 돼요. 다른 칸 수로 해 보세요.', $('m0')); } }
function check2(){ if (G.shift === D.memo2.shift && Number(G.m2val) === Number(shiftBack(D.memo2.cipher,D.memo2.shift))) unlock(1); else { G.wrongMemo++; toast('되돌리는 칸 수와 직접 계산한 금액을 함께 확인하세요.', $('m1')); } }
function check3(){
  // 메모의 비트 위치를 옮기고 직접 계산한 값까지 맞아야 해독돼요.
  const ok = parseInt(G.m3val, 10) === D.memo3.answer && G.lamps.join("") === D.memo3.bits;
  if (ok) { G.lamps = D.memo3.bits.split('').map(Number); unlock(2); }
  else { G.wrongMemo++; toast('값이 달라요. 1이 적힌 자리를 다시 찾고, 그 자리 값만 더해 보세요.', $('m2')); }
}

// ───── ② 추리 표 ─────
function cellKey(kind, s, v){ return kind + '|' + s + '|' + v; }
function gridTab(){
  const clueHtml = D.base.map((t, i) => clueBtn('b' + i, t, false, false))
    .concat(D.cipher_clues.map((t, i) => clueBtn('m' + i, G.solved[i] ? t : `🔒 메모 ${i + 1}의 근거를 연결하면 열려요`, !G.solved[i], true))).join('');
  $('body').innerHTML = `
  <div class="story"><b>판매자 한 명당 연락 방식·요구 사항·가격은 각각 하나씩이에요. 각 항목도 한 사람에게만 대응해요. 한 표의 각 행·열마다 ⭕는 하나예요.</b><br>👆 칸을 누를 때마다 <b>빈칸 → ❌ 아님 → ⭕ 맞음</b>으로 바뀌어요. 단서를 하나씩 읽고 표에 표시해 보세요. 다 쓴 단서는 눌러서 지워 두면 편해요.
  <label class="autochk"><input type="checkbox" ${G.auto ? 'checked' : ''} onchange="G.auto=this.checked"> ⭕를 표시하면 같은 줄·같은 칸의 나머지를 자동으로 ❌</label></div>
  ${gridExample()}
  <h3 style="margin:8px 2px">🔎 단서 (${D.base.length + cluesOpen()} / ${D.base.length + 3})</h3>
  <div class="legend">흰색 = 처음부터 알고 있던 단서 · <span style="background:#FFFBEA;border:1.5px solid #E6D9A8;border-radius:6px;padding:0 6px">노란색</span> = 📜 거래 기록을 조사해서 얻은 단서(3개)</div>
  <div class="clues">${clueHtml}</div>
  <div class="tools"><button onclick="resetGrid()">↺ 표 지우기</button></div>
  <div class="grids">${KINDS.map(gridHtml).join('')}</div>
  <button class="ok bigcheck" onclick="checkGrid()">✅ 표 채점하기 (⭕ 15개를 모두 채우면)</button>
  <div class="hint" style="background:#F5F3FF;border:2px solid #C4B5FD;color:#3730A3">🤖 막히면 화면 <b>오른쪽 아래 ‘AI 탐정’ 버튼</b>을 눌러 궁금한 걸 물어보세요. (남은 질문 ${AI.left} / 5)</div>
  ${cluesOpen() < 3 ? '<div class="hint">💡 단서 7개만으로는 답이 하나로 안 정해져요. 거래 기록을 조사해서 단서를 더 모아요!</div>' : ''}`;
}
function clueBtn(id, text, locked, memo){
  const src = memo ? `<span class="src">📜 거래 ${'ABC'[+id.slice(1)]} 조사에서 얻은 단서</span>` : '';
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

// ───── 🤖 AI 탐정: 피싱 방탈출의 ‘나의 폰’처럼 화면 오른쪽 아래에 떠 있는 버튼 + 열리는 대화창 ─────
// 같은 보라색 상자 디자인을 그대로 쓰고, 어느 탭에서든 열 수 있어요. 게임이 끝나거나 다른 페이지로 가면 사라져요.
function aiFloat(){
  let P, D; try { P = window.parent; D = P.document; } catch (e) { return; }
  const remove = () => { ['jk-ai-launch','jk-ai-panel'].forEach(id => { const el = D.getElementById(id); if (el) el.remove(); }); };
  if (G.done) { remove(); return; }
  if (!D.getElementById('jk-ai-style')) {
    const st = D.createElement('style'); st.id = 'jk-ai-style';
    st.textContent = `#jk-ai-launch{position:fixed;right:22px;bottom:96px;z-index:999990;background:#F5F3FF;color:#3730A3;border:3px solid #8B5CF6;border-radius:22px;padding:18px 30px;min-height:76px;font:900 25px system-ui,sans-serif;box-shadow:0 6px 18px #4C1D9555;cursor:pointer}
#jk-ai-launch{padding-left:112px}#jk-ai-launch::before{content:'';position:absolute;left:10px;bottom:4px;width:96px;height:106px;background:url(__AIBTNIMG__) no-repeat center bottom/contain;pointer-events:none}#jk-ai-launch.wait{animation:jkai 1s ease-in-out infinite}@keyframes jkai{50%{transform:translateY(-4px)}}
#jk-ai-panel{position:fixed;right:22px;bottom:96px;z-index:999995;width:min(440px,calc(100vw - 24px));max-height:72vh;display:flex;flex-direction:column;background:linear-gradient(135deg,#C4B5FD,#8B5CF6);border-radius:28px;padding:8px;box-shadow:0 18px 44px #4C1D9555;font-family:system-ui,sans-serif}
#jk-ai-panel .in{background:#F5F3FF;border-radius:20px;display:flex;flex-direction:column;overflow:hidden;min-height:0}
#jk-ai-panel .hd{background:#6D28D9;color:#fff;padding:12px 16px;font-weight:900;display:flex;align-items:center;gap:8px}
#jk-ai-panel .hd button{margin-left:auto;background:#fff2;color:#fff;border:0;border-radius:10px;padding:6px 10px;font:800 14px system-ui;cursor:pointer}
#jk-ai-panel .bd{padding:12px 14px;overflow:auto;min-height:120px}
#jk-ai-panel .tip{font-size:.88rem;color:#4C1D95;line-height:1.55;margin-bottom:8px;word-break:keep-all}
#jk-ai-panel .q{background:#E9D5FF;border-radius:14px 14px 4px 14px;padding:8px 12px;margin:8px 0 4px auto;max-width:85%;word-break:keep-all}
#jk-ai-panel .a{background:#fff;border-radius:14px 14px 14px 4px;padding:8px 12px;margin:4px auto 8px 0;max-width:90%;box-shadow:0 1px 3px #0002;word-break:keep-all;line-height:1.6}
#jk-ai-panel .ft{display:flex;gap:8px;padding:10px 12px;border-top:1px solid #DDD6FE;background:#fff}
#jk-ai-panel .ft input{flex:1;min-width:0;font:inherit;padding:10px 12px;border:2px solid #C4B5FD;border-radius:12px;outline:none}#jk-ai-panel .ft input:focus{border-color:#8B5CF6;box-shadow:0 0 0 3px #DDD6FE}
#jk-ai-panel .ft button{background:#20483F;color:#fff;border:0;border-radius:12px;padding:0 16px;font:800 15px system-ui;cursor:pointer}
#jk-ai-panel .ft button:disabled{opacity:.5;cursor:default}
@media(max-width:600px){#jk-ai-launch{right:12px;bottom:92px;font-size:19px;min-height:60px;padding:12px 18px 12px 78px}#jk-ai-launch::before{width:64px;height:72px;left:8px}#jk-ai-panel{right:12px;bottom:12px}}`;
    D.head.appendChild(st);
  }
  if (!P.__jkAiCleanup) {  // 다른 페이지로 가면 버튼과 창을 지워요
    const path = P.location.pathname;
    P.__jkAiCleanup = P.setInterval(() => { if (P.location.pathname !== path) { remove(); P.clearInterval(P.__jkAiCleanup); P.__jkAiCleanup = null; } }, 800);
    window.addEventListener('pagehide', remove);
  }
  const can = AI.left > 0 && !AI.wait;
  let launch = D.getElementById('jk-ai-launch');
  if (!launch) { launch = D.createElement('button'); launch.id = 'jk-ai-launch'; D.body.appendChild(launch); }
  launch.textContent = AI.wait ? '🤖 AI 탐정이 생각하는 중…' : `🤖 AI 탐정에게 물어보기 · ${AI.left}/5`;
  launch.classList.toggle('wait', AI.wait);
  launch.onclick = () => { P.__jkAiOpen = true; aiFloat(); };
  let panel = D.getElementById('jk-ai-panel');
  if (!P.__jkAiOpen) { if (panel) panel.remove(); launch.style.display = ''; return; }
  launch.style.display = 'none';
  if (!panel) { panel = D.createElement('div'); panel.id = 'jk-ai-panel'; D.body.appendChild(panel); }
  const qa = AI.answers.map(x => `<div class="q">🙋 ${esc(x.q)}</div><div class="a">🤖 ${esc(x.a)}</div>`).join('');
  panel.innerHTML = `<div class="in"><div class="hd">🤖 AI 탐정 · 남은 질문 ${AI.left} / 5<button type="button" data-x>닫기 ✕</button></div>
   <div class="bd"><div class="tip">정해진 힌트 대신, <b>내가 진짜 궁금한 것</b>을 물어보세요. 예: “운동화왕은 왜 전화가 아니에요?”, “다음에 어떤 단서를 쓰면 좋을까요?” AI는 정답을 바로 알려 주지 않고 생각할 방향을 알려 줘요. 이름·전화번호 같은 개인정보는 적지 마세요.</div>
   ${qa}${AI.wait ? '<div class="a">🤖 생각하는 중이에요…</div>' : ''}</div>
   <div class="ft"><input maxlength="120" placeholder="${can ? '궁금한 점을 적어 주세요' : (AI.left ? '답을 기다리는 중…' : '질문 5번을 모두 썼어요')}" ${can ? '' : 'disabled'}><button type="button" ${can ? '' : 'disabled'}>물어보기</button></div></div>`;
  const input = panel.querySelector('.ft input'), send = panel.querySelector('.ft button');
  input.value = G.aiDraft || '';
  input.oninput = () => { G.aiDraft = input.value; };
  input.onkeydown = e => { if (e.key === 'Enter') { e.preventDefault(); send.click(); } };
  send.onclick = () => { G.aiDraft = input.value; ask(); };
  panel.querySelector('[data-x]').onclick = () => { P.__jkAiOpen = false; aiFloat(); };
  const bd = panel.querySelector('.bd'); bd.scrollTop = bd.scrollHeight;
  if (can) input.focus({preventScroll: true});
}
const _renderMain = render;
render = function(){ _renderMain(); aiFloat(); };
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
  if(!G.solved.every(Boolean)){toast("먼저 거래 기록 3건의 근거 연결을 완료하세요.");return;}
  const os = Object.entries(G.grid).filter(([, v]) => v === 2).map(([k]) => k);
  if (os.length < 15) { toast(`⭕가 ${os.length}개예요. 판매자마다 연락 방식·요구·가격을 하나씩, 모두 15개를 채워요.`); return; }
  G.bad = {};
  let wrong = 0;
  os.forEach(k => { const [kind, s, v] = k.split('|'); if (D.solution[s][KINDS.indexOf(kind)] !== v) { G.bad[k] = 1; wrong++; } });
  if (!wrong) { try { window.parent.__jamkkanSound?.play('success'); } catch(e) {} G.gridChecked = true; toastMsg = '🎉 표 완성! 모든 칸이 맞았어요. 이제 진짜 판매자를 지목해요!'; G.tab = 'pick'; render(); }
  else { toastMsg = `❌ 빨간 테두리 칸 ${wrong}개가 틀렸어요. 단서를 다시 확인해요.`; render(); }
}

// ───── ③ 진짜 지목 ─────
function pickTab(){
  $('body').innerHTML = `
  <div class="story">🏁 진짜 판매자라고 생각하는 사람을 골라요. <b>앱 밖으로 나가자고 하지 않고, 안전하게 거래하는 판매자</b>는 누구였을까요?</div>
  <div class="pick" id="pk">${D.sellers.map((s, i) => `<button class="${G.pick === s ? 'on' : ''}" onclick="G.pick='${esc(s)}';render()"><em>${D.emoji[i]}</em>${esc(s)}</button>`).join('')}</div>
  <button class="go" style="width:100%" ${G.pick && G.gridChecked && G.solved.every(Boolean) ? '' : 'disabled'} onclick="answer()">🔍 이 판매자가 진짜예요!</button>
  ${G.gridChecked ? '' : '<p style="font-size:.88rem;color:#52616B">거래 기록 3건을 조사하고 추리표를 완성해야 최종 지목할 수 있어요.</p>'}`;
}
function answer(){
  if(!G.solved.every(Boolean)||!G.gridChecked){toast("거래 기록 3건과 추리표를 완성한 뒤 지목하세요.");return;}
  if (G.pick !== D.real) { G.wrongPick++; toast(`${G.pick}의 요구를 다시 떠올려 봐요. 표를 확인하고 다시 골라요!`, $('pk'));
    marketPop({mascot:'think', bar:'#64748B', tag:'신고 반려', title:`🚨 ${esc(G.pick)}님은 진짜 판매자가 아니에요`,
      body:'그 판매자가 무엇을 요구했는지 추리 표에서 다시 확인해 봐요. <b>앱 밖으로 나가자고 하지 않고, 안전하게 거래하는 판매자</b>가 진짜예요.', button:'추리 표 다시 보기 ▶'});
    return; }
  G.done = true; aiFloat();  // 게임이 끝나면 AI 탐정 버튼을 치워요
  const box = $('app');
  const steps = [['🥁', '두구두구…'], ['🔎', '거래 기록을 대조하는 중…'], ['🎉', '진짜 판매자 발견!']];
  let i = 0;
  const tick = () => { if (i < steps.length) { box.innerHTML = `<div class="drum"><div>${steps[i][0]}</div>${steps[i][1]}</div>`; i++; setTimeout(tick, 600); } else final(); };
  tick();
  try { if (window.frameElement) window.frameElement.scrollIntoView({behavior: 'smooth', block: 'start'}); } catch (e) {}
}
function final(){
  const allMemo = G.solved.every(Boolean);
  const stars = 1 + (allMemo && G.gridChecked ? 1 : 0) + (G.hints.every(h => !h) && G.stepHint === 0 && G.wrongPick === 0 && G.wrongMemo === 0 ? 1 : 0);
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
  <p style="text-align:center;font-size:.9rem;color:#52616B">⭐ 정답 · ⭐ 거래 기록 3건 조사 + 표 완성 · ⭐ 힌트 없이 한 번에 지목</p>
  ${others}
  <h3>📢 판매자별 수법 공개</h3>
  <div class="tact">${D.sellers.map((s, i) => `<div class="${s === D.real ? 'real' : ''}" style="animation-delay:${i * .08}s"><b>${D.emoji[i]} ${esc(s)} · ${esc(D.solution[s].join(' · '))}</b>${esc(D.tactics[s])}</div>`).join('')}</div>
  <section class="story" style="margin-top:12px"><b>🛡️ 중고거래 사기 막는 4가지</b><br>
  ① 판매자가 <b>앱 밖(외부 메신저·문자·오픈채팅)</b>으로 가자고 하면 멈춰요.<br>
  ② 결제는 <b>앱 안의 안전결제</b>로만. 받은 결제 링크는 누르지 말고 앱에서 직접 열어요.<br>
  ③ 시세보다 <b>너무 싼 가격</b>은 미끼일 수 있어요.<br>
  ④ <b>신분증 사진·상품권 결제</b> 요구는 거절해요.</section>
  <button class="go" style="width:100%" onclick="restart()">🔄 처음부터 다시</button>`;
  marketPop({mascot:'hooray', bar:'#15803D', tag:'🚔 사기단 검거 보고서', title:'🎉 진짜 판매자는 ‘동네이웃’!',
    body:`앱 안에서 안전결제로 거래한 판매자만 진짜였어요. 나머지 4명은 외부 메신저·선입금·상품권·신분증 사진을 요구했죠.<br><b style="font-size:1.3rem">${'⭐'.repeat(stars)}${'☆'.repeat(3-stars)}</b>`,
    button:'판매자별 수법 보기 ▶'});
}
function restart(){ iqReset(); hasInteracted=false; fresh = true; Object.assign(G, {tab: 'memo', solved: [false, false, false], hints: [false, false, false], wrongMemo: 0, wrongPick: 0, k: 2, shift: 0, lamps: [0, 0, 0, 0, 0], grid: {}, used: {}, pick: null, gridChecked: false, done: false, bad: {}, stepHint: 0, m3val: '', m2val: '', aiDraft: ''}); sendResult({type: 'ai_reset'}); render(); }

// ───── Streamlit 높이 맞추기 ─────
let lastHeight = 0;
function sendHost(type, payload = {}) { window.parent.postMessage({isStreamlitMessage: true, type, ...payload}, '*'); }
function resize(force = false){ const root = document.querySelector('main.wrap'); if (!root) return; const h = Math.ceil(root.getBoundingClientRect().height) + 16; if (force || h !== lastHeight) { sendHost('streamlit:setFrameHeight', {height: h}); lastHeight = h; } }
// 도토리시 통계: 파이썬이 보낸 다른 사람들의 기록(stats)을 받고, 게임 결과를 파이썬으로 보냅니다.
let STATS = {};
function sendResult(obj){ sendHost('streamlit:setComponentValue', {value: Object.assign({id: Date.now() + '-' + Math.random().toString(36).slice(2)}, obj), dataType: 'json'}); }
window.addEventListener('message', ev => { if (ev.source === window.parent && ev.data && ev.data.type === 'streamlit:render') { const a = ev.data.args || {}; if (a.stats) STATS = a.stats;
  if (a.ai) { const before = AI.answers.length; AI.answers = a.ai.answers || []; AI.left = a.ai.left; G.stepHint = AI.answers.length + (AI.wait && AI.answers.length === before ? 1 : 0);
    if (AI.answers.length > before) AI.wait = false; if (!G.done) render(); }
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
    "아직 조사를 완료하지 않은 거래 기록의 단서 내용은 말하지 말고 '거래 자료를 비교하고 근거를 연결해 보라'고 해. "
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
        + f"\n[검증한 거래 기록 수] {sum(map(bool, solved))} / 3"
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
from game_phone import _btn_img  # AI 탐정 버튼에 붙일 로봇 깡지 그림
page = bridge(attach(HTML), "10").replace("__AIBTNIMG__", _btn_img("btn_ai.png")).replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("<", "\\u003c"))
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
    if wrong == 0:
        dd.achieve("memo_clean")  # 업적: 잘못 지목 없이 검거
    st.session_state["memo_hall"] = dd.save_hall(
        "memo", {"stars": stars, "hints": hints, "wrong": wrong},
        lambda old, new: (new["stars"], -new["hints"], -new["wrong"]) > (old.get("stars", 0), -old.get("hints", 10**6), -old.get("wrong", 10**6)),
    )
dd.show_hall_note(st.session_state.get("memo_hall"))

with st.expander("🧠 이 페이지 속 알고리즘 (정보 과목 연계)"):
    st.markdown("- 같은 익명 판매자 이름표로 자료를 연결하고, 같은 거래의 시간 순서와 조건 변경을 비교해요.\n- 연결한 단서를 추리 표의 제약 조건으로 바꿔 가능한 조합을 줄여요.\n- AI 힌트는 현재 확보한 단서와 표를 바탕으로 비교할 지점을 안내해요.")
st.caption("교육용 가상 이야기입니다. 실제 거래 앱·판매자와 관계없으며, 진행은 새로고침하면 초기화됩니다.")
