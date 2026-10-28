from play_ui import intro, bridge
"""피싱 필터 만들기: 조건 블록(그리고·또는)을 조립해 문자를 거르는 규칙을 만드는 코딩 퍼즐.

- 규칙 한 줄 = 조건 1~2개를 '그리고(AND)'로 묶음, 규칙 줄끼리는 '또는(OR)'
- 실행하면 문자가 하나씩 필터를 지나가며 오탐(진짜인데 막음)·미탐(가짜인데 통과)을 보여 줍니다.
- 목표 블록 수는 가능한 규칙 조합을 모두 검사(완전 탐색)해서 정했습니다.
  1단계 최소 2블록, 2단계 최소 4블록, 3단계는 어떤 규칙으로도 1개는 틀릴 수밖에 없고 최소 3블록.
모든 번호·이름·기관·링크는 교육용 가상 내용입니다.
"""
import json
from filter_trials import HOLDOUT

import streamlit as st
import dotori_data as dd
from mascot_ui import show_key_question, show_mascot
from filter_component_ui import create_filter_component

with intro("11", suffix=""):
    st.title("🤖 피싱 필터 만들기")
    show_key_question("**조건 블록**을 조립해 수상한 문자만 걸러 내는 **필터 규칙**을 만들어 보세요.", "🤖")
    show_mascot("postman", "진짜 문자는 통과시키고, 가짜 문자만 막아야 해요. 적은 블록으로 다 맞히면 별 3개!", width=100)

# 조건: L 링크 있음, U 모르는 번호, S 저장된 번호(모르는 번호가 아님), M 돈 요구, R 재촉, P 인증번호·개인정보 요구, A 앱 설치 요구
VERIFIED = [
 ["주문 내역의 배송 기록과 일치함", "공식 배송 조회에 해당 반송 요청이 없었고 고객센터가 문자를 부인함",
  "기존 학원 연락처로 보강 일정을 확인함", "별도로 연락한 배송사가 해당 결제 요청을 부인함",
  "기존 가족 연락처로 본인의 메시지임을 확인함", "학교 공식 공지에서 같은 안내를 확인함"],
 ["기존 가족 번호로 확인하니 상품권을 요청한 적이 없었음", "동아리 공지와 기존 총무 연락처로 회비를 확인함",
  "은행의 공식 고객센터가 해당 설치 요청을 부인함", "직접 연 은행 공식 앱의 이용 내역과 일치함",
  "별도로 찾은 기관 연락처로 확인하니 해당 요구를 부인함", "기존 연락처로 약속을 확인함",
  "학교 공식 공지와 일치함", "직접 연 병원 예약 내역과 일치함"],
 ["공식 배송 고객센터가 해당 주소 수정 요청을 부인함", "기존 아빠 번호로 확인하니 송금을 요청한 적이 없었음",
  "서연에게 다른 경로로 확인하니 계정을 도용당했다고 함", "민준과 대면해 실제 요청임을 확인함",
  "학교 공식 공지와 일치함", "병원 공식 예약 내역과 일치함",
  "직접 연락한 카드사가 해당 정보 입력 요청을 부인함", "기존 가족 연락처로 본인의 메시지임을 확인함",
  "별도로 찾은 기관 연락처로 확인하니 해당 요구를 부인함", "주문 내역의 배송 기록과 일치함"]
]
st.info("이 활동은 제한된 특징으로 필터를 만드는 코딩 실험이에요. 문자만으로 진위를 확정하지 않아요. "
        "문자별 ‘별도 확인 결과’가 교육용 정답의 근거이며, 필터는 그 정보를 사용하지 못해요. "
        "실제 상황에서는 저장된 번호나 링크 유무만으로 안전을 보장할 수 없어요.")
DATA = {
    "conds": {
        "L": "🔗 링크 있음",
        "U": "❓ 모르는 번호",
        "S": "📇 저장된 번호",
        "M": "💸 돈 요구",
        "R": "⏰ 재촉",
        "P": "🔑 인증번호·개인정보 요구",
        "A": "📲 앱 설치 요구",
    },
    "code": {"L": "링크있음", "U": "모르는번호", "S": "저장된번호", "M": "돈요구", "R": "재촉", "P": "개인정보요구", "A": "앱설치요구"},
    "stages": [
        {
            "name": "택배 문자",
            "goal": "가짜 문자를 모두 막고, 진짜 문자는 모두 통과시키기",
            "intro": "규칙 한 줄 안에 조건을 2개까지 넣을 수 있어요. ‘그리고’로 묶으면 두 조건이 모두 맞을 때, ‘또는’으로 묶으면 하나만 맞아도 걸려요.",
            "best": 0,
            "par": 4,
            "hints": [
                "진짜 문자 중에도 링크가 있는 게 있어요. ‘링크 있음’ 하나만으로는 진짜도 막혀요.",
                "링크가 있으면서 ‘어떤 번호’에서 왔는지 같이 보세요. 새 문자에도 맞는지 시험해 보세요.",
            ],
            "msgs": [
                ["도토리택배", "S", "[도토리택배] 주문하신 상품 배송 완료! 문 앞 사진 보기 ▶ (가상 링크)", "L", False],
                ["010-48○○-○○○○", "U", "[택배] 주소 불일치로 반송 예정. 오늘 안에 주소를 수정하세요 ▶ (가상 링크)", "LR", True],
                ["010-22○○-○○○○", "U", "안녕하세요, 도토리수학학원입니다. 이번 주 토요일 보강 안내드려요.", "", False],
                ["070-○○○○-○○○○", "U", "[국제택배] 통관 보관료 3,000원 미납. 결제 후 배송 ▶ (가상 링크)", "LM", True],
                ["엄마", "S", "오늘 저녁 뭐 먹고 싶어?", "", False],
                ["도토리고", "S", "[도토리고] 가정통신문이 올라왔습니다. 확인하기 ▶ (가상 링크)", "L", False],
            ],
        },
        {
            "name": "사칭과 송금",
            "goal": "가짜 문자를 모두 막고, 진짜 문자는 모두 통과시키기",
            "intro": "🆕 가짜 문자의 종류가 다양해졌어요. 한 줄로 다 막기 어렵다면 ‘➕ 규칙 줄 추가’로 줄을 늘려요. 줄이 여러 개면 그중 하나에만 걸려도 막혀요(또는).",
            "best": 0,
            "par": 5,
            "hints": [
                "가짜 문자 4개는 모두 ‘모르는 번호’예요. 하지만 모르는 번호 중에도 진짜가 있어요.",
                "돈 요구와 재촉, 앱 설치 요구와 번호, 인증정보 요구를 나눠 비교해 보세요.",
            ],
            "msgs": [
                ["010-73○○-○○○○", "U", "엄마야~ 폰 액정 깨져서 임시 번호야. 급하게 상품권 좀 사서 번호 보내 줄래?", "MR", True],
                ["동아리 총무", "S", "이번 달 동아리 회비 5천 원 모임통장으로 보내 줘~", "M", False],
                ["02-○○○○-○○○○", "U", "[○○은행] 보안 업데이트가 필요합니다. 아래 앱을 설치하세요 ▶ (가상 링크)", "LA", True],
                ["○○은행", "S", "[○○은행] 체크카드 승인 12,800원 도토리마트", "", False],
                ["02-○○○○-○○○○", "U", "도토리지검 수사관입니다. 사건에 연루되셨어요. 지금 바로 인증번호를 불러 주세요.", "PR", True],
                ["친구 지후", "S", "빨리 와!! 영화 5분 뒤에 시작해", "R", False],
                ["도토리고", "S", "[도토리고] 학교 공지 앱 설치 안내 ▶ (가상 링크)", "LA", False],
                ["1588-○○○○", "U", "도토리병원입니다. 내일 오전 10시 진료 예약 안내드려요. 회신은 필요 없어요.", "", False],
            ],
        },
        {
            "name": "완벽한 필터?",
            "goal": "틀리는 문자를 최대한 줄이기",
            "intro": "문자가 10개로 늘었어요. 그리고·또는을 모두 써서 틀리는 문자를 최대한 줄여 보세요.",
            "best": 1,
            "par": 5,
            "hints": [
                "이번에는 완벽한 필터를 만들 수 없을지도 몰라요. 특징 태그가 똑같은 두 문자가 있는지 찾아보세요.",
                "‘인증번호·개인정보 요구’가 있는 진짜 문자는 하나도 없어요.",
            ],
            "msgs": [
                ["010-91○○-○○○○", "U", "[택배] 배송지 확인 불가. 1시간 안에 주소 수정 ▶ (가상 링크)", "LR", True],
                ["010-35○○-○○○○", "U", "아빠 폰 고장 나서 친구 폰 빌렸어. 급히 50만 원만 이 계좌로 보내 줘.", "MR", True],
                ["친구 서연", "S", "급해 ㅠㅠ 문화상품권 5만 원만 사서 핀번호 보내 줘. 이따 바로 갚을게!", "MR", True],
                ["친구 민준", "S", "급해!! 매점에서 천 원만 빌려줘 내일 줄게", "MR", False],
                ["도토리고", "S", "[도토리고] 학부모 앱 설치 안내 ▶ (가상 링크)", "LA", False],
                ["1588-○○○○", "U", "도토리치과입니다. 다음 주 화요일 검진 예약 확인 문자예요.", "", False],
                ["02-○○○○-○○○○", "U", "[○○카드] 해외 결제 승인. 본인이 아니면 링크에서 카드 정보를 입력하세요 ▶ (가상 링크)", "LP", True],
                ["엄마", "S", "언제 와? 빨리 와 밥 식는다", "R", False],
                ["02-○○○○-○○○○", "U", "도토리지검입니다. 계좌가 범죄에 쓰였어요. 확인을 위해 인증번호를 알려 주세요.", "PR", True],
                ["010-60○○-○○○○", "U", "택배 기사입니다. 문 앞에 두고 갑니다~", "", False],
            ],
        },
    ],
    # 3단계의 '규칙으로는 못 가르는' 두 문자: 서연(계정 도용, 가짜)과 민준(진짜)
    "twins": [2, 3],
}

for stage, evidence in zip(DATA['stages'], VERIFIED):
    stage['verified'] = evidence

HTML = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}
body{margin:0;background:#FFFEFA;color:#20483F;font:16px/1.6 'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
button,select{font:inherit}
button{cursor:pointer;border:0;border-radius:12px;padding:10px 14px;background:#E4F0EA;color:#173D35;font-weight:800;min-height:44px;transition:transform .15s,background .15s}
button:hover:not(:disabled){transform:translateY(-2px);background:#D7E8DF}
button:active:not(:disabled){transform:scale(.95)}
button:disabled{opacity:.45;cursor:default}
button:focus-visible,select:focus-visible{outline:3px solid #FF7A45;outline-offset:2px}
.go{background:linear-gradient(135deg,#FF7A45,#FFB347);color:#fff;box-shadow:0 5px 14px #FF7A4540}
.go:hover:not(:disabled){background:linear-gradient(135deg,#F06A35,#FFA337)}
main.wrap{max-width:980px;margin:auto;padding:6px 4px 14px}
@keyframes pop{0%{transform:scale(.6);opacity:0}65%{transform:scale(1.05);opacity:1}100%{transform:scale(1)}}
@keyframes rise{0%{transform:translateY(10px);opacity:0}100%{transform:none;opacity:1}}
@keyframes stamp{0%{transform:scale(3) rotate(-18deg);opacity:0}60%{transform:scale(.9) rotate(-12deg);opacity:1}100%{transform:scale(1) rotate(-8deg);opacity:1}}
@keyframes burst{0%{transform:translate(0,0) scale(.3);opacity:1}100%{transform:translate(var(--x),var(--y)) scale(1.2);opacity:0}}
@keyframes shake{0%,100%{transform:translateX(0)}25%,75%{transform:translateX(-6px)}50%{transform:translateX(6px)}}
@keyframes scan{0%{background-position:-200px 0}100%{background-position:200px 0}}
.hero{background:linear-gradient(135deg,#20483F,#2E7D6B);color:#fff;border-radius:22px;padding:16px 18px;text-align:center;animation:pop .5s ease-out both}
.hero b{display:block;font-size:1.4rem;font-weight:900;word-break:keep-all}.hero span{opacity:.92;font-weight:600;word-break:keep-all}
.box{background:#fff;border:1.5px solid #D7E2DD;border-radius:18px;padding:14px 16px;margin:10px 0;word-break:keep-all;animation:rise .4s ease-out both}
.box h3{margin:0 0 8px;font-size:1.12rem}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0}
.step{background:#F4F8F6;border:1.5px solid #D7E2DD;border-radius:16px;padding:12px;text-align:center;word-break:keep-all}
.step .ic{font-size:34px}.step b.h{display:block;font-size:1.02rem;margin:2px 0}.step p{margin:0;font-size:.9rem;color:#33524A;line-height:1.5}
.ex{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px}
.ex div{background:#F9FBF8;border:1.5px dashed #BFD4CA;border-radius:14px;padding:10px;font-size:.92rem;line-height:1.55}
.terms{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.terms div{border-radius:14px;padding:10px 12px;font-size:.92rem;line-height:1.55;font-weight:700}
.terms .fp{background:#FFF4E8;border:2px solid #FFB385}.terms .fn{background:#FFECEC;border:2px solid #F3A5A5}
.stages{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0}
.stages button{display:flex;flex-direction:column;align-items:center;gap:2px;background:#fff;border:2px solid #C9DCD3;padding:8px 6px}
.stages button.on{background:#20483F;color:#fff;border-color:#20483F;box-shadow:0 0 0 4px #FF7A4555}
.stages button.on:hover:not(:disabled){background:#20483F}
.stages small{font-weight:700;font-size:.8rem;opacity:.9}
.goal{background:#FFF8E6;border:2px solid #F2D58A;border-radius:14px;padding:8px 12px;font-weight:800;margin:8px 0;word-break:keep-all}
.cols{display:grid;grid-template-columns:1.05fr 1fr;gap:14px;align-items:start}
.inbox{display:flex;flex-direction:column;gap:8px}
.msg{position:relative;background:#fff;border:2px solid #D7E2DD;border-radius:16px;padding:10px 12px;word-break:keep-all;animation:rise .35s ease-out both}
.msg .who{display:flex;justify-content:space-between;align-items:center;gap:6px;font-size:.85rem;color:#52616B;font-weight:800}
.msg .txt{font-size:.98rem;font-weight:600;color:#1E2F2B;margin:4px 0 6px;line-height:1.55}
.tags{display:flex;flex-wrap:wrap;gap:4px}
.tag{font-size:.78rem;font-weight:800;border-radius:999px;padding:2px 8px;background:#EEF4F1;color:#33524A;border:1px solid #D2E1DA}
.tag.hit{background:#FFE7D6;border-color:#FF7A45;color:#9A3412}
.msg.scanning{background:linear-gradient(90deg,#fff 0%,#E8F6F0 50%,#fff 100%);background-size:400px 100%;animation:scan .5s linear infinite}
.verdict{display:none;margin-top:8px;gap:6px;flex-wrap:wrap;align-items:center}
.msg.done .verdict{display:flex;animation:pop .35s ease-out both}
.vb{font-weight:900;border-radius:10px;padding:3px 10px;font-size:.88rem}
.vb.block{background:#FFE4E4;color:#B42318}.vb.pass{background:#DFF5EA;color:#0B655B}
.vb.ok{background:#E6F4EC;color:#0F766E}.vb.fp{background:#FFF1E2;color:#B4471B}.vb.fn{background:#FFE4E4;color:#B42318}
.msg.done.good{border-color:#7FC8AE}.msg.done.bad{border-color:#E5484D;animation:shake .4s ease-in-out}
.builder{position:sticky;top:6px}
.rule{background:#F4F8F6;border:2px solid #C9DCD3;border-radius:16px;padding:10px;animation:pop .35s ease-out both}
.rule .head{display:flex;justify-content:space-between;align-items:center;font-weight:900;margin-bottom:6px}
.rule .head button{min-height:34px;padding:4px 10px;font-size:.85rem;background:#fff;border:1.5px solid #E4C7C7;color:#B42318}
.rule .line{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.kw{font-weight:900;color:#0F766E;background:#E1F3EA;border-radius:8px;padding:2px 8px}
.kw.and{color:#7C3AED;background:#EFE9FF}.kw.then{color:#B42318;background:#FFE4E4}
select{min-height:44px;border-radius:12px;border:2px solid #9DBFB2;background:#fff;color:#173D35;font-weight:800;padding:6px 8px;max-width:100%;cursor:pointer}
select.empty{border-style:dashed;color:#6B7F78}
.or{text-align:center;font-weight:900;color:#B4471B;margin:6px 0;font-size:1.05rem}
.meta{display:flex;justify-content:space-between;align-items:center;gap:6px;flex-wrap:wrap;margin:10px 0 6px;font-weight:800}
.blocks{background:#20483F;color:#fff;border-radius:999px;padding:3px 12px}
.blocks.over{background:#B4471B}
pre{background:#1E2B28;color:#D6F5E8;border-radius:14px;padding:10px 12px;font:700 .9rem/1.6 'Courier New',monospace;white-space:pre-wrap;word-break:break-all;margin:8px 0}
pre .k{color:#FFB385}pre .c{color:#8FD3B6}
.row{display:flex;gap:8px;flex-wrap:wrap}.row>button{flex:1}
.hint{background:#EEF2FF;border:2px solid #A5B4FC;border-radius:12px;padding:8px 12px;margin:8px 0;font-weight:700;word-break:keep-all;animation:pop .35s ease-out both}
.toast{min-height:1.4em;font-weight:800;color:#B4471B;margin:6px 0;word-break:keep-all}
.result{position:relative;overflow:hidden;border-radius:22px;padding:18px 14px;text-align:center;margin:12px 0;word-break:keep-all}
.result.win{background:linear-gradient(135deg,#FFF1C2,#D9F2E6)}.result.lose{background:linear-gradient(135deg,#F3F5F4,#E2E9E5)}
.result.fx{animation:pop .55s ease-out both}.result.lose.fx{animation:shake .5s ease-in-out both}
.result .big{font-size:52px}.result b.t{display:block;font-size:1.35rem;font-weight:900}
.stars{font-size:2rem;letter-spacing:4px}.fx .stars i{display:inline-block;font-style:normal;animation:pop .4s ease-out both}
.stamp{display:inline-block;margin-top:8px;border:5px solid #16815F;color:#16815F;border-radius:12px;padding:3px 16px;font-size:1.5rem;font-weight:900;transform:rotate(-8deg);background:rgba(255,255,255,.6)}
.stamp.miss{border-color:#5A7068;color:#5A7068}
.fx .stamp{animation:stamp .5s .5s ease-out both}
.spark{position:absolute;left:50%;top:40%;font-size:24px;opacity:0;pointer-events:none}
.fx .spark{animation:burst 1.1s ease-out both}
.matrix{display:grid;grid-template-columns:auto 1fr 1fr;gap:4px;max-width:440px;margin:10px auto;font-size:.9rem;font-weight:800}
.matrix div{border-radius:10px;padding:8px 6px;text-align:center;line-height:1.35}
.matrix .h{background:transparent;color:#52616B}
.matrix .tp{background:#DFF5EA}.matrix .tn{background:#DFF5EA}.matrix .fp{background:#FFF1E2;color:#B4471B}.matrix .fn{background:#FFE4E4;color:#B42318}
.matrix b{display:block;font-size:1.3rem}
.twin{background:#FFF7E6;border:3px solid #F59E0B;border-radius:18px;padding:16px 18px;margin:14px 0;font-size:1rem;line-height:1.7;box-shadow:0 6px 18px rgba(245,158,11,.25);text-align:left;word-break:keep-all;animation:rise .5s .6s ease-out both}
.twin>b:first-child{display:block;font-size:1.25rem;color:#9A3412;margin-bottom:4px}.twin .pair{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}.twin .pair .fake{border:2.5px solid #EF4444!important;background:#FEF2F2!important}.twin .pair .real{border:2.5px solid #22C55E!important;background:#F0FDF4!important}.twin .same{display:inline-block;background:#FDE68A;color:#78350F;font-weight:900;border-radius:999px;padding:1px 10px;margin:0 2px}.twin .key{background:#9A3412;color:#fff;border-radius:12px;padding:10px 12px;margin-top:10px;font-weight:700}
.twin .pair div{background:#fff;border:1.5px solid #E6D9A8;border-radius:12px;padding:10px;font-size:.95rem;line-height:1.55}
.others{background:#F0F7FF;border:2px solid #B8D4F0;border-radius:14px;padding:8px 12px;margin:10px auto 0;max-width:640px;text-align:left;font-weight:700;font-size:.92rem;line-height:1.6;color:#1E3A5F;word-break:keep-all}
.final{text-align:left}
.guide{background:#F0F7FF;border:2px solid #B8D4F0;border-radius:14px;padding:8px 12px;font-size:.9rem;line-height:1.6;margin:6px 0 8px;word-break:keep-all}
.sintro{background:#fff;border:2px solid #C9DCD3;border-left:8px solid #0F766E;border-radius:14px;padding:8px 12px;font-weight:700;margin:8px 0;word-break:keep-all}
.ex2{background:#F9FBF8;border:1.5px dashed #BFD4CA;border-radius:14px;padding:10px;margin-top:8px;font-size:.92rem;line-height:1.6}
.ex2 .r{display:inline-block;background:#fff;border:1.5px solid #C9DCD3;border-radius:10px;padding:2px 8px;margin:2px 0}
.why{background:#fff;border:2px solid #E8D6CE;border-radius:14px;padding:10px 12px;margin:10px auto 0;max-width:640px;text-align:left;font-size:.92rem;line-height:1.6}
.why li{margin:4px 0}
.vb.by{background:#EFE9FF;color:#5B21B6}
.still .hero,.still .box,.still .msg,.still .rule,.still .hint{animation:none!important}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:720px){.cols{grid-template-columns:1fr}.builder{position:static}.steps{grid-template-columns:1fr}.step{display:flex;gap:10px;align-items:center;text-align:left}.step .ic{font-size:28px}}
@media (max-width:480px){.ex,.terms,.twin .pair{grid-template-columns:1fr}.hero b{font-size:1.2rem}.stages small{font-size:.72rem}}
</style></head><body>
<main class="wrap" id="app"></main>
<script>
const D = __DATA__;
// 문자 필터실 관제 모니터 모양의 큰 창 (피싱 필터 전용)
function monitorPop(o, then){
  const lamp = o.ok ? '#22C55E' : '#EF4444';
  jkOverlay(`<div class="jk-panel" style="background:#0B1F1A;border:4px solid #1F4D42;border-radius:18px;padding:16px 18px;color:#D1FAE5;box-shadow:0 20px 50px #0008;font-family:ui-monospace,Consolas,monospace">
   <div style="display:flex;align-items:center;gap:10px;border-bottom:1px dashed #1F4D42;padding-bottom:8px;margin-bottom:12px">
    <span style="width:14px;height:14px;border-radius:50%;background:${lamp};box-shadow:0 0 12px ${lamp}"></span>
    <b style="letter-spacing:.06em">📮 도토리 우체국 · 문자 필터실 모니터</b><span style="margin-left:auto;color:#6EE7B7">${o.tag||''}</span></div>
   <div style="display:flex;gap:14px;align-items:center">${jkImg(o.mascot,145)}
    <div style="flex:1"><div style="font-size:1.4rem;font-weight:900;color:${o.ok?'#86EFAC':'#FCA5A5'}">${o.title}</div>
    <div style="margin-top:6px;line-height:1.7;font-family:system-ui,sans-serif;color:#ECFDF5">${o.body}</div></div></div>
   ${o.lines?'<div style="margin-top:12px;background:#06140F;border-radius:10px;padding:10px 12px;line-height:1.9">'+o.lines.map(l=>'&gt; '+l).join('<br>')+'</div>':''}
   <button data-close style="margin-top:14px;width:100%;min-height:50px;border:2px solid ${lamp};border-radius:12px;background:#0F2E26;color:#ECFDF5;font:800 1.05rem system-ui;cursor:pointer">${o.button||'모니터 닫기 ▶'}</button></div>`, then);
}

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const KEYS = Object.keys(D.conds);
const HOLD=__HOLDOUT__;
const G = {ops:[[],[],[]],hold:[null,null,null],review:[],reviewRoute:'',screen: 'intro', stage: 0, rules: [[['', '']], [['', '']], [['', '']]], best: [null, null, null], hintOpen: [0, 0, 0], last: null, running: false, tries: [0, 0, 0]};
let fresh = true;

// 문자 하나가 조건을 만족하는지: S(저장된 번호)는 '모르는 번호가 아님'
function has(msg, c){ if (c === 'U') return msg[1] === 'U'; if (c === 'S') return msg[1] === 'S'; return msg[3].includes(c); }
function cleanRules(st){ return G.rules[st].map(r => r.filter(c => c)).filter(r => r.length); }
function blocks(st){ return cleanRules(st).reduce((a, r) => a + r.length, 0); }

function matches(st,ri,msg){const r=G.rules[st][ri].filter(Boolean);return r.length>0&&(G.ops[st][ri]==='or'?r.some(c=>has(msg,c)):r.every(c=>has(msg,c)));}
function flagged(st,msg){return G.rules[st].some((r,i)=>matches(st,i,msg));}
function setOp(ri,v){G.ops[G.stage][ri]=v;G.last=null;G.hold[G.stage]=null;render();}

function starsFor(st, res){ const s = D.stages[st]; if (res.errors > s.best) return 0; return res.blocks <= s.par ? 3 : res.blocks <= s.par + 2 ? 2 : 1; }

function codeView(st){
 const parts=G.rules[st].map((rule,ri)=>{const r=rule.filter(Boolean);return r.length?'('+r.map(c=>D.code[c]).join(G.ops[st][ri]==='or'?' or ':' and ')+')':'';}).filter(Boolean);
 return esc(parts.length?'if '+parts.join(' or ')+': 의심 분류\nelse: 통과 분류':'조건을 선택하세요.');
}
function tagsHtml(msg, hitSet){
  const list = [msg[1]].concat(msg[3].split('').filter(Boolean));
  return list.map(c => `<span class="tag ${hitSet && hitSet.has(c) ? 'hit' : ''}">${esc(D.conds[c])}</span>`).join('');
}

function render(){
  setPlayActive(G.screen !== 'intro');
  const app = $('app');
  app.classList.toggle('still', !fresh); fresh = false;
  if (G.screen === 'intro') return renderIntro();
  if (G.screen === 'final') return renderFinal();
  renderPlay();
}

function renderIntro(){
  $('app').innerHTML = `
  <section class="hero"><span>📮 도토리 우체국 · 문자 필터실</span><b>도시로 들어오는 문자, 내가 만든 규칙으로 걸러라!</b><span>조건 블록을 조립하면 컴퓨터가 그대로 실행해요.</span></section>
  <div class="steps">
    <div class="step"><div class="ic">🏷️</div><div><b class="h">① 태그 보기</b><p>문자마다 ‘링크 있음’, ‘모르는 번호’ 같은 특징 태그가 붙어 있어요.</p></div></div>
    <div class="step"><div class="ic">🧩</div><div><b class="h">② 규칙 조립</b><p>‘만약 A <b>그리고</b>/<b>또는</b> B면 의심’처럼 블록과 연결을 고르고, 규칙 줄끼리는 <b>또는</b>으로 이어져요.</p></div></div>
    <div class="step"><div class="ic">▶️</div><div><b class="h">③ 실행하고 고치기</b><p>문자가 하나씩 필터를 지나가요. 틀린 문자를 보고 규칙을 고쳐요.</p></div></div>
  </div>
  <section class="box"><h3>🔍 예시로 먼저 볼까요?</h3>
    규칙: <span class="kw">만약</span> 🔗 링크 있음 <span class="kw and">그리고</span> ❓ 모르는 번호 <span class="kw then">→ 🚫 의심</span>
    <div class="ex">
      <div><b>문자 A</b> · 🔗 링크 있음 · ❓ 모르는 번호<br>두 조건이 <b>모두</b> 맞아요 → <b style="color:#B42318">🚫 의심</b></div>
      <div><b>문자 B</b> · 🔗 링크 있음 · 📇 저장된 번호<br>하나만 맞아요 → <b style="color:#0B655B">✅ 통과</b></div>
    </div>
    <p style="margin:10px 0 0">👉 <b>그리고</b>는 한 줄 안의 조건이 <b>모두</b> 맞아야 걸려요. 연결을 ‘또는’으로 바꾸면 하나 이상 맞을 때 걸려요.</p>
    <div class="ex2"><b>같은 줄을 ‘또는’으로 바꾸면?</b><br>
      규칙: <span class="kw">만약</span> 🔗 링크 있음 <b style="color:#B4471B">또는</b> ❓ 모르는 번호 <span class="kw then">→ 🚫 의심</span><br>
      · 문자 A (🔗 링크 있음 · ❓ 모르는 번호) → 둘 다 맞음 → <b style="color:#B42318">🚫 의심</b><br>
      · 문자 B (🔗 링크 있음 · 📇 저장된 번호) → 하나만 맞아도 → <b style="color:#B42318">🚫 의심</b> (그리고일 때는 통과였어요!)<br>
      <span style="font-size:.9rem;color:#52616B">또는은 더 넓게 걸러서 사기 문자를 놓치지 않지만, 진짜 문자까지 막을(오탐) 수 있어요.</span></div>
    <div class="ex2"><b>규칙 줄이 2개라면? (또는)</b><br>
      <span class="r">규칙 1 · 💸 돈 요구 <span class="kw and">그리고</span> ❓ 모르는 번호</span> <b style="color:#B4471B">또는</b>
      <span class="r">규칙 2 · 🔑 인증번호·개인정보 요구</span><br>
      · 문자 C (💸 돈 요구 · ❓ 모르는 번호) → 규칙 1에 걸림 → <b style="color:#B42318">🚫 의심</b><br>
      · 문자 D (🔑 인증번호 요구 · 📇 저장된 번호) → 규칙 2에 걸림 → <b style="color:#B42318">🚫 의심</b><br>
      · 문자 E (💸 돈 요구 · 📇 저장된 번호) → 어느 줄에도 다 맞지 않음 → <b style="color:#0B655B">✅ 통과</b></div>
    <p style="margin:10px 0 0">👉 규칙 줄은 <b>‘➕ 규칙 줄 추가’</b>로 3줄까지 늘릴 수 있고, 줄끼리는 <b>또는</b>이라 <b>한 줄에만 걸려도</b> 막혀요.</p>
    <div class="terms">
      <div class="fp">🟠 <b>오탐</b> · 진짜 문자인데 막아 버림<br><span style="font-weight:600">엄마 문자가 스팸함에 들어가는 경우</span></div>
      <div class="fn">🔴 <b>미탐</b> · 가짜 문자인데 통과시킴<br><span style="font-weight:600">사기 문자가 그대로 도착하는 경우</span></div>
    </div>
  </section>
  <section class="box"><h3>⭐ 별 받는 법</h3>
    ⭐ 목표 달성 · ⭐ 블록을 목표보다 2개 넘게 쓰지 않기 · ⭐ 목표 블록 수 이하로 해내기<br>
    <span style="font-size:.92rem;color:#52616B">블록 = 고른 조건 하나. 같은 결과라면 짧은 규칙이 더 좋은 프로그램이에요.</span>
  </section>
  <button class="go" style="width:100%;font-size:1.15rem;min-height:56px" onclick="startStage(0)">🤖 필터실 입장하기</button>`;
}

// 필터실 안에서 바로 전 화면(시작 화면)으로 돌아가요. 만든 규칙과 기록은 그대로 남아요.
function backIntro(){ G.screen = 'intro'; fresh = true; render(); window.scrollTo(0, 0); }
function startStage(i){if(i>0&&!G.best[i-1])return; G.screen = 'play'; G.stage = i; G.last = null; fresh = true; render(); window.scrollTo(0, 0); }

function stageButtons(){
  return `<div class="stages">${D.stages.map((s, i) => {
    const locked = i > 0 && !G.best[i - 1];
    const st = G.best[i] ? '⭐'.repeat(G.best[i].stars) + '☆'.repeat(3 - G.best[i].stars) : (locked ? '🔒' : '☆☆☆');
    return `<button class="${i === G.stage ? 'on' : ''}" ${locked ? 'disabled' : ''} onclick="startStage(${i})">${i + 1}단계 · ${esc(s.name)}<small>${st}</small></button>`;
  }).join('')}</div>`;
}

function ruleHtml(st, ri){
  const r = G.rules[st][ri];
  const sel = (ci) => `<select class="${r[ci] ? '' : 'empty'}" aria-label="규칙 ${ri + 1}의 조건 ${ci + 1}" onchange="setCond(${ri},${ci},this.value)" ${G.running ? 'disabled' : ''}>
      <option value="">${ci === 0 ? '조건 고르기 ▾' : '(추가 조건 없음) ▾'}</option>
      ${KEYS.map(k => `<option value="${k}" ${r[ci] === k ? 'selected' : ''}>${esc(D.conds[k])}</option>`).join('')}</select>`;
  return `<div class="rule"><div class="head">🧩 규칙 ${ri + 1}${G.rules[st].length > 1 ? `<button onclick="delRule(${ri})" ${G.running ? 'disabled' : ''}>🗑 빼기</button>` : ''}</div>
    <div class="line"><span class="kw">만약</span>${sel(0)}<select aria-label="규칙 ${ri+1} 연결" onchange="setOp(${ri},this.value)" ${G.running?'disabled':''}><option value="and">그리고</option><option value="or" ${G.ops[st][ri]==='or'?'selected':''}>또는</option></select>${sel(1)}<span class="kw then">→ 🚫 의심</span></div></div>`;
}

function renderPlay(){
  const st = G.stage, s = D.stages[st], res = G.last;
  const b = blocks(st);
  const rules = G.rules[st].map((_, ri) => ruleHtml(st, ri)).join('<div class="or">또는</div>');
  const msgs = s.msgs.map((m, i) => {
    let cls = '', verdict = '', hit = null;
    if (res) {
      const r = res.rows[i];
      cls = 'done ' + (r.flag === m[4] ? 'good' : 'bad');
      hit = r.hit;
      verdict = verdictHtml(m, r);
    }
    return `<div class="msg ${cls}" id="msg${i}" style="animation-delay:${i * .04}s">
      ${res ? '<details><summary>📋 시험 후 확인한 근거</summary>'+esc(s.verified[i])+'</details>' : '<small>별도 확인 근거는 필터 시험 후 공개돼요.</small>'}<div class="who"><span>${m[1] === 'S' ? '📇' : '❓'} ${esc(m[0])}</span><span>문자 ${i + 1}</span></div>
      <div class="txt">${esc(m[2])}</div><div class="tags">${tagsHtml(m, hit)}</div><div class="verdict">${verdict}</div></div>`;
  }).join('');
  const hints = s.hints.slice(0, G.hintOpen[st]).map((h, k) => `<div class="hint">💡 힌트 ${k + 1}: ${esc(h)}</div>`).join('');
  $('app').innerHTML = `
  <button style="background:#fff;border:2px solid #20483F;color:#20483F;margin:0 0 8px" onclick="backIntro()">← 이전 화면으로</button>
  <section class="hero"><span>📮 도토리 우체국 · 문자 필터실</span><b>${st + 1}단계 · ${esc(s.name)}</b><span>문자 ${s.msgs.length}개 · 목표 블록 ${s.par}개 이하</span></section>
  ${s.best > 0 ? `<div style="background:#FFF7E6;border:3px solid #F59E0B;border-radius:14px;padding:10px 14px;margin:8px 0;font-weight:800;color:#9A3412">⚠️ 이번 단계는 <b style="background:#FDE68A;padding:0 4px;border-radius:4px">어떤 규칙으로도 ${s.best}개는 꼭 틀려요.</b> 최대한 적게 틀리는 필터를 만들고, 시험 결과에서 그 이유를 확인해 보세요.</div>` : ''}
  ${stageButtons()}
  <div class="goal">🎯 목표: ${esc(s.goal)}</div>
  <div class="sintro">📢 ${esc(s.intro)}</div>
  ${res ? resultHtml(st, res) : ''}
  <div class="cols">
    <div><h3 style="margin:6px 0">📥 들어온 문자 ${s.msgs.length}개</h3><div class="inbox">${msgs}</div></div>
    <div class="builder"><h3 style="margin:6px 0">🧩 내 필터 규칙</h3>
      <div class="guide">📘 <b>읽는 법</b> · 한 줄에서 <b>그리고 / 또는</b>를 선택해요. 그리고는 모두, 또는은 하나 이상 맞으면 걸려요.<br>줄과 줄 사이는 <b>또는</b>: <b>한 줄에만</b> 걸려도 막혀요.</div>
      ${rules}
      ${G.rules[st].length < 3 ? `<button style="width:100%;margin-top:8px;background:#fff;border:2px dashed #9DBFB2" onclick="addRule()" ${G.running ? 'disabled' : ''}>➕ 규칙 줄 추가 (또는)</button>` : ''}
      <div class="meta"><span>📦 사용한 블록 <span class="blocks ${b > s.par ? 'over' : ''}">${b}개</span></span><span>목표 ${s.par}개 이하</span></div>
      <div style="font-weight:800;font-size:.92rem;margin-top:6px">💻 컴퓨터가 읽는 코드</div>
      <pre>${codeView(st)}</pre>
      <div class="toast" id="toast"></div>
      <div class="row"><button class="go" onclick="run()" ${G.running ? 'disabled' : ''}>▶ 필터 실행</button>
        <button onclick="openHint()" ${G.running || G.hintOpen[st] >= s.hints.length ? 'disabled' : ''}>💡 힌트 (${G.hintOpen[st]}/${s.hints.length})</button></div>
      ${hints}
    </div>
  </div>`;
}

function resultHtml(st, res){
  const s = D.stages[st], stars = starsFor(st, res), go = res.fresh ? ' fx' : '';
  res.fresh = false;
  const matrix = `<div class="matrix">
    <div class="h"></div><div class="h">🚫 막음</div><div class="h">✅ 통과</div>
    <div class="h">가짜 문자</div><div class="tp"><b>${res.tp}</b>잘 막음</div><div class="fn"><b>${res.fn}</b>미탐</div>
    <div class="h">진짜 문자</div><div class="fp"><b>${res.fp}</b>오탐</div><div class="tn"><b>${res.tn}</b>잘 통과</div></div>`;
  if (!stars) {
    const msg = s.best > 0 ? `더 줄일 수 있어요! 이 단계는 ${s.best}개까지는 어쩔 수 없지만, 지금은 ${res.errors}개를 틀렸어요.` : `${res.errors}개를 틀렸어요. 빨간 테두리 문자를 보고 규칙을 고쳐 보세요.`;
    return `<section class="result lose${go}"><div class="big">🔧</div><b class="t">${esc(msg)}</b>${s.best > 0 ? twinHtml(st) : ''}${matrix}
      <span class="stamp miss">다시 고치기</span>${whyHtml(st, res)}${othersHtml(st)}</section>`;
  }
  const sp = ['✨', '⭐', '🛡️', '🎉', '✨', '💫', '⭐', '🎉'].map((ic, k) => { const a = k * Math.PI / 4; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 140)}px;--y:${Math.round(Math.sin(a) * 100)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  const parMsg = res.blocks <= s.par ? `블록 ${res.blocks}개로 해냈어요. 최고 기록이에요!` : `블록 ${res.blocks}개를 썼어요. 목표는 ${s.par}개 이하! 더 짧게 줄여 볼까요?`;
  const twins = s.best > 0 ? twinHtml(st) : '';
  const next = (!G.hold[st] || !G.hold[st].ok) ? '<button class="go" onclick="runHoldout()">처음 보는 문자로 시험하기</button>' : st < D.stages.length - 1 ? `<button class="go" style="width:100%;margin-top:10px" onclick="startStage(${st + 1})">다음 단계로 ➡️</button>` : `<button class="go" style="width:100%;margin-top:10px" onclick="toFinal()">🏆 최종 결과 보기</button>`;
  return `<section class="result win${go}"><div class="big">🛡️</div><b class="t">${s.best > 0 ? '이게 규칙으로 할 수 있는 최선이에요!' : '필터 완성!'}</b>
    <div class="stars">${[0, 1, 2].map(k => `<i style="animation-delay:${.3 + k * .2}s">${k < stars ? '⭐' : '☆'}</i>`).join('')}</div>
    ${twins}<div style="font-weight:800">${esc(parMsg)}</div>${matrix}<span class="stamp">${s.best > 0 ? '최선의 필터!' : '필터 통과!'}</span>${sp}${othersHtml(st)}${holdHtml(st)}${next}</section>`;
}

function twinHtml(st){
  const s = D.stages[st], [a, b] = D.twins, A = s.msgs[a], B = s.msgs[b];
  return `<div class="twin"><b>🤔 왜 1개는 꼭 틀릴까요? · 이 단계의 진짜 비밀</b>
    <div class="pair"><div class="fake">🔴 <b>${esc(A[0])}</b> (가짜 · 계정 도용)<br>${esc(A[2])}</div><div class="real">🟢 <b>${esc(B[0])}</b> (진짜)<br>${esc(B[2])}</div></div>
    두 문자는 특징이 <span class="same">저장된 번호</span><span class="same">돈 요구</span><span class="same">재촉</span>으로 <b>똑같아요.</b> 똑같은 입력에는 규칙도 똑같이 답할 수밖에 없어서, 하나를 막으면 다른 하나도 막혀요.<br>
    <div class="key">👉 그래서 규칙(필터)만으로는 완벽할 수 없어요. 친구가 돈을 부탁하면 원래 알던 번호로 전화하거나 직접 만나서 확인하는 게 마지막 방어선이에요.</div></div>`;
}

function othersHtml(st){
  const runs = STATS[`s${st}_runs`] || 0;
  if (!runs) return '<div class="others">🌍 아직 이 단계에 모인 기록이 없어요. 첫 기록의 주인공이에요!</div>';
  const clear = STATS[`s${st}_clear`] || 0;
  let worst = -1, wv = 0;
  D.stages[st].msgs.forEach((_, i) => { const v = STATS[`s${st}_m${i}_wrong`] || 0; if (v > wv) { wv = v; worst = i; } });
  return `<div class="others">🌍 지금까지 이 단계 필터가 <b>${runs}번</b> 실행됐고, <b>${Math.round(clear * 100 / runs)}%</b>가 목표를 달성했어요.`
    + (worst >= 0 ? `<br>가장 많이 틀린 문자는 <b>문자 ${worst + 1}</b>(${esc(D.stages[st].msgs[worst][0])})예요. 실행한 필터의 ${Math.round(wv * 100 / runs)}%가 이 문자를 틀렸어요.` : '') + '</div>';
}

function verdictHtml(m, r){
  const ok = r.flag === m[4];
  const why = r.flag ? `<span class="vb by">🧩 규칙 ${r.fired.join('·')}에 걸림</span>` : '<span class="vb by">어느 규칙에도 안 걸림</span>';
  return `<span class="vb ${r.flag ? 'block' : 'pass'}">${r.flag ? '🚫 의심으로 막음' : '✅ 통과'}</span>${why}`
    + (ok ? `<span class="vb ok">⭕ 맞음 · ${m[4] ? '가짜 문자' : '진짜 문자'}</span>` : (r.flag ? '<span class="vb fp">🟠 오탐 · 진짜 문자였어요</span>' : '<span class="vb fn">🔴 미탐 · 가짜 문자였어요</span>'));
}

function whyHtml(st, res){
  const s = D.stages[st], items = [];
  res.rows.forEach((r, i) => {
    const m = s.msgs[i];
    if (r.flag === m[4]) return;
    if (st === D.stages.length - 1 && D.twins.includes(i) && res.errors <= s.best) return;
    if (!r.flag) {
      const tip = G.rules[st].length < 3 ? ' 이 문자를 막을 <b>새 규칙 줄을 ➕로 추가</b>해 보세요.' : ' 규칙 줄 하나를 이 문자도 걸리게 바꿔 보세요.';
      items.push(`<li>🔴 <b>문자 ${i + 1}</b>(${esc(m[0])}) · 가짜인데 <b>어느 규칙에도 안 걸렸어요</b>.${tip}</li>`);
    } else {
      const ri = r.fired[0], one = G.rules[st][ri - 1].filter(c => c).length === 1, isOr = G.ops[st][ri - 1] === 'or';
      const tip = isOr && !one ? ` 규칙 ${ri}의 연결이 <b>‘또는’</b>이라 넓게 걸렸어요. <b>‘그리고’</b>로 바꾸면 더 좁게 걸러져요.`
        : one ? ` 규칙 ${ri}에 <b>‘그리고’ 조건을 하나 더</b> 붙이면 더 좁게 걸러져요.` : ` 규칙 ${ri}의 조건을 다른 것으로 바꿔 보세요.`;
      items.push(`<li>🟠 <b>문자 ${i + 1}</b>(${esc(m[0])}) · 진짜인데 <b>규칙 ${r.fired.join('·')}에 걸렸어요</b>.${tip}</li>`);
    }
  });
  return items.length ? `<div class="why"><b>🔎 무엇이 틀렸을까요?</b><ul style="margin:6px 0 0;padding-left:18px">${items.join('')}</ul></div>` : '';
}

function setCond(ri, ci, v){ G.rules[G.stage][ri][ci] = v; G.last = null; G.hold[G.stage]=null; render(); }
function addRule(){ G.rules[G.stage].push(['', '']); G.last = null; G.hold[G.stage]=null; render(); }
function delRule(ri){ G.rules[G.stage].splice(ri, 1);G.ops[G.stage].splice(ri,1); G.last = null; G.hold[G.stage]=null; render(); }
function openHint(){ G.hintOpen[G.stage]++; render(); }

function run(){
  const st = G.stage, s = D.stages[st];
  if (!cleanRules(st).length) { $('toast').textContent = '먼저 규칙 1의 조건을 하나 이상 골라 주세요.'; return; }
  G.running = true; G.last = null; render();
  const rows = s.msgs.map(m => {
    const fired = [], hit = new Set();
    G.rules[st].forEach((r, ri) => { const conds = r.filter(c => c); if (matches(st,ri,m)) { fired.push(ri + 1); conds.forEach(c => hit.add(c)); } });
    return {flag: fired.length > 0, hit, fired};
  });
  // 문자가 하나씩 필터를 지나가는 모습
  s.msgs.forEach((m, i) => {
    setTimeout(() => { const el = $('msg' + i); if (el) { el.classList.add('scanning'); el.scrollIntoView({block: 'nearest', behavior: 'smooth'}); } }, i * 260);
    setTimeout(() => {
      const el = $('msg' + i); if (!el) return;
      el.classList.remove('scanning');
      const r = rows[i], ok = r.flag === m[4];
      el.classList.add('done', ok ? 'good' : 'bad');
      el.querySelector('.tags').innerHTML = tagsHtml(m, r.hit);
      el.querySelector('.verdict').innerHTML = verdictHtml(m, r);
    }, i * 260 + 230);
  });
  setTimeout(() => {
    let tp = 0, tn = 0, fp = 0, fn = 0;
    rows.forEach((r, i) => { const scam = s.msgs[i][4]; if (scam && r.flag) tp++; else if (scam) fn++; else if (r.flag) fp++; else tn++; });
    const res = {rows, tp, tn, fp, fn, errors: fp + fn, blocks: blocks(st), fresh: true};
    G.tries[st]++;
    const stars = starsFor(st, res);
    G.hold[st]=null;
    G.running = false; G.last = res; fresh = false; render();
    sendResult({game: 'filter', type: 'run', stage: st, clear: false, stars, blocks: res.blocks,
      wrong: res.rows.map((r, i) => r.flag !== s.msgs[i][4] ? i : -1).filter(i => i >= 0)});
    const box = document.querySelector('.result'); if (box) box.scrollIntoView({block: 'start', behavior: 'smooth'});
    const lines = [`잘 막은 가짜 문자 ${res.tp}건`, `잘 통과한 진짜 문자 ${res.tn}건`, `놓친 가짜 문자(미탐) ${res.fn}건`, `잘못 막은 진짜 문자(오탐) ${res.fp}건`, `사용한 블록 ${res.blocks}개 (목표 ${s.par}개 이하)`];
    if (stars) monitorPop({ok:true, mascot:'postman', tag:`${st + 1}단계 · ${'★'.repeat(stars)}${'☆'.repeat(3 - stars)}`,
      title: s.best > 0 ? '✅ 규칙으로 할 수 있는 최선!' : '✅ 필터 가동 성공!',
      body: s.best > 0 ? '어떤 규칙으로도 1개는 틀릴 수밖에 없는 단계예요. 결과 화면의 설명 상자를 꼭 읽어 보세요.' : '이제 처음 보는 문자로도 시험해 봐요.', lines});
    else monitorPop({ok:false, mascot:'think', tag:`${st + 1}단계 · 경고`, title:`⚠️ ${res.errors}건 잘못 분류됨`,
      body:'빨간 테두리 문자를 보고 규칙을 고쳐 보세요. 놓친 가짜 문자는 막고, 진짜 문자는 통과시켜야 해요.', lines, button:'규칙 고치러 가기 ▶'});
  }, s.msgs.length * 260 + 500);
}


function holdHtml(st){
 const h=G.hold[st];if(!h)return '<p>현재 규칙으로 새 문자 시험도 마쳐야 해요.</p>';
 return '<section class="box"><h3>새 문자 시험</h3>'+h.rows.map(x=>'<p>'+esc(x.text)+'<br><b>'+(x.flag?'의심':'통과')+' · '+(x.flag===x.answer?'일치':'오차단·누락')+'</b><br>'+esc(x.proof)+'</p>').join('')+'<p>'+h.errors+'개 오차. '+(h.ok?'시험 통과':'규칙을 고치고 연습과 새 문자 시험을 다시 실행하세요.')+'</p></section>';
}
function runHoldout(){
 const st=G.stage;if(!G.last||!starsFor(st,G.last))return;
 const rows=HOLD[st].map(m=>({text:m[2],flag:flagged(st,m),answer:m[4],proof:m[4]?'별도로 연락한 당사자·기관이 해당 요구를 부인한 교육용 사례':'기존 연락처나 직접 연 공식 기록에서 요청을 확인한 교육용 사례'}));
 const errors=rows.filter(x=>x.flag!==x.answer).length;G.hold[st]={rows,errors,ok:errors===0};
 if(!errors)G.best[st]={stars:starsFor(st,G.last),blocks:blocks(st)};
 sendResult({game:'filter',type:'run',stage:st,clear:errors===0,trial:true,wrong:[]});
 render();
 monitorPop(errors?{ok:false,mascot:'think',tag:'새 문자 시험',title:`⚠️ 새 문자 ${errors}건 오분류`,body:'처음 보는 문자에서는 규칙이 맞지 않았어요. 특정 문자에만 맞춘 규칙은 아닌지 살펴보세요.',button:'규칙 다시 보기 ▶'}
   :{ok:true,mascot:'hooray',tag:'새 문자 시험',title:'🎉 처음 보는 문자도 통과!',body:'외운 규칙이 아니라 진짜로 통하는 규칙이에요. 다음 단계로 가 볼까요?'});
}
function toFinal(){
 if(!G.best.every(Boolean))return;
 if(!G.review.includes(2)||!G.review.includes(3)||G.review.length!==2||G.reviewRoute!=='separate'){
  G.review=[];G.reviewRoute='';
  $('app').innerHTML='<section class="box"><h3>마지막 확인: 태그만으로 구별할 수 없는 두 문자</h3><p>3단계에서 특징이 같지만 실제 결과가 다른 두 문자를 고르고 확인 방법을 선택하세요.</p>'+D.stages[2].msgs.map((m,i)=>'<label style="display:block;padding:8px"><input type="checkbox" onchange="G.review=G.review.filter(x=>x!=='+i+');if(this.checked)G.review.push('+i+')">'+(i+1)+'. '+esc(m[0])+' · '+esc(m[2])+'</label>').join('')+'<select aria-label="추가 확인 경로" onchange="G.reviewRoute=this.value"><option value="">확인 경로</option><option value="reply">받은 메시지에 답장해서 확인</option><option value="separate">기존 연락처나 대면으로 별도 확인</option></select><button onclick="toFinal()">확인 제출</button><p>완료되지 않으면 두 문자의 태그와 확인 경로를 다시 비교하세요.</p></section>';return;
 }

  sendResult({game: 'filter', type: 'final', stars: G.best.reduce((a, b) => a + (b ? b.stars : 0), 0), blocks: G.best.reduce((a, b) => a + (b ? b.blocks : 0), 0)});
  G.screen = 'final'; fresh = true; render(); window.scrollTo(0, 0);
}

function renderFinal(){
  const total = G.best.reduce((a, b) => a + (b ? b.stars : 0), 0);
  const title = total >= 9 ? '🏅 수석 필터 엔지니어' : total >= 6 ? '🛠️ 필터 엔지니어' : '🌱 새내기 필터 개발자';
  const sp = ['✨', '⭐', '🤖', '🎉', '✨', '💫', '⭐', '🎉', '🛡️', '✨'].map((ic, k) => { const a = k * Math.PI / 5; return `<span class="spark" style="--x:${Math.round(Math.cos(a) * 150)}px;--y:${Math.round(Math.sin(a) * 110)}px;animation-delay:${.45 + k * .03}s">${ic}</span>`; }).join('');
  $('app').innerHTML = `
  <section class="result win fx"><div class="big">🏆</div><b class="t">${title}</b>
    <div class="stars">${'⭐'.repeat(total)}${'☆'.repeat(9 - total)}</div><div style="font-weight:800">별 ${total} / 9</div>
    <span class="stamp">필터실 수료!</span>${sp}</section>
  <section class="box final"><h3>📌 오늘 만든 필터에서 배운 것</h3>
    ① <b>조건문</b>: “만약 ~라면 의심, 아니면 통과”. 컴퓨터는 규칙을 적힌 그대로만 실행해요.<br>
    ② <b>그리고(AND)·또는(OR)</b>: 그리고는 조건을 더 좁게, 또는는 더 넓게 만들어요.<br>
    ③ <b>오탐과 미탐</b>: 너무 넓게 막으면 진짜 문자가 막히고(오탐), 너무 좁게 막으면 사기 문자가 들어와요(미탐). 실제 스팸 필터도 이 균형을 고민해요.<br>
    ④ <b>규칙의 한계</b>: 특징이 똑같은 문자는 규칙으로 가를 수 없어요. 마지막엔 <b>원래 알던 번호로 직접 확인</b>하는 사람의 판단이 필요해요.</section>
  <div class="row"><button onclick="startStage(0)">🔁 1단계부터 다시 줄여 보기</button><button class="go" onclick="restart()">🔄 처음부터 다시</button></div>`;
}

function restart(){ Object.assign(G, {ops:[[],[],[]],hold:[null,null,null],review:[],reviewRoute:'',screen: 'intro', stage: 0, best: [null, null, null], hintOpen: [0, 0, 0], last: null, running: false, tries: [0, 0, 0]}); G.rules = [[['', '']], [['', '']], [['', '']]]; fresh = true; render(); }

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

page = bridge(HTML, "11").replace("__HOLDOUT__",json.dumps(HOLDOUT,ensure_ascii=False).replace("<","\\u003c")).replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("<", "\\u003c"))
value = create_filter_component(page)(key="jamkkan_phishing_filter_v1", default=None, stats=dd.stats("filter"))

# 결과를 익명 통계(+1)에 더하고, 시민증이 있으면 명예의 전당에 저장해요.
event = dd.take_event(value)
if event and event.get("type") == "run" and event.get("stage") in (0, 1, 2):
    s = int(event["stage"])
    counts = {f"s{s}_runs": 1, f"s{s}_clear": 1 if event.get("clear") else 0}
    counts.update({f"s{s}_m{int(i)}_wrong": 1 for i in event.get("wrong", []) if 0 <= int(i) < 12})
    dd.record("filter", counts)

elif event and event.get("type") == "final":
    stars, blocks = max(0, min(9, int(event.get("stars", 0)))), max(0, int(event.get("blocks", 0)))
    dd.record("filter", {"finals": 1})
    dd.stamp("11")
    dd.note_mine("filter", f"별 {stars}/9 · 블록 {blocks}개")
    st.session_state["filter_hall"] = dd.save_hall(
        "filter", {"stars": stars, "blocks": blocks},
        lambda old, new: (new["stars"], -new["blocks"]) > (old.get("stars", 0), -old.get("blocks", 10**6)),
    )
dd.show_hall_note(st.session_state.get("filter_hall"))

with st.expander("🧠 이 페이지 속 알고리즘 (정보 과목 연계)"):
    st.markdown(
        "- **조건문과 논리 연산**: 규칙 한 줄은 `and`, 규칙 줄끼리는 `or`로 이어진 `if` 문이에요. 오른쪽 코드 창에서 내가 만든 규칙이 코드로 바뀌는 걸 볼 수 있어요.\n"
        "- **오탐·미탐과 혼동 행렬**: 결과 표는 실제 스팸 필터와 인공지능 분류 모델을 평가할 때 쓰는 2×2 표와 같아요.\n"
        "- **새 자료 시험**: 같은 규칙을 연습 문자와 새 문자에 적용해요. 목표 블록 수는 권장 목표이며, 3단계 동일 태그 두 문자는 별도 확인이 필요해요."
    )
st.caption("교육용 가상 문자입니다. 실제 번호·기관·링크와 관계없으며, 진행은 새로고침하면 초기화됩니다.")
