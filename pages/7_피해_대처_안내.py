"""대한민국 기준 피해 대처 안내. 개인정보 입력이나 신고 접수 기능은 없습니다."""
import streamlit as st
from mascot_ui import show_mascot

CHECKED = "2026-10-22"
SOURCES = {
    "금융 피해 대응 · 정부 정책브리핑": "https://www.korea.kr/news/policyNewsView.do?newsId=148925712",
    "스미싱 대응 · KISA 보안공지": "https://www.krcert.or.kr/kr/bbs/view.do?bbsId=B0000133&menuNo=205020&nttId=72049",
    "118 상담 안내 · KISA": "https://www.kisa.kr/118",
}
GUIDES = {
    "돈을 보냈어요": [
        "지금 다른 사람의 안전한 전화 등으로 112 또는 송금·입금 금융회사 고객센터에 피해를 알리고 지급정지를 요청하세요. 증거 정리 때문에 연락을 미루지 마세요.",
        "금융회사가 안내하는 피해구제 신청 절차와 필요한 서류를 확인하세요. 지급정지 요청만으로 환급이 보장되지는 않습니다.",
        "은행 앱 거래 내역의 이체 시각·금액·받는 계좌와 상대의 문자·대화·통화 기록을 보관해 경찰과 금융회사에 전달하세요.",
    ],
    "개인정보·인증번호를 알려줬어요": [
        "계좌·카드·금융 인증정보를 알려줬다면 해당 금융회사에 즉시 사고를 알리고 이용 제한·인증수단 재발급 등 필요한 조치를 상담하세요. 이미 돈이 빠져나갔다면 돈을 보낸 경우의 안내도 따르세요.",
        "비밀번호를 입력했다면 안전한 기기에서 직접 연 공식 서비스의 비밀번호를 바꾸고 다른 로그인 기기·세션과 추가 인증 설정을 확인하세요. 같은 비밀번호를 사용한 서비스도 확인하세요.",
        "신분증 등 개인정보가 노출됐다면 금융감독원 개인정보노출자 사고예방시스템 등록을 검토하세요. 휴대전화 명의도용이 걱정되면 통신사 또는 Msafer에서 가입 내역·가입 제한 방법을 확인하세요.",
    ],
    "의심스러운 앱을 설치했어요": [
        "의심 기기에서 금융 업무와 추가 입력을 멈추세요. 악성앱이 확인되면 비행기 모드로 전환하고 Wi-Fi도 끈 뒤, 다른 사람의 안전한 전화로 112에 신고하세요. 의심 기기로 건 전화가 가로채질 수 있습니다.",
        "KISA 118 또는 제조사 서비스센터에 점검·악성앱 제거 방법을 상담하세요. 설치 파일만 지웠다고 설치된 앱까지 제거됐다고 판단하지 마세요.",
        "해당 기기로 금융 서비스를 이용했다면 금융회사에 인증수단 폐기·재발급 등 후속 조치를 문의하세요. 초기화가 필요할 수 있으므로 증거 보관 방법과 데이터 손실 여부도 상담하세요.",
    ],
    "링크를 눌렀어요": [
        "열린 화면에서 추가 입력·다운로드·앱 설치·결제를 멈추고 닫으세요. 링크를 눌렀다는 사실만으로 피해나 안전 여부를 확정할 수 없습니다.",
        "앱을 설치했는지, 로그인·카드·인증정보를 입력했는지 확인하세요. 해당 사항이 있으면 위에서 관련 상황도 함께 선택하세요.",
        "의심 문자를 다시 열어 실험하지 말고 KISA 118에 상담하거나 공식 보호나라의 확인 서비스를 이용하세요. 모바일 결제가 의심되면 통신사에 결제 내역 확인과 피해 신고 방법을 문의하세요.",
    ],
    "무슨 일이 일어났는지 모르겠어요": [
        "상대의 요구를 잠시 멈추고 믿을 수 있는 가족·지인과 함께 상황을 정리하세요. 혼자 해결할 필요는 없습니다.",
        "거래 내역, 알려준 정보의 종류, 앱 설치 여부를 확인하세요. 이 페이지에는 실제 계좌번호·인증번호·신분증을 입력하지 마세요.",
        "범죄 피해나 송금 피해가 의심되면 112, 악성앱·스미싱 점검이 필요하면 KISA 118에 문의하세요. 다른 안전한 기기를 사용하는 것이 좋습니다.",
    ],
}


def checklist(selected):
    lines = ["잠깐! 피해 대처 안내", f"대한민국 기준 / 자료 확인일 {CHECKED}", ""]
    lines += ["긴급: 금전 피해는 112 또는 금융회사에 먼저 연락하세요.",
              "악성앱이 의심되면 다른 안전한 전화로 연락하세요.", ""]
    for name in GUIDES:
        if name in selected:
            lines.append(name)
            lines.extend(f"{i}. {text}" for i, text in enumerate(GUIDES[name], 1))
            lines.append("")
    lines += [f"{title}: {url}" for title, url in SOURCES.items()]
    return "\n".join(lines)


def main():
    st.title("🚨 피해가 의심될 때")
    st.error("돈을 보냈거나 범죄 피해가 진행 중이라면 112 또는 금융회사에 먼저 연락하세요.")
    st.warning("악성앱·원격제어가 의심되면 다른 안전한 전화로 연락하세요. 이 페이지는 신고를 대신 접수하지 않습니다.")
    st.write("**112** · 범죄 피해 신고 / **118** · KISA 해킹·스미싱 상담")
    st.caption("대한민국 기준. 상담 범위·시간은 아래 공식 안내에서 확인하세요.")
    show_mascot("phone", "당황스러워도 혼자 해결하지 않아도 괜찮아요.", width=90)
    st.subheader("지금 어떤 상황인가요?")
    selected = st.multiselect("해당하는 상황을 모두 선택하세요", list(GUIDES), placeholder="눌러서 상황을 골라 주세요")
    if not selected:
        st.info("상황을 선택하면 지금 할 일과 확인할 곳을 보여드려요. 선택 전에도 위 연락처로 도움을 요청할 수 있어요.")
    for name in GUIDES:
        if name in selected:
            with st.container(border=True):
                st.subheader(name)
                for i, text in enumerate(GUIDES[name], 1):
                    st.write(f"**{i}.** {text}")

    st.subheader("보관하면 도움이 되는 자료")
    st.write("상대의 번호·아이디, 문자와 대화, 거래 내역, 앱 이름, 발생 시각을 보관하세요. 신고를 늦추거나 의심 링크를 다시 실행하면서 자료를 모으지는 마세요.")
    st.caption("보관한 증거는 경찰·금융회사에 전달하고, 공개 게시하거나 이 웹앱에 올리지 마세요.")
    with st.expander("개인정보 노출·명의도용 확인 경로"):
        st.markdown("- [금융감독원 개인정보노출자 사고예방시스템](https://pd.fss.or.kr)")
        st.markdown("- [Msafer 명의도용방지서비스](https://www.msafer.or.kr)")
        st.caption("이 사이트들은 별도 외부 서비스입니다. 주소를 확인하고 안전한 기기에서 이용하세요.")
    if selected:
        st.download_button("선택한 대처 안내 내려받기", checklist(selected).encode("utf-8-sig"),
                           file_name="jamkkan_help.txt", mime="text/plain")
    st.subheader("공식 출처")
    for title, url in SOURCES.items():
        st.markdown(f"- [{title}]({url})")
    st.caption(f"자료 확인일: {CHECKED} · 자동 갱신 자료가 아닙니다. 개별 조치는 담당 기관 안내를 따르세요.")


if __name__ == "__main__":
    main()
