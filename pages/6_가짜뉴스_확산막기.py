from play_ui import intro, bridge
"""가짜뉴스 확산 막기: 주민 연결망(그래프) 위에서 퍼지는 가짜 소식을 카드로 막는 전략 게임.

- 퍼지는 방식은 너비 우선 탐색(BFS)처럼 한 단계씩 이웃에게 번집니다.
- 연결이 많은 사람(허브)을 먼저 지키는 것이 핵심 전략입니다.
- 모든 인물·소식·기관은 가상의 도토리시 이야기입니다.
"""
import json

import streamlit as st
import dotori_data as dd
from mascot_ui import show_key_question, show_mascot
from river_component_ui import create_river_component

with intro("06", suffix=""):
    st.title("🌐 가짜뉴스 확산 막기")
    from mascot_ui import show_scene
    import scene_ui
    SCENE_SLOT = st.empty() if scene_ui.ready("scene_plaza") else None  # 장면 보드 자리(게임 결과를 처리한 뒤 그려요)
    if SCENE_SLOT is None:
        show_scene("scene_plaza", "")
    show_key_question("가짜 소식은 **사람과 사람 사이를 타고** 번져요. 카드 몇 장으로 **누구를 먼저 지킬지** 골라 보세요.", "🌐")

# 단계: 수법, 마을 크기, 카드 수, 퍼지는 간격(ms), 처음 올린 계정 수, 가짜 소식, 진실, 수법 공개, 정정 문구 퀴즈
STAGES = [
    {
        "tactic": "사칭", "icon": "🎭", "n": 18, "cards": 4, "tick": 1500, "sources": 1,
        "account": "도토리시청 공식🏛️ (사칭 계정)",
        "post": "시청 공식! 24일 오전 10시 분수 앞에서 아이스크림 무료 증정!",
        "truth": "진짜 시청 공지: 24일 오전 10시는 분수 시운전이에요. 아이스크림 증정 행사는 없어요.",
        "reveal": "공식 기관 이름과 로고를 흉내 내면 사람들은 내용을 확인하지 않고 믿어요. 진짜 공지의 시간(오전 10시)을 그대로 섞어 더 그럴듯하게 만들었어요.",
        "options": [
            ["시청 누리집 공지에는 시운전만 있고 증정 행사는 없대. 직접 확인해 봐!", True, "근거(공식 공지)와 확인 방법을 함께 알려 줬어요."],
            ["이거 올린 사람 완전 사기꾼이네. 다 같이 욕하자", False, "화내기와 비난은 오히려 글을 더 퍼뜨려요. 근거가 없어요."],
            ["아이스크림이라니 일단 가 보고 판단하자", False, "확인을 미루는 사이 소식은 계속 퍼져요."],
        ],
    },
    {
        "tactic": "감정 자극", "icon": "🔥", "n": 20, "cards": 4, "tick": 1350, "sources": 1,
        "account": "@도토리속보24",
        "post": "충격!! 시장 노점 10곳 전부 철거, 영업 중단!! 이게 말이 됩니까?",
        "truth": "시장 공지 원문: 노점 10곳 중 2곳만 옆 골목으로 이전하고, 8곳은 그대로 영업해요.",
        "reveal": "‘충격’, ‘이게 말이 됩니까?’처럼 화나게 하는 말은 확인보다 공유를 먼저 하게 만들어요. 2곳 이전을 ‘전부 철거’로 부풀렸어요.",
        "options": [
            ["공지 원문 보니 10곳 중 2곳만 옆 골목으로 옮긴대. 나머지 8곳은 그대로야", True, "원문의 숫자와 범위로 바로잡았어요."],
            ["너무 화난다! 시청에 항의 전화 돌리자", False, "감정에 휩쓸리면 사실 확인을 건너뛰게 돼요."],
            ["철거라니… 이번 주에 미리 다 사 두자", False, "가짜 소식을 믿고 행동하면 피해가 커져요."],
        ],
    },
    {
        "tactic": "가짜 증거", "icon": "📸", "n": 22, "cards": 4, "tick": 1200, "sources": 1,
        "account": "@도토리_제보방",
        "post": "[사진] 지금 도토리시 시내 전부 물에 잠겼어요!! 다들 조심하세요",
        "truth": "사진 원본: 2023년 7월 솔빛시에서 찍은 사진이에요. 오늘 도토리시 공지에는 시내 침수가 없어요.",
        "reveal": "사진이나 캡처가 붙으면 증거처럼 보여요. 다른 날, 다른 도시의 사진을 ‘지금 여기’라고 바꿔 붙였어요.",
        "options": [
            ["사진 원본 찾아보니 2023년 솔빛시 사진이래. 오늘 공지엔 시내 침수 없음", True, "사진의 원본(날짜·장소)과 공식 공지로 바로잡았어요."],
            ["사진까지 있으면 진짜지. 빨리 피하라고 공유하자", False, "사진이 있다고 진짜는 아니에요. 오히려 퍼뜨리는 쪽이 돼요."],
            ["사진이 좀 이상한데? 합성 같아", False, "느낌만으로는 설득이 안 돼요. 원본이라는 근거가 필요해요."],
        ],
    },
    {
        "tactic": "편 가르기", "icon": "🧩", "n": 24, "cards": 5, "tick": 1100, "sources": 2,
        "account": "북부 소식통 · 남부 소식통 (같은 운영자)",
        "post": "남부가 축제 예산을 빼앗았다! 남부 900만 원, 북부 100만 원!",
        "truth": "축제 예산 배분표: 북부 500만 원, 남부 500만 원으로 같아요.",
        "reveal": "‘우리 편 대 저쪽 편’으로 나누면 내 편의 말은 확인 없이 믿게 돼요. 같은 운영자가 양쪽 동네에서 동시에 올렸어요.",
        "options": [
            ["예산 배분표 보니 북부·남부 각각 500만 원으로 같아", True, "양쪽 숫자를 모두 보여 줘서 편 가르기를 멈췄어요."],
            ["남부 사람들은 원래 그래. 이번에 따끔하게 말해 주자", False, "상대 동네를 탓하는 말은 갈등만 키워요."],
            ["북부도 똑같이 900만 원 달라고 하자", False, "가짜 숫자를 사실로 받아들인 대응이에요."],
        ],
    },
    {
        "tactic": "음모론", "icon": "🛰️", "n": 26, "cards": 5, "tick": 1000, "sources": 2,
        "account": "@진실을_말하는_계정",
        "post": "곧 사라질 진실! 21일 회의록 전부 삭제된다! 반박하는 사람은 다 한통속!",
        "truth": "시 누리집 공개 기록: 21일부터 누구나 회의록을 열람할 수 있고, 삭제 예정도 없어요.",
        "reveal": "‘반박하는 사람은 한통속’이라고 미리 말해 두면, 어떤 정정도 믿지 않게 만들 수 있어요. 확인할 수 있는 기록을 숨겨진 비밀처럼 꾸몄어요.",
        "options": [
            ["시 누리집에서 21일 회의록 지금도 열람돼. 삭제 예정도 없대", True, "누구나 직접 확인할 수 있는 기록으로 바로잡았어요."],
            ["맞아, 원래 다 숨기잖아. 캡처해서 퍼뜨리자", False, "근거 없이 의심을 키우는 쪽이에요."],
            ["반박하면 한통속이라니까 그냥 조용히 있자", False, "음모론의 ‘입막음’에 넘어간 거예요."],
        ],
    },
]

with intro("06", suffix="_hint"):
    show_mascot("megaphone", "연결선이 많은 사람이 막히면 소문이 크게 막혀요. 처음 1명은 퍼지기 전에 미리 알려 줄 수 있어요!", width=100)

HTML = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;background:#FFFEFA;color:#20483F;font:16px/1.6 'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
button{font:inherit;cursor:pointer;border:0;border-radius:12px;padding:11px 16px;background:#E4F0EA;color:#173D35;font-weight:800;min-height:46px;transition:transform .15s,background .15s}
button:hover:not(:disabled){transform:translateY(-2px);background:#D7E8DF}
button:active:not(:disabled){transform:scale(.96)}
button:disabled{opacity:.5;cursor:default}
button:focus-visible,.node:focus-visible{outline:3px solid #FF7A45;outline-offset:3px}
.go{background:linear-gradient(135deg,#FF7A45,#FFB347);color:#fff;box-shadow:0 5px 14px #FF7A4540;font-size:1.1rem}
.go:hover:not(:disabled){background:linear-gradient(135deg,#FF6A30,#FFA530)}
.ok{background:#0F766E;color:#fff}.ok:hover:not(:disabled){background:#0B655B}
main.wrap{max-width:980px;margin:auto;padding:6px 4px 14px}
.hero{background:linear-gradient(135deg,#1F5F55,#2E8B78);color:#fff;border-radius:22px;padding:18px;text-align:center;animation:pop .5s ease-out both}
.hero b{display:block;font-size:1.45rem;font-weight:900;word-break:keep-all}
.hero span{opacity:.92;font-weight:600;word-break:keep-all}
.hud{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.hud span{background:#EDF4F1;border-radius:999px;padding:5px 12px;font-weight:800;font-size:.92rem}
.hud .cards{background:#FFF1E6;color:#B4471B}
.post{display:flex;gap:10px;background:#fff;border:2px solid #FFC9A8;border-radius:18px;padding:12px 14px;margin:10px 0;animation:pop .45s ease-out both}
.post .ava{font-size:30px}.post .acc{font-size:.85rem;font-weight:800;color:#B4471B}
.post .txt{font-weight:800;font-size:1.05rem;word-break:keep-all}
.tip{background:#F0F7F3;border-left:5px solid #0F766E;border-radius:10px;padding:9px 12px;font-weight:700;word-break:keep-all}
.readme{position:absolute;inset:0;z-index:5;background:rgba(255,252,244,.95);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:18px;text-align:center;word-break:keep-all;animation:pop .45s ease-out both}
.readme .rm-tag{font-weight:900;color:#B4471B;font-size:1.05rem}
.readme .rm-post{background:#fff;border:3px solid #FF9A62;border-radius:18px;padding:16px 18px;max-width:560px;box-shadow:0 6px 18px rgba(180,71,27,.15)}
.readme .rm-post .acc{font-size:.9rem;font-weight:800;color:#B4471B;margin-bottom:6px}
.readme .rm-post .txt{font-size:1.3rem;font-weight:900;color:#1F2D29;line-height:1.5}
.readme .rm-tip{font-weight:700;color:#33524A}
.board.locked{min-height:400px}
@media (max-width:560px){.readme{gap:10px;padding:12px}.readme .rm-post{padding:12px 14px}.readme .rm-post .txt{font-size:1.1rem}}
.board{position:relative;background:radial-gradient(circle at 30% 20%,#F4FBF7,#E2EFE8);border:2px solid #D7E2DD;border-radius:22px;overflow:hidden;margin:10px 0}
svg{display:block;width:100%;height:auto;touch-action:manipulation}
.edge{stroke:#B7CBC2;stroke-width:2.5}
.edge.hot{stroke:#E5484D;stroke-width:4;animation:flash .7s ease-out}
.node{cursor:pointer}
.node circle.body{fill:#fff;stroke:#9DB5AA;stroke-width:3;transition:fill .2s,stroke .2s}
.node.I circle.body{fill:#FFE1DE;stroke:#E5484D}
.node.R circle.body{fill:#D7F2E3;stroke:#0F766E;stroke-width:4}
.node.C circle.body{fill:#E8EEFF;stroke:#5B6FD6;stroke-width:4}
.node.src circle.body{fill:#3B2A2A;stroke:#E5484D}
.node text{pointer-events:none;text-anchor:middle;dominant-baseline:central}
.node .badge{font-size:15px}
.node.pulse{animation:pulse .5s ease-out}
.ring{fill:none;stroke:#E5484D;stroke-width:3;animation:ring .8s ease-out forwards;pointer-events:none}
.ring.g{stroke:#0F766E}.ring.b{stroke:#5B6FD6}
.float{font-weight:900;font-size:20px;pointer-events:none;animation:float 1s ease-out forwards;text-anchor:middle}
.toast{min-height:1.6em;font-weight:800;color:#B4471B;text-align:center;margin:6px 0;word-break:keep-all}
.row{display:flex;gap:10px;flex-wrap:wrap}.row button{flex:1}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0}
.step{background:#fff;border:2px solid #D7E2DD;border-radius:18px;padding:14px 10px;text-align:center;animation:pop .45s ease-out both;word-break:keep-all}
.step.key{border:3px solid #FF7A45;background:#FFF6EE;position:relative;box-shadow:0 6px 16px #FF7A4530}
.step.key b{color:#B4471B}
.badge3{position:absolute;top:-11px;right:10px;background:#FF7A45;color:#fff;border-radius:999px;padding:1px 10px;font-size:.78rem;font-weight:900;animation:bob 1.6s ease-in-out infinite}
.hubtip{border-radius:18px;padding:16px;margin:10px 0;font-weight:800;word-break:keep-all;animation:pop .5s .3s ease-out both;line-height:1.6}
.hubtip.miss{background:#FFF1E6;border:3px solid #FF7A45;color:#7A2E0E}
.hubtip.hit{background:#E6F4EC;border:3px solid #0F766E;color:#174D40}
.hubtip big{display:block;font-size:1.2rem;font-weight:900;margin-bottom:4px}
.step .num{display:inline-block;background:#0F766E;color:#fff;border-radius:999px;width:28px;height:28px;line-height:28px;font-weight:900;font-size:.9rem;text-align:center}
.step .ic{font-size:38px;margin:4px 0}
.step b{display:block;font-size:1.05rem;margin-bottom:4px}
.step p{margin:0;font-size:.92rem;color:#33524A;line-height:1.5}
.goal{background:#FFF1C2;border-radius:14px;padding:10px 14px;font-weight:800;text-align:center;word-break:keep-all}
.todo{background:#20483F;color:#fff;border-radius:16px;padding:12px 16px;font-weight:900;font-size:1.08rem;text-align:center;margin:10px 0;word-break:keep-all;animation:pop .35s ease-out both}
.todo small{display:block;font-weight:600;opacity:.85;font-size:.85rem;margin-top:2px}
.legend2{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px;margin:10px 0}
.legend2 div{background:#fff;border:1.5px solid #D7E2DD;border-radius:14px;padding:10px 12px;font-size:.88rem;color:#33524A;line-height:1.5;word-break:keep-all}
.legend2 em{font-style:normal;font-size:22px;margin-right:4px}
.legend2 b{display:inline;color:#20483F;font-size:.98rem}
.legend2 b::after{content:'';display:block}
.em{color:#B4471B;font-weight:900}
.example h3{margin:0 0 4px}.exlead{margin:0 0 8px;word-break:keep-all}
.exgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.ex{border-radius:16px;padding:10px;text-align:center;border:2px solid #D7E2DD;animation:pop .45s ease-out both}
.ex:nth-child(2){animation-delay:.15s}.ex:nth-child(3){animation-delay:.3s}
.ex.bad{background:#FFF4F3;border-color:#F3B4B0}.ex.mid{background:#FFFBEA;border-color:#F1D98A}.ex.good{background:#EEF8F2;border-color:#8FD0AE}
.ex svg{display:block;width:100%}
.ex p{margin:4px 0 0;font-size:.88rem;word-break:keep-all;line-height:1.5}
.extag{display:inline-block;background:#20483F;color:#fff;border-radius:999px;padding:2px 10px;font-size:.8rem;font-weight:800}
.exquiz{background:#EEF2FF;border:2px solid #A5B4FC;border-radius:14px;padding:10px 14px;margin-top:10px;word-break:keep-all}
.exopt{background:#fff;border-radius:10px;padding:7px 10px;margin-top:6px;font-weight:700}
.exopt span{display:block;font-weight:600;font-size:.82rem}
.exopt.yes{border:2px solid #0F766E}.exopt.yes span{color:#0F766E}
.exopt.no{border:2px solid #E5484D}.exopt.no span{color:#C62828}
.howto{background:#EEF2FF;border:2px solid #A5B4FC;border-radius:16px;padding:12px 16px;margin:10px 0;word-break:keep-all}
.howto>b{color:#3730A3;font-size:1.05rem}
.howto ol{margin:6px 0 0;padding-left:22px}.howto li{margin:3px 0}
.keys{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:6px 0}
.keys div{background:#F4F8F6;border:1px solid #D7E2DD;border-radius:12px;padding:7px 4px;text-align:center;font-size:.82rem;font-weight:700;word-break:keep-all;line-height:1.35}
.keys div em{display:block;font-style:normal;font-size:20px}
.node.S:hover circle.body{stroke:#0F766E;stroke-width:5}
.node.I:not(.src):hover circle.body{stroke:#5B6FD6;stroke-width:5}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.85rem;color:#52616B;margin:4px 2px}
.panel{background:#fff;border:1.5px solid #D7E2DD;border-radius:18px;padding:16px;margin:10px 0;animation:pop .45s ease-out both}
.panel h3{margin:0 0 6px}
.result{text-align:center;border-radius:22px;padding:20px;margin:10px 0;animation:pop .55s ease-out both;position:relative;overflow:hidden}
.result.good{background:linear-gradient(135deg,#FFF1C2,#FFD6A5)}.result.bad{background:linear-gradient(135deg,#EEF2EF,#D3DED8);animation:shake .6s}
.result .stars{font-size:46px;letter-spacing:6px}
.result .stars i{display:inline-block;font-style:normal;animation:starpop .45s ease-out both}
.result b{display:block;font-size:1.5rem;font-weight:900;word-break:keep-all}
.meter{height:16px;background:#E8EFE6;border-radius:999px;overflow:hidden;margin:10px auto;max-width:420px}
.meter div{height:100%;background:linear-gradient(90deg,#0F766E,#7FD1B9);width:0;transition:width 1s ease-out}
.bars{display:flex;align-items:flex-end;gap:6px;height:90px;padding:6px 0;border-bottom:2px solid #D7E2DD}
.bars div{flex:1;background:#E5484D;border-radius:6px 6px 0 0;position:relative;min-height:4px;animation:grow .6s ease-out both}
.bars div span{position:absolute;top:-20px;left:0;right:0;text-align:center;font-size:.78rem;font-weight:800;color:#20483F}
.barlab{display:flex;gap:6px;font-size:.72rem;color:#52616B}.barlab span{flex:1;text-align:center}
.hubs li{margin:4px 0}
.dialog{background:#FFFEFA;border:3px solid #5B6FD6;border-radius:22px;padding:16px;margin:10px 0;animation:pop .3s ease-out both;box-shadow:0 8px 22px #5B6FD630}
.dialog[hidden]{display:none!important}
.dialog h3{margin:4px 0 10px;word-break:keep-all}
.dialog .opt{display:block;width:100%;text-align:left;margin:8px 0;background:#fff;border:2px solid #D7E2DD;word-break:keep-all}
.dialog .opt:hover:not(:disabled){border-color:#0F766E;background:#F0F7F3}
.final{background:linear-gradient(135deg,#1F5F55,#2E8B78);color:#fff;border-radius:22px;padding:22px;text-align:center;animation:pop .6s ease-out both}
.final .big{font-size:60px;animation:bob 1.6s ease-in-out infinite}
.map{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0}
.map div{background:#EDF4F1;border-radius:14px;padding:8px 4px;text-align:center;font-weight:800;font-size:.85rem}
.map div.done{background:#FFF1C2}.map div.now{outline:3px solid #FF7A45}
.map div em{display:block;font-style:normal;font-size:22px}
@keyframes pop{0%{transform:scale(.6);opacity:0}65%{transform:scale(1.04);opacity:1}100%{transform:scale(1)}}
@keyframes pulse{0%{transform:scale(1)}40%{transform:scale(1.25)}100%{transform:scale(1)}}
@keyframes ring{0%{r:24;opacity:1}100%{r:50;opacity:0}}
@keyframes float{0%{transform:translateY(0);opacity:1}100%{transform:translateY(-36px);opacity:0}}
@keyframes flash{0%{stroke:#FFB347;stroke-width:8}100%{stroke:#E5484D;stroke-width:4}}
@keyframes starpop{0%{transform:scale(0) rotate(-40deg)}70%{transform:scale(1.3)}100%{transform:scale(1)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%,75%{transform:translateX(-8px)}50%{transform:translateX(8px)}}
@keyframes grow{from{transform:scaleY(0);transform-origin:bottom}to{transform:scaleY(1);transform-origin:bottom}}
@keyframes bob{50%{transform:translateY(-8px)}}
.node{transform-box:fill-box;transform-origin:center}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:560px){.exgrid{gap:5px}.ex{padding:6px 4px}.ex p{font-size:.7rem;line-height:1.4}.extag{font-size:.64rem;padding:2px 6px}.steps{grid-template-columns:1fr;gap:8px}.step{display:flex;align-items:center;gap:10px;text-align:left;padding:10px 12px}.step .ic{font-size:30px;margin:0}.step .num{flex-shrink:0}.step b{font-size:1rem}.keys{grid-template-columns:repeat(2,1fr)}.hero b{font-size:1.2rem}.map{grid-template-columns:repeat(5,1fr)}.map div{font-size:.7rem}.post .txt{font-size:.98rem}}
</style></head><body><main class="wrap" id="app"></main>
<script>
const DATA = __DATA__;
const ST = DATA.stages;
const PEOPLE = ['🧑‍🎓','👵','👨‍🍳','👩‍💼','🧒','👴','👩‍🏫','🧑‍🔧','👨‍💻','👩‍🌾','🧑‍🎨','👮','👩‍⚕️','🧑‍🍳','👦','👧','🧓','👨‍🔬','👩‍🎤','🧑‍✈️','👨‍🏫','👩‍🔧','🧑‍💼','👱','🧕','👲'];
const W = 640, H = 420, R = 25;
const G = {stage: 0, stars: [0,0,0,0,0], best: [0,0,0,0,0]};
let S = null, timer = null;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// ───── 시드 고정 난수: 같은 단계는 언제나 같은 마을 지도 ─────
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

function makeGraph(idx){
  const st = ST[idx], n = st.n, rnd = rng(9001 + idx * 37);
  const pts = [];
  let minD = 84, tries = 0;
  while (pts.length < n) {
    const p = {x: 40 + rnd() * (W - 80), y: 40 + rnd() * (H - 80)};
    if (pts.every(q => (q.x - p.x) ** 2 + (q.y - p.y) ** 2 >= minD * minD)) pts.push(p);
    if (++tries > 4000) { minD -= 4; tries = 0; }
  }
  const adj = pts.map(() => new Set());
  const d2 = (a, b) => (pts[a].x - pts[b].x) ** 2 + (pts[a].y - pts[b].y) ** 2;
  const link = (a, b) => { if (a !== b) { adj[a].add(b); adj[b].add(a); } };
  // 1) 가까운 이웃 2명과 연결
  for (let i = 0; i < n; i++) {
    const near = [...Array(n).keys()].filter(j => j !== i).sort((a, b) => d2(i, a) - d2(i, b));
    link(i, near[0]); link(i, near[1]);
  }
  // 2) 허브(연결이 많은 사람) 3명: 마을 곳곳의 중심에서 멀리까지 연결
  const anchors = [[.32, .45], [.55, .3], [.68, .68]];
  const hubs = [];
  anchors.forEach(([ax, ay]) => {
    const h = [...Array(n).keys()].filter(i => !hubs.includes(i))
      .sort((a, b) => ((pts[a].x - ax * W) ** 2 + (pts[a].y - ay * H) ** 2) - ((pts[b].x - ax * W) ** 2 + (pts[b].y - ay * H) ** 2))[0];
    hubs.push(h);
    [...Array(n).keys()].filter(j => j !== h && !adj[h].has(j) && d2(h, j) < 250 * 250)
      .sort((a, b) => d2(h, a) - d2(h, b)).slice(0, 4).forEach(j => link(h, j));
  });
  // 3) 떨어진 무리가 없도록 가장 가까운 두 사람을 이어 줌
  const comp = () => { const c = Array(n).fill(-1); let k = 0; for (let i = 0; i < n; i++) { if (c[i] >= 0) continue; const q = [i]; c[i] = k; while (q.length) { const v = q.shift(); adj[v].forEach(u => { if (c[u] < 0) { c[u] = k; q.push(u); } }); } k++; } return [c, k]; };
  for (let [c, k] = comp(); k > 1; [c, k] = comp()) {
    let best = null;
    for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) if (c[a] === 0 && c[b] !== 0 && (!best || d2(a, b) < d2(best[0], best[1]))) best = [a, b];
    link(best[0], best[1]);
  }
  // 4) 처음 올린 계정: 왼쪽 끝(2개면 오른쪽 끝도). 허브는 제외
  const order = [...Array(n).keys()].filter(i => !hubs.includes(i)).sort((a, b) => pts[a].x - pts[b].x);
  const sources = st.sources === 2 ? [order[0], order[order.length - 1]] : [order[0]];
  sources.forEach(s => { if (adj[s].size < 3) { [...Array(n).keys()].filter(j => j !== s && !adj[s].has(j)).sort((a, b) => d2(s, a) - d2(s, b)).slice(0, 3 - adj[s].size).forEach(j => link(s, j)); } });
  const edges = [];
  adj.forEach((set, a) => set.forEach(b => { if (a < b) edges.push([a, b]); }));
  return {pts, adj: adj.map(s => [...s]), edges, sources, emoji: pts.map((_, i) => PEOPLE[(i * 7 + idx * 3) % PEOPLE.length])};
}

// ───── 화면 ─────
function stageMap(){
  return '<div class="map">' + ST.map((s, i) => `<div class="${G.stars[i] ? 'done' : ''} ${i === G.stage ? 'now' : ''}"><em>${s.icon}</em>${esc(s.tactic)}<br>${'⭐'.repeat(G.stars[i]) + '☆'.repeat(3 - G.stars[i])}</div>`).join('') + '</div>';
}

// ───── 시작 화면 예시: 6명짜리 작은 마을 ─────
const EX = {
  pts: [[28, 80], [92, 40], [92, 120], [160, 80], [160, 140], [160, 26]],
  names: ['📢', 'A', 'B', 'C', 'D', 'E'],
  edges: [[0, 1], [0, 2], [1, 5], [2, 3], [2, 4], [2, 5]],
};
function miniGraph(states){
  const col = {S: ['#fff', '#9DB5AA'], I: ['#FFE1DE', '#E5484D'], R: ['#D7F2E3', '#0F766E'], X: ['#3B2A2A', '#E5484D']};
  let h = `<svg viewBox="0 0 196 162" aria-hidden="true" style="max-width:240px;margin:auto">`;
  EX.edges.forEach(([a, b]) => {
    const hot = states[a] !== 'R' && states[b] !== 'R' && (states[a] === 'I' || states[a] === 'X') && states[b] === 'I';
    const hot2 = states[b] !== 'R' && (states[b] === 'I' || states[b] === 'X') && states[a] === 'I';
    h += `<line x1="${EX.pts[a][0]}" y1="${EX.pts[a][1]}" x2="${EX.pts[b][0]}" y2="${EX.pts[b][1]}" stroke="${hot || hot2 ? '#E5484D' : '#B7CBC2'}" stroke-width="${hot || hot2 ? 3.5 : 2.5}"/>`;
  });
  EX.pts.forEach(([x, y], i) => {
    const [f, st] = col[states[i]];
    h += `<circle cx="${x}" cy="${y}" r="14" fill="${f}" stroke="${st}" stroke-width="3"/>`;
    h += `<text x="${x}" y="${y + 1}" text-anchor="middle" dominant-baseline="central" font-size="${i ? 13 : 15}" font-weight="900" fill="${states[i] === 'X' ? '#fff' : '#20483F'}">${EX.names[i]}</text>`;
    if (states[i] === 'R') h += `<text x="${x + 12}" y="${y - 12}" font-size="12">🛡️</text>`;
  });
  return h + '</svg>';
}
function exampleHtml(){
  return `<section class="panel example"><h3>👀 먼저 예시로 볼까요? (주민 5명짜리 작은 마을)</h3>
  <p class="exlead">📢가 가짜 소식을 올렸어요. <b>B</b>는 친구가 4명으로 연결선이 가장 많은 사람이에요.</p>
  <div class="exgrid">
    <div class="ex bad"><div class="extag">그냥 두면</div>${miniGraph(['X', 'I', 'I', 'I', 'I', 'I'])}
      <p>📢 → A, B → C, D, E 순서로 번져서<br><b>5명 모두 속아요.</b></p></div>
    <div class="ex mid"><div class="extag">① B 미리 지키기</div>${miniGraph(['X', 'I', 'R', 'S', 'S', 'I'])}
      <p>연결선이 많은 B를 🛡️ 미리 지키면<br>C, D까지 안전! <b>3명 지킴</b></p></div>
    <div class="ex good"><div class="extag">② E도 카드로</div>${miniGraph(['X', 'I', 'R', 'S', 'S', 'R'])}
      <p>A가 속은 뒤, A의 친구 E를 카드로 막으면<br><b>4명 지킴 ⭐⭐⭐</b></p></div>
  </div>
  <div class="exquiz"><b>💬 속은 사람(🔴)을 누르면? 정정 문구를 골라요</b>
    <div class="exopt yes">✅ “시장 공지 원문 보니 10곳 중 2곳만 옮긴대” <span>근거 있음 → 퍼뜨리기 멈춤</span></div>
    <div class="exopt no">❌ “너무 화난다! 다 같이 항의하자” <span>근거 없음 → 카드만 1장 줄어요</span></div>
  </div></section>`;
}

function intro(){
  setPlayActive(false);
  $('app').innerHTML = `
  <section class="hero"><span>🌐 전략 게임 · 수법 5단계</span><b>도토리시에 가짜 소식이 퍼지고 있다!</b>
  <span>퍼지기 전에 막을수록, 연결이 많은 사람을 지킬수록 마을이 지켜져요.</span></section>
  ${stageMap()}
  ${exampleHtml()}
  <div class="steps">
    <div class="step"><span class="num">1</span><div class="ic">🛡️</div><div class="txt"><b>퍼지기 전, 1명 지키기</b><p>시작 전에 흰 동그라미 <b style="display:inline">1명</b>을 눌러 미리 알려 줘요.</p></div></div>
    <div class="step" style="animation-delay:.1s"><span class="num">2</span><div class="ic">📶</div><div class="txt"><b>시작하면 한 칸씩 퍼짐</b><p>📢에서 시작해 <b style="display:inline">연결선을 따라</b> 빨간색이 번져요.</p></div></div>
    <div class="step key" style="animation-delay:.2s"><span class="badge3">핵심!</span><span class="num">3</span><div class="ic">🃏</div><div class="txt"><b>남은 카드로 막기</b><p>카드는 단계마다 4~5장. <b style="display:inline">1장으로 1명</b>에게 써요.<br>⚪ 아직 모르는 사람을 누르면 🛡️ 지킴<br>🔴 속은 사람을 누르면 💬 근거 있는 정정 문구 고르기</p></div></div>
  </div>
  <div class="goal">🎯 목표: 안 속은 사람 75% 이상 ⭐⭐⭐ · 55% 이상 ⭐⭐</div>
  <div class="legend2">
    <div><em>⚪</em><b>아직 모르는 사람</b>소식을 아직 못 들었어요. <strong class="em">누르면 🛡️ 지킬 수 있어요.</strong></div>
    <div><em>🔴</em><b>속은 사람</b>가짜 소식을 믿고 친구들에게 퍼뜨려요. <strong class="em">누르면 💬 정정 문구를 보낼 수 있어요.</strong></div>
    <div><em>🛡️</em><b>지킨 사람</b>미리 알려 줘서 끝까지 속지 않고, 소문도 여기서 멈춰요.</div>
    <div><em>💬</em><b>정정한 사람</b>알맞은 정정 문구를 받고 더 이상 퍼뜨리지 않아요.</div>
    <div><em>📢</em><b>처음 올린 계정</b>가짜 소식을 만든 계정이에요. 눌러도 막을 수 없어요.</div>
  </div>
  <div class="howto"><b>💬 정정 문구는 이렇게 골라요</b>
    <ol><li><b>근거</b>가 있다: 원문, 공식 공지, 사진 원본 같은 확인한 자료</li>
    <li><b>확인 방법</b>을 알려 준다: “누리집에서 직접 확인해 봐”</li>
    <li><b>비난·느낌·추측</b>이 아니다: “사기꾼이네”, “합성 같아”, “일단 가 보자”는 ❌</li></ol></div>
  <button class="go" style="width:100%" onclick="startStage(${G.stage})">🚀 ${G.stage + 1}단계 시작 · ${esc(ST[G.stage].icon + ' ' + ST[G.stage].tactic)}</button>`;
}

// 단계 화면에서 바로 전 화면(단계 설명)으로 돌아가요. 퍼지던 시뮬레이션은 멈춰요.
function backIntro(){ clearInterval(timer); clearTimeout(timer); timer = null; closeQuiz(); intro(); toTop(); }
function startStage(idx){
  clearInterval(timer); clearTimeout(timer); timer = null;
  G.stage = idx;
  const g = makeGraph(idx);
  S = {g, st: ST[idx], state: g.pts.map(() => 'S'), cards: ST[idx].cards, phase: 'prep', pre: 1, tickNo: 0, levels: [], quizFor: null, used: [], read: false};
  g.sources.forEach(s => S.state[s] = 'I');
  render();
  toTop();
}

function counts(){
  const c = {S: 0, I: 0, R: 0, C: 0};
  S.state.forEach(x => c[x]++);
  return c;
}

function render(){
  setPlayActive(true);
  const st = S.st, c = counts(), n = st.n;
  const phaseText = S.phase === 'prep' ? `🛡️ 사전 알림 ${S.pre}장 남음 · 퍼지기 전에 1명을 골라요` : S.phase === 'run' ? `📶 퍼지는 중… ${S.tickNo}단계` : '';
  $('app').innerHTML = `
  <button style="background:#fff;border:2px solid #20483F;color:#20483F;margin:0 0 8px" onclick="backIntro()">← 이전 화면으로</button>
  <section class="hero"><span>${G.stage + 1}단계 · 수법 ${esc(st.icon + ' ' + st.tactic)}</span><b>${S.phase === 'prep' ? '이 소식이 곧 퍼지려고 해요! 먼저 1명을 지켜요' : '소식이 마을에 퍼지고 있어요!'}</b></section>
  <div class="post"><div class="ava">📢</div><div><div class="acc">${esc(st.account)}</div><div class="txt">${esc(st.post)}</div></div></div>
  <div class="hud"><span class="cards">🃏 남은 카드 ${S.cards}장 (1장 = 1명 지키기·정정)</span><span>🔴 속은 사람 ${c.I}명</span><span>🛡️ 지킨 사람 ${c.R}명</span><span>💬 정정한 사람 ${c.C}명</span><span>⚪ 아직 모르는 사람 ${c.S}명</span>${S.phase === 'run' ? `<span>📶 ${S.tickNo}단계</span>` : ''}</div>
  <div class="todo" id="now"></div>
  ${S.phase === 'prep' ? `<button class="go" style="width:100%;margin-bottom:8px" onclick="run()" ${S.pre ? 'disabled' : ''}>${S.pre ? '🔒 지킬 사람 1명을 먼저 골라야 시작할 수 있어요' : '▶ 소문 퍼지기 시작'}</button>` : ''}
  <div class="board${S.read ? '' : ' locked'}"><svg id="svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="도토리시 주민 연결망"></svg>${S.read ? '' : `
    <div class="readme"><div class="rm-tag">📢 방금 올라온 소식</div>
      <div class="rm-post"><div class="acc">${esc(st.account)}</div><div class="txt">${esc(st.post)}</div></div>
      <div class="rm-tip">이 소식이 마을에 퍼지려고 해요. 어디가 수상한지 생각해 보고 막으러 가요!</div>
      <button class="go" onclick="S.read=true;render()">읽었어요, 막으러 가기 ▶</button></div>`}</div>
  <div class="keys"><div><em>⚪ 👆</em>아직 모르는 사람 → 🛡️ 지킴</div><div><em>🔴 👆</em>속은 사람 → 💬 근거 있는 정정</div><div><em>📢</em>눌러도 소용없음</div><div><em>🃏 ${S.cards}</em>남은 카드 · 1장으로 1명</div></div>
  <div class="dialog" id="dlg" hidden></div>
  <div class="toast" id="toast" aria-live="polite"></div>
  <div class="row" id="ctrl"></div>`;
  drawSvg();
  nowText();
  const ctrl = $('ctrl');
  if (S.phase === 'prep') {
    ctrl.innerHTML = '';
    toast(S.pre ? '퍼지기 전! 연결선이 많은 사람 1명을 눌러 🛡️ 지켜 주세요.' : '준비 완료! 지도 위 ‘소문 퍼지기 시작’을 눌러요.');
  } else if (S.phase === 'run') {
    ctrl.innerHTML = `<button onclick="startStage(${G.stage})">↺ 이 단계 다시</button>`;
  }
}

function drawSvg(){
  const svg = $('svg'), g = S.g;
  let h = '';
  g.edges.forEach(([a, b], i) => { h += `<line class="edge" id="e${a}_${b}" x1="${g.pts[a].x}" y1="${g.pts[a].y}" x2="${g.pts[b].x}" y2="${g.pts[b].y}"/>`; });
  g.pts.forEach((p, i) => {
    const s = S.state[i], src = g.sources.includes(i);
    const label = src ? '📢' : g.emoji[i];
    const badge = s === 'R' ? '🛡️' : s === 'C' ? '💬' : (s === 'I' && !src) ? '❗' : '';
    const name = src ? '처음 올린 계정' : `주민 ${i + 1}`;
    const what = s === 'S' ? '아직 모르는 사람' : s === 'I' ? '속은 사람' : s === 'R' ? '지킨 사람' : '정정한 사람';
    h += `<g class="node ${s} ${src ? 'src' : ''}" id="n${i}" tabindex="0" role="button" aria-label="${name}, 친구 ${g.adj[i].length}명, ${what}" onclick="tap(${i})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();tap(${i})}">
      <circle class="body" cx="${p.x}" cy="${p.y}" r="${R}"/>
      <text x="${p.x}" y="${p.y + 1}" font-size="25">${label}</text>
      ${badge ? `<text class="badge" x="${p.x + 19}" y="${p.y - 19}">${badge}</text>` : ''}
    </g>`;
  });
  svg.innerHTML = h + '<g id="fx"></g>';
}

function fx(i, kind, text){
  const p = S.g.pts[i], fxg = $('fx');
  if (!fxg) return;
  fxg.insertAdjacentHTML('beforeend', `<circle class="ring ${kind}" cx="${p.x}" cy="${p.y}" r="20"/>` + (text ? `<text class="float" x="${p.x}" y="${p.y - 26}" fill="${kind === 'g' ? '#0F766E' : kind === 'b' ? '#3B4DB0' : '#C62828'}">${text}</text>` : ''));
  setTimeout(() => { if (fxg.firstChild) fxg.removeChild(fxg.firstChild); if (text && fxg.firstChild) fxg.removeChild(fxg.firstChild); }, 1000);
}

function toTop(){ try { if (window.frameElement) window.frameElement.scrollIntoView({behavior: 'smooth', block: 'start'}); } catch (e) {} }

function toast(t){ const el = $('toast'); if (el) el.textContent = t; }

function tap(i){
  if (!S || S.phase === 'result') return;
  const s = S.state[i];
  if (S.g.sources.includes(i)) { toast('📢 처음 올린 계정은 정정해도 계속 올려요. 퍼지는 길목을 막아요!'); return; }
  if (S.phase === 'prep') {
    if (s !== 'S') return;
    if (!S.pre) { toast('사전 알림은 1명만! 이제 시작을 눌러요.'); return; }
    S.pre--; S.cards--; S.state[i] = 'R'; S.used.push(i);
    render(); fx(i, 'g', '🛡️'); return;
  }
  if (S.cards <= 0) { toast('카드를 모두 썼어요. 끝까지 지켜봐요!'); return; }
  if (s === 'S') { S.state[i] = 'R'; S.cards--; S.used.push(i); refresh(); fx(i, 'g', '🛡️'); return; }
  if (s === 'I') { openQuiz(i); return; }
}

function nowText(){
  const el = $('now'); if (!el) return;
  const goal = Math.ceil(S.st.n * 0.75);
  let t;
  if (S.phase === 'prep') t = S.pre ? '① 지금 할 일: 🛡️ 지킬 사람 1명을 골라 눌러요 (연결선이 많은 사람 추천)' : '② 지금 할 일: 바로 아래 ‘소문 퍼지기 시작’을 눌러요';
  else if (S.cards > 0) t = `👆 지금 할 일: ⚪ 아직 모르는 사람은 눌러서 지키고, 🔴 속은 사람은 눌러서 정정해요 (카드 ${S.cards}장)`;
  else t = '👀 카드를 다 썼어요. 소문이 멈출 때까지 지켜봐요';
  el.innerHTML = `${t}<small>⭐⭐⭐ 목표: 주민 ${S.st.n}명 중 ${goal}명 이상 안 속게 하기</small>`;
  document.querySelectorAll('.keys div em').forEach(e => { if (e.textContent.startsWith('🃏')) e.textContent = '🃏 ' + S.cards; });
}

function refresh(){
  // 진행 중에는 지도만 다시 그려 깜빡임을 줄입니다.
  const c = counts();
  const hud = document.querySelector('.hud');
  if (hud) hud.innerHTML = `<span class="cards">🃏 남은 카드 ${S.cards}장 (1장 = 1명 지키기·정정)</span><span>🔴 속은 사람 ${c.I}명</span><span>🛡️ 지킨 사람 ${c.R}명</span><span>💬 정정한 사람 ${c.C}명</span><span>⚪ 아직 모르는 사람 ${c.S}명</span><span>📶 ${S.tickNo}단계</span>`;
  drawSvg();
  nowText();
}

function run(){
  if (S.pre) { toast('먼저 지킬 사람 1명을 골라 주세요.'); return; }
  S.phase = 'run'; render();
  tick();  // 시작하자마자 첫 단계가 번져요: 미리 알리기(사전 알림)가 중요한 이유
  if (S.phase === 'run') {
    toast('퍼지기 시작! 다음 퍼짐까지 잠깐 여유가 있어요. 빨간 사람 옆을 막아요!');
    // 첫 퍼짐 뒤에는 조금 더 기다려 줘서, 지도를 보고 고를 시간을 줍니다.
    timer = setTimeout(() => { if (S.phase === 'run') timer = setInterval(tick, S.st.tick); }, S.st.tick + 1500);
  }
}

// ───── 한 단계 퍼지기: 너비 우선 탐색(BFS)처럼 '이번에 믿은 사람'의 이웃에게 번짐 ─────
function tick(){
  if (S.quizFor !== null) return; // 정정 문구를 고르는 동안은 멈춤
  const g = S.g, next = [], hot = [];
  S.state.forEach((s, i) => {
    if (s !== 'I') return;
    g.adj[i].forEach(j => { if (S.state[j] === 'S' && !next.includes(j)) { next.push(j); hot.push([i, j]); } });
  });
  if (!next.length) { finish(); return; }
  S.tickNo++;
  next.forEach(j => S.state[j] = 'I');
  S.levels.push(next.length);
  refresh();
  hot.forEach(([a, b]) => { const e = $(`e${Math.min(a, b)}_${Math.max(a, b)}`); if (e) e.classList.add('hot'); });
  next.forEach(j => { const nd = $('n' + j); if (nd) nd.classList.add('pulse'); fx(j, '', ''); });
  toast(`📶 ${S.tickNo}단계: ${next.length}명이 새로 믿었어요!`);
}

function openQuiz(i){
  S.quizFor = i;
  const opts = S.st.options.map((o, k) => ({o, k})).sort((a, b) => ((a.k * 7 + i) % 3) - ((b.k * 7 + i) % 3));
  $('dlg').innerHTML = `<div style="font-size:30px">${S.g.emoji[i]}💬</div><h3>주민 ${i + 1}에게 어떤 정정 문구를 보낼까요?</h3>
  <p class="tip">👇 아래 3개 중 <b>1개</b>를 눌러요. 근거가 있는 문구면 이 주민이 퍼뜨리기를 멈추고(💬), 아니면 카드만 1장 줄어요.<br><span style="font-weight:600">수법: ${esc(S.st.icon + ' ' + S.st.tactic)} · 남은 카드 ${S.cards}장</span></p>
  <p class="howto" style="margin:8px 0;font-weight:700">✅ <b>근거(원문·공식 기록)</b>와 <b>확인 방법</b>이 있는 문구를 골라요.<br>❌ 비난, 느낌, 추측, 일단 따라 하기는 효과가 없어요.</p>
  ${opts.map(({o, k}) => `<button class="opt" onclick="answer(${k})">${esc(o[0])}</button>`).join('')}
  <button onclick="closeQuiz()" style="width:100%;margin-top:6px">취소</button>`;
  $('dlg').hidden = false;
  toast('⏸ 정정 문구를 고르는 동안 잠깐 멈췄어요.');
  const first = document.querySelector('.dialog .opt'); if (first) first.focus({preventScroll: true});
  $('dlg').scrollIntoView({block: 'nearest'});
}

function closeQuiz(){ S.quizFor = null; const d = $('dlg'); if (d) { d.hidden = true; d.innerHTML = ''; } }

function answer(k){
  const i = S.quizFor, o = S.st.options[k];
  S.cards--; closeQuiz();
  if (o[1]) { S.state[i] = 'C'; S.used.push(i); refresh(); fx(i, 'b', '💬'); toast('✅ ' + o[2]); }
  else { refresh(); fx(i, '', '✖'); toast('❌ ' + o[2]); }
}

function finish(){
  clearInterval(timer); clearTimeout(timer); timer = null;
  S.phase = 'result';
  const n = S.st.n, c = counts();
  const saved = n - c.I;  // 처음 올린 계정도 '속은 사람'에 포함
  const pct = Math.round(saved * 100 / n);
  const stars = pct >= 75 ? 3 : pct >= 55 ? 2 : 1;
  G.stars[G.stage] = Math.max(G.stars[G.stage], stars);
  G.best[G.stage] = Math.max(G.best[G.stage], pct);
  const deg = S.g.adj.map((a, i) => ({i, d: a.length})).filter(x => !S.g.sources.includes(x.i)).sort((a, b) => b.d - a.d).slice(0, 3);
  const good = stars >= 2;
  const last = G.stage === ST.length - 1;
  sendResult({game: 'fakenews', type: 'stage', stage: G.stage, stars, pct});
  const plays = STATS[`s${G.stage}_plays`] || 0;
  const others = plays ? `<section class="panel"><h3>🌍 다른 친구들은?</h3><p>이 단계는 지금까지 <b>${plays}판</b> 진행됐고, 평균 <b>${Math.round((STATS[`s${G.stage}_pctsum`] || 0) / plays)}%</b>의 주민을 지켰어요. 별 3개는 <b>${Math.round((STATS[`s${G.stage}_star3`] || 0) * 100 / plays)}%</b>예요.</p></section>`
    : '<section class="panel"><h3>🌍 다른 친구들은?</h3><p>아직 이 단계에 모인 기록이 없어요. 첫 기록의 주인공이에요!</p></section>';
  $('app').innerHTML = `
  <section class="result ${good ? 'good' : 'bad'}">
    <div class="stars">${[0,1,2].map(k => `<i style="animation-delay:${.2 + k * .2}s">${k < stars ? '⭐' : '☆'}</i>`).join('')}</div>
    <b>${good ? '마을을 지켰어요!' : '소문이 많이 퍼졌어요…'}</b>
    <span>주민 ${n}명 중 <b style="display:inline;font-size:1.2rem">${saved}명</b>이 속지 않았어요 (${pct}%)</span>
    <div class="meter"><div id="mtr"></div></div>
  </section>
  ${hubTip(deg)}
  ${others}
  <section class="panel"><h3>📢 수법 공개 · ${esc(S.st.icon + ' ' + S.st.tactic)}</h3><p>${esc(S.st.reveal)}</p><p class="tip">🔎 진실: ${esc(S.st.truth)}</p></section>
  <section class="panel"><h3>🧠 연결이 가장 많은 사람 TOP 3</h3>
    <ul class="hubs">${deg.map(x => `<li>${S.g.emoji[x.i]} 주민 ${x.i + 1} · 친구 ${x.d}명 → ${S.state[x.i] === 'I' ? '🔴 믿어 버림' : S.state[x.i] === 'R' ? '🛡️ 지킴' : S.state[x.i] === 'C' ? '💬 정정됨' : '⚪ 소식이 닿지 않음'}</li>`).join('')}</ul>
    <p style="font-size:.9rem;color:#52616B">친구가 많은 사람은 한 번에 여러 명에게 퍼뜨려요. 이런 사람을 먼저 지키면 효과가 커요.</p></section>
  <section class="panel"><h3>📶 단계별로 새로 믿은 사람</h3>
    ${S.levels.length ? `<div class="bars">${S.levels.map((v, k) => `<div style="height:${Math.max(6, v * 100 / Math.max(...S.levels))}%;animation-delay:${k * .08}s"><span>${v}</span></div>`).join('')}</div>
    <div class="barlab">${S.levels.map((_, k) => `<span>${k + 1}</span>`).join('')}</div>` : '<p>처음 단계에서 모두 막았어요!</p>'}
    <p style="font-size:.9rem;color:#52616B">한 단계마다 ‘방금 믿은 사람’의 친구에게 번져요. 컴퓨터가 그래프를 넓게 탐색하는 방식(너비 우선 탐색, BFS)과 같아요.</p></section>
  ${stageMap()}
  <div class="row"><button onclick="startStage(${G.stage})">🔄 다른 방법으로 다시 도전</button>
  <button class="go" onclick="${last ? 'final()' : `startStage(${G.stage + 1})`}">${last ? '🏆 최종 결과' : '다음 단계 ▶'}</button></div>`;
  requestAnimationFrame(() => setTimeout(() => { const m = $('mtr'); if (m) m.style.width = pct + '%'; }, 120));
  toTop();
}

function hubTip(deg){
  const lost = deg.filter(x => S.state[x.i] === 'I');
  const names = list => list.map(x => `${S.g.emoji[x.i]} 주민 ${x.i + 1}(친구 ${x.d}명)`).join(', ');
  if (lost.length) {
    return `<section class="hubtip miss"><big>💡 연결선이 많은 사람을 먼저 골랐다면 더 유리했을 거예요!</big>
    ${names(lost)}이(가) 소문을 믿어 버렸어요. 친구가 많은 사람이 믿으면 한 번에 여러 명에게 퍼져요.
    다음엔 <strong class="em">연결선이 가장 많이 뻗은 사람</strong>에게 사전 알림이나 카드를 먼저 써 보세요.</section>`;
  }
  return `<section class="hubtip hit"><big>👍 연결선이 많은 사람을 잘 지켰어요!</big>
  ${names(deg)} 모두 소문을 믿지 않았어요. 이런 사람을 지키면 그 너머 친구들까지 함께 지켜져요.</section>`;
}

function final(){
  const total = G.stars.reduce((a, b) => a + b, 0);
  const avg = Math.round(G.best.reduce((a, b) => a + b, 0) / ST.length);
  const title = total >= 13 ? '🛡️ 마을 수호자' : total >= 9 ? '🔍 팩트체크 요원' : '🌱 새내기 확인러';
  sendResult({game: 'fakenews', type: 'final', stars: total, avg});
  $('app').innerHTML = `
  <section class="final"><div class="big">🏆</div><b style="font-size:1.6rem;display:block">${title}</b>
  <span>별 ${total} / 15 · 평균 ${avg}%의 주민을 지켰어요</span></section>
  ${stageMap()}
  <section class="panel"><h3>🧠 오늘 배운 것</h3>
  <p>🛡️ <b>미리 알리기</b>: 퍼진 뒤 고치는 것보다 퍼지기 전에 알려 주는 게 훨씬 효과적이에요.</p>
  <p>🕸️ <b>연결이 많은 사람</b>: 친구가 많은 사람이 믿으면 한꺼번에 퍼져요. 나도 누군가에겐 연결이 많은 사람이에요.</p>
  <p>💬 <b>근거 있는 정정</b>: 비난이나 느낌이 아니라 원문·공식 기록을 보여 줘야 바로잡혀요.</p>
  <p>📢 <b>수법 5가지</b>: 사칭 · 감정 자극 · 가짜 증거 · 편 가르기 · 음모론. 피싱 문자에도 똑같이 쓰여요.</p></section>
  <button class="go" style="width:100%" onclick="G.stars=[0,0,0,0,0];G.best=[0,0,0,0,0];G.stage=0;intro()">🔄 처음부터 다시</button>`;
  toTop();
}

document.addEventListener('keydown', e => { if (e.key === 'Escape' && S && S.quizFor !== null) closeQuiz(); });

// ───── Streamlit 높이 맞추기 ─────
let lastHeight = 0;
function sendHost(type, payload = {}) { window.parent.postMessage({isStreamlitMessage: true, type, ...payload}, '*'); }
function resize(force = false){
  const root = document.querySelector('main.wrap'); if (!root) return;
  const height = Math.ceil(root.getBoundingClientRect().height) + 16;
  if (force || height !== lastHeight) { sendHost('streamlit:setFrameHeight', {height}); lastHeight = height; }
}
// 도토리시 통계: 파이썬이 보낸 다른 사람들의 기록(stats)을 받고, 게임 결과를 파이썬으로 보냅니다.
let STATS = {};
function sendResult(obj){ sendHost('streamlit:setComponentValue', {value: Object.assign({id: Date.now() + '-' + Math.random().toString(36).slice(2)}, obj), dataType: 'json'}); }
window.addEventListener('message', ev => { if (ev.source === window.parent && ev.data && ev.data.type === 'streamlit:render') { if (ev.data.args && ev.data.args.stats) STATS = ev.data.args.stats; requestAnimationFrame(() => resize(true)); } });
sendHost('streamlit:componentReady', {apiVersion: 1});
new ResizeObserver(() => requestAnimationFrame(resize)).observe(document.querySelector('main.wrap'));
window.addEventListener('load', resize); window.addEventListener('resize', resize);
intro();
</script></body></html>
'''

page = bridge(HTML, "06").replace("__DATA__", json.dumps({"stages": STAGES}, ensure_ascii=False).replace("<", "\\u003c"))
spread_component = create_river_component(page)
value = spread_component(key="jamkkan_spread_v1", default=None, stats=dd.stats("fakenews"))

# 결과를 익명 통계(+1)에 더하고, 시민증이 있으면 명예의 전당에 저장해요.
event = dd.take_event(value)
if event and event.get("type") == "stage" and event.get("stage") in (0, 1, 2, 3, 4):
    s, stars, pct = int(event["stage"]), int(event.get("stars", 1)), max(0, min(100, int(event.get("pct", 0))))
    dd.record("fakenews", {f"s{s}_plays": 1, f"s{s}_pctsum": pct, f"s{s}_star3": 1 if stars == 3 else 0})
    dd.stamp("06")
elif event and event.get("type") == "final":
    stars, avg = max(0, min(15, int(event.get("stars", 0)))), max(0, min(100, int(event.get("avg", 0))))
    dd.record("fakenews", {"finals": 1})
    dd.note_mine("fakenews", f"별 {stars}/15 · 평균 {avg}% 지킴")
    st.session_state["fakenews_hall"] = dd.save_hall(
        "fakenews", {"stars": stars, "avg": avg},
        lambda old, new: (new["stars"], new["avg"]) > (old.get("stars", 0), old.get("avg", 0)),
    )
dd.show_hall_note(st.session_state.get("fakenews_hall"))
if SCENE_SLOT is not None:
    if event and event.get("type") == "stage" and event.get("stage") in (0, 1, 2, 3, 4):
        best = st.session_state.setdefault("fakenews_scene_stars", {})
        best[int(event["stage"])] = max(best.get(int(event["stage"]), 0), int(event.get("stars", 1)))
        st.session_state["fakenews_scene_pct"] = max(0, min(100, int(event.get("pct", 0))))
    SCENE_SLOT.markdown(scene_ui.plaza(st.session_state.get("fakenews_scene_pct"), sum(st.session_state.get("fakenews_scene_stars", {}).values())),
                        unsafe_allow_html=True)

with st.expander("🧠 이 게임 속 알고리즘 (정보 과목 연계)"):
    st.markdown(
        "- **그래프**: 주민은 *점(정점)*, 친구 관계는 *선(간선)*이에요. 단계마다 정해진 시드로 같은 마을 지도를 만들어요.\n"
        "- **너비 우선 탐색(BFS)**: 한 단계마다 ‘방금 믿은 사람’의 이웃에게만 번져요. 결과 화면의 단계별 막대가 BFS의 단계(거리)예요.\n"
        "- **연결 수(차수 중심성)**: 친구가 많은 사람일수록 막았을 때 효과가 커요. 결과 화면에서 TOP 3를 보여 줘요.\n"
        "- **전략**: 카드가 적어서 ‘퍼지는 길목(연결을 끊는 사람)’을 찾아야 해요."
    )
st.caption("교육용 가상 이야기입니다. 진행은 새로고침·페이지 이동 시 초기화되며 저장하지 않습니다.")
