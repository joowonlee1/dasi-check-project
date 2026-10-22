# 6번 페이지 전체 교체용. 추가 패키지나 인터넷 게임 라이브러리가 필요하지 않습니다.
import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.title("🌊 진짜·가짜 강 건너기")
st.caption("가상 소식의 수법을 배우고, 직접 판단하며 건너는 1인칭 점프 게임")

STAGES = [{'tactic': '사칭',
  'title': '믿을 만한 이름 빌리기',
  'icon': '🎭',
  'level': 1,
  'time': 18,
  'pauses': 2,
  'mission': {'prompt': '도토리시 공원에 새 분수가 생긴대요. 팔로워를 가장 많이 모을 방법을 골라 보세요.',
              'choices': [{'label': '🎭 계정 이름을 ‘도토리시청 공식’으로 바꾸고 시청 로고와 비슷한 프로필 사진을 단다',
                           'followers': 800,
                           'good': True,
                           'post': '[도토리시청 공식] 새 분수 개장 기념! 오늘 오후 3시 선착순 100명 무료 아이스크림 🍦 공유하면 2개!'},
                          {'label': '📰 ‘공원 분수 공사가 끝났대요’라고 들은 그대로 쓴다',
                           'followers': 20,
                           'good': False,
                           'post': '공원 분수 공사가 끝났대요. 언제 틀어 주는지는 모르겠어요.'},
                          {'label': '😂 분수 사진에 웃긴 자막만 달아 올린다',
                           'followers': 60,
                           'good': False,
                           'post': '(분수 사진) 드디어 우리 동네에도 바다가… 🌊'}],
              'why': '사람들은 내용보다 ‘누가 말했는지’를 먼저 보고 믿어요. 공식 기관처럼 보이기만 해도 의심이 확 줄어요.',
              'spot': '인증 표시, 계정 개설일, 이전 게시물을 확인하고, 기관 홈페이지에 같은 공지가 있는지 찾아봐요.'},
  'pairs': [{'stones': [{'sender': '도토리시청 · 인증된 계정 · 2015년 개설',
                         'real': True,
                         'text': '공원 분수 시운전은 이번 주 토요일입니다. 자세한 일정은 시청 홈페이지 공지를 확인해 주세요.',
                         'why': '오래된 인증 계정이고, 홈페이지에서 다시 확인하라고 해요.'},
                        {'sender': '도토리시청 공식 · 개설 3일 · 게시물 2개',
                         'real': False,
                         'text': '분수 개장 기념! 오늘 오후 3시 선착순 무료 아이스크림. 공유하면 2개!',
                         'why': '이름만 공식처럼 지은 새 계정이에요. 공유를 조건으로 걸어요.'}],
             'clue': '두 계정의 개설일과 게시물 수를 비교해 보세요.'},
            {'stones': [{'sender': '도토리일보 · 언론사 홈페이지 기사',
                         'real': True,
                         'text': '시립 도서관, 다음 달부터 일요일에도 문 열어… 시의회 예산안 통과',
                         'why': '언론사 홈페이지에 올라온 기사이고, 근거(예산안 통과)를 밝혀요.'},
                        {'sender': '‘도토리 일보 속보’ 캡처 · 단체 대화방에서 퍼짐',
                         'real': False,
                         'text': '[속보] 도서관 24시간 무료 개방 확정!! 시장님 직접 발표',
                         'why': '언론사 이름을 띄어 써서 흉내 냈고, 원문 없이 캡처로만 퍼졌어요.'}],
             'clue': '언론사 이름이 똑같나요? 원래 기사는 어디 있나요?'},
            {'stones': [{'sender': '도토리소방서 · 인증된 계정',
                         'real': True,
                         'text': '건조한 날씨가 이어져 이번 주 공원 내 취사를 금지합니다.',
                         'why': '기관다운 차분한 안내이고, 인증된 계정이에요.'},
                        {'sender': '도토리소방서 · 팔로워 12명',
                         'real': False,
                         'text': '불꽃 축제 취소래요ㅠㅠ 소방서가 방금 발표했어요!! 다들 빨리 공유해 주세요',
                         'why': '기관 이름을 썼지만 말투와 팔로워 수가 공식 계정과 달라요.'}],
             'clue': '공식 기관이 ‘ㅠㅠ’, ‘다들 공유’라고 쓸까요?'},
            {'stones': [{'sender': '도토리시 교육청 · 공식 홈페이지 공지',
                         'real': True,
                         'text': '다음 주 수요일 개교기념일로 쉬는 학교 목록을 안내합니다.',
                         'why': '공식 홈페이지 공지이고, 구체적인 목록을 줘요.'},
                        {'sender': '‘교육청 관계자’ · 익명 계정',
                         'real': False,
                         'text': '내일 도토리시 전체 학교 휴교 확정이래요! 관계자한테 직접 들었어요.',
                         'why': '‘관계자’라는 말로 권위를 빌렸지만 누구인지 알 수 없어요.'}],
             'clue': '‘관계자’는 누구일까요? 이름도 소속도 없어요.'}]},
 {'tactic': '감정 자극',
  'title': '화나고 불안하게 만들기',
  'icon': '😡',
  'level': 2,
  'time': 16,
  'pauses': 2,
  'mission': {'prompt': '평범한 소식은 잘 안 퍼져요. ‘붕어빵 노점 2곳이 옆 골목으로 옮긴다’는 소식을 어떻게 올릴까요?',
              'choices': [{'label': '😡 제목에 ‘충격’, ‘분노’를 넣고 누군가를 탓하며 크게 부풀린다',
                           'followers': 1500,
                           'good': True,
                           'post': '【충격】 도토리시, 붕어빵 노점 전부 강제 철거?! 이게 맞습니까 😡😡 (실제: 노점 2곳 위치 이동)'},
                          {'label': '📊 ‘노점 2곳이 다음 주부터 시장 옆 골목으로 옮겨요’라고 정리한다',
                           'followers': 40,
                           'good': False,
                           'post': '붕어빵 노점 2곳이 다음 주부터 시장 입구 옆 골목으로 옮긴대요.'},
                          {'label': '❓ ‘붕어빵 어디로 갔는지 아시는 분?’이라고 묻는다',
                           'followers': 90,
                           'good': False,
                           'post': '시장 앞 붕어빵 어디로 갔는지 아시는 분…?'}],
              'why': '화나거나 불안하면 확인하기 전에 먼저 공유하게 돼요. 감정이 큰 글일수록 더 빨리, 더 멀리 퍼져요.',
              'spot': '마음이 크게 흔들리는 글일수록 한 번 멈추고, 숫자(‘전부’ vs ‘2곳’)와 원문 출처를 확인해요.'},
  'pairs': [{'stones': [{'sender': '도토리일보',
                         'real': True,
                         'text': '붕어빵 노점 2곳, 다음 주부터 시장 입구 옆 골목으로 이전',
                         'why': '숫자와 장소가 구체적이고 차분해요.'},
                        {'sender': '@도토리분노',
                         'real': False,
                         'text': '【충격】 붕어빵 노점 전부 강제 철거… 시장님 이게 맞습니까?? 😡😡',
                         'why': '‘전부’로 부풀리고 분노를 부추겨요.'}],
             'clue': '‘전부’와 ‘2곳’, 어느 쪽이 구체적인가요?'},
            {'stones': [{'sender': '@속보는여기',
                         'real': False,
                         'text': '이 글 보고 울었습니다… 도토리 보호소가 내일 문을 닫는대요ㅠㅠ 지금 바로 공유해 주세요',
                         'why': '출처 없이 슬픔과 다급함만 내세워요.'},
                        {'sender': '@도토리맘카페',
                         'real': False,
                         'text': '어린이집 간식에 이상한 게 나왔대요!! 사진은 못 올리지만 진짜예요. 다 퍼뜨려 주세요',
                         'why': '‘사진은 못 올리지만’이라며 확인을 막고 불안을 퍼뜨려요.'}],
             'clue': '둘 다 출처 없이 ‘지금 공유’를 재촉하고 있지 않나요?'},
            {'stones': [{'sender': '도토리 동물보호소 · 인증된 계정',
                         'real': True,
                         'text': '이번 주말 입양 행사를 엽니다. 봉사자 사전 신청은 홈페이지에서 받아요.',
                         'why': '공식 계정이고, 할 수 있는 일을 차분히 안내해요.'},
                        {'sender': '@동물사랑도토리',
                         'real': False,
                         'text': '보호소 강아지들이 오늘 밤 모두 다른 곳으로 보내진대요. 막으려면 이 글 1만 공유!!',
                         'why': '공유 수로 무언가를 막을 수 있다며 감정을 이용해요.'}],
             'clue': '공유 수로 무언가를 막을 수 있을까요?'},
            {'stones': [{'sender': '도토리일보',
                         'real': True,
                         'text': '시내버스 요금 다음 달 100원 인상… 시 ‘연료비 상승분 반영’',
                         'why': '반갑지 않은 소식이지만 금액과 이유를 정확히 밝혀요.'},
                        {'sender': '@시민의소리',
                         'real': False,
                         'text': '버스 요금 2배 폭등!!! 서민은 걸어 다니라는 거냐',
                         'why': '숫자를 부풀려 분노를 키워요.'}],
             'clue': '숫자를 부풀리고 분노를 키우는 쪽은?'}]},
 {'tactic': '가짜 증거',
  'title': '그럴듯한 증거 만들기',
  'icon': '📸',
  'level': 3,
  'time': 15,
  'pauses': 1,
  'mission': {'prompt': '팔로워들이 ‘증거 있어?’라고 물어요. 어떻게 할까요?',
              'choices': [{'label': '📸 몇 년 전 다른 도시 사진을 가져와 ‘오늘 도토리시’라고 붙인다',
                           'followers': 2000,
                           'good': True,
                           'post': '[사진] 오늘 아침 도토리강 완전 범람!! 시내 다 잠김 (사진: 3년 전 다른 도시 태풍 사진)'},
                          {'label': '🙅 ‘증거는 없어요, 들은 이야기예요’라고 솔직히 말한다',
                           'followers': -100,
                           'good': False,
                           'post': '사실 증거는 없어요. 들은 이야기라 확실하지 않아요.'},
                          {'label': '🔗 시청 공지 원문을 찾아서 붙인다',
                           'followers': 30,
                           'good': False,
                           'post': '시청 공지 원문: 도토리강 산책로 일부 통제 (오늘 07:00)'}],
              'why': '사진이나 캡처가 붙으면 사실처럼 느껴져요. 하지만 사진이 ‘언제, 어디서’ 찍혔는지는 잘 보이지 않아요.',
              'spot': '누가 언제 찍었는지 확인하고, 이미지 검색으로 원본을 찾아봐요. 캡처는 원문이 있는지 확인해요.'},
  'pairs': [{'stones': [{'sender': '도토리일보 · 사진: 본사 기자, 오늘 07:30',
                         'real': True,
                         'text': '밤사이 내린 비로 도토리강 수위 상승… 산책로 일부 통제',
                         'why': '누가 언제 찍었는지 밝혔고, 내용도 과장 없이 구체적이에요.'},
                        {'sender': '@실시간도토리 · 사진 출처 없음',
                         'real': False,
                         'text': '[사진] 도토리강 완전 범람, 시내 전부 잠김!!',
                         'why': '사진 출처와 날짜가 없고, 내용을 부풀렸어요.'}],
             'clue': '사진에 누가, 언제 찍었는지 적혀 있나요?'},
            {'stones': [{'sender': '도토리시청 · 인증된 계정',
                         'real': True,
                         'text': '공원 공사 현장 사진을 공개합니다. (촬영일 10월 14일, 시청 홍보팀)',
                         'why': '촬영일과 찍은 곳을 밝혔어요.'},
                        {'sender': '@도토리팩트',
                         'real': False,
                         'text': '공원 공사 중 고대 유물 발견! [사진] — 사진 속 표지판 글자가 다른 나라 말이에요',
                         'why': '다른 곳 사진을 가져온 흔적이 사진 안에 남아 있어요.'}],
             'clue': '사진 속에 도토리시가 아닌 흔적이 있나요?'},
            {'stones': [{'sender': '@뉴스캡처',
                         'real': False,
                         'text': '뉴스 화면 캡처: ‘도토리시, 내일부터 전 시민 지원금’ (방송사 다시보기에는 그런 뉴스가 없음)',
                         'why': '방송 화면처럼 꾸민 캡처예요. 원래 방송에 없어요.'},
                        {'sender': '@도토리소식통',
                         'real': False,
                         'text': '시장님 문자 캡처 입수: ‘내일 깜짝 발표 있음’ (보낸 사람 번호는 가려짐)',
                         'why': '누가 보냈는지 가린 캡처는 누구나 만들 수 있어요.'}],
             'clue': '캡처는 누구나 만들 수 있어요. 원본을 확인할 수 있나요?'},
            {'stones': [{'sender': '도토리일보 · 시의회 생중계 다시보기 연결',
                         'real': True,
                         'text': '시의회, 공공자전거 확대안 통과',
                         'why': '원본 영상을 직접 찾아볼 수 있어요.'},
                        {'sender': '@짤방도토리 · 영상 날짜 없음',
                         'real': False,
                         'text': '시의회 회의 중 의원들 몸싸움 영상!! (알고 보니 다른 나라 의회 영상)',
                         'why': '날짜도 장소도 없는 영상을 도토리시 일처럼 붙였어요.'}],
             'clue': '원본 영상을 찾아볼 수 있는 쪽은?'}]},
 {'tactic': '편 가르기',
  'title': '우리 편 vs 저쪽 편',
  'icon': '👥',
  'level': 4,
  'time': 14,
  'pauses': 1,
  'mission': {'prompt': '팔로워들이 계속 머물게 하고 싶어요. 어떤 글을 올릴까요?',
              'choices': [{'label': '👥 ‘슈크림파가 팥붕파를 공격한다’는 글로 두 편을 싸우게 만든다',
                           'followers': 2500,
                           'good': True,
                           'post': '슈크림파들이 팥붕 가게 리뷰 테러 중이랍니다… 팥붕파 여러분, 가만히 있을 건가요? 🔥'},
                          {'label': '🤝 ‘팥도 슈크림도 다 맛있다’는 글을 올린다',
                           'followers': 30,
                           'good': False,
                           'post': '팥도 슈크림도 다 맛있어요. 오늘은 반반 사 먹었어요 😋'},
                          {'label': '🗳️ ‘팥 vs 슈크림’ 투표만 올린다',
                           'followers': 200,
                           'good': False,
                           'post': '여러분의 붕어빵 취향은? 🗳️ 팥 / 슈크림'}],
              'why': '사람들이 ‘우리 편’과 ‘저쪽 편’으로 나뉘면, 우리 편 말은 확인하지 않고 믿고 저쪽 말은 무조건 의심하게 돼요.',
              'spot': '‘저쪽 사람들은 다 ~래’, ‘우리가 공격받고 있다’ 같은 말이 보이면 멈추고 근거를 찾아요.'},
  'pairs': [{'stones': [{'sender': '도토리일보',
                         'real': True,
                         'text': '붕어빵 축제 설문: 팥 54%, 슈크림 46%… 상인들 ‘둘 다 판매 늘어’',
                         'why': '숫자를 근거로 양쪽을 고르게 전해요.'},
                        {'sender': '@팥붕수호대',
                         'real': False,
                         'text': '슈크림파가 팥붕 가게 리뷰 테러 중!! 우리도 가만있으면 안 됩니다',
                         'why': '근거 없이 ‘저쪽이 공격한다’며 우리 편을 부추겨요.'}],
             'clue': '‘저쪽이 공격한다’며 우리 편을 부추기는 쪽은?'},
            {'stones': [{'sender': '@도토리남부',
                         'real': False,
                         'text': '북쪽 동네 사람들 때문에 우리 동네 버스가 줄었대요. 다 그쪽 탓이에요',
                         'why': '근거 없이 다른 동네 사람들을 탓해요.'},
                        {'sender': '@도토리북부',
                         'real': False,
                         'text': '남쪽 사람들이 축제 예산을 다 가져갔다는 소문 들었어요? 이번엔 참지 맙시다',
                         'why': '소문을 근거로 편을 갈라 화를 부추겨요.'}],
             'clue': '둘 다 근거 없이 다른 동네를 탓하고 있지 않나요?'},
            {'stones': [{'sender': '도토리시청 · 인증된 계정',
                         'real': True,
                         'text': '버스 노선 개편 설명회를 엽니다. 동네별 변경 내용은 홈페이지 자료에서 확인하세요.',
                         'why': '모두가 확인할 수 있는 자료를 공개해요.'},
                        {'sender': '@도토리진실',
                         'real': False,
                         'text': '노선 개편은 특정 동네만 챙기려는 거예요! 우리 동네만 손해 보는 거 아시죠?',
                         'why': '자료 대신 ‘우리만 손해’라는 감정으로 편을 갈라요.'}],
             'clue': '자료를 보여 주는 쪽과 ‘우리만 손해’를 강조하는 쪽의 차이는?'},
            {'stones': [{'sender': '도토리일보 칼럼 · 필자 이름과 직함 표시',
                         'real': True,
                         'text': '축제 예산, 동네별 배분 기준부터 공개해야',
                         'why': '의견이지만 누가 썼는지 밝히고, 확인할 방법(기준 공개)을 말해요.'},
                        {'sender': '@익명의도토리인',
                         'real': False,
                         'text': '모두가 아는 사실: 그 동네 사람들은 원래 다 이기적이에요',
                         'why': '‘모두가 아는 사실’이라며 한 집단 전체를 몰아세워요.'}],
             'clue': '의견을 말할 때 이름과 근거를 밝히는 쪽은?'}]},
 {'tactic': '음모론',
  'title': '아무도 말해 주지 않는 ‘진실’',
  'icon': '🧩',
  'level': 5,
  'time': 12,
  'pauses': 1,
  'mission': {'prompt': '팔로워들이 의심을 시작했어요. 계정을 지킬 마지막 한 방은?',
              'choices': [{'label': '🧩 ‘와이파이가 끊기는 건 비둘기 때문이고 시청은 알고도 숨긴다’고 쓰고, 반박하면 ‘그것도 조작’이라고 한다',
                           'followers': 3000,
                           'good': True,
                           'post': '도토리시 와이파이가 자꾸 끊기는 진짜 이유: 비둘기 🐦 시청은 알고도 숨기는 중. 이 글 곧 삭제될지도 몰라요.'},
                          {'label': '🙇 그동안의 글이 틀렸다고 인정하고 정정한다',
                           'followers': -500,
                           'good': False,
                           'post': '그동안 올린 글 중 확인되지 않은 내용이 있었습니다. 정정합니다.'},
                          {'label': '🔇 당분간 아무것도 올리지 않는다', 'followers': 0, 'good': False, 'post': '(조용…)'}],
              'why': '음모론은 반박까지 ‘숨기려는 증거’로 바꿔 버려서, 어떤 사실을 보여 줘도 믿음이 흔들리지 않게 만들어요.',
              'spot': '‘곧 삭제될지도’, ‘언론이 말 안 해 주는’, ‘반박도 조작’ 같은 말은 확인을 막는 장치예요. 확인할 수 있는 근거가 있는지부터 봐요.'},
  'pairs': [{'stones': [{'sender': '도토리시청 · 인증된 계정',
                         'real': True,
                         'text': '공공 와이파이 끊김은 장비가 낡아서 생긴 문제입니다. 11월까지 교체하겠습니다.',
                         'why': '원인과 해결 계획을 공개해요.'},
                        {'sender': '@깨어있는도토리',
                         'real': False,
                         'text': '와이파이 끊김의 진짜 이유는 아무도 말해 주지 않아요. 이 글 곧 삭제될 수 있으니 저장하세요.',
                         'why': '‘곧 삭제될지도’라는 말로 확인 대신 저장과 공유를 재촉해요.'}],
             'clue': '‘곧 삭제될지도’는 무엇을 막으려는 말일까요?'},
            {'stones': [{'sender': '도토리일보 · 팩트체크',
                         'real': True,
                         'text': '‘비둘기가 와이파이 끊는다’는 소문, 사실 아냐… 통신 전문가 ‘장비 문제’',
                         'why': '전문가 확인을 거친 팩트체크예요.'},
                        {'sender': '@진실탐사',
                         'real': False,
                         'text': '팩트체크 기사도 조작입니다. 기자들도 다 한통속이에요.',
                         'why': '반박까지 ‘조작’이라고 해서 어떤 증거도 받아들이지 않게 만들어요.'}],
             'clue': '반박까지 ‘조작’이라고 하면, 어떤 증거가 나와도 생각이 바뀔까요?'},
            {'stones': [{'sender': '@비밀문서',
                         'real': False,
                         'text': '시청 내부 문서 유출: ‘비둘기 프로젝트’ (문서 출처 없음)',
                         'why': '확인할 수 없는 ‘비밀 문서’를 내세워요.'},
                        {'sender': '@도토리각성',
                         'real': False,
                         'text': 'TV는 절대 알려 주지 않는 진실. 알고 싶으면 우리 단체방으로 오세요.',
                         'why': '‘숨겨진 진실’을 미끼로 확인이 어려운 다른 곳으로 끌어들여요.'}],
             'clue': '둘 다 확인할 수 없는 ‘비밀’을 내세우고 있지 않나요?'},
            {'stones': [{'sender': '도토리 과학관 · 인증된 계정',
                         'real': True,
                         'text': '주말 특강: 와이파이는 어떻게 작동할까? 직접 실험해 봐요. 누구나 참여 가능',
                         'why': '누구나 직접 보고 질문할 수 있는 공개 행사예요.'},
                        {'sender': '@숨겨진진실',
                         'real': False,
                         'text': '과학관 특강은 진실을 감추려는 쇼! 비둘기 이야기 꺼내면 쫓겨난대요.',
                         'why': '공개된 행사까지 ‘숨기려는 쇼’로 몰아가요.'}],
             'clue': '누구나 확인할 수 있는 행사를 ‘쇼’라고 몰아가는 쪽은?'}]}]

GAME_HTML = r'''
<!doctype html>
<html lang="ko">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>잠깐! 리버 점프</title>
<style>
:root{color-scheme:light;--ink:#163e3c;--green:#176650;--cream:#fffdf5;--line:#d4e1d5}*{box-sizing:border-box}body{margin:0;background:#f1f5ec;color:var(--ink);font:16px/1.6 'Malgun Gothic',sans-serif}button,input{font:inherit}button{cursor:pointer;touch-action:manipulation;border:1px solid var(--line);border-radius:12px;padding:12px 17px;background:white;color:var(--ink);font-weight:700;min-height:48px}button:hover:not(:disabled){background:#e5efe4}button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #b35b17;outline-offset:3px}button:disabled{opacity:.48;cursor:default}.primary{background:var(--green);color:white;border-color:var(--green)}.primary:hover:not(:disabled){background:#104b3b}.wrap{max-width:1080px;margin:auto;padding:16px}.top{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.brand{font-weight:900;font-size:20px}.eyebrow{font-size:12px;font-weight:800;letter-spacing:2px;color:#657961}h1{font-size:clamp(26px,5vw,42px);line-height:1.25;margin:12px 0}h2{font-size:23px;margin:10px 0}h3{font-size:18px;margin:8px 0}p{margin:8px 0}.muted{color:#566e65;font-size:14px}.card{padding:22px;background:var(--cream);border:1px solid var(--line);border-radius:20px;margin-top:14px}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.stagegrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.stage{padding:16px;background:#fff;border:1px solid var(--line);border-radius:16px}.stage button{width:100%;margin-top:12px}.choices{display:grid;gap:10px;margin:18px 0}.choices button{text-align:left}.note{background:#e7eee0;border-radius:12px;padding:12px 16px;margin:12px 0}.warn{background:#fff0cc;color:#63400c}.badge{display:inline-block;border-radius:30px;background:#e2eadb;padding:4px 12px;font-size:13px;font-weight:700}.scene{position:relative;border-radius:20px;overflow:hidden;background:#99d9e0;margin:14px 0 10px;border:1px solid #94b5a5}canvas{display:block;width:100%;height:340px;touch-action:pan-y}.hud{position:absolute;left:12px;right:12px;top:12px;display:flex;justify-content:space-between;gap:8px;pointer-events:none}.hud span{background:#fffdf2ed;padding:5px 11px;border-radius:30px;font-size:13px;font-weight:800}.reticle{position:absolute;left:50%;top:50%;color:#fff;font-size:24px;text-shadow:0 1px 4px #183b3b;pointer-events:none}.banner{position:absolute;bottom:15px;left:50%;transform:translateX(-50%);max-width:92%;width:max-content;background:#183e39e8;color:white;padding:8px 18px;border-radius:30px;text-align:center;font-size:14px}.stonecard{border:2px solid var(--line);border-radius:15px;padding:14px;background:white;min-width:0}.stonecard.selected{border-color:#a75917;box-shadow:0 0 0 2px #f0c977}.stonecard p{font-size:15px;overflow-wrap:anywhere}.stonecard .sender{font-size:12px;color:#547063}.stonecard button{width:100%;padding:8px;margin-top:8px}.controls{display:grid;grid-template-columns:1fr 1.4fr 1fr;gap:8px;margin:12px 0}.controls button{padding:10px 4px}.secondary{display:grid;grid-template-columns:1fr 1fr;gap:8px}.feedback{border-left:5px solid #2b7660}.feedback.bad{border-left-color:#bc6c25}details{margin:10px 0}summary{cursor:pointer;font-weight:700}.settings{margin-top:15px;font-size:14px;display:flex;gap:20px;flex-wrap:wrap}label{cursor:pointer}input[type=checkbox]{width:18px;height:18px;vertical-align:middle}#view:focus{outline:none}#toast{color:#75440a;font-weight:700}progress{width:100%;accent-color:var(--green);height:9px}.mascot{width:110px;height:110px;overflow:hidden;position:relative;flex-shrink:0}.mascot img{width:330px;max-width:none;position:absolute;left:-220px;top:-110px}footer{font-size:12px;color:#61766b;margin:20px 0}a{color:#176650}.sr{position:absolute;left:-10000px} @media(max-width:520px){.wrap{padding:8px}.card{padding:16px}canvas{height:270px}.grid{gap:8px}.stonecard{padding:10px}.hud span{font-size:11px;padding:4px 8px}.controls{gap:5px}.controls button{font-size:14px}.brand{font-size:17px}.stonecard p{font-size:14px}.secondary button{font-size:13px;padding:10px 5px}}
</style></head>
<body><main class="wrap"><div class="top"><div class="brand">✋ 잠깐! <span class="muted">리버 점프</span></div><button id="mapButton" hidden>스테이지 지도</button></div><div id="view" tabindex="-1"></div><footer>교육용 가상 도시·계정·소식입니다. 게임의 확인 자료도 가상입니다. 실제 게시·송금·정보 입력은 없어요.</footer></main>
<script>
'use strict';
const STAGES=__STAGES__;
const MASCOT='__MASCOT__';
const view=document.getElementById('view'), mapButton=document.getElementById('mapButton');
const state={phase:'intro',stage:0,pos:0,lives:3,cleared:[],followers:0,awarded:[],round:[],selected:null,checked:false,hinted:false,results:[],motion:!matchMedia('(prefers-reduced-motion: reduce)').matches,pressure:false,remaining:0,feedback:null,cam:{x:0,z:0,y:1.7},anim:null,last:0};
let canvas=null,ctx=null,clockNode=null,liveNode=null;
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const stage=()=>STAGES[state.stage], pair=()=>state.round[state.pos];
function shuffle(a){a=[...a];for(let i=a.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function mount(markup){canvas=null;ctx=null;clockNode=null;liveNode=null;view.innerHTML=markup;mapButton.hidden=['intro','map'].includes(state.phase);mapButton.disabled=state.phase==='jump';view.focus({preventScroll:true});window.scrollTo(0,0)}
function button(id,fn){document.getElementById(id).addEventListener('click',fn)}
function showIntro(){state.phase='intro';mount(`<section class="card"><span class="eyebrow">THINK · CHOOSE · JUMP</span><h1>한 번 멈추고,<br>한 칸 더 멀리.</h1><p>가짜 소식이 떠다니는 강이에요.<br>근거를 확인하고, 믿을 수 있는 돌로 점프하세요.</p><div class="note"><b>① 수법 알아보기 → ② 두 소식 확인 → ③ 선택하고 점프</b><p>왼쪽·오른쪽 중 하나를 선택한 뒤 점프해요.<br>두 소식 모두 가짜면 <b>우회하기</b>를 누르세요.</p></div><p class="muted">컴퓨터: A/D 또는 ←/→ 선택 · Space 점프<br>휴대폰: 화면 아래 큰 버튼으로 조작<br>점프 타이밍이나 거리 조절은 필요 없어요.</p><div class="settings"><label><input id="motion" type="checkbox" ${state.motion?'checked':''}> 점프·물 움직임</label><label><input id="pressure" type="checkbox" ${state.pressure?'checked':''}> 시간 압박 모드</label></div><p class="muted">기본은 시간 제한 없이 연습해요. 압박 모드에서도 단서 확인과 확인 자료를 열면 시간이 멈춰요.</p><button class="primary" id="start">강으로 출발하기 →</button></section>`);button('start',()=>{state.motion=document.getElementById('motion').checked;state.pressure=document.getElementById('pressure').checked;showMap()})}
function showMap(){state.phase='map';state.anim=null;mount(`<section class="card"><span class="eyebrow">RIVER MAP</span><h2>다섯 개의 강, 다섯 가지 수법</h2><p>${state.cleared.length} / ${STAGES.length} 통과 · 가상 팔로워 ${state.followers.toLocaleString()}명</p><p class="muted">팔로워는 수법이 퍼지는 과정을 표현한 게임 속 숫자이며 실제 예측값이 아니에요.</p><div class="stagegrid">${STAGES.map((s,i)=>`<article class="stage"><span class="badge">${state.cleared.includes(i)?'✓ 통과':`STAGE ${i+1}`}</span><h3>${s.icon} ${escapeHTML(s.tactic)}</h3><p class="muted">${escapeHTML(s.title)}</p><button data-stage="${i}" ${i>0&&!state.cleared.includes(i-1)?'disabled':''}>${i>0&&!state.cleared.includes(i-1)?'🔒 앞 강을 건너세요':'도전하기 →'}</button></article>`).join('')}</div>${state.cleared.length===STAGES.length?'<div class="note"><b>🏆 모든 강을 건넜어요!</b><p>말투·사진·팔로워 수만으로 믿지 않고, 별도 경로에서 확인하는 습관을 이어 가세요.</p></div>':''}<div class="settings"><label><input id="motion" type="checkbox" ${state.motion?'checked':''}> 점프·물 움직임</label><label><input id="pressure" type="checkbox" ${state.pressure?'checked':''}> 시간 압박 모드</label></div><details><summary>내 판단 기록</summary><p>${state.results.length}번 판단 · 올바른 판단 ${state.results.filter(r=>r.correct).length}번 · 시간 초과 ${state.results.filter(r=>r.timeout).length}번</p><p class="muted">시간 초과는 판단 정답률과 분리합니다. 이 기록은 능력 검사나 실제 피해 위험 점수가 아니에요.</p></details></section>`);document.querySelectorAll('[data-stage]').forEach(b=>b.onclick=()=>{state.stage=Number(b.dataset.stage);showMission()});document.getElementById('motion').onchange=e=>state.motion=e.target.checked;document.getElementById('pressure').onchange=e=>state.pressure=e.target.checked}
function showMission(){state.phase='mission';const s=stage();mount(`<section class="card"><span class="badge">STAGE ${state.stage+1} · ${escapeHTML(s.tactic)}</span><h2>🎭 속이는 쪽의 수법 알아보기</h2><p>${escapeHTML(s.mission.prompt)}</p><p class="muted">교육용 역할 체험이에요. 실제로 게시하지 않습니다.</p><div class="choices">${shuffle(s.mission.choices.map((c,i)=>({c,i}))).map(({c,i})=>`<button data-choice="${i}">${escapeHTML(c.label)}</button>`).join('')}</div></section>`);document.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>showExplanation(Number(b.dataset.choice)))}
function showExplanation(i){state.phase='explain';const s=stage(),c=s.mission.choices[i];if(!state.awarded.includes(state.stage)){state.followers=Math.max(0,state.followers+c.followers);state.awarded.push(state.stage)}mount(`<section class="card"><span class="eyebrow">TACTIC REVEALED</span><h2>${s.icon} ${escapeHTML(s.tactic)}</h2><div class="note">${escapeHTML(c.post)}</div><p><b>수법 해설</b><br>${escapeHTML(s.mission.why)}</p><div class="note warn"><b>받는 사람의 대응</b><p>${escapeHTML(s.mission.spot)}</p><p>말투나 인증 표시 하나만으로는 진위를 확정할 수 없어요. 별도 공식 경로의 원문과 대조하세요.</p></div><button id="riverStart" class="primary">이제 받는 사람이 되어 점프하기 →</button></section>`);button('riverStart',startRiver)}
function startRiver(){state.round=shuffle(stage().pairs).map(p=>({...p,stones:shuffle(p.stones)}));state.pos=0;state.lives=3;state.cam={x:0,z:0,y:1.7};beginTurn()}
function beginTurn(){state.phase='river';state.selected=null;state.checked=false;state.hinted=false;state.remaining=stage().time;state.feedback=null;state.anim=null;renderRiver()}
function renderRiver(){const p=pair();mount(`<div class="top" style="margin-top:12px"><h3>${stage().icon} ${escapeHTML(stage().tactic)}의 강</h3><span class="badge">${state.pos+1} / ${state.round.length} 구간</span></div><div class="scene"><canvas id="world" aria-label="강 위에 두 갈래 돌다리가 보이는 1인칭 게임 화면"></canvas><div class="hud"><span id="lives">${'♥'.repeat(state.lives)}${'♡'.repeat(3-state.lives)}</span><span id="clock">${state.pressure?'남은 시간 '+Math.ceil(state.remaining)+'초':'천천히 확인해도 괜찮아요'}</span></div><div class="reticle" aria-hidden="true">＋</div><div class="banner" id="sceneMessage">돌을 고른 뒤 점프하세요</div></div><div class="grid">${p.stones.map((s,i)=>`<article class="stonecard" id="stone${i}"><b>${i===0?'A · 왼쪽 돌':'B · 오른쪽 돌'}</b><div class="sender">${escapeHTML(s.sender)}</div><p>${escapeHTML(s.text)}</p><button id="select${i}" aria-pressed="false">${i===0?'← 왼쪽':'오른쪽 →'} 선택</button></article>`).join('')}</div><div class="controls"><button id="left">← 왼쪽</button><button class="primary" id="jump">점프 ↑</button><button id="right">오른쪽 →</button></div><div class="secondary"><button id="verify">🔎 별도 확인 자료</button><button id="bypass">둘 다 위험해요 · 우회</button></div><div class="row" style="margin-top:10px"><button id="hint">✋ 잠깐! 단서 확인</button><label class="muted"><input id="motion" type="checkbox" ${state.motion?'checked':''}> 움직임 켜기</label></div><div id="toast" role="status" aria-live="polite"></div><div id="evidence"></div><div id="feedback" aria-live="polite"></div><p class="muted">A/D 또는 ←/→ 선택 · Space 점프 · 두 돌 모두 가짜면 우회<br>점프 버튼은 방향을 선택한 뒤 눌러 주세요.</p>`);canvas=document.getElementById('world');ctx=canvas.getContext('2d');clockNode=document.getElementById('clock');liveNode=document.getElementById('sceneMessage');button('left',()=>select(0));button('right',()=>select(1));button('select0',()=>select(0));button('select1',()=>select(1));button('jump',()=>act(state.selected));button('bypass',()=>act('none'));button('verify',verify);button('hint',hint);document.getElementById('motion').onchange=e=>state.motion=e.target.checked;draw(0)}
function select(i){if(state.phase!=='river')return;state.selected=i;view.focus({preventScroll:true});for(let j=0;j<2;j++){document.getElementById('stone'+j).classList.toggle('selected',j===i);document.getElementById('select'+j).setAttribute('aria-pressed',String(i===j))}liveNode.textContent=(i===0?'왼쪽 A':'오른쪽 B')+' 돌 선택 · 점프를 누르세요';document.getElementById('toast').textContent=''}
function hint(){if(state.phase!=='river')return;state.hinted=true;document.getElementById('toast').textContent='✋ '+pair().clue+' · 시간이 멈췄어요.';updateClock()}
function verify(){if(state.phase!=='river')return;state.checked=true;updateClock();document.getElementById('evidence').innerHTML=`<section class="card"><b>🔎 별도 경로에서 대조한 결과</b><p class="muted">교육용으로 미리 작성한 확인 결과입니다. 실제 사이트를 조회하는 기능은 아니에요.</p>${pair().stones.map((s,i)=>`<p><b>${i===0?'A · 왼쪽':'B · 오른쪽'}</b> — ${s.real?'게임 속 원문 자료와 대조했을 때 이 소식의 핵심 내용이 일치합니다.':'게임 속 원문 자료와 대조했을 때 핵심 내용이 일치하지 않거나, 주장하는 근거를 확인할 수 없습니다.'}</p>`).join('')}<p class="muted">실제 상황에서는 검색한 공식 홈페이지·저장된 연락처 등 별도 경로로 확인하세요. 근거가 없다는 이유만으로 거짓을 확정하지 말고, 확인 전 공유·송금을 보류하세요.</p></section>`}
function updateClock(){if(clockNode)clockNode.textContent=!state.pressure?'시간 제한 없음':state.checked||state.hinted?'✋ 확인 중 · 시간 멈춤':'남은 시간 '+Math.ceil(Math.max(0,state.remaining))+'초'}
function act(choice,timeout=false){if(state.phase!=='river')return;if(choice===null&&!timeout){document.getElementById('toast').textContent='먼저 왼쪽 또는 오른쪽 돌을 선택해 주세요.';return}const stones=pair().stones;const correct=!timeout&&(choice==='none'?!stones.some(s=>s.real):stones[choice].real);state.feedback={choice,correct,timeout,stones};state.results.push({stage:state.stage,correct,timeout,checked:state.checked,hinted:state.hinted});state.phase='jump';document.querySelectorAll('#view button,#view input').forEach(b=>b.disabled=true);mapButton.disabled=true;const target={x:choice==='none'?3.7:choice===0?-1.35:choice===1?1.35:state.cam.x,z:(state.pos+1)*4,y:1.7};state.anim={start:performance.now(),from:{...state.cam},to:target,correct,choice};liveNode.textContent=timeout?'시간이 다 되었어요':choice==='none'?'우회로를 확인하는 중…':'점프!';if(!state.motion){state.cam=correct?target:{...state.cam};state.anim=null;finishJump()}}
function finishJump(){state.anim=null;state.phase='feedback';const f=state.feedback;if(!f.correct)state.lives--;document.getElementById('lives').textContent='♥'.repeat(state.lives)+'♡'.repeat(3-state.lives);mapButton.disabled=false;let message=f.timeout?'시간이 다 되었어요. 목숨이 하나 줄었어요.':f.correct?(f.choice==='none'?'두 소식 모두 확인되지 않았어요. 우회로로 안전하게 건넜어요!':'착지 성공! 확인된 소식의 돌을 건넜어요.'):'풍덩! 이번 선택을 다시 확인해 봐요.';liveNode.textContent=f.correct?'✓ 안전하게 착지했어요':'직전 발판으로 돌아왔어요';document.getElementById('feedback').innerHTML=`<section class="card feedback ${f.correct?'':'bad'}"><h3>${escapeHTML(message)}</h3>${f.stones.map((s,i)=>`<details><summary>${i===0?'A · 왼쪽':'B · 오른쪽'} — ${s.real?'설정상 진짜 소식':'설정상 가짜 소식'}</summary><p>${escapeHTML(s.why)}</p></details>`).join('')}<p class="muted">위 설명은 의심하거나 확인할 단서예요. 말투·인증 표시·팔로워 수만으로 진위를 확정하지 마세요.</p><button class="primary" id="next">${state.lives<=0?'다시 도전하기':f.correct?'다음 발판으로 →':'같은 구간 다시 판단하기'}</button></section>`;button('next',()=>{if(state.lives<=0){startRiver();return}if(f.correct)state.pos++;if(state.pos>=state.round.length){showClear()}else{beginTurn()}});document.getElementById('feedback').scrollIntoView({behavior:'auto',block:'nearest'})}
function showClear(){state.phase='clear';if(!state.cleared.includes(state.stage))state.cleared.push(state.stage);mount(`<section class="card"><div class="row">${MASCOT?`<div class="mascot"><img alt="축하하는 깡지 캐릭터" src="${MASCOT}"></div>`:'<span style="font-size:64px">🏁</span>'}<div><span class="eyebrow">RIVER CLEARED</span><h1>무사히 건넜어요!</h1></div></div><p><b>${escapeHTML(stage().tactic)}</b> 수법을 알아보고, ${state.round.length}개 구간을 건넜어요.</p><div class="note">${escapeHTML(stage().mission.spot)}</div><p>실제 연락에서도 <b>멈추기 → 별도 경로로 확인하기 → 행동하기</b>를 기억하세요.</p><button id="back" class="primary">지도에서 다음 강 고르기 →</button></section>`);button('back',showMap)}
mapButton.onclick=showMap;
document.addEventListener('keydown',e=>{if(state.phase!=='river'||e.repeat||e.ctrlKey||e.metaKey||e.altKey)return;const tag=e.target.tagName;if(['INPUT','TEXTAREA','SELECT','BUTTON','SUMMARY','A'].includes(tag))return;const k=e.key.toLowerCase();if(['arrowleft','a','arrowright','d',' '].includes(k))e.preventDefault();if(k==='a'||k==='arrowleft')select(0);else if(k==='d'||k==='arrowright')select(1);else if(k===' ')act(state.selected)});
// Lightweight software 3D: project world coordinates from an eye-level camera.
// All geometry and textures are local canvas drawings; no CDN or WebGL requirement.
function draw(t){if(!canvas||!ctx)return;const w=canvas.clientWidth,h=canvas.clientHeight,dpr=Math.min(devicePixelRatio||1,2);if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}ctx.setTransform(dpr,0,0,dpr,0,0);const cam=state.cam,fl=Math.min(w*.66,560),horizon=h*.37;
function project(p){let z=p[2]-cam.z;if(z<.18)return null;return [w/2+(p[0]-cam.x)*fl/z,horizon+(cam.y-p[1])*fl/z]}
function poly(points,color,stroke){let ps=points.map(project);if(ps.some(p=>!p))return;ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.stroke()}}
function block(x,y,z,sx,sy,sz,color,top){poly([[x-sx,y-sy,z-sz],[x+sx,y-sy,z-sz],[x+sx,y,z-sz],[x-sx,y,z-sz]],color,'#416c6470');poly([[x-sx,y,z-sz],[x+sx,y,z-sz],[x+sx,y,z+sz],[x-sx,y,z+sz]],top,'#416c6470');poly([[x+sx,y-sy,z-sz],[x+sx,y-sy,z+sz],[x+sx,y,z+sz],[x+sx,y,z-sz]],color)}
let sky=ctx.createLinearGradient(0,0,0,h);sky.addColorStop(0,'#a9dee5');sky.addColorStop(.5,'#e2f0d3');sky.addColorStop(.51,'#54b9bc');sky.addColorStop(1,'#247f91');ctx.fillStyle=sky;ctx.fillRect(0,0,w,h);ctx.fillStyle='#fff1ad';ctx.beginPath();ctx.arc(w*.8,h*.16,24,0,Math.PI*2);ctx.fill();ctx.fillStyle='#7eaa86';ctx.beginPath();ctx.moveTo(0,horizon+10);for(let x=0;x<=w;x+=40)ctx.lineTo(x,horizon-20-Math.sin(x*.018)*17);ctx.lineTo(w,horizon+30);ctx.fill();ctx.fillStyle='#51aeb6';ctx.fillRect(0,horizon+22,w,h);
poly([[-30,0,cam.z+.3],[-5,0,cam.z+.3],[-5,0,40],[-30,0,40]],'#6f9d68');poly([[5,0,cam.z+.3],[30,0,cam.z+.3],[30,0,40],[5,0,40]],'#6f9d68');
let flow=state.motion?t*.00045:0;ctx.strokeStyle='#c3f3df66';ctx.lineWidth=2;for(let z=Math.ceil(cam.z)+1;z<cam.z+32;z+=1.7){for(let x=-4;x<5;x+=2.3){let zz=z+(flow%1.7),p=project([x+Math.sin(z)*.3,.015,zz]),q=project([x+.9+Math.sin(z)*.3,.015,zz]);if(p&&q){ctx.beginPath();ctx.moveTo(...p);ctx.lineTo(...q);ctx.stroke()}}}
for(let z=36;z>cam.z+1;z-=4){for(let x of [-7.5,7.5]){block(x,1,z,.18,1,.18,'#866d48','#9e8057');block(x,2.7,z,.8,1.6,.8,'#417a58','#76a96b')}}
const goal=(state.round.length+1)*4;block(0,.35,goal,4,.8,1.7,'#7f8d63','#b1be80');block(.2,3.4,goal,.05,3,.05,'#faf6df','#fff');poly([[.25,3.4,goal],[1.8,3.4,goal],[1.8,2.6,goal],[.25,2.6,goal]],'#e7a257');
for(let row=state.round.length;row>=1;row--){const z=row*4;if(z<cam.z+.2)continue;for(let i=0;i<2;i++){let active=row===state.pos+1,selected=active&&state.selected===i;let y=.28;if(state.anim&&!state.anim.correct&&state.anim.choice===i&&active){let a=Math.min(1,(t-state.anim.start)/1100);if(a>.6)y-=Math.pow((a-.6)/.4,2)*2}block(i===0?-1.35:1.35,y,z,.9,.48,.8,selected?'#b98443':'#657d77',selected?'#f5d58a':active?'#e4e7d3':'#a4b8a3');if(active){let p=project([i===0?-1.35:1.35,y+.65,z]);if(p){ctx.fillStyle='#173d39';ctx.font='bold 19px sans-serif';ctx.textAlign='center';ctx.fillText(i===0?'A':'B',p[0],p[1])}}}}
if(state.anim&&state.anim.choice==='none')block(3.7,.3,(state.pos+1)*4,.9,.5,.85,'#967441','#e9cc8a');
// First-person hands rise with the jump; they are drawn independently of the mascot.
const jumping=state.phase==='jump';let lift=jumping&&state.motion?Math.sin(Math.min(1,(t-state.anim.start)/1100)*Math.PI)*24:0;ctx.fillStyle='#f2d59a';ctx.strokeStyle='#775c39';ctx.lineWidth=3;for(let side of [-1,1]){ctx.save();ctx.translate(w/2+side*w*.36,h+12-lift);ctx.rotate(side*-.25);ctx.fillRect(-26,-49,52,78);ctx.strokeRect(-26,-49,52,78);ctx.fillStyle='#438474';ctx.fillRect(-29,-2,58,32);ctx.restore();ctx.fillStyle='#f2d59a'}
if(state.anim&&!state.anim.correct){let a=(t-state.anim.start)/1100;if(a>.75){ctx.fillStyle=`rgba(42,150,173,${Math.sin((a-.75)/.25*Math.PI)*.65})`;ctx.fillRect(0,0,w,h)}}}
function frame(t){const dt=Math.min(.08,(t-(state.last||t))/1000);state.last=t;if(!document.hidden){if(state.phase==='river'&&state.pressure&&!state.checked&&!state.hinted){state.remaining-=dt;updateClock();if(state.remaining<=0)act(null,true)}if(state.anim){const a=state.anim,p=Math.min(1,(t-a.start)/1100),ease=p*p*(3-2*p);state.cam={x:a.from.x+(a.to.x-a.from.x)*ease,z:a.from.z+(a.to.z-a.from.z)*ease,y:1.7+Math.sin(p*Math.PI)*1.55};if(!a.correct&&p>.72)state.cam.y-=((p-.72)/.28)*2;if(p>=1){state.cam=a.correct?a.to:a.from;finishJump()}}draw(t)}requestAnimationFrame(frame)}
document.addEventListener('visibilitychange',()=>{state.last=0;if(state.phase==='jump'&&state.anim){state.cam=state.anim.correct?state.anim.to:state.anim.from;finishJump()}});
showIntro();requestAnimationFrame(frame);
</script></body></html>

'''

# 기존 마스코트가 있으면 완료 화면에 사용하고, 없어도 게임은 동작합니다.
mascot_path = Path(__file__).resolve().parents[1] / "assets" / "mascot_six.png"
mascot = ""
if mascot_path.is_file():
    mascot = "data:image/png;base64," + base64.b64encode(mascot_path.read_bytes()).decode("ascii")
game_html = GAME_HTML.replace("__STAGES__", json.dumps(STAGES, ensure_ascii=False).replace("<", "\\u003c")).replace("__MASCOT__", mascot)
components.html(game_html, height=1050, scrolling=True)
st.caption("진행은 게임 화면이 열린 동안 유지됩니다. 새로고침하거나 다른 페이지로 이동하면 처음부터 시작해요. 랭킹에는 저장하지 않습니다.")
