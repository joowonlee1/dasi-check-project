import html
import random
import time

import streamlit as st
from mascot_ui import show_mascot


# 모든 도시·계정·기관·게시물은 교육용 가상 자료입니다. (가상 도시 '도토리시')
# 케임브리지대 'Bad News' 게임처럼, 속이는 쪽의 수법을 약하게 미리 체험하고(접종 이론)
# 받는 사람 입장에서 그 수법을 가려내는 연습을 합니다.
KEY = "river_v3"
LIVES = 3
ACCOUNT = "@도토리속보24"

# 스테이지마다 수법 하나를 다룹니다.
# mission: 가짜 계정 운영자가 되어 수법 카드를 고르는 부분
# pairs: 받는 사람이 되어 건너는 두 갈래 돌 (둘 다 가짜일 수도 있어요)
STAGES = [
    {
        "tactic": "사칭",
        "title": "믿을 만한 이름 빌리기",
        "icon": "🎭",
        "level": 1,
        "time": 18,
        "pauses": 2,
        "mission": {
            "prompt": "도토리시 공원에 새 분수가 생긴대요. 팔로워를 가장 많이 모을 방법을 골라 보세요.",
            "choices": [
                {"label": "🎭 계정 이름을 ‘도토리시청 공식’으로 바꾸고 시청 로고와 비슷한 프로필 사진을 단다",
                 "followers": 800, "good": True,
                 "post": "[도토리시청 공식] 새 분수 개장 기념! 오늘 오후 3시 선착순 100명 무료 아이스크림 🍦 공유하면 2개!"},
                {"label": "📰 ‘공원 분수 공사가 끝났대요’라고 들은 그대로 쓴다",
                 "followers": 20, "good": False,
                 "post": "공원 분수 공사가 끝났대요. 언제 틀어 주는지는 모르겠어요."},
                {"label": "😂 분수 사진에 웃긴 자막만 달아 올린다",
                 "followers": 60, "good": False,
                 "post": "(분수 사진) 드디어 우리 동네에도 바다가… 🌊"},
            ],
            "why": "사람들은 내용보다 ‘누가 말했는지’를 먼저 보고 믿어요. 공식 기관처럼 보이기만 해도 의심이 확 줄어요.",
            "spot": "인증 표시, 계정 개설일, 이전 게시물을 확인하고, 기관 홈페이지에 같은 공지가 있는지 찾아봐요.",
        },
        "pairs": [
            {
                "stones": [
                    {"sender": "도토리시청 · 인증된 계정 · 2015년 개설", "real": True,
                     "text": "공원 분수 시운전은 이번 주 토요일입니다. 자세한 일정은 시청 홈페이지 공지를 확인해 주세요.",
                     "why": "오래된 인증 계정이고, 홈페이지에서 다시 확인하라고 해요."},
                    {"sender": "도토리시청 공식 · 개설 3일 · 게시물 2개", "real": False,
                     "text": "분수 개장 기념! 오늘 오후 3시 선착순 무료 아이스크림. 공유하면 2개!",
                     "why": "이름만 공식처럼 지은 새 계정이에요. 공유를 조건으로 걸어요."},
                ],
                "clue": "두 계정의 개설일과 게시물 수를 비교해 보세요.",
            },
            {
                "stones": [
                    {"sender": "도토리일보 · 언론사 홈페이지 기사", "real": True,
                     "text": "시립 도서관, 다음 달부터 일요일에도 문 열어… 시의회 예산안 통과",
                     "why": "언론사 홈페이지에 올라온 기사이고, 근거(예산안 통과)를 밝혀요."},
                    {"sender": "‘도토리 일보 속보’ 캡처 · 단체 대화방에서 퍼짐", "real": False,
                     "text": "[속보] 도서관 24시간 무료 개방 확정!! 시장님 직접 발표",
                     "why": "언론사 이름을 띄어 써서 흉내 냈고, 원문 없이 캡처로만 퍼졌어요."},
                ],
                "clue": "언론사 이름이 똑같나요? 원래 기사는 어디 있나요?",
            },
            {
                "stones": [
                    {"sender": "도토리소방서 · 인증된 계정", "real": True,
                     "text": "건조한 날씨가 이어져 이번 주 공원 내 취사를 금지합니다.",
                     "why": "기관다운 차분한 안내이고, 인증된 계정이에요."},
                    {"sender": "도토리소방서 · 팔로워 12명", "real": False,
                     "text": "불꽃 축제 취소래요ㅠㅠ 소방서가 방금 발표했어요!! 다들 빨리 공유해 주세요",
                     "why": "기관 이름을 썼지만 말투와 팔로워 수가 공식 계정과 달라요."},
                ],
                "clue": "공식 기관이 ‘ㅠㅠ’, ‘다들 공유’라고 쓸까요?",
            },
            {
                "stones": [
                    {"sender": "도토리시 교육청 · 공식 홈페이지 공지", "real": True,
                     "text": "다음 주 수요일 개교기념일로 쉬는 학교 목록을 안내합니다.",
                     "why": "공식 홈페이지 공지이고, 구체적인 목록을 줘요."},
                    {"sender": "‘교육청 관계자’ · 익명 계정", "real": False,
                     "text": "내일 도토리시 전체 학교 휴교 확정이래요! 관계자한테 직접 들었어요.",
                     "why": "‘관계자’라는 말로 권위를 빌렸지만 누구인지 알 수 없어요."},
                ],
                "clue": "‘관계자’는 누구일까요? 이름도 소속도 없어요.",
            },
        ],
    },
    {
        "tactic": "감정 자극",
        "title": "화나고 불안하게 만들기",
        "icon": "😡",
        "level": 2,
        "time": 16,
        "pauses": 2,
        "mission": {
            "prompt": "평범한 소식은 잘 안 퍼져요. ‘붕어빵 노점 2곳이 옆 골목으로 옮긴다’는 소식을 어떻게 올릴까요?",
            "choices": [
                {"label": "😡 제목에 ‘충격’, ‘분노’를 넣고 누군가를 탓하며 크게 부풀린다",
                 "followers": 1500, "good": True,
                 "post": "【충격】 도토리시, 붕어빵 노점 전부 강제 철거?! 이게 맞습니까 😡😡 (실제: 노점 2곳 위치 이동)"},
                {"label": "📊 ‘노점 2곳이 다음 주부터 시장 옆 골목으로 옮겨요’라고 정리한다",
                 "followers": 40, "good": False,
                 "post": "붕어빵 노점 2곳이 다음 주부터 시장 입구 옆 골목으로 옮긴대요."},
                {"label": "❓ ‘붕어빵 어디로 갔는지 아시는 분?’이라고 묻는다",
                 "followers": 90, "good": False,
                 "post": "시장 앞 붕어빵 어디로 갔는지 아시는 분…?"},
            ],
            "why": "화나거나 불안하면 확인하기 전에 먼저 공유하게 돼요. 감정이 큰 글일수록 더 빨리, 더 멀리 퍼져요.",
            "spot": "마음이 크게 흔들리는 글일수록 한 번 멈추고, 숫자(‘전부’ vs ‘2곳’)와 원문 출처를 확인해요.",
        },
        "pairs": [
            {
                "stones": [
                    {"sender": "도토리일보", "real": True,
                     "text": "붕어빵 노점 2곳, 다음 주부터 시장 입구 옆 골목으로 이전",
                     "why": "숫자와 장소가 구체적이고 차분해요."},
                    {"sender": "@도토리분노", "real": False,
                     "text": "【충격】 붕어빵 노점 전부 강제 철거… 시장님 이게 맞습니까?? 😡😡",
                     "why": "‘전부’로 부풀리고 분노를 부추겨요."},
                ],
                "clue": "‘전부’와 ‘2곳’, 어느 쪽이 구체적인가요?",
            },
            {
                "stones": [
                    {"sender": "@속보는여기", "real": False,
                     "text": "이 글 보고 울었습니다… 도토리 보호소가 내일 문을 닫는대요ㅠㅠ 지금 바로 공유해 주세요",
                     "why": "출처 없이 슬픔과 다급함만 내세워요."},
                    {"sender": "@도토리맘카페", "real": False,
                     "text": "어린이집 간식에 이상한 게 나왔대요!! 사진은 못 올리지만 진짜예요. 다 퍼뜨려 주세요",
                     "why": "‘사진은 못 올리지만’이라며 확인을 막고 불안을 퍼뜨려요."},
                ],
                "clue": "둘 다 출처 없이 ‘지금 공유’를 재촉하고 있지 않나요?",
            },
            {
                "stones": [
                    {"sender": "도토리 동물보호소 · 인증된 계정", "real": True,
                     "text": "이번 주말 입양 행사를 엽니다. 봉사자 사전 신청은 홈페이지에서 받아요.",
                     "why": "공식 계정이고, 할 수 있는 일을 차분히 안내해요."},
                    {"sender": "@동물사랑도토리", "real": False,
                     "text": "보호소 강아지들이 오늘 밤 모두 다른 곳으로 보내진대요. 막으려면 이 글 1만 공유!!",
                     "why": "공유 수로 무언가를 막을 수 있다며 감정을 이용해요."},
                ],
                "clue": "공유 수로 무언가를 막을 수 있을까요?",
            },
            {
                "stones": [
                    {"sender": "도토리일보", "real": True,
                     "text": "시내버스 요금 다음 달 100원 인상… 시 ‘연료비 상승분 반영’",
                     "why": "반갑지 않은 소식이지만 금액과 이유를 정확히 밝혀요."},
                    {"sender": "@시민의소리", "real": False,
                     "text": "버스 요금 2배 폭등!!! 서민은 걸어 다니라는 거냐",
                     "why": "숫자를 부풀려 분노를 키워요."},
                ],
                "clue": "숫자를 부풀리고 분노를 키우는 쪽은?",
            },
        ],
    },
    {
        "tactic": "가짜 증거",
        "title": "그럴듯한 증거 만들기",
        "icon": "📸",
        "level": 3,
        "time": 15,
        "pauses": 1,
        "mission": {
            "prompt": "팔로워들이 ‘증거 있어?’라고 물어요. 어떻게 할까요?",
            "choices": [
                {"label": "📸 몇 년 전 다른 도시 사진을 가져와 ‘오늘 도토리시’라고 붙인다",
                 "followers": 2000, "good": True,
                 "post": "[사진] 오늘 아침 도토리강 완전 범람!! 시내 다 잠김 (사진: 3년 전 다른 도시 태풍 사진)"},
                {"label": "🙅 ‘증거는 없어요, 들은 이야기예요’라고 솔직히 말한다",
                 "followers": -100, "good": False,
                 "post": "사실 증거는 없어요. 들은 이야기라 확실하지 않아요."},
                {"label": "🔗 시청 공지 원문을 찾아서 붙인다",
                 "followers": 30, "good": False,
                 "post": "시청 공지 원문: 도토리강 산책로 일부 통제 (오늘 07:00)"},
            ],
            "why": "사진이나 캡처가 붙으면 사실처럼 느껴져요. 하지만 사진이 ‘언제, 어디서’ 찍혔는지는 잘 보이지 않아요.",
            "spot": "누가 언제 찍었는지 확인하고, 이미지 검색으로 원본을 찾아봐요. 캡처는 원문이 있는지 확인해요.",
        },
        "pairs": [
            {
                "stones": [
                    {"sender": "도토리일보 · 사진: 본사 기자, 오늘 07:30", "real": True,
                     "text": "밤사이 내린 비로 도토리강 수위 상승… 산책로 일부 통제",
                     "why": "누가 언제 찍었는지 밝혔고, 내용도 과장 없이 구체적이에요."},
                    {"sender": "@실시간도토리 · 사진 출처 없음", "real": False,
                     "text": "[사진] 도토리강 완전 범람, 시내 전부 잠김!!",
                     "why": "사진 출처와 날짜가 없고, 내용을 부풀렸어요."},
                ],
                "clue": "사진에 누가, 언제 찍었는지 적혀 있나요?",
            },
            {
                "stones": [
                    {"sender": "도토리시청 · 인증된 계정", "real": True,
                     "text": "공원 공사 현장 사진을 공개합니다. (촬영일 10월 14일, 시청 홍보팀)",
                     "why": "촬영일과 찍은 곳을 밝혔어요."},
                    {"sender": "@도토리팩트", "real": False,
                     "text": "공원 공사 중 고대 유물 발견! [사진] — 사진 속 표지판 글자가 다른 나라 말이에요",
                     "why": "다른 곳 사진을 가져온 흔적이 사진 안에 남아 있어요."},
                ],
                "clue": "사진 속에 도토리시가 아닌 흔적이 있나요?",
            },
            {
                "stones": [
                    {"sender": "@뉴스캡처", "real": False,
                     "text": "뉴스 화면 캡처: ‘도토리시, 내일부터 전 시민 지원금’ (방송사 다시보기에는 그런 뉴스가 없음)",
                     "why": "방송 화면처럼 꾸민 캡처예요. 원래 방송에 없어요."},
                    {"sender": "@도토리소식통", "real": False,
                     "text": "시장님 문자 캡처 입수: ‘내일 깜짝 발표 있음’ (보낸 사람 번호는 가려짐)",
                     "why": "누가 보냈는지 가린 캡처는 누구나 만들 수 있어요."},
                ],
                "clue": "캡처는 누구나 만들 수 있어요. 원본을 확인할 수 있나요?",
            },
            {
                "stones": [
                    {"sender": "도토리일보 · 시의회 생중계 다시보기 연결", "real": True,
                     "text": "시의회, 공공자전거 확대안 통과",
                     "why": "원본 영상을 직접 찾아볼 수 있어요."},
                    {"sender": "@짤방도토리 · 영상 날짜 없음", "real": False,
                     "text": "시의회 회의 중 의원들 몸싸움 영상!! (알고 보니 다른 나라 의회 영상)",
                     "why": "날짜도 장소도 없는 영상을 도토리시 일처럼 붙였어요."},
                ],
                "clue": "원본 영상을 찾아볼 수 있는 쪽은?",
            },
        ],
    },
    {
        "tactic": "편 가르기",
        "title": "우리 편 vs 저쪽 편",
        "icon": "👥",
        "level": 4,
        "time": 14,
        "pauses": 1,
        "mission": {
            "prompt": "팔로워들이 계속 머물게 하고 싶어요. 어떤 글을 올릴까요?",
            "choices": [
                {"label": "👥 ‘슈크림파가 팥붕파를 공격한다’는 글로 두 편을 싸우게 만든다",
                 "followers": 2500, "good": True,
                 "post": "슈크림파들이 팥붕 가게 리뷰 테러 중이랍니다… 팥붕파 여러분, 가만히 있을 건가요? 🔥"},
                {"label": "🤝 ‘팥도 슈크림도 다 맛있다’는 글을 올린다",
                 "followers": 30, "good": False,
                 "post": "팥도 슈크림도 다 맛있어요. 오늘은 반반 사 먹었어요 😋"},
                {"label": "🗳️ ‘팥 vs 슈크림’ 투표만 올린다",
                 "followers": 200, "good": False,
                 "post": "여러분의 붕어빵 취향은? 🗳️ 팥 / 슈크림"},
            ],
            "why": "사람들이 ‘우리 편’과 ‘저쪽 편’으로 나뉘면, 우리 편 말은 확인하지 않고 믿고 저쪽 말은 무조건 의심하게 돼요.",
            "spot": "‘저쪽 사람들은 다 ~래’, ‘우리가 공격받고 있다’ 같은 말이 보이면 멈추고 근거를 찾아요.",
        },
        "pairs": [
            {
                "stones": [
                    {"sender": "도토리일보", "real": True,
                     "text": "붕어빵 축제 설문: 팥 54%, 슈크림 46%… 상인들 ‘둘 다 판매 늘어’",
                     "why": "숫자를 근거로 양쪽을 고르게 전해요."},
                    {"sender": "@팥붕수호대", "real": False,
                     "text": "슈크림파가 팥붕 가게 리뷰 테러 중!! 우리도 가만있으면 안 됩니다",
                     "why": "근거 없이 ‘저쪽이 공격한다’며 우리 편을 부추겨요."},
                ],
                "clue": "‘저쪽이 공격한다’며 우리 편을 부추기는 쪽은?",
            },
            {
                "stones": [
                    {"sender": "@도토리남부", "real": False,
                     "text": "북쪽 동네 사람들 때문에 우리 동네 버스가 줄었대요. 다 그쪽 탓이에요",
                     "why": "근거 없이 다른 동네 사람들을 탓해요."},
                    {"sender": "@도토리북부", "real": False,
                     "text": "남쪽 사람들이 축제 예산을 다 가져갔다는 소문 들었어요? 이번엔 참지 맙시다",
                     "why": "소문을 근거로 편을 갈라 화를 부추겨요."},
                ],
                "clue": "둘 다 근거 없이 다른 동네를 탓하고 있지 않나요?",
            },
            {
                "stones": [
                    {"sender": "도토리시청 · 인증된 계정", "real": True,
                     "text": "버스 노선 개편 설명회를 엽니다. 동네별 변경 내용은 홈페이지 자료에서 확인하세요.",
                     "why": "모두가 확인할 수 있는 자료를 공개해요."},
                    {"sender": "@도토리진실", "real": False,
                     "text": "노선 개편은 특정 동네만 챙기려는 거예요! 우리 동네만 손해 보는 거 아시죠?",
                     "why": "자료 대신 ‘우리만 손해’라는 감정으로 편을 갈라요."},
                ],
                "clue": "자료를 보여 주는 쪽과 ‘우리만 손해’를 강조하는 쪽의 차이는?",
            },
            {
                "stones": [
                    {"sender": "도토리일보 칼럼 · 필자 이름과 직함 표시", "real": True,
                     "text": "축제 예산, 동네별 배분 기준부터 공개해야",
                     "why": "의견이지만 누가 썼는지 밝히고, 확인할 방법(기준 공개)을 말해요."},
                    {"sender": "@익명의도토리인", "real": False,
                     "text": "모두가 아는 사실: 그 동네 사람들은 원래 다 이기적이에요",
                     "why": "‘모두가 아는 사실’이라며 한 집단 전체를 몰아세워요."},
                ],
                "clue": "의견을 말할 때 이름과 근거를 밝히는 쪽은?",
            },
        ],
    },
    {
        "tactic": "음모론",
        "title": "아무도 말해 주지 않는 ‘진실’",
        "icon": "🧩",
        "level": 5,
        "time": 12,
        "pauses": 1,
        "mission": {
            "prompt": "팔로워들이 의심을 시작했어요. 계정을 지킬 마지막 한 방은?",
            "choices": [
                {"label": "🧩 ‘와이파이가 끊기는 건 비둘기 때문이고 시청은 알고도 숨긴다’고 쓰고, 반박하면 ‘그것도 조작’이라고 한다",
                 "followers": 3000, "good": True,
                 "post": "도토리시 와이파이가 자꾸 끊기는 진짜 이유: 비둘기 🐦 시청은 알고도 숨기는 중. 이 글 곧 삭제될지도 몰라요."},
                {"label": "🙇 그동안의 글이 틀렸다고 인정하고 정정한다",
                 "followers": -500, "good": False,
                 "post": "그동안 올린 글 중 확인되지 않은 내용이 있었습니다. 정정합니다."},
                {"label": "🔇 당분간 아무것도 올리지 않는다",
                 "followers": 0, "good": False,
                 "post": "(조용…)"},
            ],
            "why": "음모론은 반박까지 ‘숨기려는 증거’로 바꿔 버려서, 어떤 사실을 보여 줘도 믿음이 흔들리지 않게 만들어요.",
            "spot": "‘곧 삭제될지도’, ‘언론이 말 안 해 주는’, ‘반박도 조작’ 같은 말은 확인을 막는 장치예요. 확인할 수 있는 근거가 있는지부터 봐요.",
        },
        "pairs": [
            {
                "stones": [
                    {"sender": "도토리시청 · 인증된 계정", "real": True,
                     "text": "공공 와이파이 끊김은 장비가 낡아서 생긴 문제입니다. 11월까지 교체하겠습니다.",
                     "why": "원인과 해결 계획을 공개해요."},
                    {"sender": "@깨어있는도토리", "real": False,
                     "text": "와이파이 끊김의 진짜 이유는 아무도 말해 주지 않아요. 이 글 곧 삭제될 수 있으니 저장하세요.",
                     "why": "‘곧 삭제될지도’라는 말로 확인 대신 저장과 공유를 재촉해요."},
                ],
                "clue": "‘곧 삭제될지도’는 무엇을 막으려는 말일까요?",
            },
            {
                "stones": [
                    {"sender": "도토리일보 · 팩트체크", "real": True,
                     "text": "‘비둘기가 와이파이 끊는다’는 소문, 사실 아냐… 통신 전문가 ‘장비 문제’",
                     "why": "전문가 확인을 거친 팩트체크예요."},
                    {"sender": "@진실탐사", "real": False,
                     "text": "팩트체크 기사도 조작입니다. 기자들도 다 한통속이에요.",
                     "why": "반박까지 ‘조작’이라고 해서 어떤 증거도 받아들이지 않게 만들어요."},
                ],
                "clue": "반박까지 ‘조작’이라고 하면, 어떤 증거가 나와도 생각이 바뀔까요?",
            },
            {
                "stones": [
                    {"sender": "@비밀문서", "real": False,
                     "text": "시청 내부 문서 유출: ‘비둘기 프로젝트’ (문서 출처 없음)",
                     "why": "확인할 수 없는 ‘비밀 문서’를 내세워요."},
                    {"sender": "@도토리각성", "real": False,
                     "text": "TV는 절대 알려 주지 않는 진실. 알고 싶으면 우리 단체방으로 오세요.",
                     "why": "‘숨겨진 진실’을 미끼로 확인이 어려운 다른 곳으로 끌어들여요."},
                ],
                "clue": "둘 다 확인할 수 없는 ‘비밀’을 내세우고 있지 않나요?",
            },
            {
                "stones": [
                    {"sender": "도토리 과학관 · 인증된 계정", "real": True,
                     "text": "주말 특강: 와이파이는 어떻게 작동할까? 직접 실험해 봐요. 누구나 참여 가능",
                     "why": "누구나 직접 보고 질문할 수 있는 공개 행사예요."},
                    {"sender": "@숨겨진진실", "real": False,
                     "text": "과학관 특강은 진실을 감추려는 쇼! 비둘기 이야기 꺼내면 쫓겨난대요.",
                     "why": "공개된 행사까지 ‘숨기려는 쇼’로 몰아가요."},
                ],
                "clue": "누구나 확인할 수 있는 행사를 ‘쇼’라고 몰아가는 쪽은?",
            },
        ],
    },
]


st.markdown(
    """
    <style>
    .rv-river {background:linear-gradient(180deg,#BFE7F5 0%,#7CC8E6 100%); border-radius:18px;
               padding:18px 12px; margin:6px 0 14px; display:flex; align-items:center;
               justify-content:space-between; gap:4px; overflow-x:auto;}
    .rv-bank {font-size:1.9rem; flex:0 0 auto;}
    .rv-stone {flex:0 0 42px; width:42px; height:42px; border-radius:50%; background:#94A3B8;
               display:flex; align-items:center; justify-content:center; font-size:1.3rem;
               border:3px solid #64748B;}
    .rv-stone.done {background:#86EFAC; border-color:#16A34A;}
    .rv-stone.here {background:#FDE68A; border-color:#D97706;}
    .rv-msg {background:#0B1220; color:#F1F5F9; border-radius:16px; padding:14px 16px; margin:4px 0 10px;
             border:2px solid #FBBF24; min-height:140px;}
    .rv-msg.real {border-color:#22C55E;}
    .rv-msg.fake {border-color:#EF4444;}
    .rv-msg .from {font-size:.8rem; color:#AAB7C6; margin-bottom:6px;}
    .rv-msg .body {font-size:1.02rem; line-height:1.6; word-break:keep-all; overflow-wrap:anywhere;}
    .rv-tag {display:inline-block; font-weight:800; font-size:.85rem; margin-bottom:4px;}
    .rv-post {background:#fff; border:1px solid #CBD5E1; border-radius:16px; padding:12px 14px; margin:6px 0 12px; color:#172B3A;}
    .rv-post .who {font-weight:800; font-size:.9rem;}
    .rv-post .who span {font-weight:400; color:#64748B;}
    .rv-post .txt {margin-top:6px; line-height:1.6;}
    .rv-clock {font-weight:800; color:#B45309;}
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(text):
    return html.escape(str(text))


def stars(level):
    return "★" * level + "☆" * (5 - level)


# ─────────────────────────────────────
# 게임 상태
# ─────────────────────────────────────

def new_game():
    return {
        "started": False,
        "timer": True,          # 시간 제한 사용 여부
        "cleared": [],          # 깬 스테이지 번호
        "stage": None,          # 현재 스테이지 번호
        "phase": "mission",     # mission(운영자 미션) / explain(수법 공개) / river / clear / fail
        "picked": None,         # 이번 미션에서 고른 카드 번호
        "followers": 0,         # 가짜 계정 팔로워 (게임 속 숫자)
        "used": [],             # 미션에서 수법 카드를 고른 스테이지
        "order": [],            # 이번 도전의 칸 순서
        "flips": [],            # 칸마다 돌 순서를 뒤집었는지
        "pos": 0,
        "lives": LIVES,
        "pauses": 0,
        "paused": False,
        "deadline": 0.0,
        "feedback": None,
        # 잠깐!을 쓰고 고른 판단과 바로 고른 판단의 [맞힌 수, 전체 수]
        "stats": {"paused": [0, 0], "rushed": [0, 0]},
    }


def game():
    if KEY not in st.session_state:
        st.session_state[KEY] = new_game()
    return st.session_state[KEY]


def start():
    g = game()
    g["started"] = True
    g["timer"] = st.session_state.get("rv_timer_toggle", True)


def open_stage(index):
    g = game()
    g["stage"] = index
    g["phase"] = "mission"
    g["picked"] = None
    g["feedback"] = None


def pick_card(index):
    g = game()
    if g["picked"] is not None:
        return
    stage = STAGES[g["stage"]]
    card = stage["mission"]["choices"][index]
    g["picked"] = index
    g["followers"] = max(0, g["followers"] + card["followers"])
    if card["good"] and g["stage"] not in g["used"]:
        g["used"].append(g["stage"])
    g["phase"] = "explain"


def begin_step(g):
    g["paused"] = False
    g["deadline"] = time.time() + STAGES[g["stage"]]["time"]


def go_river():
    g = game()
    stage = STAGES[g["stage"]]
    count = len(stage["pairs"])
    g["order"] = random.sample(range(count), count)
    g["flips"] = [random.random() < 0.5 for _ in range(count)]
    g["pos"] = 0
    g["lives"] = LIVES
    g["pauses"] = stage["pauses"]
    g["feedback"] = None
    g["phase"] = "river"
    begin_step(g)


def current_pair(g):
    return STAGES[g["stage"]]["pairs"][g["order"][g["pos"]]]


def shown_stones(g):
    stones = current_pair(g)["stones"]
    return list(reversed(stones)) if g["flips"][g["pos"]] else list(stones)


def press_pause():
    g = game()
    if g["pauses"] > 0 and not g["paused"] and not g["feedback"]:
        g["pauses"] -= 1
        g["paused"] = True


def record(g, correct, choice, timeout=False):
    bucket = g["stats"]["paused" if g["paused"] else "rushed"]
    bucket[0] += 1 if correct else 0
    bucket[1] += 1
    g["feedback"] = {
        "correct": correct,
        "timeout": timeout,
        "choice": choice,
        "stones": shown_stones(g),
    }
    if correct:
        g["pos"] += 1
    else:
        g["lives"] -= 1


def choose(choice):
    """choice: 0(🅰 돌), 1(🅱 돌), 'none'(둘 다 위험해요)"""
    g = game()
    if g["feedback"] or g["phase"] != "river":
        return
    stones = shown_stones(g)
    any_real = any(stone["real"] for stone in stones)
    if choice == "none":
        correct = not any_real
    else:
        correct = stones[choice]["real"]
    record(g, correct, choice)


def sink():
    """시간이 다 되면 돌이 가라앉아요. 고르지 않은 것도 틀린 것으로 셉니다."""
    g = game()
    if not g["feedback"] and g["phase"] == "river":
        record(g, False, None, timeout=True)


def next_step():
    g = game()
    g["feedback"] = None
    if g["lives"] <= 0:
        g["phase"] = "fail"
    elif g["pos"] >= len(STAGES[g["stage"]]["pairs"]):
        if g["stage"] not in g["cleared"]:
            g["cleared"].append(g["stage"])
        g["phase"] = "clear"
    else:
        begin_step(g)


def back_to_map():
    g = game()
    g["stage"] = None
    g["feedback"] = None


def restart_all():
    timer = game()["timer"]
    st.session_state[KEY] = new_game()
    st.session_state[KEY]["started"] = True
    st.session_state[KEY]["timer"] = timer


def toggle_timer():
    g = game()
    g["timer"] = not g["timer"]


# ─────────────────────────────────────
# 화면 조각
# ─────────────────────────────────────

def river_html(pos, total):
    stones = []
    for i in range(total):
        if i < pos:
            stones.append('<div class="rv-stone done">✓</div>')
        elif i == pos:
            stones.append('<div class="rv-stone here">🧍</div>')
        else:
            stones.append('<div class="rv-stone"></div>')
    goal = "🧍🏁" if pos >= total else "🏁"
    return f'<div class="rv-river"><div class="rv-bank">🏝️</div>{"".join(stones)}<div class="rv-bank">{goal}</div></div>'


def card_html(item, tag="", kind=""):
    tag_html = f'<div class="rv-tag">{esc(tag)}</div>' if tag else ""
    return (
        f'<div class="rv-msg {kind}">{tag_html}<div class="from">{esc(item["sender"])}</div>'
        f'<div class="body">{esc(item["text"])}</div></div>'
    )


def post_html(text, followers):
    return (
        f'<div class="rv-post"><div class="who">{esc(ACCOUNT)} <span>· 가상 계정 · 팔로워 {followers:,}명</span></div>'
        f'<div class="txt">{esc(text)}</div></div>'
    )


def rate(bucket):
    right, total = bucket
    return f"{round(right * 100 / total)}% ({right}/{total})" if total else "기록 없음"


def show_stats(g):
    paused, rushed = g["stats"]["paused"], g["stats"]["rushed"]
    left, right = st.columns(2)
    left.metric("✋ 잠깐! 하고 고른 판단", rate(paused))
    right.metric("⚡ 바로 고른 판단", rate(rushed))
    if paused[1] and rushed[1]:
        if paused[0] / paused[1] > rushed[0] / rushed[1]:
            st.success("멈추고 단서를 본 판단이 더 정확했어요. 실제 상황에서도 **잠깐!** 멈추는 게 가장 강한 무기예요.")
        else:
            st.info("이번에는 바로 고른 판단도 정확했어요! 그래도 실제 상황에서는 헷갈릴수록 한 번 멈춰요.")
    elif not paused[1]:
        st.info("아직 잠깐!을 한 번도 쓰지 않았어요. 다음엔 헷갈릴 때 써 보세요.")
    st.caption("판단 횟수가 적어서 참고용 기록이에요. 시간이 다 되어 가라앉은 돌은 ‘바로 고른 판단’의 오답으로 셉니다.")


def show_intro():
    show_mascot("suspicious", "오늘은 속이는 쪽이 되어 봐요. 수법을 알면 속지 않아요!")
    st.markdown(
        "### 🕹️ 미션: 가짜 계정을 운영하고, 그 수법을 가려내라!\n"
        f"가상 도시 **도토리시**에서 당신은 가짜 소식 계정 **{ACCOUNT}**의 운영자예요. "
        f"스테이지는 **{len(STAGES)}개**, 스테이지마다 속이는 수법 하나를 다뤄요.\n\n"
        "1. **🕹️ 운영자 미션** — 수법 카드를 골라 팔로워를 모아요. 어떤 수법이 왜 먹히는지 직접 느껴 봐요.\n"
        "2. **🔍 수법 공개** — 방금 쓴 수법이 왜 통하는지, 받는 사람은 어떻게 알아챌 수 있는지 알려 줘요.\n"
        "3. **🌊 강 건너기** — 이번엔 **받는 사람**이 되어 두 갈래 돌 중 **진짜 소식**을 골라 밟아요. "
        "**두 돌이 모두 가짜일 때도 있어요** → 🚫 *둘 다 위험해요*\n"
        "4. **⏳ 가라앉는 돌 · ✋ 잠깐!** — 시간 안에 못 고르면 돌이 가라앉아요. 잠깐!을 누르면 시간이 멈추고 단서가 보여요.\n\n"
        "스테이지가 올라갈수록 시간이 짧아지고 잠깐! 횟수가 줄어요. (난이도 ★1~★5)"
    )
    st.info(
        "📚 케임브리지대 연구진의 게임 ‘Bad News’처럼, 속이는 수법을 약하게 미리 체험하면 "
        "실제로 덜 속는다는 ‘접종 이론’을 바탕으로 했어요. 피싱도 사칭·감정 자극·가짜 증거 같은 같은 수법을 써요."
    )
    st.toggle("⏳ 시간 제한 켜기 (끄면 천천히 할 수 있어요)", value=True, key="rv_timer_toggle")
    st.caption("모든 도시·계정·게시물은 교육용 가상 자료예요. 실존 인물이나 실제 사건과 관계없어요.")
    st.button("🕹️ 운영 시작하기", type="primary", on_click=start)


def show_map(g):
    done = len(g["cleared"])
    if done == 0:
        show_mascot("welcome", "첫 번째 수법부터 써 볼까요? 그다음엔 받는 사람이 되어 가려내요.", width=90)
    elif done < len(STAGES):
        show_mascot("welcome", f"벌써 {done}개의 수법을 알아냈어요! 다음 수법도 파헤쳐 봐요.", width=90)
    st.markdown(f"### 🗺️ 스테이지 지도 · {done} / {len(STAGES)} 통과")
    st.progress(done / len(STAGES))
    left, mid, right = st.columns([2, 2, 1.4])
    left.metric("📈 가짜 계정 팔로워", f"{g['followers']:,}명")
    mid.caption(f"⏳ 시간 제한: {'켜짐' if g['timer'] else '꺼짐'}")
    right.button(
        "시간 제한 끄기" if g["timer"] else "시간 제한 켜기",
        on_click=toggle_timer,
        key="rv_timer_switch",
        use_container_width=True,
    )

    for index, stage in enumerate(STAGES):
        unlocked = index == 0 or (index - 1) in g["cleared"]
        cleared = index in g["cleared"]
        mark = "✅" if cleared else ("🔓" if unlocked else "🔒")
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{mark} STAGE {index + 1} · {stage['icon']} {stage['tactic']} — {stage['title']}**")
                st.caption(
                    f"난이도 {stars(stage['level'])} · 돌 {stage['time']}초 · 잠깐! {stage['pauses']}번"
                    if unlocked else "앞 스테이지를 통과하면 열려요."
                )
            with right:
                st.button(
                    "다시 하기" if cleared else "도전",
                    key=f"rv_open_{index}",
                    disabled=not unlocked,
                    use_container_width=True,
                    on_click=open_stage,
                    args=(index,),
                )

    if done == len(STAGES):
        show_ending(g)


def show_ending(g):
    show_mascot("trophy", "모든 수법을 써 보고, 모두 가려냈어요! 이제 쉽게 속지 않을 거예요.")
    st.success(f"🏅 **수법 해독가 배지 획득!** · 가짜 계정 최종 팔로워 {g['followers']:,}명")
    st.markdown(
        "#### 🔍 정체 공개\n"
        f"당신이 운영한 {ACCOUNT}처럼, 실제 가짜 계정도 사실이 아니라 **수법**으로 사람을 모아요. "
        "팔로워가 많다고 믿을 만한 계정은 아니에요."
    )
    st.markdown("#### ✋ 멈춘 판단 vs 바로 고른 판단")
    show_stats(g)
    st.markdown(
        "#### 🧩 이 수법들, 피싱에서도 똑같이 쓰여요\n"
        "| 수법 | 가짜 소식에서 | 피싱에서 |\n"
        "|---|---|---|\n"
        "| 🎭 사칭 | ‘시청 공식’ 흉내 계정 | 검찰·은행·택배사 사칭 |\n"
        "| 😡 감정 자극 | 충격·분노 제목 | ‘엄마 급해’, ‘계좌 정지’ |\n"
        "| 📸 가짜 증거 | 남의 사진, 가짜 캡처 | 가짜 공문, 가짜 사건번호 |\n"
        "| 👥 편 가르기 | 우리 편 vs 저쪽 편 | ‘가족에게도 말하지 마세요’ |\n"
        "| 🧩 음모론 | ‘아무도 말 안 해 주는 진실’ | ‘은행 직원도 한패예요’ |\n"
    )
    st.button("🔄 처음부터 다시", on_click=restart_all)


def show_mission(g, stage):
    mission = stage["mission"]
    show_mascot("phone", f"{ACCOUNT} 운영 중… 이번엔 어떤 수법을 써 볼까요?", width=90)
    st.markdown(f"### 🕹️ 운영자 미션 · STAGE {g['stage'] + 1} {stage['icon']} {stage['tactic']}")
    st.caption(f"난이도 {stars(stage['level'])} · 현재 팔로워 {g['followers']:,}명")
    st.write(mission["prompt"])
    order = list(range(len(mission["choices"])))
    random.Random(g["stage"]).shuffle(order)
    for index in order:
        st.button(
            mission["choices"][index]["label"],
            key=f"rv_card_{g['stage']}_{index}",
            use_container_width=True,
            on_click=pick_card,
            args=(index,),
        )
    st.caption("게임 속 가상 계정이에요. 실제로 이런 글을 올리면 다른 사람에게 피해를 줄 수 있어요.")
    st.button("🗺️ 지도로 돌아가기", on_click=back_to_map)


def show_explain(g, stage):
    mission = stage["mission"]
    card = mission["choices"][g["picked"]]
    best = next(choice for choice in mission["choices"] if choice["good"])
    change = card["followers"]

    if card["good"]:
        st.success(f"📈 팔로워 +{change:,}명! 수법이 통했어요.")
    elif change < 0:
        st.warning(f"📉 팔로워 {change:,}명. 솔직한 글은 오히려 덜 퍼졌어요.")
    else:
        st.info(f"📊 팔로워 +{change:,}명. 사실대로 쓴 글은 조용히 지나갔어요.")

    st.markdown(post_html(card["post"], g["followers"]), unsafe_allow_html=True)

    if not card["good"]:
        st.markdown("**가짜 계정 운영자라면 이렇게 했을 거예요 👇**")
        st.markdown(post_html(best["post"], g["followers"] + best["followers"]), unsafe_allow_html=True)

    show_mascot("hint", f"이번 수법은 ‘{stage['tactic']}’이에요.", width=90)
    st.markdown(f"**🧪 왜 먹혔을까?** {mission['why']}")
    st.info(f"🛡️ **받는 사람은 이렇게 알아챌 수 있어요** · {mission['spot']}")
    st.button("🌊 이제 받는 사람이 되어 강 건너기", type="primary", on_click=go_river)


@st.fragment(run_every=1)
def countdown():
    """1초마다 남은 시간을 보여 주고, 시간이 다 되면 돌을 가라앉혀요."""
    g = game()
    if g["phase"] != "river" or g["feedback"] or g["paused"] or not g["timer"]:
        return
    limit = STAGES[g["stage"]]["time"]
    left = g["deadline"] - time.time()
    if left <= 0:
        sink()
        st.rerun()
    seconds = max(0, int(left + 0.999))
    st.progress(max(0.0, min(1.0, left / limit)))
    st.markdown(f'<span class="rv-clock">⏳ {seconds}초 뒤 돌이 가라앉아요</span>', unsafe_allow_html=True)


def show_feedback(g):
    feedback = g["feedback"]
    stones = feedback["stones"]
    both_fake = not any(stone["real"] for stone in stones)

    if feedback["timeout"]:
        st.error("🫧 꼬르륵… 시간이 다 되어 돌이 가라앉았어요. 목숨이 하나 줄었어요.")
        show_mascot("suspicious", "급하면 판단이 흐려져요. 다음엔 잠깐!으로 시간을 멈춰 봐요.", width=80)
    elif feedback["correct"] and both_fake:
        st.success("🚫 정답! 두 돌 모두 가짜였어요. 밟지 않고 돌아간 게 맞아요.")
    elif feedback["correct"]:
        st.success("✅ 진짜 소식을 밟았어요! 한 칸 앞으로!")
    elif feedback["choice"] == "none":
        st.error("💦 아쉬워요! 한쪽은 진짜 소식이었어요. 모든 걸 의심하는 것도 함정이에요.")
    elif both_fake:
        st.error("💦 풍덩! 두 돌 모두 가짜였어요. ‘둘 다 위험해요’를 골라야 했어요.")
    else:
        st.error("💦 풍덩! 가짜 소식을 밟았어요. 목숨이 하나 줄었어요.")

    if feedback["correct"] and g["pos"] >= len(STAGES[g["stage"]]["pairs"]):
        show_mascot("shield", "마지막 돌까지 무사히 건넜어요!", width=80)

    left, right = st.columns(2)
    for column, stone, name in ((left, stones[0], "🅰"), (right, stones[1], "🅱")):
        with column:
            tag = f"{name} · {'✅ 진짜' if stone['real'] else '🚨 가짜'}"
            st.markdown(card_html(stone, tag, "real" if stone["real"] else "fake"), unsafe_allow_html=True)
            st.caption(stone["why"])
    st.button("다음 ➡️", type="primary", on_click=next_step)


def show_river(g, stage):
    total = len(stage["pairs"])
    st.markdown(f"### 🌊 STAGE {g['stage'] + 1} · {stage['icon']} {stage['tactic']} 가려내기")
    st.markdown(
        f"**난이도** {stars(stage['level'])}  ·  "
        f"**목숨** {'❤️' * g['lives']}{'🤍' * (LIVES - g['lives'])}  ·  "
        f"**✋ 잠깐!** {g['pauses']} / {stage['pauses']}  ·  "
        f"**건넌 칸** {g['pos']} / {total}"
    )
    st.markdown(river_html(g["pos"], total), unsafe_allow_html=True)

    if g["feedback"]:
        show_feedback(g)
        return

    pair = current_pair(g)
    stone_a, stone_b = shown_stones(g)

    st.markdown(f"#### 칸 {g['pos'] + 1} · 진짜 소식은 어느 돌일까요?")

    if g["paused"]:
        show_mascot("stop", f"잠깐! 시간이 멈췄어요. 단서 · {pair['clue']}", width=90)
    elif g["timer"]:
        countdown()

    left, right = st.columns(2)
    with left:
        st.markdown(card_html(stone_a, "🅰 돌"), unsafe_allow_html=True)
        st.button("🅰 이 돌을 밟는다", use_container_width=True, on_click=choose, args=(0,), key=f"rv_a_{g['pos']}")
    with right:
        st.markdown(card_html(stone_b, "🅱 돌"), unsafe_allow_html=True)
        st.button("🅱 이 돌을 밟는다", use_container_width=True, on_click=choose, args=(1,), key=f"rv_b_{g['pos']}")

    st.button(
        "🚫 둘 다 위험해요 (밟지 않고 돌아간다)",
        use_container_width=True,
        on_click=choose,
        args=("none",),
        key=f"rv_none_{g['pos']}",
    )

    if not g["paused"]:
        st.button(
            f"✋ 잠깐! (남은 횟수 {g['pauses']})",
            on_click=press_pause,
            disabled=g["pauses"] <= 0,
            key=f"rv_pause_{g['pos']}",
        )


def show_clear(g, stage):
    show_mascot("escape", f"‘{stage['tactic']}’ 수법을 가려내고 건너편에 도착했어요!", width=100)
    st.markdown(river_html(len(stage["pairs"]), len(stage["pairs"])), unsafe_allow_html=True)
    st.success(f"🎉 STAGE {g['stage'] + 1} 통과! 남은 목숨 {'❤️' * g['lives']}")
    st.write(f"**기억할 점:** {stage['mission']['spot']}")
    with st.expander("✋ 지금까지의 판단 기록 보기"):
        show_stats(g)
    st.button("🗺️ 지도에서 다음 스테이지로", type="primary", on_click=back_to_map)


def show_fail(g, stage):
    show_mascot("retry", "괜찮아요. 수법을 다시 떠올리고, 이번엔 잠깐!도 써 봐요.", width=100)
    st.error(f"💦 STAGE {g['stage'] + 1}에서 목숨을 모두 잃었어요.")
    st.write(f"**다시 떠올려 봐요:** {stage['mission']['spot']}")
    st.button("🌊 바로 다시 건너기", type="primary", on_click=go_river)
    st.button("🗺️ 지도로 돌아가기", on_click=back_to_map)


# ─────────────────────────────────────
# 화면
# ─────────────────────────────────────

st.title("🌊 잠깐! · 진짜·가짜 강 건너기")
st.write("가짜 계정 운영자가 되어 **속이는 수법**을 써 보고, 받는 사람이 되어 **그 수법을 가려내요**.")
st.caption("교육용 가상 게임입니다. 모든 도시·계정·게시물은 가상이며, 실제 게시나 공유는 일어나지 않아요.")

g = game()

if not g["started"]:
    show_intro()
elif g["stage"] is None:
    show_map(g)
else:
    stage = STAGES[g["stage"]]
    if g["phase"] == "mission":
        show_mission(g, stage)
    elif g["phase"] == "explain":
        show_explain(g, stage)
    elif g["phase"] == "river":
        show_river(g, stage)
    elif g["phase"] == "clear":
        show_clear(g, stage)
    else:
        show_fail(g, stage)
