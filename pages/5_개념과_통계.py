import streamlit as st


SOURCE_URL = "https://www.data.go.kr/data/15063815/fileData.do"
KISA_URL = "https://www.kisa.kr/1020601"

# 공공데이터포털의 경찰청 자료 설명에서 확인한 수치입니다.
# 임의로 생성한 예시 수치가 아닙니다.
STATISTICS = [
    {"유형": "기관사칭형", "발생 건수": 13323},
    {"유형": "대출사기형", "발생 건수": 10037},
]

CONCEPTS = {
    "가족·지인 사칭": (
        "가족이나 아는 사람인 것처럼 접근하는 방식입니다. "
        "이 앱에서는 익숙한 이름이나 개인적인 정보를 들었을 때 "
        "어떤 근거로 상대방을 믿는지 돌아봅니다."
    ),
    "발신번호 조작": (
        "전화 화면에 표시되는 발신번호를 속이는 것을 말합니다. "
        "화면 표시를 읽는 것과 상대의 신원을 별도로 확인하는 것은 "
        "다른 과정이라는 점을 학습합니다."
    ),
    "AI 음성 사칭": (
        "음성 합성·복제 기술을 타인을 사칭하는 데 악용하는 상황입니다. "
        "이 앱은 실제 음성을 분석하거나 딥페이크 여부를 판별하지 않습니다."
    ),
    "스미싱": (
        "문자메시지로 링크 접속이나 앱 설치 등을 유도해 "
        "정보 탈취 등의 피해를 일으키는 수법입니다."
    ),
    "심리적 압박": (
        "급하다는 말, 불이익에 대한 두려움, 비밀 유지 요구 등으로 "
        "확인할 시간을 줄이는 상황입니다. "
        "대화 연습에서는 이런 요구에 대응하는 말을 연습합니다."
    ),
}


st.title("📊 잠깐! · 개념과 통계")
st.write("체험에서 만난 수법을 이해하고 공식 자료를 살펴봐요.")

concept_tab, statistics_tab = st.tabs(["개념 알아보기", "공식 통계"])

with concept_tab:
    for name, explanation in CONCEPTS.items():
        with st.expander(name):
            st.write(explanation)

    st.subheader("체험에서 생각해 볼 세 가지")

    st.markdown(
        """
        1. **무엇 때문에 믿었나요?**  
           이름, 번호, 목소리, 개인적인 정보 중 어떤 단서였나요?

        2. **무엇을 직접 확인했나요?**  
           상대방의 설명 외에 별도로 확인한 사실이 있나요?

        3. **어떤 행동을 요구했나요?**  
           설치, 정보 전달, 링크 접속 같은 요구가 있었나요?
        """
    )

    st.link_button("KISA 스미싱 대응 안내 보기", KISA_URL)

with statistics_tab:
    st.subheader("2025년 보이스피싱 유형별 발생 건수")
    st.caption("집계 기간: 2025년 · 단위: 건 · 제공기관: 경찰청")

    first, second = st.columns(2)

    with first:
        st.metric("기관사칭형", "13,323건")

    with second:
        st.metric("대출사기형", "10,037건")

    st.bar_chart(
        {
            "유형": [row["유형"] for row in STATISTICS],
            "발생 건수": [row["발생 건수"] for row in STATISTICS],
        },
        x="유형",
        y="발생 건수",
        color="#0F766E",
        horizontal=True,
    )

    st.dataframe(
        STATISTICS,
        hide_index=True,
        use_container_width=True,
    )

    st.info(
        "이 자료는 기관사칭형과 대출사기형 보이스피싱 통계입니다. "
        "가족 사칭 또는 AI 음성 사칭만의 발생 건수를 뜻하지 않습니다."
    )

    st.markdown("**자료 정보**")
    st.write("자료명: 경찰청_보이스피싱 현황_20251231")
    st.write("원문에 표시된 수정일: 2026-01-21")
    st.write("이 앱에 사용할 자료를 확인한 날짜: 2026-09-22")
    st.write("원문 갱신 주기: 연간")

    st.link_button("공식 통계 원문 확인", SOURCE_URL)

    st.caption(
        "현재 화면은 출처 확인 당시 수치를 담은 고정 자료입니다. "
        "실시간 통계나 자동 갱신 기능은 아닙니다. "
        "새로운 발표 여부는 원문에서 확인할 수 있습니다."
    )

    csv_text = (
        "연도,유형,발생건수\n"
        "2025,기관사칭형,13323\n"
        "2025,대출사기형,10037\n"
    )

    st.download_button(
        "화면에 표시된 통계 내려받기",
        data=csv_text.encode("utf-8-sig"),
        file_name="jamkkan_statistics_2025.csv",
        mime="text/csv",
    )
