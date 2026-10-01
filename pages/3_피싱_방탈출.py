import re
import time

import streamlit as st

from firebase_support import (
    ConnectionProblem,
    explain,
    result_panel,
    show_ranking,
    sign_in,
    user,
)


# 모든 인물, 기록, 연락 결과는 교육용 가상 자료입니다.
EVIDENCE = {
    "call": {
        "title": "E01 · 09:10 통화 기록",
        "body": (
            "화면 표시: 엄마\n\n"
            "상대의 말: “민서야. 나 엄마야. 우리 강아지 이름이 "
            "보리인 것도 알잖아. 오늘 10시에 도서관 가기로 했지? "
            "나 지금 집에 혼자 있는데 급한 일이 생겼어. "
            "다른 가족에게 연락하지 말고 내가 보내는 안내부터 봐.”"
        ),
    },
    "message": {
        "title": "E02 · 09:12 후속 문자",
        "body": (
            "“아까 전화한 엄마야. 확인은 아래 새 연락처로만 해. "
            "거기서 안내하는 앱을 설치하면 돼.”\n\n"
            "[상대가 새로 알려준 연락처]\n"
            "[가상의 설치 안내]\n\n"
            "실제 연락이나 설치는 실행되지 않습니다."
        ),
    },
    "sns_pet": {
        "title": "E03 · 공개 SNS 사진 설명",
        "body": (
            "공개 범위: 전체 공개\n\n"
            "게시물: “민서와 보리의 산책! 보리가 가족이 된 지 3년.”\n\n"
            "작성 시각: 사건 전날 18:00"
        ),
    },
    "sns_plan": {
        "title": "E04 · 공개 SNS 일정",
        "body": (
            "공개 범위: 전체 공개\n\n"
            "게시물: “내일 오전 10시, 민서랑 도서관에 가기로!”\n\n"
            "작성 시각: 사건 전날 20:00\n"
            "수정 기록: 없음"
        ),
    },
    "calendar": {
        "title": "E05 · 가족 달력 수정 기록",
        "body": (
            "오늘 08:55 일정 수정\n\n"
            "수정 전: 10:00 도서관\n"
            "수정 후: 10:30 과학관\n\n"
            "공유 범위: 가족만\n"
            "일정은 계획이며 실제 방문 여부를 증명하지 않습니다."
        ),
    },
    "photo": {
        "title": "E06 · 사진 액자 원본 정보",
        "body": (
            "사진 내용: 엄마가 집에서 보리와 함께 있는 모습\n\n"
            "원본 촬영: 사건 전날 19:40\n"
            "액자로 전송: 오늘 09:03\n\n"
            "액자에는 전송 시간이 크게 표시되어 있습니다."
        ),
    },
    "notice": {
        "title": "E07 · 도서관 알림",
        "body": (
            "오늘 09:00 자동 알림\n\n"
            "“대출 도서의 반납 예정일은 내일입니다. "
            "대출 내역은 평소 이용하시는 도서관 앱에서 확인하세요.”\n\n"
            "링크·결제·앱 설치 요청 없음"
        ),
    },
    "memo": {
        "title": "E08 · 가족의 확인 약속",
        "body": (
            "급한 연락일수록 받은 연락 속 새 번호를 확인 경로로 삼지 않기.\n\n"
            "연락이 안 되면 바로 결론 내리지 말고, "
            "평소 알고 있던 다른 가족에게 확인하기.\n\n"
            "연락처 목록에는 기존에 저장된 엄마와 이모가 있습니다."
        ),
    },
    "no_answer": {
        "title": "E09 · 저장된 엄마 연락처 확인",
        "body": (
            "09:15 · 응답 없음\n\n"
            "전화가 연결되지 않았습니다. "
            "응답이 없는 이유는 확인되지 않았습니다."
        ),
    },
    "new_contact": {
        "title": "E10 · 문자 속 새 연락처의 답변",
        "body": (
            "“맞습니다. 저희가 담당자입니다. 안내에 따라 주세요.”\n\n"
            "이 연락처는 최초 통화 상대가 제공했습니다. "
            "상대의 신원을 별도로 확인한 기록은 없습니다."
        ),
    },
    "aunt": {
        "title": "E11 · 기존에 저장된 이모와의 확인",
        "body": (
            "09:18 · 게임 속 독립 확인 결과\n\n"
            "평소 저장된 이모 연락처로 연결됐습니다.\n"
            "이모가 엄마와 함께 있는 상태에서 직접 확인했습니다.\n\n"
            "엄마: “09:10에 전화한 적 없어. "
            "앱을 설치해 달라고 보낸 문자도 내가 보낸 게 아니야.”\n\n"
            "이 게임에서는 이 확인 결과를 검증된 사실로 제공합니다."
        ),
    },
}

HINTS = {
    1: [
        "상대가 아는 정보의 출처를 찾아보세요.",
        "공개된 정보와 가족에게만 공유된 수정 기록을 비교해 보세요.",
        (
            "이름·반려견은 E03, 도서관 계획은 E04에서 찾을 수 있어요. "
            "공개 정보만으로 상대 신원을 확정할 수는 없어요."
        ),
    ],
    2: [
        "사진이 도착한 시간과 찍힌 시간은 같을까요?",
        "사진 원본 날짜까지 살펴본 뒤 오늘 기록들을 배열해 보세요.",
        (
            "원본 촬영 → 일정 수정 → 액자 전송 → 통화 순서예요. "
            "하지만 현재 위치는 아직 확인되지 않았어요."
        ),
    ],
    3: [
        "확인 경로가 최초 통화 상대에게서 나온 것은 아닌지 살펴보세요.",
        "엄마의 무응답과 새 연락처의 동의는 독립적인 확인이 아니에요.",
        "기존 이모 연락처로 확인한 E11을 통화 E01, 문자 E02와 연결하세요.",
    ],
}


def fresh_game(ranked=False):
    """게임을 초기화하고, 선택한 참여 방식을 연결합니다."""
    for key in list(st.session_state):
        if key.startswith("escape_"):
            del st.session_state[key]

    account = user()

    st.session_state["escape_game"] = {
        "started": time.time(),
        "evidence": [],
        "unlocked": 0,
        "mistakes": 0,
        "hints": {1: 0, 2: 0, 3: 0},
        "place": "📱 휴대전화",
        "finished": None,
        "rank_uid": account["uid"] if ranked and account else None,
        "rank_nickname": (
            account["nickname"] if ranked and account else None
        ),
        "rank_status": None,
    }


def save_evidence(evidence_id):
    if evidence_id not in game["evidence"]:
        game["evidence"].append(evidence_id)


def evidence_card(evidence_id):
    item = EVIDENCE[evidence_id]

    with st.container(border=True):
        st.markdown(f"**{item['title']}**")
        st.write(item["body"])

        if evidence_id in game["evidence"]:
            st.caption("✓ 증거 보관함에 저장됨")

        elif st.button(
            "증거 보관함에 넣기",
            key=f"escape_collect_{evidence_id}",
        ):
            save_evidence(evidence_id)
            st.rerun()


def evidence_name(evidence_id):
    return EVIDENCE[evidence_id]["title"]


def wrong(message):
    game["mistakes"] += 1
    st.warning(message)


def hint_panel(stage):
    with st.expander("💡 막혔을 때 힌트"):
        used = game["hints"][stage]

        if used < len(HINTS[stage]):
            if st.button(
                "힌트 하나 더 보기",
                key=f"escape_hint_{stage}",
            ):
                game["hints"][stage] += 1
                st.rerun()

        for text in HINTS[stage][:game["hints"][stage]]:
            st.write(text)


def lock_one():
    st.subheader("🔒 잠금 1 · 상대는 어떻게 알고 있을까?")
    st.write("통화 속 정보 두 개를, 확인 가능한 공개 출처와 연결하세요.")

    required = {"call", "sns_pet", "sns_plan"}

    if not required.issubset(set(game["evidence"])):
        st.info("아직 연결할 자료가 부족합니다. 방을 더 조사해 보세요.")
        return

    options = [None] + game["evidence"]

    def label(value):
        return "선택하세요" if value is None else evidence_name(value)

    with st.form("escape_source_form"):
        name_source = st.selectbox(
            "‘민서’와 ‘보리’를 알 수 있는 공개 자료",
            options,
            format_func=label,
        )

        plan_source = st.selectbox(
            "‘10시 도서관 계획’을 알 수 있는 공개 자료",
            options,
            format_func=label,
        )

        conclusion = st.radio(
            "이 연결로 말할 수 있는 것은?",
            [
                "이 정보를 알고 있으므로 엄마가 확실하다.",
                "공개 정보로도 알 수 있어 신원 확인 근거로 충분하지 않다.",
                "공개 정보와 같으므로 사칭이 확정된다.",
            ],
            index=None,
        )

        submitted = st.form_submit_button("서랍 잠금 해제")

    if submitted:
        if (
            name_source is None
            or plan_source is None
            or conclusion is None
        ):
            st.warning("두 자료와 판단을 모두 선택하세요.")

        elif (
            name_source == "sns_pet"
            and plan_source == "sns_plan"
            and conclusion.startswith("공개 정보로도")
        ):
            game["unlocked"] = 1
            st.rerun()

        else:
            wrong(
                "정보가 맞는다는 사실과 상대의 신원이 확인됐다는 판단을 "
                "구분해 보세요."
            )

    hint_panel(1)


def lock_two():
    st.subheader("🔒 잠금 2 · 뒤섞인 시간")
    st.write(
        "다음 사건을 실제 발생한 순서대로 배열하세요. "
        "날짜도 확인해야 합니다."
    )

    required = {"calendar", "photo", "call"}

    if not required.issubset(set(game["evidence"])):
        st.info("달력, 사진, 통화 자료를 보관함에 모아 주세요.")
        return

    events = [
        "통화가 걸려 옴",
        "사진이 액자로 전송됨",
        "사진 원본이 촬영됨",
        "가족 일정이 수정됨",
    ]

    with st.form("escape_time_form"):
        order = [
            st.selectbox(
                f"{number + 1}번째 사건",
                [None] + events,
                format_func=lambda value: value or "선택하세요",
                key=f"escape_order_{number}",
            )
            for number in range(4)
        ]

        location = st.radio(
            "현재 자료만으로 엄마의 09:10 위치를 알 수 있을까?",
            [
                "사진이 있으므로 집에 있다.",
                "과학관 일정이 있으므로 과학관에 있다.",
                "사진은 과거이고 일정은 계획이므로 아직 확정할 수 없다.",
            ],
            index=None,
        )

        submitted = st.form_submit_button("확인 장치 잠금 해제")

    if submitted:
        if None in order or location is None:
            st.warning("모든 순서와 판단을 선택하세요.")

        elif len(set(order)) != 4:
            st.warning("같은 사건을 중복해서 배치할 수 없습니다.")

        elif (
            order
            == [
                "사진 원본이 촬영됨",
                "가족 일정이 수정됨",
                "사진이 액자로 전송됨",
                "통화가 걸려 옴",
            ]
            and location.startswith("사진은 과거이고")
        ):
            game["unlocked"] = 2
            st.rerun()

        else:
            wrong(
                "사진의 촬영·전송 시간을 구분하고, "
                "계획이 실제 위치를 증명하는지 살펴보세요."
            )

    hint_panel(2)


def lock_three():
    st.subheader("🔒 잠금 3 · 출입문의 사건 보고서")

    if "aunt" not in game["evidence"]:
        st.info(
            "상대의 주장을 독립적으로 확인한 결과가 필요합니다. "
            "서랍의 확인 장치를 사용하세요."
        )
        hint_panel(3)
        return

    with st.form("escape_final_form"):
        conclusion = st.radio(
            "확인 결과에 따른 사건 판단",
            [
                "연락 내용이 실제 가족의 요청과 불일치한다.",
                "엄마가 전화를 받지 않았으므로 위험에 처했다.",
                "표시된 번호가 같으므로 정상 연락이다.",
            ],
            index=None,
        )

        proof = st.multiselect(
            "최초 요청과 독립 확인 결과를 대조할 핵심 증거 3개",
            game["evidence"],
            format_func=evidence_name,
        )

        action = st.radio(
            "다음 행동",
            [
                "상대가 알려준 앱을 설치해 확인한다.",
                "요구 이행을 멈추고 확인된 가족 연락 경로로 소통한다.",
                "문자 속 새 담당자가 맞다고 했으니 따른다.",
            ],
            index=None,
        )

        submitted = st.form_submit_button(
            "최종 잠금 해제",
            type="primary",
        )

    if submitted:
        if conclusion is None or action is None or len(proof) != 3:
            st.warning(
                "판단·행동을 고르고 핵심 증거를 정확히 3개 선택하세요."
            )

        elif (
            conclusion.startswith("연락 내용이")
            and set(proof) == {"call", "message", "aunt"}
            and action.startswith("요구 이행을")
        ):
            game["unlocked"] = 3
            game["finished"] = time.time()
            st.rerun()

        else:
            wrong(
                "최초 통화와 후속 문자에서 받은 요청을, "
                "독립 확인 결과와 직접 대조해 보세요."
            )

    hint_panel(3)


def show_drawer():
    if game["unlocked"] < 1:
        st.warning(
            "서랍이 잠겨 있습니다. "
            "‘잠금 해제’ 탭에서 첫 퍼즐을 해결하세요."
        )
        return

    evidence_card("memo")

    if game["unlocked"] < 2:
        st.info("확인 장치는 두 번째 잠금을 풀면 사용할 수 있습니다.")
        return

    st.subheader("📞 확인 장치")
    st.caption("모든 연락 결과는 게임 안의 가상 기록입니다.")

    routes = [
        ("저장된 엄마 연락처로 확인", "no_answer"),
        ("문자 속 새 연락처로 확인", "new_contact"),
        ("기존에 저장된 이모 연락처로 확인", "aunt"),
    ]

    for title, evidence_id in routes:
        if st.button(
            title,
            key=f"escape_contact_{evidence_id}",
        ):
            save_evidence(evidence_id)
            st.rerun()

        if evidence_id in game["evidence"]:
            with st.expander(
                EVIDENCE[evidence_id]["title"],
                expanded=True,
            ):
                st.write(EVIDENCE[evidence_id]["body"])


def show_room():
    st.write(
        "물건을 눌러 조사하고 필요한 자료를 증거 보관함에 넣으세요."
    )

    places = [
        "📱 휴대전화",
        "💻 노트북",
        "📅 달력",
        "🖼️ 사진 액자",
        "🗄️ 잠긴 서랍",
        "🚪 출입문",
    ]

    for start in (0, 3):
        columns = st.columns(3)

        for column, place in zip(columns, places[start:start + 3]):
            with column:
                if st.button(
                    place,
                    use_container_width=True,
                ):
                    game["place"] = place
                    st.rerun()

    st.divider()

    place = game["place"]
    st.subheader(place)

    if place == "📱 휴대전화":
        for evidence_id in ("call", "message", "notice"):
            evidence_card(evidence_id)

    elif place == "💻 노트북":
        evidence_card("sns_pet")
        evidence_card("sns_plan")

    elif place == "📅 달력":
        evidence_card("calendar")

    elif place == "🖼️ 사진 액자":
        evidence_card("photo")

    elif place == "🗄️ 잠긴 서랍":
        show_drawer()

    else:
        st.write("출입문에는 세 개의 잠금이 있습니다.")
        st.write("공개 정보의 출처 → 시간의 의미 → 독립 확인")
        st.info("‘잠금 해제’ 탭에서 현재 퍼즐에 도전하세요.")


def show_inventory():
    if not game["evidence"]:
        st.info("아직 수집한 증거가 없습니다.")
        return

    for evidence_id in game["evidence"]:
        with st.expander(evidence_name(evidence_id)):
            st.write(EVIDENCE[evidence_id]["body"])

    st.caption(
        "모든 자료가 결정적 증거인 것은 아닙니다. "
        "시각·출처·확인 경로를 비교하세요."
    )


def show_ending():
    seconds = max(
        0,
        int(game["finished"] - game["started"]),
    )

    minutes, remaining = divmod(seconds, 60)
    hint_count = sum(game["hints"].values())

    st.success("🚪 잠금 해제! 사건의 확인 경로를 완성했습니다.")
    st.subheader("엔딩 · 번호보다 근거")

    st.write(
        "상대는 공개된 정보를 알고 있었지만, "
        "그것만으로는 신원을 확인할 수 없었습니다. "
        "과거 사진과 일정도 현재 위치를 확정하지 못했습니다. "
        "마지막에 별도 연락 경로로 최초 요청을 대조하면서 사건을 해결했습니다."
    )

    first, second, third = st.columns(3)

    first.metric(
        "경과 시간",
        f"{minutes}분 {remaining}초",
    )
    second.metric(
        "힌트 사용",
        f"{hint_count}회",
    )
    third.metric(
        "퍼즐 재검토",
        f"{game['mistakes']}회",
    )

    st.caption(
        "시간은 페이지를 떠난 동안도 포함됩니다. "
        "빠르기나 실패 횟수로 능력을 평가하지 않습니다."
    )

    report = (
        "잠깐! 피싱 방탈출 — 엄마의 번호, 두 개의 진실\n\n"
        "결과: 세 개의 잠금 해제\n"
        f"경과 시간: {minutes}분 {remaining}초\n"
        f"힌트 사용: {hint_count}회\n"
        f"퍼즐 재검토: {game['mistakes']}회\n\n"
        "1. 공개된 개인 정보를 아는 것만으로 신원을 확인할 수 없다.\n"
        "2. 사진의 촬영 시간과 공유 시간을 구분해야 한다.\n"
        "3. 계획과 무응답만으로 실제 상황을 단정할 수 없다.\n"
        "4. 최초 상대와 독립된 경로에서 요청을 확인했다.\n\n"
        "교육용 가상 사건의 결과이며 실제 신원 확인을 보장하지 않는다."
    )

    result_panel(game)

    st.download_button(
        "탈출 기록 내려받기",
        data=report.encode("utf-8-sig"),
        file_name="jamkkan_escape_report.txt",
        mime="text/plain",
    )


def show_game_guide():
    with st.expander(
        "📖 처음 오셨나요? 게임 방법 보기",
        expanded="escape_game" not in st.session_state,
    ):
        st.markdown("### 당신은 이 연락의 진실을 확인할 조사자입니다")

        st.write(
            "휴대전화에는 ‘엄마’라는 이름이 뜹니다. "
            "상대는 나에 대해 잘 알고 있지만, "
            "다른 가족에게 연락하지 말라고 해요. "
            "방 안에 남은 기록을 비교하고, 무엇을 믿을 수 있는지 판단해 "
            "출입문의 세 잠금을 풀어 보세요."
        )

        st.markdown(
            "**이 게임은 글을 읽고 증거를 연결하는 추리형 방탈출이에요.** "
            "화면 속 장소 버튼을 눌러 조사하고, 선택한 근거로 퍼즐을 풉니다."
        )

        st.markdown("### 이렇게 진행해요")

        st.markdown(
            """
1. **방 조사** — 휴대전화·노트북·달력 등 장소 버튼을 눌러 자료를 읽어요.
2. **증거 수집** — 자료 아래 ‘증거 보관함에 넣기’를 눌러요. 읽기만 하면 수집되지 않아요.
3. **증거 비교** — ‘증거 보관함’ 탭에서 모은 자료의 시각과 출처를 비교해요.
4. **잠금 해제** — ‘잠금 해제’ 탭에서 자료와 판단을 선택하고 제출해요.
5. **다시 조사** — 잠금을 풀면 새로 조사할 수 있는 곳이 생겨요. ‘방 조사’로 돌아가요.
6. **탈출 완료** — 마지막 잠금까지 풀면 결과와 배운 점을 확인하고 기록을 내려받아요.
"""
        )

        st.markdown("### 막히면 이렇게 해 보세요")

        st.write(
            "‘자료가 부족하다’고 나오면 다른 장소를 조사하고 "
            "증거를 보관함에 넣어 보세요. "
            "잠긴 곳은 퍼즐을 해결한 뒤 다시 방문하세요. "
            "필요한 자료를 모았는데도 어렵다면 "
            "‘막혔을 때 힌트’를 열어 단계별 도움을 받을 수 있어요."
        )

        st.caption(
            "힌트 버튼을 누를 때마다 사용 횟수가 올라가요. "
            "답을 완성해 제출했지만 틀렸을 때는 "
            "‘퍼즐 재검토’ 횟수가 올라가며 다시 도전할 수 있어요."
        )

        st.markdown("### 연습할까요, 기록을 공유할까요?")

        st.markdown(
            """
- **혼자 연습:** 로그인 없이 시작하고 탈출 후 결과 파일을 받을 수 있어요.
- **랭킹 참여:** 이 화면에서 닉네임과 공개 동의를 입력하고 시작하세요.
- **이미 게임 중이라면:** 현재 게임 초기화에 동의한 뒤 새 게임을 시작할 수 있어요.
"""
        )

        st.info(
            "시간 제한은 없어요. 화면을 떠난 시간도 경과 시간에 포함돼요. "
            "새로고침하거나 접속을 종료하면 진행 중인 게임이 사라질 수 있으니, "
            "완료 후 결과를 다운로드해 주세요."
        )

        st.caption(
            "랭킹은 힌트가 적은 순, 재검토가 적은 순이며 "
            "같으면 공동 순위예요. 시간은 순위에 반영하지 않아요."
        )


def go_to(section):
    """다음 실행에서 방탈출 내부 메뉴를 변경합니다."""
    st.session_state["room_next_section"] = section
    st.rerun()


def start_game(ranked):
    fresh_game(ranked=ranked)
    go_to("🗝️ 게임 진행")


def show_entry():
    show_game_guide()

    st.subheader("어떻게 참여할까요?")

    existing = st.session_state.get("escape_game")
    replace_ok = True

    if existing:
        st.info(
            "진행 중이거나 완료한 게임이 있어요. "
            "‘게임 진행’ 메뉴에서 이어서 확인할 수 있어요."
        )

        if st.button("현재 게임으로 돌아가기"):
            go_to("🗝️ 게임 진행")

        replace_ok = st.checkbox(
            "새 게임을 시작하면 현재 진행과 미저장 결과가 "
            "초기화되는 것에 동의합니다."
        )

    with st.container(border=True):
        st.markdown("### 🌱 연습으로 시작")

        st.write(
            "로그인 없이 퍼즐을 풀고 결과를 다운로드해요. "
            "이미 입장한 상태여도 이 버튼으로 시작하면 공개 저장하지 않아요."
        )

        if st.button(
            "연습으로 시작",
            disabled=not replace_ok,
        ):
            start_game(False)

    with st.container(border=True):
        st.markdown("### 🏆 닉네임으로 입장하고 시작")

        st.write(
            "입장과 게임 시작을 한 번에 진행해요. "
            "탈출 완료 시 닉네임과 결과를 공동 랭킹에 자동 저장합니다."
        )

        st.caption(
            "닉네임·힌트·재검토 횟수·경과 시간·완료 여부·등록 시각이 공개돼요. "
            "같은 익명 계정의 첫 저장 결과를 유지하며 "
            "재도전으로 덮어쓰지 않아요."
        )

        st.info(
            "익명 계정 연결은 현재 접속 동안 유지됩니다. "
            "새로고침·접속 종료 후에는 이전 계정을 복구하지 못할 수 있어요. "
            "저장된 공개 기록은 남으며, 연결이 유지되는 동안 "
            "‘탈출 랭킹’에서 내 기록을 삭제할 수 있어요."
        )

        account = user()

        with st.form("room_join_start"):
            nickname = st.text_input(
                "닉네임 (한글·영문·숫자·밑줄 2~12자)",
                value=account["nickname"] if account else "",
                max_chars=12,
                disabled=bool(account),
            )

            consent = st.checkbox(
                "닉네임과 탈출 결과의 공개에 동의합니다."
            )

            submitted = st.form_submit_button(
                (
                    "현재 닉네임으로 랭킹 참여 시작"
                    if account
                    else "닉네임으로 입장하고 시작"
                ),
                type="primary",
                disabled=not replace_ok,
            )

        if submitted:
            nickname = nickname.strip()

            if not re.fullmatch(
                r"[가-힣a-zA-Z0-9_]{2,12}",
                nickname,
            ):
                st.warning(
                    "닉네임을 형식에 맞게 입력해 주세요. "
                    "실명은 피해주세요."
                )

            elif not consent:
                st.warning(
                    "공개에 동의하거나 연습 모드를 선택하세요."
                )

            else:
                try:
                    if not account:
                        sign_in(nickname)

                    start_game(True)

                except ConnectionProblem as exc:
                    st.error(explain(exc))

                    st.info(
                        "입장에 실패해 새 게임을 시작하지 않았어요. "
                        "연결을 확인하거나 연습 모드를 이용하세요."
                    )


def show_play():
    global game

    if "escape_game" not in st.session_state:
        st.info(
            "먼저 시작 안내·입장에서 "
            "연습 또는 랭킹 참여를 선택해 주세요."
        )

        if st.button("시작 안내·입장으로 이동"):
            go_to("🚪 시작 안내·입장")

        return

    game = st.session_state["escape_game"]

    st.progress(game["unlocked"] / 3)

    st.caption(
        f"해제한 잠금 {game['unlocked']} / 3 · "
        f"수집한 증거 {len(game['evidence'])}개"
    )

    if game["unlocked"] == 3:
        show_ending()

        if st.button("🏆 탈출 랭킹 보기"):
            go_to("🏆 탈출 랭킹")

    else:
        room_tab, inventory_tab, lock_tab = st.tabs(
            [
                "🔎 방 조사",
                "📁 증거 보관함",
                "🔐 잠금 해제",
            ]
        )

        with room_tab:
            show_room()

        with inventory_tab:
            show_inventory()

        with lock_tab:
            if game["unlocked"] == 0:
                lock_one()
            elif game["unlocked"] == 1:
                lock_two()
            else:
                lock_three()

    st.divider()

    if st.button("참여 방식 선택 / 새 게임 준비"):
        go_to("🚪 시작 안내·입장")

    st.caption(
        "시작 안내로 이동하는 것만으로 게임을 초기화하지 않아요. "
        "새 게임을 시작할 때 초기화 동의를 받습니다."
    )


st.title("🗝️ 잠깐! · 피싱 방탈출")
st.subheader("사건 01 — 엄마의 번호, 두 개의 진실")
st.caption(
    "교육용 가상 사건 · 시간 제한 없음 · 실제 전화나 앱 설치 없음"
)

current = st.session_state.get("escape_game")

if current:
    if current.get("rank_uid"):
        st.info(
            f"🏆 {current['rank_nickname']} · 랭킹 참여 모드 "
            "(계정별 첫 저장 기록 유지)"
        )
    else:
        st.info("🌱 연습 모드 · 공개 저장 안 함")

if "room_next_section" in st.session_state:
    st.session_state["room_section"] = st.session_state.pop(
        "room_next_section"
    )

def show_section_menu_style(game_running):
    """방탈출 메뉴(라디오)를 큰 단계 카드처럼 보이게 꾸밉니다. 동작은 그대로입니다."""
    running_badge = ""
    if game_running:
        # 게임이 진행 중이면 ‘게임 진행’ 카드에 깜빡이는 표시를 붙입니다.
        running_badge = """
        .st-key-room_section [role="radiogroup"] > div:nth-child(2) label::before {
            content: "● 진행 중";
            color: #DC2626;
            animation: room-pulse 1.4s ease-in-out infinite;
        }
        .st-key-room_section [role="radiogroup"] > div:nth-child(2) label[data-selected="true"]::before {
            color: #FECACA;
        }
        """

    st.markdown(
        f"""
        <style>
        .room-nav-title {{
            font-weight: 800; color: #0F766E; font-size: .95rem;
            margin: 6px 0 4px; letter-spacing: -0.01em;
        }}
        .st-key-room_section {{
            position: sticky; top: 3.2rem; z-index: 20;
            background: #FFFEF8; padding: 6px 0 10px;
        }}
        .st-key-room_section [role="radiogroup"] {{
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px; width: 100%;
        }}
        .st-key-room_section [role="radiogroup"] > div {{ width: 100%; margin: 0; }}
        .st-key-room_section label[data-testid="stRadioOption"] {{
            display: flex; flex-direction: column; align-items: center;
            width: 100%; min-height: 112px; justify-content: center;
            padding: 14px 10px; margin: 0;
            background: #FFFFFF; border: 2px solid #CDDAD6; border-radius: 18px;
            box-shadow: 0 2px 0 #CDDAD6; cursor: pointer;
            transition: transform .15s, box-shadow .15s, border-color .15s, background .15s;
        }}
        .st-key-room_section label[data-testid="stRadioOption"]:hover {{
            border-color: #0F766E; transform: translateY(-2px);
            box-shadow: 0 6px 14px rgba(15, 118, 110, .18);
        }}
        /* 동그라미 선택 표시는 숨깁니다. */
        .st-key-room_section label[data-testid="stRadioOption"] > div > div:first-child {{
            display: none;
        }}
        .st-key-room_section label[data-testid="stRadioOption"] p {{
            font-size: 1.15rem !important; font-weight: 800; text-align: center;
            line-height: 1.4 !important; color: #172B3A; margin: 0;
        }}
        .st-key-room_section label[data-testid="stRadioOption"]::before {{
            font-size: .72rem; font-weight: 800; letter-spacing: .08em;
            color: #0F766E; margin-bottom: 4px;
        }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(1) label::before {{ content: "STEP 1"; }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(2) label::before {{ content: "STEP 2"; }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(3) label::before {{ content: "STEP 3"; }}
        .st-key-room_section label[data-testid="stRadioOption"]::after {{
            font-size: .82rem; color: #52636B; margin-top: 4px; text-align: center;
        }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(1) label::after {{ content: "규칙 확인하고 입장하기"; }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(2) label::after {{ content: "증거 모아 잠금 풀기"; }}
        .st-key-room_section [role="radiogroup"] > div:nth-child(3) label::after {{ content: "기록 확인하기"; }}
        /* 지금 보고 있는 메뉴 */
        .st-key-room_section label[data-testid="stRadioOption"][data-selected="true"] {{
            background: #0F766E; border-color: #0F766E;
            box-shadow: 0 8px 18px rgba(15, 118, 110, .35); transform: translateY(-2px);
        }}
        .st-key-room_section label[data-testid="stRadioOption"][data-selected="true"] p,
        .st-key-room_section label[data-testid="stRadioOption"][data-selected="true"]::after {{
            color: #FFFFFF !important;
        }}
        .st-key-room_section label[data-testid="stRadioOption"][data-selected="true"]::before {{
            color: #A7F3D0;
        }}
        @keyframes room-pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
        {running_badge}
        @media (max-width: 640px) {{
            .st-key-room_section label[data-testid="stRadioOption"] {{ min-height: 92px; padding: 10px 6px; }}
            .st-key-room_section label[data-testid="stRadioOption"] p {{ font-size: .98rem !important; }}
            .st-key-room_section label[data-testid="stRadioOption"]::after {{ display: none; }}
        }}
        </style>
        <div class="room-nav-title">👇 아래 단계를 눌러 이동하세요</div>
        """,
        unsafe_allow_html=True,
    )


_running = st.session_state.get("escape_game")
show_section_menu_style(
    bool(_running) and _running.get("unlocked", 0) < 3 and not _running.get("failed")
)

section = st.radio(
    "방탈출 메뉴",
    [
        "🚪 시작 안내·입장",
        "🗝️ 게임 진행",
        "🏆 탈출 랭킹",
    ],
    horizontal=True,
    key="room_section",
    label_visibility="collapsed",
)

# 선택한 화면만 실행해 랭킹 조회 중 게임 저장이 실행되지 않게 합니다.
if section == "🚪 시작 안내·입장":
    show_entry()

elif section == "🗝️ 게임 진행":
    show_play()

else:
    show_ranking(embedded=True)

    if st.button("게임으로 돌아가기"):
        go_to("🗝️ 게임 진행")
