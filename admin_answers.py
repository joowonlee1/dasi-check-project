"""관리자 인증 후에만 표시하는 정답·판정 기준. 페이지 코드를 실행하지 않고 정적 자료만 읽습니다."""
from pathlib import Path
import ast
import streamlit as st

GUIDES = {
 "1": "각 상황의 선택지별 결과·해설을 확인하세요. 결말은 선택과 신뢰도에 따라 달라져요.",
 "2": "자유 입력 대화는 고정 정답 문장이 없어요. 요구 중단, 독립 확인, 개인정보·인증정보 전달 여부를 판정 기준과 대조하세요.",
 "3": "잠금 1: 1820 + 가족끼리 수정한 일정과 통화 내용의 불일치. 잠금 2: 40550310 + 현재 위치는 확정 불가. 잠금 3: 실제 가족 요청과 불일치 / call·message·aunt 증거 / SCAM 번호 / 요구를 멈추고 확인된 가족 번호로 소통 후 신고.",
 "6": "실시간 확산 시뮬레이션은 하나의 고정 정답 순서가 없어요. 단계별 확산 조건·개입 수단과 결과 기준을 확인하세요.",
 "8": "대처유형 테스트는 정답·오답이 없어요. 응답별 유형 점수와 결과 설명을 확인하세요.",
 "9": "사건별 정답 인물과 공개 단서·해설을 확인하세요.",
 "10": "메모 1은 DATA의 memo1.answer 칸 수. 메모 2는 3칸 되돌리기 + 120000원. 메모 3은 01110 전구 + 14만 원. 판매자 표와 최종 정답은 DATA의 정답표를 확인하세요.",
 "11": "각 stages.msgs의 마지막 true/false가 교육용 정답이에요. VERIFIED는 별도 확인 근거예요. 단일 조건으로 실제 문자의 안전을 확정하지 않아요. 여러 필터 조합이 정답일 수 있어요.",
 "12": "DATA.stages.pic에서 #은 칠할 칸, .은 빈칸이에요. 그림 복원과 QR 안전성 판단은 별개예요.",
 "14": "1번 정상 확인: 실제 방문과 안내 내용이 일치. 2번 위조 확인: 실제 등기는 있지만 인증번호 요구를 기관이 부인. 3번 판단 보류: 전산 지연으로 조회 결과가 불충분.",
}
def show_answers():
    from admin_tools import OPEN
    if not st.session_state.get(OPEN):
        return
    st.subheader("📖 게임 정답·판정 기준")
    st.caption("고정 정답이 없는 대화·시뮬레이션·유형 테스트는 판정 기준을 보여 줘요. 아래 자료는 현재 배포 파일에서 읽으므로 수정 내용을 그대로 반영해요.")
    pages=Path(__file__).resolve().parent/"pages"
    choices=sorted((p for p in pages.glob("*.py") if p.name.split("_",1)[0] in GUIDES), key=lambda p:int(p.name.split("_",1)[0]))
    if not choices:
        st.info("게임 페이지 파일을 찾지 못했어요.");return
    picked=st.selectbox("게임 선택", choices, format_func=lambda p:p.stem.split("_",1)[1].replace("_"," "))
    st.info(GUIDES[picked.name.split("_",1)[0]])
    source=picked.read_text(encoding="utf-8")
    tree=ast.parse(source)
    values={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            try: values[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError,SyntaxError): pass
    _readable_answers(picked.name.split("_",1)[0], values)
    found=False
    for node in tree.body:
        if not isinstance(node,(ast.Assign,ast.AnnAssign)):
            continue
        targets=node.targets if isinstance(node,ast.Assign) else [node.target]
        names=[t.id for t in targets if isinstance(t,ast.Name)]
        if not names or any(n in {"HTML","CSS","SYSTEM_PROMPT","KEY"} for n in names):
            continue
        try:
            value=ast.literal_eval(node.value)
        except (ValueError,TypeError,SyntaxError):
            continue
        if names[0] in {"MOM","DAD","AUNT","SCAM"}:
            st.write(names[0]+": "+str(value))
        if not isinstance(value,(dict,list,tuple)) or not value:
            continue
        found=True
        with st.expander("문항·정답 자료: "+", ".join(names)):
            st.json(value,expanded=False)
    with st.expander("판정 코드 확인 (개발자용)"):
        # Source is local public game code, never Secrets or service-account credentials.
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(t in node.name.lower() for t in ("check","verdict","score","judge","lock_","report","ending")):
                st.code(ast.get_source_segment(source,node),language="python")
    if not found:
        st.caption("정적 문항표가 없는 게임이에요. 위 판정 기준과 판정 코드를 확인하세요.")

def _readable_answers(number, values):
    """정답을 개발자용 JSON 밖에서도 읽을 수 있게 표시합니다."""
    if number == "1":
        for i, event in enumerate(values.get("EVENTS", []), 1):
            with st.expander(f"{i}. {event.get('stage', event.get('sender', '상황'))}"):
                st.write("교육용 사건 판정: " + ("정상 연락" if event.get("real") else "사칭·사기 연락"))
                for key, label in [("route","확인 경로"),("result","확인 결과"),("together","함께 확인하는 답변"),("reason","판단 이유")]:
                    if event.get(key): st.write(label+": "+str(event[key]))
    elif number == "3":
        st.table([
            {"단계":"잠금 1","입력":"1820","판단":"가족끼리 수정한 일정과 통화 내용의 불일치"},
            {"단계":"잠금 2","입력":"40550310","판단":"현재 위치는 확정할 수 없음"},
            {"단계":"잠금 3","입력":str(values.get("SCAM","현재 코드의 SCAM 번호 확인")),"판단":"call·message·aunt 증거 / 실제 가족 요청과 불일치 / 요구 중단·독립 확인·신고"}
        ])
    elif number == "9":
        for case in values.get("CASES", []):
            st.markdown("**"+case.get("title","사건")+" · 정답: "+case["answer"]+"**")
            for clue in case.get("decisive",[]): st.write("• "+clue)
    elif number == "10":
        data=values.get("DATA",{})
        st.write("메모 1: 4칸 / 메모 2: 3칸 되돌리기와 120000원 / 메모 3: 전구 01110과 14만 원")
        st.write("최종 판매자: "+data.get("real",""))
        st.table([{"판매자":name,"연락 방식":v[0],"요구":v[1],"가격":v[2]} for name,v in data.get("solution",{}).items()])
    elif number == "11":
        for i,stage in enumerate(values.get("DATA",{}).get("stages",[])):
            with st.expander(stage["name"]+" · 문자별 정답"):
                proofs=values.get("VERIFIED",[[],[],[]])[i]
                st.table([{"문자":j+1,"보낸 사람":m[0],"교육용 정답":"차단 대상" if m[4] else "통과 대상","별도 확인":proofs[j] if j<len(proofs) else ""} for j,m in enumerate(stage["msgs"])])
    elif number == "12":
        for stage in values.get("DATA",{}).get("stages",[]):
            st.markdown("**"+stage["title"]+" 정답 그림**")
            st.code("\n".join(row.replace("#","■").replace(".","□") for row in stage["pic"]),language=None)
    elif number == "14":
        for i,case in enumerate(values.get("CASES",[]),1):
            st.markdown(f"**{i}. {case['answer']}**")
            st.write(case["reason"])
    elif number == "6":
        for stage in values.get("STAGES",[]):
            st.write({k:v for k,v in stage.items() if isinstance(v,(str,int,float))})
    elif number == "2":
        for name,scenario in values.get("SCENARIOS",{}).items():
            st.markdown("**"+name+"**")
            st.write(scenario.get("guide",""))
