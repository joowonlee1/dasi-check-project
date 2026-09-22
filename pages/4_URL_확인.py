import streamlit as st

st.title("🔗 의심 URL 확인 도우미")
st.write("문자에 들어 있는 링크를 붙여 넣어 확인하는 공간입니다.")

# strip()은 입력 내용 양 끝의 불필요한 공백을 제거합니다.
url = st.text_input(
    "확인할 URL을 입력하세요.",
    placeholder="https://example.com",
).strip()

if st.button("확인하기"):
    if not url:
        st.warning("URL을 먼저 입력해 주세요.")
    else:
        st.info(
            "입력이 완료되었습니다. "
            "현재 버전에는 URL 분석 기능이 아직 연결되지 않았습니다."
        )

st.caption(
    "다음 버전에서는 링크에 접속하지 않고 주소의 특징을 분석합니다. "
    "주소 분석만으로 사이트의 안전성을 확정할 수는 없습니다."
)
