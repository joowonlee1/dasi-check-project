"""관리자 인증 후에만 표시하는 정답·판정 기준. 페이지 코드를 실행하지 않고 정적 자료만 읽습니다."""
from pathlib import Path
import ast
import streamlit as st
from investigation_content import CASES as INVESTIGATIONS
from notice_inquiry import DATA as NOTICE
from filter_trials import HOLDOUT

GUIDES = {
 "1": "각 상황의 선택지별 결과·해설을 확인하세요. 결말은 선택과 신뢰도에 따라 달라져요.",
 "3": "각 잠금의 입력값과 선택할 문장을 아래에서 확인하세요.",
 "6": "실시간 확산 시뮬레이션은 하나의 고정 정답 순서가 없어요. 단계별 확산 조건·개입 수단과 결과 기준을 확인하세요.",
 "9": "사건별 정답 인물과 공개 단서·해설을 확인하세요.",
 "10": "거래 자료의 결론·필요한 증거와 판매자별 최종 정답을 확인하세요.",
 "11": "문자별 차단·통과 정답과 별도 확인 근거를 보여 줘요. 단일 조건으로 실제 문자의 안전을 확정하지 않아요. 여러 필터 조합이 정답일 수 있어요.",
 "12": "■는 칠할 칸, □는 빈칸이에요. 그림 복원과 QR 안전성 판단은 별개예요.",
 "14": "1번 정상 확인: 실제 방문과 안내 내용이 일치. 2번 위조 확인: 실제 등기는 있지만 인증번호 요구를 기관이 부인. 3번 판단 보류: 전산 지연으로 조회 결과가 불충분.",
}
def show_answers():
    from admin_tools import OPEN
    if not st.session_state.get(OPEN):
        return
    st.subheader("📖 게임 정답·판정 기준")
    st.caption("정답이 정해진 게임만 보여 줘요. (AI 모의대화·대처유형 테스트는 정답이 없어서 빼 두었어요.)")
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

def _readable_answers(number, values):
    """정답을 개발자용 JSON 밖에서도 읽을 수 있게 표시합니다."""
    if number == "1":
        for i, event in enumerate(values.get("EVENTS", []), 1):
            with st.container(border=True):
                st.markdown(f"### {i}. {event.get('stage', event.get('sender', '상황'))}")
                st.write("교육용 사건 판정: " + ("정상 연락" if event.get("real") else "사칭·사기 연락"))
                options = (values["NORMAL_OPTIONS"] + ["police"]) if event.get("final") else values["NORMAL_OPTIONS"]
                if event.get("real"):
                    st.success("정답 판정: " + values["APPROACHES"]["watch"]["label"])

                else:
                    st.success("끼어들기 정답 판정: " + " / ".join(values["APPROACHES"][k]["label"] for k in options if k != "watch"))

                for key, label in [("reason","판단 이유")]:
                    if event.get(key): st.write(label+": "+str(event[key]))
    elif number == "3":
        st.table([
            {"단계":"잠금 1","입력":"1820","판단":"가족끼리만 수정한 일정과 달리, 통화에서는 이전 공개 일정을 말했다."},
            {"단계":"잠금 2","입력":"40550310","판단":"사진은 과거 촬영본이고 일정은 계획이므로, 아직 확정할 수 없다."},
        ])
        st.markdown("**잠금 3 · 네 칸 모두 입력**")
        st.write("① 사건 판단: 연락 내용이 실제 가족의 요청과 일치하지 않는다.")
        st.write("② 핵심 증거 3개: " + " / ".join(values["EVIDENCE"][k]["title"] for k in ("call","message","aunt")))
        st.write("③ 차단하고 신고할 번호: " + values["SCAM"])
        st.write("④ 지금 할 행동: 요구를 멈추고 확인된 가족 번호로 소통한 뒤, 112에 신고한다.")
        st.caption("필요한 증거는 먼저 방 조사에서 ‘증거 보관함에 넣기’를 눌러야 선택할 수 있어요.")
        for key,label in [("MOM","엄마"),("AUNT","진짜 이모"),("DAD","아빠"),("SCAM","사칭 문자")]:
            st.write(label + ": " + values[key])
    elif number == "9":
        for case in values.get("CASES", []):
            st.markdown("**"+case.get("title","사건")+" · 정답: "+case["answer"]+"**")
            for clue in case.get("decisive",[]): st.write("• "+clue)
    elif number == "10":
        data=values.get("DATA",{})
        for case in INVESTIGATIONS[:3]:
            show_investigation_answer(case)
        st.write("최종 판매자: "+data.get("real",""))
        st.table([{"판매자":name,"연락 방식":v[0],"요구":v[1],"가격":v[2]} for name,v in data.get("solution",{}).items()])
    elif number == "11":
        for i,stage in enumerate(values.get("DATA",{}).get("stages",[])):
            with st.container(border=True):
                st.markdown("### "+stage["name"]+" · 문자별 정답")
                proofs=values.get("VERIFIED",[[],[],[]])[i]
                st.table([{"문자":j+1,"보낸 사람":m[0],"내용":m[2],"교육용 정답":"차단 대상" if m[4] else "통과 대상","별도 확인":proofs[j] if j<len(proofs) else ""} for j,m in enumerate(stage["msgs"])])
        st.caption("필터 조합은 여러 가지일 수 있어요. 3단계에는 같은 태그지만 실제 판정이 다른 문자가 있어 태그만으로 전부 구분할 수 없어요.")
        st.markdown("### 새 문자 시험까지 통과하는 규칙 예시")
        st.write("1단계: (링크 그리고 재촉) 또는 (링크 그리고 돈 요구)")
        st.write("2단계: (돈 요구 그리고 재촉) 또는 (모르는 번호 그리고 앱 설치) 또는 인증정보 요구")
        st.write("3단계: (링크 그리고 재촉) 또는 (돈 요구 그리고 재촉) 또는 인증정보 요구")
        st.caption("유일한 정답 조합은 아닙니다. 3단계의 서연·민준 문자는 같은 태그여서 규칙만으로 구별할 수 없어요. 두 문자를 골라 기존 연락처나 대면으로 별도 확인을 선택합니다.")
        for i,rows in enumerate(HOLDOUT,1):
            st.markdown(f"**{i}단계 새 문자 정답**")
            st.table([{"문자":m[2],"확인 결과":"사칭·사기" if m[4] else "정상"} for m in rows])
    elif number == "12":
        for stage in values.get("DATA",{}).get("stages",[]):
            st.markdown("**"+stage["title"]+" 정답 그림**")
            st.code("\n".join(row.replace("#","■").replace(".","□") for row in stage["pic"]),language=None)
        for case in INVESTIGATIONS[3:]:
            show_investigation_answer(case)
    elif number == "14":
        for i,case in enumerate(values.get("CASES",[]),1):
            st.markdown(f"**{i}. {case['answer']}**")
            st.write("확인 경로: " + values["ROUTES"][1])
            st.success("판단 근거: " + case["reason"])
            st.write("필요한 확인 기록: "+" / ".join(NOTICE["questions"][k] for k in NOTICE["required"][i-1]))
            st.write("다음 행동: "+NOTICE["actions"][i-1])
    elif number == "6":
        for i, stage in enumerate(values.get("STAGES",[]),1):
            st.markdown(f"**{i}. {stage['tactic']}**")
            st.write("확인된 사실: " + stage["truth"])
            for text, correct, reason in stage["options"]:
                if correct:
                    st.write("정정 문구 정답: " + text)
                    st.write("해설: " + reason)


def show_investigation_answer(case):
    with st.container(border=True):
        st.markdown("### "+case["title"])
        st.success(case["options"][case["answer"]])
        names={x[0]:x[1] for x in case["sources"]}
        st.write("선택할 근거: "+" / ".join(names[k] for k in case["proof"]))
        with st.expander("자세한 해설"):
            st.write(case["lesson"])
