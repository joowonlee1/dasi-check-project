import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.title("🌊 진짜·가짜 강 건너기")
st.caption(
    "확인 자료를 비교하고, 직접 판단하며 건너는 1인칭 점프 게임"
)


# ─────────────────────────────────────
# 스테이지와 운영자 미션
# ─────────────────────────────────────

STAGES = [
    {
        "tactic": "사칭",
        "title": "믿을 만한 이름 빌리기",
        "icon": "🎭",
        "time": 18,
        "mission": {
            "prompt": (
                "도토리시 공원에 새 분수가 생긴대요. "
                "가짜 계정 운영자는 어떤 방법으로 관심을 끌까요?"
            ),
            "choices": [
                {
                    "label": "계정 이름을 ‘도토리시청 공식’으로 바꾸고 시청 로고를 흉내 낸다",
                    "followers": 800,
                    "post": (
                        "[도토리시청 공식] 새 분수 개장 기념! "
                        "선착순 무료 아이스크림! 공유하면 2개!"
                    ),
                },
                {
                    "label": "‘공원 분수 공사가 끝났대요’라고 들은 내용을 적는다",
                    "followers": 20,
                    "post": (
                        "공원 분수 공사가 끝났대요. "
                        "운영 일정은 아직 확인하지 못했어요."
                    ),
                },
                {
                    "label": "분수 사진에 웃긴 자막을 붙인다",
                    "followers": 60,
                    "post": "(분수 사진) 드디어 우리 동네에도 바다가…",
                },
            ],
            "why": (
                "익숙한 기관 이름과 로고를 사용하면 공식 안내처럼 보일 수 있어요. "
                "하지만 이름이나 프로필 사진만으로 발신자를 확인할 수는 없어요."
            ),
            "spot": (
                "전달받은 링크만 누르지 말고, 직접 찾은 기관 홈페이지에 "
                "같은 공지가 있는지 확인해요."
            ),
        },
    },
    {
        "tactic": "감정 자극",
        "title": "화나고 불안하게 만들기",
        "icon": "😡",
        "time": 16,
        "mission": {
            "prompt": (
                "붕어빵 노점 2곳이 옆 골목으로 이전한대요. "
                "가짜 계정 운영자는 이 소식을 어떻게 부풀릴까요?"
            ),
            "choices": [
                {
                    "label": "‘충격’, ‘분노’를 넣고 모든 노점이 철거된다고 부풀린다",
                    "followers": 1500,
                    "post": (
                        "【충격】 도토리시 붕어빵 노점 전부 강제 철거?! "
                        "(실제 내용: 노점 2곳 위치 이동)"
                    ),
                },
                {
                    "label": "노점 2곳이 시장 옆 골목으로 이전한다고 정리한다",
                    "followers": 40,
                    "post": "붕어빵 노점 2곳이 다음 주부터 시장 옆 골목으로 옮긴대요.",
                },
                {
                    "label": "붕어빵 노점이 어디로 옮기는지 질문한다",
                    "followers": 90,
                    "post": "시장 앞 붕어빵 노점이 어디로 옮기는지 아시는 분?",
                },
            ],
            "why": (
                "분노나 불안을 크게 자극하면 내용을 확인하기 전에 "
                "반응하거나 공유하도록 유도할 수 있어요."
            ),
            "spot": (
                "감정적인 표현보다 원문에 적힌 숫자, 날짜, 대상 범위를 비교해요."
            ),
        },
    },
    {
        "tactic": "가짜 증거",
        "title": "그럴듯한 증거 만들기",
        "icon": "📸",
        "time": 15,
        "mission": {
            "prompt": (
                "팔로워들이 ‘증거 있어?’라고 물어요. "
                "가짜 계정 운영자는 무엇을 증거처럼 보이게 할까요?"
            ),
            "choices": [
                {
                    "label": "몇 년 전 다른 도시의 사진을 ‘오늘 도토리시’라고 소개한다",
                    "followers": 2000,
                    "post": (
                        "[사진] 오늘 도토리강 범람! "
                        "(실제 사진: 3년 전 다른 도시)"
                    ),
                },
                {
                    "label": "확인하지 못한 이야기라고 밝힌다",
                    "followers": -100,
                    "post": "들은 이야기라 확실하지 않아요. 아직 확인하지 못했어요.",
                },
                {
                    "label": "시청 공지 원문을 찾아 함께 보여 준다",
                    "followers": 30,
                    "post": "시청 공지 원문: 도토리강 산책로 일부 통제",
                },
            ],
            "why": (
                "사진과 캡처도 날짜나 장소를 바꾸어 소개할 수 있어요. "
                "이미지가 있다는 사실만으로 내용까지 사실인 것은 아니에요."
            ),
            "spot": (
                "촬영 날짜와 장소, 원본 게시물, 전체 영상의 맥락을 확인해요."
            ),
        },
    },
    {
        "tactic": "편 가르기",
        "title": "우리 편 vs 저쪽 편",
        "icon": "👥",
        "time": 14,
        "mission": {
            "prompt": (
                "가짜 계정 운영자가 사람들을 서로 싸우게 만들려고 해요. "
                "어떤 글을 사용할까요?"
            ),
            "choices": [
                {
                    "label": "‘슈크림파가 팥붕파를 공격한다’는 확인되지 않은 글을 쓴다",
                    "followers": 2500,
                    "post": (
                        "슈크림파가 팥붕 가게를 공격한대요! "
                        "팥붕파 여러분, 가만히 있을 건가요?"
                    ),
                },
                {
                    "label": "팥과 슈크림 모두 맛있다는 글을 올린다",
                    "followers": 30,
                    "post": "팥도 슈크림도 맛있어요. 오늘은 반반 샀어요.",
                },
                {
                    "label": "붕어빵 취향을 묻는 투표를 올린다",
                    "followers": 200,
                    "post": "여러분의 붕어빵 취향은? 팥 / 슈크림",
                },
            ],
            "why": (
                "‘우리 편이 피해를 본다’는 표현으로 감정을 자극하면 "
                "자기편의 주장을 확인 없이 받아들이게 만들 수 있어요."
            ),
            "spot": (
                "어느 편의 주장인지보다 공개된 숫자와 기록이 일치하는지 확인해요."
            ),
        },
    },
    {
        "tactic": "음모론",
        "title": "아무도 말해 주지 않는 ‘진실’",
        "icon": "🧩",
        "time": 12,
        "mission": {
            "prompt": (
                "가짜 계정의 글에 반박이 올라왔어요. "
                "운영자는 어떻게 확인을 피하려 할까요?"
            ),
            "choices": [
                {
                    "label": "반박 자료까지 모두 조작이라며 확인을 거부한다",
                    "followers": 3000,
                    "post": (
                        "와이파이가 끊기는 진짜 이유를 숨기고 있어요. "
                        "반박 자료도 전부 조작입니다. 이 글은 곧 삭제될지도 몰라요."
                    ),
                },
                {
                    "label": "틀린 내용을 인정하고 정정한다",
                    "followers": -500,
                    "post": "확인되지 않은 내용을 올렸습니다. 잘못된 내용을 정정합니다.",
                },
                {
                    "label": "새 글을 올리지 않고 자료부터 확인한다",
                    "followers": 0,
                    "post": "추가 게시를 멈추고 자료를 확인합니다.",
                },
            ],
            "why": (
                "어떤 반박도 ‘조작’이라고만 하면 주장을 검증하기 어려워져요. "
                "주장과 실제로 확인할 수 있는 기록을 구분해야 해요."
            ),
            "spot": (
                "‘곧 삭제된다’는 말에 서두르지 말고 "
                "구체적인 기록과 원문을 확인해요."
            ),
        },
    },
]


# ─────────────────────────────────────
# 각 문제:
# 자료 제목, 확인 자료, 일치 소식, 불일치 소식,
# 불일치 이유, 힌트
# ─────────────────────────────────────

QUESTION_ROWS = [
    [
        (
            "도토리시청 행사 안내",
            "분수 시운전은 10월 24일 오전 10시입니다. 아이스크림 증정 행사는 진행하지 않습니다.",
            "분수 시운전은 10월 24일 오전 10시이며, 아이스크림 증정 행사는 없습니다.",
            "시청 공식 행사입니다! 10월 24일 오전 10시 분수 시운전에서 아이스크림을 무료로 나눠 줍니다.",
            "확인 자료에는 아이스크림 증정 행사를 진행하지 않는다고 적혀 있습니다.",
            "행사 시간뿐 아니라 증정 행사 여부도 비교해 보세요.",
        ),
        (
            "시립도서관 운영 공지",
            "11월 1일부터 일요일 운영 시간은 오전 9시~오후 6시입니다. 야간에는 개방하지 않습니다.",
            "11월 1일부터 도서관은 일요일 오전 9시~오후 6시에 운영합니다.",
            "도서관 관계자가 알려 드립니다. 11월 1일부터 일요일에는 24시간 개방합니다.",
            "공지의 운영 시간은 오전 9시~오후 6시로, 24시간 개방과 다릅니다.",
            "개방하는 요일이 같아도 운영 시간이 같은지 확인하세요.",
        ),
        (
            "도토리소방서 축제 안전 공지",
            "10월 25일 불꽃 축제는 예정대로 진행됩니다. 안전을 위해 공원 내 취사는 금지합니다.",
            "10월 25일 불꽃 축제는 진행되며 공원 내 취사는 금지됩니다.",
            "소방서 공식 발표입니다. 취사 금지와 함께 10월 25일 불꽃 축제도 취소되었습니다.",
            "공지는 취사만 금지하고 축제는 예정대로 진행한다고 안내합니다.",
            "취사 금지와 축제 취소는 같은 내용일까요?",
        ),
        (
            "도토리교육청 휴업 안내",
            "10월 28일 개교기념일로 쉬는 학교는 도토리초등학교 한 곳입니다. 다른 학교는 정상 수업합니다.",
            "10월 28일에는 도토리초등학교만 개교기념일로 쉽니다.",
            "교육청 관계자입니다. 10월 28일 도토리시의 모든 학교가 쉽니다.",
            "안내 대상은 도토리초등학교 한 곳이며 모든 학교가 아닙니다.",
            "공지에 나온 학교의 범위를 확인하세요.",
        ),
    ],
    [
        (
            "도토리시장 이전 안내",
            "붕어빵 노점 10곳 중 2곳이 11월 2일 시장 옆 골목으로 이전합니다. 나머지 8곳은 현재 위치에서 영업합니다.",
            "붕어빵 노점 2곳이 11월 2일 옆 골목으로 옮기고, 8곳은 그대로 영업합니다.",
            "충격! 11월 2일 시장 붕어빵 노점 10곳이 전부 철거되어 영업을 중단합니다.",
            "자료는 2곳의 위치 이전과 8곳의 정상 영업을 안내합니다. 전부 철거가 아닙니다.",
            "전체 수와 이전하는 수를 나누어 비교하세요.",
        ),
        (
            "도토리보호소 입양 행사 공지",
            "보호소는 이번 주 정상 운영합니다. 토요일 오후 2시 입양 행사를 열며 행사 참가비는 없습니다.",
            "보호소는 정상 운영하고, 토요일 오후 2시 입양 행사 참가비는 무료입니다.",
            "마지막 기회예요! 보호소가 토요일에 폐쇄됩니다. 폐쇄를 막으려면 행사 참가비 3만 원을 보내 주세요.",
            "공지는 정상 운영과 참가비 없음을 명시합니다. 폐쇄 주장과 3만 원 요구가 모두 다릅니다.",
            "운영 여부와 참가비 두 항목을 확인하세요.",
        ),
        (
            "도토리어린이집 검사 결과",
            "10월 21일 간식 12개 품목의 검사 결과, 12개 모두 기준에 적합했습니다. 부적합 품목은 0개입니다.",
            "10월 21일 검사한 간식 12개 품목은 모두 기준에 적합했습니다.",
            "분노합니다! 10월 21일 검사한 간식 12개가 모두 기준 미달로 확인됐습니다.",
            "검사 결과는 모두 적합이며 부적합은 0개입니다. 모두 기준 미달이라는 주장은 반대입니다.",
            "적합·부적합 결과와 각각의 개수를 확인하세요.",
        ),
        (
            "시내버스 요금 변경표",
            "11월 1일부터 일반 성인 요금은 1,500원에서 1,600원으로 100원 인상됩니다.",
            "11월 1일부터 성인 버스 요금이 100원 올라 1,600원이 됩니다.",
            "서민은 걷기만 하라는 건가요! 11월 1일부터 성인 버스 요금이 2배인 3,000원으로 오릅니다.",
            "새 요금은 1,600원으로 3,000원이 아닙니다. 인상액은 100원입니다.",
            "인상 전·후 금액을 직접 비교하세요.",
        ),
    ],
    [
        (
            "사진 원본 정보와 도토리강 공지",
            "침수 사진 원본: 2023년 7월 솔빛시 촬영. 도토리강의 2026년 10월 22일 공지: 산책로 일부 통제, 시내 침수 없음.",
            "공유된 침수 사진은 2023년 솔빛시 사진이며, 오늘 도토리시는 시내 침수가 없습니다.",
            "이 사진은 2026년 10월 22일 도토리시에서 찍었습니다. 오늘 시내가 전부 잠겼습니다.",
            "원본의 촬영 연도와 도시가 다르고, 오늘 공지에도 시내 침수가 없다고 나옵니다.",
            "사진이 실제로 촬영된 날짜와 장소를 비교하세요.",
        ),
        (
            "공원 공사 사진의 촬영 기록",
            "2026년 10월 14일 도토리시 홍보팀 촬영. 사진 속 작업은 배수관 교체이며 유물 발견 기록은 없습니다.",
            "10월 14일 공원 공사 사진에는 배수관을 교체하는 작업이 담겨 있습니다.",
            "10월 14일 공원 공사 사진에 고대 유물 발굴 장면이 담겼습니다. 유물 발견이 확인되었습니다.",
            "촬영 기록은 배수관 교체 작업이라고 명시합니다. 유물 발굴 장면이라는 설명과 다릅니다.",
            "사진 설명과 촬영 기록의 작업 내용을 대조하세요.",
        ),
        (
            "도토리방송 뉴스 원문",
            "10월 22일 저녁 뉴스: 지원금 지급안은 다음 달 심의 예정입니다. 지급 여부와 금액은 결정되지 않았습니다.",
            "방송 원문에 따르면 지원금 지급안은 다음 달 심의 예정이며 금액은 미정입니다.",
            "뉴스 캡처입니다. 10월 22일 방송에서 내일부터 전 시민에게 50만 원 지급을 확정했다고 발표했습니다.",
            "원문은 심의 예정과 금액 미정을 알립니다. 내일부터 50만 원 지급 확정과 모순됩니다.",
            "심의 예정과 지급 확정은 다른 단계예요.",
        ),
        (
            "시의회 영상 원본 기록",
            "2026년 10월 20일 도토리시의회. 공공자전거 확대안은 찬성 8표, 반대 2표로 가결되었습니다.",
            "10월 20일 회의에서 공공자전거 확대안은 찬성 8표, 반대 2표로 통과됐습니다.",
            "회의 영상에 따르면 공공자전거 확대안은 찬성 2표, 반대 8표로 부결됐습니다.",
            "찬반 표 수가 뒤바뀌었고, 가결을 부결로 바꾸어 전했습니다.",
            "찬반 숫자와 최종 처리 결과를 함께 확인하세요.",
        ),
    ],
    [
        (
            "붕어빵 축제 설문 결과",
            "응답자 100명 중 팥 선호 54명, 슈크림 선호 46명입니다. 두 종류 모두 축제에서 판매합니다.",
            "설문 결과 팥 54명, 슈크림 46명이며 두 종류 모두 판매합니다.",
            "우리 슈크림파가 90표로 압승했어요. 팥은 10표뿐이라 이번 축제에서 판매하지 않습니다.",
            "결과는 54대 46이며 두 종류 모두 판매합니다. 90대 10과 팥 판매 제외는 자료와 다릅니다.",
            "선호 집단에 관계없이 숫자와 판매 계획을 비교하세요.",
        ),
        (
            "동네별 버스 운행표",
            "11월 개편안: 북부 노선 하루 20회, 남부 노선 하루 20회. 두 노선 모두 기존 운행 횟수를 유지합니다.",
            "11월 개편안은 북부와 남부 모두 하루 20회 운행을 유지합니다.",
            "북쪽 동네 때문에 남쪽만 손해 봅니다! 남부 운행은 하루 10회로 줄고 북부는 30회로 늘어납니다.",
            "운행표에는 북부·남부 모두 20회 유지라고 적혀 있습니다. 10회와 30회로 바뀌지 않습니다.",
            "두 동네의 운행 횟수를 확인하세요.",
        ),
        (
            "축제 예산 배분표",
            "북부 행사 예산 500만 원, 남부 행사 예산 500만 원입니다. 총예산은 1,000만 원입니다.",
            "북부와 남부 행사에 각각 500만 원씩 배분합니다.",
            "남쪽이 우리 예산을 빼앗았어요! 남부는 900만 원, 북부는 100만 원만 받습니다.",
            "배분표는 두 지역 각각 500만 원으로 동일합니다. 900만 원과 100만 원이 아닙니다.",
            "총액뿐 아니라 각 지역의 배분액을 비교하세요.",
        ),
        (
            "주민 설명회 참석 안내",
            "11월 3일 설명회는 북부·남부 주민 누구나 참석할 수 있습니다. 지역별 입장 제한은 없습니다.",
            "11월 3일 설명회는 북부·남부 주민 모두 참석할 수 있습니다.",
            "남부가 북부를 쫓아냅니다! 11월 3일 설명회는 남부 주민만 입장할 수 있습니다.",
            "안내에는 양쪽 주민 누구나 참석할 수 있고 지역별 제한도 없다고 적혀 있습니다.",
            "누가 참석할 수 있는지 안내문에서 확인하세요.",
        ),
    ],
    [
        (
            "공공 와이파이 점검 기록",
            "10월 22일 오전 9시~10시 중단 원인은 전원 장치 교체입니다. 같은 날 오전 10시 교체와 복구가 완료됐습니다.",
            "와이파이는 전원 장치 교체로 오전 9시~10시 중단됐고 오전 10시에 복구됐습니다.",
            "숨겨진 사실입니다. 와이파이가 10월 22일 하루 종일 끊겼으며 밤 12시까지 복구되지 않았습니다.",
            "기록은 오전 10시 복구 완료를 명시합니다. 밤 12시까지 중단됐다는 내용과 다릅니다.",
            "기록에 적힌 중단·복구 시각을 비교하세요.",
        ),
        (
            "수돗물 검사 성적서",
            "10월 20일 도토리시 수돗물 검사: 60개 항목 중 60개 적합, 부적합 0개. 성적서는 공개되어 있습니다.",
            "공개된 10월 20일 검사 성적서에는 60개 항목 모두 적합이라고 나옵니다.",
            "당국이 감추는 자료를 봤어요. 10월 20일 성적서에 60개 항목 모두 부적합이라고 적혀 있습니다.",
            "공개 성적서는 모두 적합·부적합 0개라고 명시합니다. 모두 부적합이라고 적혔다는 주장이 틀립니다.",
            "성적서에 실제로 무엇이 적혔는지 비교하세요.",
        ),
        (
            "도토리역 공사 일정표",
            "승강기 교체 공사는 11월 2일~11월 6일입니다. 열차는 공사 기간에도 정상 운행합니다.",
            "11월 2일~6일 승강기를 교체하며 열차는 정상 운행합니다.",
            "공개하지 않는 계획입니다. 11월 2일부터 도토리역의 모든 열차 운행이 영구 중단됩니다.",
            "일정표는 승강기 교체와 열차 정상 운행을 안내합니다. 열차 영구 중단과 다릅니다.",
            "공사 대상이 승강기인지 열차인지 구분하세요.",
        ),
        (
            "시의회 회의록 열람 안내",
            "10월 20일 회의록은 10월 21일부터 시의회 자료실에서 누구나 열람할 수 있습니다. 삭제 예정은 없습니다.",
            "10월 20일 회의록은 10월 21일부터 누구나 열람할 수 있습니다.",
            "곧 지워질 진실입니다. 10월 20일 회의록은 10월 21일 전부 삭제되어 열람할 수 없습니다.",
            "안내는 10월 21일부터 공개 열람 가능하다고 명시하며 삭제 예정도 없습니다.",
            "자료 공개 날짜와 열람 가능 여부를 비교하세요.",
        ),
    ],
]


# 문제 데이터 구성: 각 문제에는 일치 1개, 불일치 1개만 있습니다.
for stage_data, rows in zip(STAGES, QUESTION_ROWS):
    stage_data["pairs"] = []

    for title, evidence, matching, conflicting, reason, clue in rows:
        stage_data["pairs"].append(
            {
                "source_title": title,
                "evidence": evidence,
                "stones": [
                    {
                        "sender": "전달받은 소식",
                        "real": True,
                        "text": matching,
                        "why": (
                            "확인 자료: "
                            + evidence
                            + " 이 소식은 해당 내용과 일치합니다."
                        ),
                    },
                    {
                        "sender": "전달받은 소식",
                        "real": False,
                        "text": conflicting,
                        "why": reason,
                    },
                ],
                "clue": clue,
            }
        )


# ─────────────────────────────────────
# 게임 화면
# ─────────────────────────────────────

GAME_HTML = r"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>잠깐! 리버 점프</title>

<style>
:root {
    color-scheme: light;
    --ink: #163e3c;
    --green: #176650;
    --cream: #fffdf5;
    --line: #d4e1d5;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    background: #f1f5ec;
    color: var(--ink);
    font: 16px/1.6 "Malgun Gothic", sans-serif;
}

button, input { font: inherit; }

button {
    cursor: pointer;
    touch-action: manipulation;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 12px 17px;
    background: white;
    color: var(--ink);
    font-weight: 700;
    min-height: 48px;
}

button:hover:not(:disabled) { background: #e5efe4; }

button:focus-visible,
input:focus-visible,
summary:focus-visible {
    outline: 3px solid #b35b17;
    outline-offset: 3px;
}

button:disabled {
    opacity: .48;
    cursor: default;
}

.primary {
    background: var(--green);
    color: white;
    border-color: var(--green);
}

.primary:hover:not(:disabled) { background: #104b3b; }

.wrap {
    max-width: 1080px;
    margin: auto;
    padding: 16px;
}

.top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
}

.brand { font-weight: 900; font-size: 20px; }

.eyebrow {
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #657961;
}

h1 {
    font-size: clamp(26px, 5vw, 42px);
    line-height: 1.25;
    margin: 12px 0;
}

h2 { font-size: 23px; margin: 10px 0; }
h3 { font-size: 18px; margin: 8px 0; }
p { margin: 8px 0; }

.muted { color: #566e65; font-size: 14px; }

.card {
    padding: 22px;
    background: var(--cream);
    border: 1px solid var(--line);
    border-radius: 20px;
    margin-top: 14px;
}

.row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    align-items: center;
}

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.stagegrid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
}

.stage {
    padding: 16px;
    background: white;
    border: 1px solid var(--line);
    border-radius: 16px;
}

.stage button { width: 100%; margin-top: 12px; }

.choices {
    display: grid;
    gap: 10px;
    margin: 18px 0;
}

.choices button { text-align: left; }

.note {
    background: #e7eee0;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 12px 0;
}

.warn { background: #fff0cc; color: #63400c; }

.badge {
    display: inline-block;
    border-radius: 30px;
    background: #e2eadb;
    padding: 4px 12px;
    font-size: 13px;
    font-weight: 700;
}

.scene {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    background: #99d9e0;
    margin: 14px 0 10px;
    border: 1px solid #94b5a5;
}

canvas {
    display: block;
    width: 100%;
    height: 340px;
    touch-action: pan-y;
}

.hud {
    position: absolute;
    left: 12px;
    right: 12px;
    top: 12px;
    display: flex;
    justify-content: space-between;
    gap: 8px;
    pointer-events: none;
}

.hud span {
    background: #fffdf2ed;
    padding: 5px 11px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 800;
}

.reticle {
    position: absolute;
    left: 50%;
    top: 50%;
    color: white;
    font-size: 24px;
    text-shadow: 0 1px 4px #183b3b;
    pointer-events: none;
}

.banner {
    position: absolute;
    bottom: 15px;
    left: 50%;
    transform: translateX(-50%);
    max-width: 92%;
    width: max-content;
    background: #183e39e8;
    color: white;
    padding: 8px 18px;
    border-radius: 30px;
    text-align: center;
    font-size: 14px;
}

.stonecard {
    border: 2px solid var(--line);
    border-radius: 15px;
    padding: 14px;
    background: white;
    min-width: 0;
}

.stonecard.selected {
    border-color: #a75917;
    box-shadow: 0 0 0 2px #f0c977;
}

.stonecard p {
    font-size: 15px;
    overflow-wrap: anywhere;
}

.sender { font-size: 12px; color: #547063; }

.stonecard button {
    width: 100%;
    padding: 8px;
    margin-top: 8px;
}

.controls {
    display: grid;
    grid-template-columns: 1fr;
    margin: 12px 0;
}

.feedback { border-left: 5px solid #2b7660; }
.feedback.bad { border-left-color: #bc6c25; }

details { margin: 10px 0; }
summary { cursor: pointer; font-weight: 700; }

.settings {
    margin: 15px 0;
    font-size: 14px;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

label { cursor: pointer; }

input[type=checkbox] {
    width: 18px;
    height: 18px;
    vertical-align: middle;
}

#view:focus { outline: none; }
#toast { color: #75440a; font-weight: 700; }

.mascot {
    width: 110px;
    height: 110px;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
}

.mascot img {
    width: 330px;
    max-width: none;
    position: absolute;
    left: -220px;
    top: -110px;
}

footer {
    font-size: 12px;
    color: #61766b;
    margin: 20px 0;
}

@media (max-width: 520px) {
    .wrap { padding: 8px; }
    .card { padding: 16px; }
    canvas { height: 270px; }
    .grid { gap: 8px; }
    .stonecard { padding: 10px; }
    .stonecard p { font-size: 14px; }
    .hud span { font-size: 11px; padding: 4px 8px; }
    .brand { font-size: 17px; }
}
</style>
</head>

<body>
<main class="wrap">
    <div class="top">
        <div class="brand">
            ✋ 잠깐! <span class="muted">리버 점프</span>
        </div>
        <button id="mapButton" hidden>스테이지 지도</button>
    </div>

    <div id="view" tabindex="-1"></div>

    <footer>
        교육용 가상 도시·계정·소식입니다.
        확인 자료도 가상이며 실제 사이트 조회 결과는 아닙니다.
        실제 게시·송금·정보 입력은 없어요.
    </footer>
</main>

<script>
"use strict";

const STAGES = __STAGES__;
const MASCOT = "__MASCOT__";

const view = document.getElementById("view");
const mapButton = document.getElementById("mapButton");

const state = {
    phase: "intro",
    stage: 0,
    pos: 0,
    lives: 3,
    cleared: [],
    followers: 0,
    awarded: [],
    round: [],
    selected: null,
    hinted: false,
    results: [],
    motion: !matchMedia("(prefers-reduced-motion: reduce)").matches,
    pressure: false,
    remaining: 0,
    feedback: null,
    cam: {x: 0, z: 0, y: 1.7},
    anim: null,
    last: 0
};

let canvas = null;
let ctx = null;
let clockNode = null;
let liveNode = null;

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[character]));
}

const stage = () => STAGES[state.stage];
const pair = () => state.round[state.pos];

function shuffle(items) {
    const result = [...items];

    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
}

function mount(markup) {
    canvas = null;
    ctx = null;
    clockNode = null;
    liveNode = null;

    view.innerHTML = markup;
    mapButton.hidden = ["intro", "map"].includes(state.phase);
    mapButton.disabled = state.phase === "jump";

    view.focus({preventScroll: true});
    window.scrollTo(0, 0);
}

function button(id, handler) {
    document.getElementById(id).addEventListener("click", handler);
}

function showIntro() {
    state.phase = "intro";

    mount(`
        <section class="card">
            <span class="eyebrow">THINK · CHOOSE · JUMP</span>

            <h1>한 번 멈추고,<br>한 칸 더 멀리.</h1>

            <p>
                확인 자료와 일치하는 소식의 돌로 점프하세요.
            </p>

            <div class="note">
                <b>① 확인 자료 읽기 → ② 두 소식 비교 → ③ 선택하고 점프</b>
                <p>
                    모든 구간에서 자료와 일치하는 소식은
                    <b>하나</b>입니다.
                </p>
            </div>

            <p class="muted">
                컴퓨터: A/D 또는 ←/→ 선택 · Space 또는 ↑/W 점프<br>
                휴대폰: 카드의 선택 버튼과 점프 버튼<br>
                점프 거리나 타이밍을 맞출 필요는 없어요.
            </p>

            <div class="settings">
                <label>
                    <input id="motion" type="checkbox"
                        ${state.motion ? "checked" : ""}>
                    점프·물 움직임
                </label>
                <label>
                    <input id="pressure" type="checkbox"
                        ${state.pressure ? "checked" : ""}>
                    시간 압박 모드
                </label>
            </div>

            <p class="muted">
                기본은 시간 제한 없이 연습해요.
                압박 모드에서도 단서 확인을 누르면 시간이 멈춰요.
            </p>

            <button class="primary" id="start">
                강으로 출발하기 →
            </button>
        </section>
    `);

    button("start", () => {
        state.motion = document.getElementById("motion").checked;
        state.pressure = document.getElementById("pressure").checked;
        showMap();
    });
}

function showMap() {
    state.phase = "map";
    state.anim = null;

    const choices = STAGES.map((item, index) => {
        const unlocked =
            index === 0 || state.cleared.includes(index - 1);

        const cleared = state.cleared.includes(index);

        return `
            <article class="stage">
                <span class="badge">
                    ${cleared ? "✓ 통과" : `STAGE ${index + 1}`}
                </span>
                <h3>${item.icon} ${escapeHTML(item.tactic)}</h3>
                <p class="muted">${escapeHTML(item.title)}</p>
                <button data-stage="${index}"
                    ${unlocked ? "" : "disabled"}>
                    ${unlocked ? "도전하기 →" : "🔒 앞 강을 건너세요"}
                </button>
            </article>
        `;
    }).join("");

    const judged = state.results.filter(item => !item.timeout);
    const correct = judged.filter(item => item.correct).length;
    const timeouts = state.results.filter(item => item.timeout).length;

    mount(`
        <section class="card">
            <span class="eyebrow">RIVER MAP</span>
            <h2>다섯 개의 강, 다섯 가지 수법</h2>

            <p>
                ${state.cleared.length} / ${STAGES.length} 통과 ·
                가상 팔로워 ${state.followers.toLocaleString()}명
            </p>

            <p class="muted">
                팔로워는 게임 속 숫자이며 실제 확산 예측값이 아니에요.
            </p>

            <div class="stagegrid">${choices}</div>

            ${state.cleared.length === STAGES.length ? `
                <div class="note">
                    <b>🏆 모든 강을 건넜어요!</b>
                    <p>
                        말투·사진·팔로워 수만으로 믿지 않고,
                        별도 경로에서 확인하는 습관을 이어 가세요.
                    </p>
                </div>
            ` : ""}

            <div class="settings">
                <label>
                    <input id="motion" type="checkbox"
                        ${state.motion ? "checked" : ""}>
                    점프·물 움직임
                </label>
                <label>
                    <input id="pressure" type="checkbox"
                        ${state.pressure ? "checked" : ""}>
                    시간 압박 모드
                </label>
            </div>

            <details>
                <summary>내 판단 기록</summary>
                <p>
                    선택한 횟수 ${judged.length}번 ·
                    올바른 판단 ${correct}번 ·
                    시간 초과 ${timeouts}번
                </p>
                <p class="muted">
                    시간 초과는 선택 결과와 별도로 셉니다.
                    실제 피해 위험이나 능력을 평가하는 점수가 아니에요.
                </p>
            </details>
        </section>
    `);

    document.querySelectorAll("[data-stage]").forEach(element => {
        element.onclick = () => {
            state.stage = Number(element.dataset.stage);
            showMission();
        };
    });

    document.getElementById("motion").onchange = event => {
        state.motion = event.target.checked;
    };

    document.getElementById("pressure").onchange = event => {
        state.pressure = event.target.checked;
    };
}

function showMission() {
    state.phase = "mission";

    const current = stage();

    const choices = shuffle(
        current.mission.choices.map((choice, index) => ({
            choice,
            index
        }))
    );

    mount(`
        <section class="card">
            <span class="badge">
                STAGE ${state.stage + 1} ·
                ${escapeHTML(current.tactic)}
            </span>

            <h2>🎭 속이는 쪽의 수법 알아보기</h2>
            <p>${escapeHTML(current.mission.prompt)}</p>

            <p class="muted">
                수법을 알아보기 위한 가상 역할 체험입니다.
                실제로 게시하지 않습니다.
            </p>

            <div class="choices">
                ${choices.map(({choice, index}) => `
                    <button data-choice="${index}">
                        ${escapeHTML(choice.label)}
                    </button>
                `).join("")}
            </div>
        </section>
    `);

    document.querySelectorAll("[data-choice]").forEach(element => {
        element.onclick = () => {
            showExplanation(Number(element.dataset.choice));
        };
    });
}

function showExplanation(index) {
    state.phase = "explain";

    const current = stage();
    const choice = current.mission.choices[index];

    if (!state.awarded.includes(state.stage)) {
        state.followers = Math.max(
            0,
            state.followers + choice.followers
        );
        state.awarded.push(state.stage);
    }

    mount(`
        <section class="card">
            <span class="eyebrow">TACTIC REVEALED</span>
            <h2>${current.icon} ${escapeHTML(current.tactic)}</h2>

            <div class="note">${escapeHTML(choice.post)}</div>

            <p>
                <b>수법 해설</b><br>
                ${escapeHTML(current.mission.why)}
            </p>

            <div class="note warn">
                <b>받는 사람의 대응</b>
                <p>${escapeHTML(current.mission.spot)}</p>
                <p>
                    말투나 인증 표시 하나만으로는 진위를 확정할 수 없어요.
                    별도 경로에서 원문을 확인하세요.
                </p>
            </div>

            <button id="riverStart" class="primary">
                이제 받는 사람이 되어 점프하기 →
            </button>
        </section>
    `);

    button("riverStart", startRiver);
}

function startRiver() {
    state.round = shuffle(stage().pairs).map(item => ({
        ...item,
        stones: shuffle(item.stones)
    }));

    state.pos = 0;
    state.lives = 3;
    state.cam = {x: 0, z: 0, y: 1.7};

    beginTurn();
}

function beginTurn() {
    state.phase = "river";
    state.selected = null;
    state.hinted = false;
    state.remaining = stage().time;
    state.feedback = null;
    state.anim = null;

    renderRiver();
}

function renderRiver() {
    const currentPair = pair();

    mount(`
        <div class="top" style="margin-top:12px">
            <h3>
                ${stage().icon}
                ${escapeHTML(stage().tactic)}의 강
            </h3>
            <span class="badge">
                ${state.pos + 1} / ${state.round.length} 구간
            </span>
        </div>

        <div class="scene">
            <canvas id="world"
                aria-label="두 갈래 돌다리가 보이는 1인칭 게임 화면">
            </canvas>

            <div class="hud">
                <span id="lives">
                    ${"♥".repeat(state.lives)}
                    ${"♡".repeat(3 - state.lives)}
                </span>
                <span id="clock">
                    ${state.pressure
                        ? `남은 시간 ${Math.ceil(state.remaining)}초`
                        : "천천히 확인해도 괜찮아요"}
                </span>
            </div>

            <div class="reticle" aria-hidden="true">＋</div>
            <div class="banner" id="sceneMessage">
                돌을 고른 뒤 점프하세요
            </div>
        </div>

        <section class="note" id="evidence">
            <b>
                📋 확인 자료 ·
                ${escapeHTML(currentPair.source_title)}
            </b>
            <p>${escapeHTML(currentPair.evidence)}</p>
            <span class="muted">
                교육용 가상 자료입니다.
            </span>
        </section>

        <h3>확인 자료와 일치하는 소식은?</h3>

        <div class="grid">
            ${currentPair.stones.map((stone, index) => `
                <article class="stonecard" id="stone${index}">
                    <b>
                        ${index === 0 ? "A · 왼쪽 돌" : "B · 오른쪽 돌"}
                    </b>
                    <div class="sender">
                        ${escapeHTML(stone.sender)}
                    </div>
                    <p>${escapeHTML(stone.text)}</p>
                    <button id="select${index}" aria-pressed="false">
                        ${index === 0 ? "← 왼쪽 선택" : "오른쪽 선택 →"}
                    </button>
                </article>
            `).join("")}
        </div>

        <div class="controls">
            <button class="primary" id="jump">
                선택한 돌로 점프 ↑
            </button>
        </div>

        <div class="row">
            <button id="hint">✋ 잠깐! 단서 확인</button>
            <label class="muted">
                <input id="motion" type="checkbox"
                    ${state.motion ? "checked" : ""}>
                움직임 켜기
            </label>
        </div>

        <div id="toast" role="status" aria-live="polite"></div>
        <div id="feedback" aria-live="polite"></div>

        <p class="muted">
            A/D 또는 ←/→ 선택 · Space 또는 ↑/W 점프<br>
            게임 영역을 한 번 클릭하면 키보드로 조작할 수 있어요.
        </p>
    `);

    canvas = document.getElementById("world");
    ctx = canvas.getContext("2d");
    clockNode = document.getElementById("clock");
    liveNode = document.getElementById("sceneMessage");

    button("select0", () => selectStone(0));
    button("select1", () => selectStone(1));
    button("jump", () => act(state.selected));
    button("hint", showHint);

    document.getElementById("motion").onchange = event => {
        state.motion = event.target.checked;
    };

    draw(0);
}

function selectStone(index) {
    if (state.phase !== "river") return;

    state.selected = index;
    view.focus({preventScroll: true});

    for (let i = 0; i < 2; i++) {
        document.getElementById(`stone${i}`)
            .classList.toggle("selected", i === index);

        document.getElementById(`select${i}`)
            .setAttribute("aria-pressed", String(i === index));
    }

    liveNode.textContent =
        `${index === 0 ? "왼쪽 A" : "오른쪽 B"} 돌 선택 · 점프하세요`;

    document.getElementById("toast").textContent = "";
}

function showHint() {
    if (state.phase !== "river") return;

    state.hinted = true;

    document.getElementById("toast").textContent =
        "✋ " + pair().clue +
        (state.pressure ? " · 시간이 멈췄어요." : "");

    updateClock();
}

function updateClock() {
    if (!clockNode) return;

    if (!state.pressure) {
        clockNode.textContent = "시간 제한 없음";
    } else if (state.hinted) {
        clockNode.textContent = "✋ 확인 중 · 시간 멈춤";
    } else {
        clockNode.textContent =
            `남은 시간 ${Math.ceil(Math.max(0, state.remaining))}초`;
    }
}

function act(choice, timeout = false) {
    if (state.phase !== "river") return;

    if (choice === null && !timeout) {
        document.getElementById("toast").textContent =
            "먼저 왼쪽 또는 오른쪽 돌을 선택해 주세요.";
        return;
    }

    if (!timeout && choice !== 0 && choice !== 1) return;

    const stones = pair().stones;
    const correct = !timeout && stones[choice].real;

    state.feedback = {
        choice,
        correct,
        timeout,
        stones
    };

    state.results.push({
        stage: state.stage,
        correct,
        timeout,
        hinted: state.hinted
    });

    state.phase = "jump";

    document.querySelectorAll("#view button, #view input")
        .forEach(element => {
            element.disabled = true;
        });

    mapButton.disabled = true;

    const target = {
        x: choice === 0 ? -1.35 : choice === 1 ? 1.35 : state.cam.x,
        z: (state.pos + 1) * 4,
        y: 1.7
    };

    state.anim = {
        start: performance.now(),
        from: {...state.cam},
        to: target,
        correct,
        choice
    };

    liveNode.textContent = timeout
        ? "시간이 다 되었어요"
        : "점프!";

    if (!state.motion) {
        if (correct) state.cam = target;
        finishJump();
    }
}

function finishJump() {
    state.anim = null;
    state.phase = "feedback";

    const feedback = state.feedback;

    if (!feedback.correct) state.lives--;

    document.getElementById("lives").textContent =
        "♥".repeat(state.lives) +
        "♡".repeat(3 - state.lives);

    mapButton.disabled = false;

    let message;

    if (feedback.timeout) {
        message = "시간이 다 되었어요. 목숨이 하나 줄었어요.";
    } else if (feedback.correct) {
        message = "착지 성공! 확인 자료와 일치하는 소식이에요.";
    } else {
        message = "풍덩! 선택한 소식이 확인 자료와 달라요.";
    }

    liveNode.textContent = feedback.correct
        ? "✓ 안전하게 착지했어요"
        : "직전 발판으로 돌아왔어요";

    document.getElementById("feedback").innerHTML = `
        <section class="card feedback ${feedback.correct ? "" : "bad"}">
            <h3>${escapeHTML(message)}</h3>

            ${feedback.stones.map((stone, index) => `
                <details open>
                    <summary>
                        ${index === 0 ? "A · 왼쪽" : "B · 오른쪽"}
                        — ${stone.real ? "자료와 일치" : "자료와 불일치"}
                    </summary>
                    <p>${escapeHTML(stone.why)}</p>
                </details>
            `).join("")}

            <p class="muted">
                이 문제는 제시된 자료와의 일치를 판단해요.
                실제 상황에서 확인 자료가 없다는 것만으로
                가짜라고 단정하지 마세요.
            </p>

            <button class="primary" id="next">
                ${state.lives <= 0
                    ? "다시 도전하기"
                    : feedback.correct
                        ? "다음 발판으로 →"
                        : "같은 구간 다시 판단하기"}
            </button>
        </section>
    `;

    button("next", () => {
        if (state.lives <= 0) {
            startRiver();
            return;
        }

        if (feedback.correct) state.pos++;

        if (state.pos >= state.round.length) {
            showClear();
        } else {
            beginTurn();
        }
    });

    document.getElementById("feedback").scrollIntoView({
        behavior: "auto",
        block: "nearest"
    });
}

function showClear() {
    state.phase = "clear";

    if (!state.cleared.includes(state.stage)) {
        state.cleared.push(state.stage);
    }

    mount(`
        <section class="card">
            <div class="row">
                ${MASCOT ? `
                    <div class="mascot">
                        <img
                            alt="축하하는 깡지 캐릭터"
                            src="${MASCOT}">
                    </div>
                ` : '<span style="font-size:64px">🏁</span>'}

                <div>
                    <span class="eyebrow">RIVER CLEARED</span>
                    <h1>무사히 건넜어요!</h1>
                </div>
            </div>

            <p>
                <b>${escapeHTML(stage().tactic)}</b> 수법을 알아보고,
                ${state.round.length}개 구간을 건넜어요.
            </p>

            <div class="note">
                ${escapeHTML(stage().mission.spot)}
            </div>

            <p>
                실제 연락에서도
                <b>멈추기 → 별도 경로로 확인하기 → 행동하기</b>를
                기억하세요.
            </p>

            <button id="back" class="primary">
                지도에서 다음 강 고르기 →
            </button>
        </section>
    `);

    button("back", showMap);
}

mapButton.onclick = showMap;


// ─────────────────────────────────────
// 키보드 조작
// ─────────────────────────────────────

document.addEventListener("keydown", event => {
    if (
        state.phase !== "river" ||
        event.repeat ||
        event.ctrlKey ||
        event.metaKey ||
        event.altKey
    ) {
        return;
    }

    if (
        ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName) ||
        event.target.isContentEditable
    ) {
        return;
    }

    const key = event.key.toLowerCase();

    if (["arrowleft", "a", "arrowright", "d"].includes(key)) {
        event.preventDefault();
        selectStone(key === "arrowleft" || key === "a" ? 0 : 1);
        return;
    }

    if (key === "arrowup" || key === "w" || key === " ") {
        if (
            key === " " &&
            event.target.closest("button, summary, a") &&
            !["jump", "select0", "select1"].includes(event.target.id)
        ) {
            return;
        }

        event.preventDefault();
        act(state.selected);
    }
});


// ─────────────────────────────────────
// 1인칭 원근 화면
// ─────────────────────────────────────

function draw(time) {
    if (!canvas || !ctx) return;

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const ratio = Math.min(devicePixelRatio || 1, 2);

    if (
        canvas.width !== Math.round(width * ratio) ||
        canvas.height !== Math.round(height * ratio)
    ) {
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
    }

    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);

    const camera = state.cam;
    const focal = Math.min(width * .66, 560);
    const horizon = height * .37;

    function project(point) {
        const distance = point[2] - camera.z;

        if (distance < .18) return null;

        return [
            width / 2 + (point[0] - camera.x) * focal / distance,
            horizon + (camera.y - point[1]) * focal / distance
        ];
    }

    function polygon(points, color, stroke) {
        const projected = points.map(project);

        if (projected.some(point => !point)) return;

        ctx.beginPath();

        projected.forEach((point, index) => {
            if (index === 0) {
                ctx.moveTo(point[0], point[1]);
            } else {
                ctx.lineTo(point[0], point[1]);
            }
        });

        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();

        if (stroke) {
            ctx.strokeStyle = stroke;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }

    function block(x, y, z, sx, sy, sz, color, top) {
        polygon(
            [
                [x - sx, y - sy, z - sz],
                [x + sx, y - sy, z - sz],
                [x + sx, y, z - sz],
                [x - sx, y, z - sz]
            ],
            color,
            "#416c6470"
        );

        polygon(
            [
                [x - sx, y, z - sz],
                [x + sx, y, z - sz],
                [x + sx, y, z + sz],
                [x - sx, y, z + sz]
            ],
            top,
            "#416c6470"
        );

        polygon(
            [
                [x + sx, y - sy, z - sz],
                [x + sx, y - sy, z + sz],
                [x + sx, y, z + sz],
                [x + sx, y, z - sz]
            ],
            color
        );
    }

    const sky = ctx.createLinearGradient(0, 0, 0, height);

    sky.addColorStop(0, "#a9dee5");
    sky.addColorStop(.5, "#e2f0d3");
    sky.addColorStop(.51, "#54b9bc");
    sky.addColorStop(1, "#247f91");

    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = "#fff1ad";
    ctx.beginPath();
    ctx.arc(width * .8, height * .16, 24, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#7eaa86";
    ctx.beginPath();
    ctx.moveTo(0, horizon + 10);

    for (let x = 0; x <= width; x += 40) {
        ctx.lineTo(x, horizon - 20 - Math.sin(x * .018) * 17);
    }

    ctx.lineTo(width, horizon + 30);
    ctx.fill();

    ctx.fillStyle = "#51aeb6";
    ctx.fillRect(0, horizon + 22, width, height);

    polygon(
        [
            [-30, 0, camera.z + .3],
            [-5, 0, camera.z + .3],
            [-5, 0, 40],
            [-30, 0, 40]
        ],
        "#6f9d68"
    );

    polygon(
        [
            [5, 0, camera.z + .3],
            [30, 0, camera.z + .3],
            [30, 0, 40],
            [5, 0, 40]
        ],
        "#6f9d68"
    );

    const flow = state.motion ? time * .00045 : 0;

    ctx.strokeStyle = "#c3f3df66";
    ctx.lineWidth = 2;

    for (let z = Math.ceil(camera.z) + 1; z < camera.z + 32; z += 1.7) {
        for (let x = -4; x < 5; x += 2.3) {
            const zz = z + (flow % 1.7);

            const start = project([
                x + Math.sin(z) * .3,
                .015,
                zz
            ]);

            const end = project([
                x + .9 + Math.sin(z) * .3,
                .015,
                zz
            ]);

            if (start && end) {
                ctx.beginPath();
                ctx.moveTo(...start);
                ctx.lineTo(...end);
                ctx.stroke();
            }
        }
    }

    for (let z = 36; z > camera.z + 1; z -= 4) {
        for (const x of [-7.5, 7.5]) {
            block(x, 1, z, .18, 1, .18, "#866d48", "#9e8057");
            block(x, 2.7, z, .8, 1.6, .8, "#417a58", "#76a96b");
        }
    }

    const goal = (state.round.length + 1) * 4;

    block(0, .35, goal, 4, .8, 1.7, "#7f8d63", "#b1be80");
    block(.2, 3.4, goal, .05, 3, .05, "#faf6df", "#ffffff");

    polygon(
        [
            [.25, 3.4, goal],
            [1.8, 3.4, goal],
            [1.8, 2.6, goal],
            [.25, 2.6, goal]
        ],
        "#e7a257"
    );

    for (let row = state.round.length; row >= 1; row--) {
        const z = row * 4;

        if (z < camera.z + .2) continue;

        for (let index = 0; index < 2; index++) {
            const active = row === state.pos + 1;
            const selected = active && state.selected === index;
            let y = .28;

            if (
                state.anim &&
                !state.anim.correct &&
                state.anim.choice === index &&
                active
            ) {
                const progress = Math.min(
                    1,
                    (time - state.anim.start) / 1100
                );

                if (progress > .6) {
                    y -= Math.pow((progress - .6) / .4, 2) * 2;
                }
            }

            const x = index === 0 ? -1.35 : 1.35;

            block(
                x,
                y,
                z,
                .9,
                .48,
                .8,
                selected ? "#b98443" : "#657d77",
                selected ? "#f5d58a" : active ? "#e4e7d3" : "#a4b8a3"
            );

            if (active) {
                const label = project([x, y + .65, z]);

                if (label) {
                    ctx.fillStyle = "#173d39";
                    ctx.font = "bold 19px sans-serif";
                    ctx.textAlign = "center";
                    ctx.fillText(index === 0 ? "A" : "B", label[0], label[1]);
                }
            }
        }
    }

    let lift = 0;

    if (state.phase === "jump" && state.motion && state.anim) {
        const progress = Math.min(
            1,
            (time - state.anim.start) / 1100
        );
        lift = Math.sin(progress * Math.PI) * 24;
    }

    ctx.strokeStyle = "#775c39";
    ctx.lineWidth = 3;

    for (const side of [-1, 1]) {
        ctx.save();
        ctx.translate(
            width / 2 + side * width * .36,
            height + 12 - lift
        );
        ctx.rotate(side * -.25);
        ctx.fillStyle = "#f2d59a";
        ctx.fillRect(-26, -49, 52, 78);
        ctx.strokeRect(-26, -49, 52, 78);
        ctx.fillStyle = "#438474";
        ctx.fillRect(-29, -2, 58, 32);
        ctx.restore();
    }

    if (state.anim && !state.anim.correct) {
        const progress = (time - state.anim.start) / 1100;

        if (progress > .75) {
            const alpha =
                Math.sin((progress - .75) / .25 * Math.PI) * .65;

            ctx.fillStyle = `rgba(42,150,173,${Math.max(0, alpha)})`;
            ctx.fillRect(0, 0, width, height);
        }
    }
}


// ─────────────────────────────────────
// 타이머와 점프 애니메이션
// ─────────────────────────────────────

function frame(time) {
    const elapsed = Math.min(
        .08,
        (time - (state.last || time)) / 1000
    );

    state.last = time;

    if (!document.hidden) {
        if (
            state.phase === "river" &&
            state.pressure &&
            !state.hinted
        ) {
            state.remaining -= elapsed;
            updateClock();

            if (state.remaining <= 0) {
                act(null, true);
            }
        }

        if (state.anim) {
            const animation = state.anim;

            const progress = Math.min(
                1,
                (time - animation.start) / 1100
            );

            const easing =
                progress * progress * (3 - 2 * progress);

            state.cam = {
                x: animation.from.x +
                    (animation.to.x - animation.from.x) * easing,
                z: animation.from.z +
                    (animation.to.z - animation.from.z) * easing,
                y: 1.7 + Math.sin(progress * Math.PI) * 1.55
            };

            if (!animation.correct && progress > .72) {
                state.cam.y -= ((progress - .72) / .28) * 2;
            }

            if (progress >= 1) {
                state.cam = animation.correct
                    ? animation.to
                    : animation.from;

                finishJump();
            }
        }

        draw(time);
    }

    requestAnimationFrame(frame);
}

document.addEventListener("visibilitychange", () => {
    state.last = 0;

    if (state.phase === "jump" && state.anim) {
        state.cam = state.anim.correct
            ? state.anim.to
            : state.anim.from;

        finishJump();
    }
});

showIntro();
requestAnimationFrame(frame);
</script>
</body>
</html>
"""


# ─────────────────────────────────────
# 기존 마스코트 연결
# ─────────────────────────────────────

mascot_path = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "mascot_six.png"
)

mascot_data = ""

if mascot_path.is_file():
    mascot_data = (
        "data:image/png;base64,"
        + base64.b64encode(
            mascot_path.read_bytes()
        ).decode("ascii")
    )


# HTML 안에 문제 데이터 넣기
stage_json = json.dumps(
    STAGES,
    ensure_ascii=False,
).replace("<", "\\u003c")

game_html = (
    GAME_HTML
    .replace("__STAGES__", stage_json)
    .replace("__MASCOT__", mascot_data)
)


# 게임 실행
components.html(
    game_html,
    height=1150,
    scrolling=True,
)

st.caption(
    "진행은 게임 화면이 열린 동안 유지됩니다. "
    "새로고침하거나 다른 페이지로 이동하면 초기화될 수 있어요. "
    "방탈출 랭킹에는 저장하지 않습니다."
)
