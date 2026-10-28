from play_ui import intro, bridge
from notice_inquiry import DATA as INQUIRY
"""안내서 3건의 주장과 별도 공식 확인 결과를 대조하는 교육용 가상 활동."""
import streamlit as st
import dotori_data as dd
from card_ui import show_result_card
from sound_effects import queue_effect
from mascot_ui import show_key_question

KEY = "notice_verify_v3"
CASES = [
 {"door":"101호", "claim":"오늘 14:25 등기 방문. 부재중이어서 내일 다시 방문합니다.",
  "looks":"종이가 구겨지고 테이프로 붙어 있어요.", "reference":"A-102",
  "official":"별도로 연 도토리 우체국 공식 조회에서 A-102의 수취 주소가 101호이고, 오늘 14:25 부재중 방문과 다음 날 재방문이 기록돼 있어요. 공식 고객센터도 이 안내 내용을 확인했어요.",
  "answer":"안내 내용 정상 확인",
  "reason":"수취 주소·방문 시각·후속 절차가 별도로 확인한 기록과 일치한다.",
  "options":["종이가 구겨졌지만 기관 로고가 있으므로 정상이다.","수취 주소·방문 시각·후속 절차가 별도로 확인한 기록과 일치한다.","실제 우편물이 하나라도 있으면 모든 추가 요구가 안전하다."],
  "lesson":"종이 상태만으로 위조라고 단정하지 않아요. 이 사례에서는 안내 내용까지 독립 확인했기 때문에 정상으로 판단했어요."},
 {"door":"102호", "claim":"등기가 도착했습니다. 재배달하려면 이 QR에서 계정 비밀번호와 문자 인증번호를 입력하세요.",
  "looks":"깨끗한 종이이며 흔적 없이 떨어져요. 실제 등기번호가 적혀 있어요.", "reference":"A-205",
  "official":"별도로 연 공식 조회에 A-205 등기는 실제로 있어요. 하지만 공식 고객센터는 해당 QR과 비밀번호·인증번호 입력 요구를 자신들이 보낸 것이 아니라고 확인했어요. 정식 재배달 절차도 따로 안내했어요.",
  "answer":"안내 내용 위조 확인",
  "reason":"실제 등기는 있지만, 기관이 이 안내의 추가 요구를 명시적으로 부인했다.",
  "options":["종이가 깨끗하고 접착 흔적이 없으므로 정상이다.","실제 등기는 있지만, 기관이 이 안내의 추가 요구를 명시적으로 부인했다.","등기번호가 조회되므로 QR의 목적지도 검증됐다."],
  "lesson":"실제 등기번호를 베껴 쓸 수도 있어요. 우편물 존재와 안내서의 추가 요구가 정당한지는 별도로 확인해야 해요."},
 {"door":"103호", "claim":"오늘 등기 방문. 부재중이므로 연락 바랍니다.",
  "looks":"접착 흔적이 남아 있어요. 사진에서는 방문 시각 일부가 흐려요.", "reference":"A-309",
  "official":"공식 조회 시스템이 점검 중이라 기록을 확인할 수 없어요. 별도로 연락한 공식 고객센터도 지금은 방문 여부를 확정하지 못했고, 복구 후 재확인하거나 창구에서 확인하도록 안내했어요.",
  "answer":"판단 보류",
  "reason":"조회 실패는 위조 증거가 아니며, 현재 확인된 정보만으로는 결론을 낼 수 없다.",
  "options":["조회되지 않으니 무조건 위조다.","접착 흔적이 있으므로 위조가 확정됐다.","조회 실패는 위조 증거가 아니며, 현재 확인된 정보만으로는 결론을 낼 수 없다."],
  "lesson":"모르는 것을 안다고 단정하지 않는 것도 판단이에요. 안내서 속 경로로 이동하지 말고 독립적인 공식 경로에서 재확인해요."}
]
ROUTES = ["안내서에 적힌 번호나 QR로 확인", "안내서와 별도로 찾은 공식 홈페이지·고객센터에서 확인"]
VERDICTS = ["안내 내용 정상 확인","안내 내용 위조 확인","판단 보류"]
def fresh():
    return {"i":0,"checks":{},"answers":{},"recorded":False,"done":False,"attempts":{}}
S=st.session_state.setdefault(KEY,fresh())
with intro("14", suffix=""):
    st.title("📬 가짜 안내서 감별소")
    show_key_question("안내서의 주장과 **별도로 확인한 기록**을 대조해요. 근거가 부족하면 **판단을 보류**할 수 있어요.","📬")
    st.caption("모든 기관·등기번호·응답은 교육용 가상 자료예요. 실제 웹사이트 접속이나 전화 연결은 하지 않아요.")

def _quit_notice():
    st.session_state[KEY]=fresh()

if not S["done"]:
    i=S["i"]; case=CASES[i]
    # 감별 중에도 언제든 그만두고 처음(1번 안내서)으로 돌아갈 수 있어요.
    st.button("⏹️ 그만하고 처음 화면으로", on_click=_quit_notice, key="nv_quit",
              help="지금 감별을 멈추고 처음으로 돌아가요. 지금까지의 판단은 지워져요.")
    st.progress(i/len(CASES))
    st.subheader(f"{i+1}/3 · 다람쥐아파트 {case['door']}")
    with st.container(border=True):
        st.markdown("**안내서에 적힌 내용**")
        st.write(case["claim"])
        st.caption(f"참조번호: {case['reference']} · 겉모습: {case['looks']}")

    st.info("안내서의 주장을 검증할 질문을 직접 고르세요. 등기가 있다는 사실과 추가 요구의 정당성은 다른 항목이에요.")
    checked=S["checks"].setdefault(i,{})
    route=st.radio("확인 경로",ROUTES,index=None,key=f"nv_route_{i}")
    question=st.selectbox("어떤 사실을 확인할까요?",list(INQUIRY["questions"]),format_func=INQUIRY["questions"].get,key=f"nv_question_{i}")
    if st.button("자료 확인",disabled=route is None,key=f"nv_get_{i}"):
        if question=="procedure" and "delivery" not in checked:
            st.warning("먼저 등기번호·주소·방문 시각을 확인해야 해당 거래의 절차를 물을 수 있어요.")
        elif question in ("surface","printed"):
            checked[question]=INQUIRY["responses"][i][question]
        elif route==ROUTES[1]:
            checked[question]=INQUIRY["responses"][i][question]
            queue_effect("clue")
        else:
            st.warning("안내서에 적힌 경로에서는 안내서 자체를 별도로 검증할 수 없어요. 공식 경로를 찾아 같은 질문을 확인하세요.")
    if checked:
        st.markdown("#### 내가 모은 확인 기록")
        for q,text in checked.items():
            with st.container(border=True):
                st.markdown("**"+INQUIRY["questions"][q]+"**")
                st.write(text)
    with st.form(f"nv_answer_{i}"):
        verdict=st.radio("현재 근거로 내릴 수 있는 판단",VERDICTS,index=None)
        reason=st.radio("판단 이유",case["options"],index=None)
        evidence=st.multiselect("판단을 직접 뒷받침하는 확인 기록",list(checked),format_func=INQUIRY["questions"].get,placeholder="먼저 필요한 자료를 확인하세요")
        action=st.radio("다음 행동",INQUIRY["actions"],index=None)
        submitted=st.form_submit_button("근거를 연결해 판단 제출",disabled=i in S["answers"])
    if submitted:
        if verdict is None or reason is None or action is None or not evidence:
            st.warning("판단·이유·근거·다음 행동을 모두 선택하세요.")
        else:
            S["attempts"][i]=S["attempts"].get(i,0)+1
            needed=set(INQUIRY["required"][i])
            ok=(verdict==case["answer"] and reason==case["reason"] and set(evidence)==needed and needed.issubset(checked) and action==INQUIRY["actions"][i])
            if ok:
                S["answers"][i]={"ok":True,"first":S["attempts"][i]==1}
                queue_effect("correct")
                st.rerun()
            else:
                queue_effect("notice")
                st.warning("아직 자료와 결론이 충분히 연결되지 않았어요. 같은 번호·주소·시각인지, 조회가 완료됐는지, 추가 요구까지 확인했는지 다시 살펴보세요.")
    if i in S["answers"]:
        st.success("근거 연결 완료")
        st.write(case["lesson"])
        st.write("판단 근거: "+case["reason"])
        if st.button("다음 안내서" if i<2 else "결과 보기",type="primary"):
            if i<2:S["i"]+=1
            else:S["done"]=True
            st.rerun()
else:
    score=sum(a.get("first",False) for a in S["answers"].values())
    if not S["recorded"]:
        stats_ok=dd.record("notice",{"v3_plays":1,"v3_perfect":int(score==3),
                      **{f"v3_h{i}_ok":int(S["answers"][i].get("first",False)) for i in range(3)}})
        S["hall"]=dd.save_hall("notice",{"score":score,"total":3,"probes":sum(len(v) for v in S["checks"].values()),"version":3},
            lambda old,new: new["score"]/new["total"]>old.get("score",0)/max(old.get("total",5),1))
        S["recorded"]=True
        dd.note_mine("notice",f"조사 완료 3/3 · 첫 제출 정확도 {score}/3")
        if not stats_ok:
            st.warning("활동 결과의 통계 저장에 실패했어요. 화면의 결과는 확인할 수 있어요.")
    dd.stamp("14")
    st.subheader(f"조사 완료 3/3 · 첫 제출에서 맞힌 사례 {score}/3")
    dd.show_hall_note(S.get("hall"))
    for case in CASES:
        with st.expander(f"{case['door']} · {case['answer']}",expanded=True):
            st.write(case["lesson"])
    st.info("현실에서는 안내서 속 연락처·QR 대신 별도로 확인한 공식 경로를 이용하세요. 조회가 안 되는 이유를 확인하고, 확인 전에는 안내서가 요구하는 결제나 정보 전달을 보류하세요.")
    me=dd.citizen()
    show_result_card({"color":"#9A3412","place":"다람쥐아파트 관리사무소","game":"가짜 안내서 감별소","emoji":"📬",
        "title":"독립 확인 완료","subtitle":f"첫 제출 정확도 {score}/3",
        "stats":[("첫 제출 정확도",f"{score}/3"),("사례 수","3")],
        "sections":[("확인 습관",["겉모습으로 단정하지 않기","우편물 존재와 추가 요구를 구분하기","근거가 부족하면 판단 보류"])],
        "nickname":me["nickname"] if me else "","mascot":"trophy" if score==3 else "retry"},
        "jamkkan_notice_card.png")
    if st.button("🔄 다른 방법으로 다시 도전"):
        st.session_state[KEY]=fresh()
        for k in list(st.session_state):
            if k.startswith(("nv_route_","nv_question_")): del st.session_state[k]
        st.rerun()
