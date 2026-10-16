import html
import random
import time

import streamlit as st
from mascot_ui import show_mascot


# 모든 문자·기관명·상황은 교육용 가상 자료입니다.
# 다른 페이지(할머니·모의대화·방탈출·URL)에서 다루지 않는 피싱 유형을 다룹니다.
KEY = "river_v2"
LIVES = 3               # 스테이지마다 목숨
TIME_LIMIT = 15         # 돌이 가라앉기까지 걸리는 시간(초)
PAUSES_PER_STAGE = 2    # 스테이지마다 쓸 수 있는 '잠깐!' 횟수

# 스테이지마다 수법 하나를 다룹니다.
# note: 이미 만들어진 가짜 문자를 뜯어보며 수법을 미리 알아보는 부분
# pairs: 강의 한 칸마다 나오는 두 갈래 돌 (진짜 하나, 가짜 하나)
#        clue는 '잠깐!'을 누르면 보이는 단서입니다.
STAGES = [
    {
        "title": "중고거래의 함정",
        "icon": "🛒",
        "lesson": "중고거래는 앱 안에서만 대화하고 결제해요. 앱 밖 링크와 선입금은 멈춤 신호예요.",
        "note": {
            "message": "물건 아직 있죠? 지금 지방이라 직거래는 어렵고, 제가 안전결제로 먼저 보낼게요. 카톡 주시면 결제 링크 드릴게요!",
            "parts": [
                ("카톡 주시면", "중고거래 앱 밖 메신저로 옮겨 가요. 앱 밖에서는 거래 기록과 보호를 받기 어려워요."),
                ("안전결제로 먼저 보낼게요", "‘안전결제’라는 말로 안심시키지만, 링크로 보내는 가짜 결제 페이지일 수 있어요."),
                ("지방이라 직거래는 어렵고", "직접 만나지 않을 이유를 미리 만들어요."),
            ],
            "defense": "대화와 결제는 중고거래 앱 안의 기능으로만 해요. 앱 밖 링크는 누르지 않아요.",
        },
        "pairs": [
            {
                "real": {"sender": "중고거래 앱 채팅", "text": "토요일 오후 2시에 ○○역 2번 출구에서 직거래 가능할까요?",
                         "why": "앱 안에서 직접 만나 확인하는 거래 약속이에요."},
                "fake": {"sender": "중고거래 앱 채팅", "text": "제가 바빠서요. 카톡 주시면 안전결제 링크 보내 드릴게요.",
                         "why": "대화를 앱 밖으로 옮기고 링크로 결제하게 해요."},
                "clue": "한쪽은 대화를 앱 밖으로 옮기려 해요.",
            },
            {
                "real": {"sender": "중고거래 앱 알림", "text": "구매자가 앱 안 결제를 완료했어요. 앱에서 거래 상태를 확인하세요.",
                         "why": "앱 안 결제 기능의 알림이고, 확인도 앱에서 하라고 해요."},
                "fake": {"sender": "문자 (저장 안 됨)", "text": "[안전결제] 구매자 대금 입금 완료. 판매 확정을 위해 수수료 5,000원을 먼저 결제하세요.",
                         "why": "문자로 온 가짜 결제 안내예요. 판매자에게 돈을 먼저 내라고 해요."},
                "clue": "결제 알림이 앱 안에서 왔나요, 문자로 왔나요?",
            },
            {
                "real": {"sender": "중고거래 앱 채팅", "text": "물건 상태 사진 몇 장 더 보내 주실 수 있나요?",
                         "why": "물건을 확인하려는 평범한 질문이에요."},
                "fake": {"sender": "중고거래 앱 채팅", "text": "예약금 3만 원 먼저 보내 주시면 다른 분께 안 팔고 기다릴게요.",
                         "why": "물건을 보기도 전에 돈부터 보내게 해요."},
                "clue": "물건을 보기도 전에 돈을 요구하는 쪽이 있어요.",
            },
            {
                "real": {"sender": "중고거래 앱 채팅", "text": "택배 거래면 앱의 안전결제 기능으로 결제해 주세요.",
                         "why": "앱이 제공하는 보호 기능을 쓰자고 해요."},
                "fake": {"sender": "중고거래 앱 채팅", "text": "앱 결제는 수수료가 아까워서요. 제 계좌로 바로 입금해 주시면 오늘 발송할게요.",
                         "why": "앱의 보호 기능을 피하려고 그럴듯한 이유를 대요."},
                "clue": "앱의 보호 기능을 피하려는 이유를 대는 쪽은?",
            },
        ],
    },
    {
        "title": "범죄가 되는 고액 알바",
        "icon": "💼",
        "lesson": "현금을 받아 옮기거나 통장·체크카드를 빌려주는 일은 내가 범죄에 가담하게 될 수 있어요.",
        "note": {
            "message": "[채용] 하루 2시간, 일당 25만 원! 고객님께 받은 서류 봉투를 지정 장소에 전달만 하면 됩니다. 경험·면접 없음, 즉시 출근.",
            "parts": [
                ("일당 25만 원", "하는 일에 비해 보수가 지나치게 많아요."),
                ("봉투를 지정 장소에 전달만", "보이스피싱 피해자의 현금을 받아 옮기는 ‘수거책’ 일일 수 있어요."),
                ("면접 없음, 즉시 출근", "회사와 사람을 확인할 기회를 주지 않아요."),
            ],
            "defense": "회사 정보와 근로계약을 확인하고, 현금 전달·계좌 대여·체크카드 전달 일은 거절해요. 몰랐어도 처벌받을 수 있어요.",
        },
        "pairs": [
            {
                "real": {"sender": "구인 앱 · ○○카페", "text": "주말 홀 서빙 알바. 시급은 최저임금 이상, 근로계약서 작성, 매장 방문 면접.",
                         "why": "가게가 공개돼 있고 계약서와 면접이 있는 일반 알바예요."},
                "fake": {"sender": "구인 문자", "text": "고객에게 현금을 받아 지정 계좌로 입금만 하면 건당 10만 원 지급!",
                         "why": "피해자의 돈을 옮기는 수거책 일이에요. 하는 순간 범죄에 가담할 수 있어요."},
                "clue": "한쪽은 남의 돈을 받아 옮기는 일이에요.",
            },
            {
                "real": {"sender": "구인 앱 · ○○서점", "text": "도서 정리 단기 알바. 근무 장소 ○○서점 본점, 문의는 매장 대표번호로.",
                         "why": "근무 장소와 연락처가 확인되고, 돈을 다루라는 요구가 없어요."},
                "fake": {"sender": "메신저 (모르는 사람)", "text": "통장이랑 체크카드 잠깐 빌려주면 한 달에 50만 원 드려요. 세금 처리용이에요.",
                         "why": "넘긴 통장·카드는 범죄 계좌로 쓰일 수 있고, 빌려준 사람도 처벌받을 수 있어요."},
                "clue": "내 통장이나 카드를 넘기라는 쪽이 있어요.",
            },
            {
                "real": {"sender": "구인 앱 · ○○학원", "text": "채점 보조 알바. 학원 주소 공개, 첫 출근 날 근로계약서 작성.",
                         "why": "일하는 곳이 분명하고 계약 절차가 있어요."},
                "fake": {"sender": "구인 문자", "text": "서류 봉투 전달만 하면 일당 25만 원. 면접 없음, 즉시 출근.",
                         "why": "하는 일에 비해 보수가 지나치게 많고, 봉투 속은 피해자의 현금일 수 있어요."},
                "clue": "하는 일에 비해 보수가 지나치게 많은 쪽은?",
            },
            {
                "real": {"sender": "구인 앱 · ○○물류", "text": "상하차 단기 알바. 4대 보험 가입, 사업자등록번호 공개.",
                         "why": "회사를 확인할 수 있는 정보가 공개돼 있어요."},
                "fake": {"sender": "구인 문자", "text": "구매대행 회사입니다. 회사 대신 고객 돈을 받아 상품권으로 바꿔 보내 주시면 됩니다.",
                         "why": "남의 돈을 받아 다른 형태로 바꿔 보내는 일은 돈세탁에 이용될 수 있어요."},
                "clue": "돈을 받아 다른 형태로 바꿔 보내는 일은 무엇에 쓰일까요?",
            },
        ],
    },
    {
        "title": "수익을 보장하는 투자방",
        "icon": "📈",
        "lesson": "‘원금 보장’, ‘확정 수익’을 말하는 투자 권유는 의심해요. 투자는 등록된 금융회사 앱에서만 해요.",
        "note": {
            "message": "[VIP 리딩방] 유명 애널리스트 ○○○ 선생님의 비밀 종목! 원금 보장, 한 달 300% 수익 인증 다수. 지금 입장하면 첫 종목 무료!",
            "parts": [
                ("원금 보장, 한 달 300% 수익", "진짜 투자에는 손실 위험이 있어요. 보장한다는 말 자체가 신호예요."),
                ("유명 애널리스트 ○○○", "유명인의 이름이나 사진을 허락 없이 빌려 써요."),
                ("수익 인증 다수", "인증 캡처는 쉽게 조작할 수 있어요."),
            ],
            "defense": "금융감독원 ‘파인’에서 등록된 금융회사인지 확인하고, 투자는 내가 직접 설치한 증권사 앱에서만 해요.",
        },
        "pairs": [
            {
                "real": {"sender": "○○증권 앱 (직접 설치)", "text": "보유 종목의 주주총회 일정이 공시되었어요. 앱에서 확인하세요.",
                         "why": "직접 설치한 증권사 앱의 공지이고, 입금 요구가 없어요."},
                "fake": {"sender": "단체 대화방 초대", "text": "하루 1%씩 확정 수익! 전용 앱에 입금하면 매일 수익금이 쌓여요.",
                         "why": "‘확정 수익’은 투자에서 나올 수 없는 말이에요. 전용 앱은 가짜 거래 화면일 수 있어요."},
                "clue": "‘확정’이라는 말이 붙은 쪽은?",
            },
            {
                "real": {"sender": "○○증권 앱 (직접 설치)", "text": "투자 위험 고지: 이 상품은 원금 손실이 발생할 수 있습니다.",
                         "why": "진짜 금융회사는 손실 가능성을 꼭 알려 줘요."},
                "fake": {"sender": "투자 대화방", "text": "원금 보장! 손실이 나면 100% 돌려드립니다. 오늘만 선착순 10명.",
                         "why": "손실을 보장해 준다는 투자는 없어요. 선착순으로 서두르게도 해요."},
                "clue": "진짜 투자 상품은 손실 가능성을 어떻게 다룰까요?",
            },
            {
                "real": {"sender": "○○은행 앱 (직접 설치)", "text": "예금 만기가 다가왔어요. 재예치 여부를 앱에서 선택하세요.",
                         "why": "직접 설치한 은행 앱 안에서 선택하라고 해요."},
                "fake": {"sender": "SNS 광고", "text": "유명 경제 유튜버 ○○○도 추천! 지금 상담 신청하면 무료 종목 3개.",
                         "why": "유명인 이름을 빌린 광고일 수 있어요. 본인의 공식 채널에서 직접 확인해요."},
                "clue": "유명인 이름을 앞세운 쪽, 본인이 정말 말했을까요?",
            },
            {
                "real": {"sender": "○○증권 고객센터 (대표번호로 직접 전화)", "text": "상품 가입 전에 투자 성향 진단부터 진행하겠습니다.",
                         "why": "내가 직접 건 대표번호이고, 정상적인 가입 절차예요."},
                "fake": {"sender": "투자 대화방 매니저", "text": "수익금을 출금하려면 세금 20%를 먼저 입금하셔야 합니다.",
                         "why": "돈을 빼려면 돈을 더 내라는 건 전형적인 수법이에요."},
                "clue": "돈을 빼려면 돈을 더 내라는 쪽은?",
            },
        ],
    },
    {
        "title": "QR코드 속 숨은 주소",
        "icon": "📷",
        "lesson": "QR코드는 찍기 전에는 어디로 가는지 보이지 않아요. 누가 붙였는지부터 생각해요.",
        "note": {
            "message": "(자동차 앞유리에 붙은 스티커) 주차 위반 과태료 안내 · 아래 QR코드를 찍어 즉시 납부하면 20% 감면!",
            "parts": [
                ("자동차 앞유리에 붙은 스티커", "누구나 프린트해서 붙일 수 있어요. 공식 고지인지 알 수 없어요."),
                ("QR코드를 찍어", "찍기 전에는 어떤 주소로 가는지 볼 수 없어요."),
                ("즉시 납부하면 20% 감면", "할인으로 서두르게 만들어요."),
            ],
            "defense": "과태료는 공식 앱이나 직접 검색한 정부 사이트에서 조회해요. QR을 찍었다면 열리는 주소부터 확인해요.",
        },
        "pairs": [
            {
                "real": {"sender": "상황 카드", "text": "식당 테이블에 처음부터 인쇄된 메뉴 주문 QR. 찍으면 가게 이름의 주문 페이지가 열려요.",
                         "why": "가게가 직접 둔 QR이에요. 그래도 결제 전에 가게 이름과 주소를 확인하면 더 좋아요."},
                "fake": {"sender": "상황 카드", "text": "전봇대에 붙은 ‘정부 지원금 즉시 지급’ 전단. QR을 찍으면 이름과 주민번호를 입력하래요.",
                         "why": "누가 붙였는지 모르는 전단이고, 민감한 개인정보를 요구해요."},
                "clue": "누가 붙였는지 알 수 있는 쪽은?",
            },
            {
                "real": {"sender": "상황 카드", "text": "학교 가정통신문에 인쇄된 설문 QR. 같은 주소가 글자로도 적혀 있어요.",
                         "why": "보낸 곳이 확실하고, QR과 같은 주소를 글자로 비교할 수 있어요."},
                "fake": {"sender": "상황 카드", "text": "택배 상자 송장 옆에 따로 덧붙인 ‘배송 오류 확인’ QR 스티커.",
                         "why": "송장과 따로 덧붙인 스티커는 누군가 몰래 붙였을 수 있어요."},
                "clue": "원래 인쇄된 것과 위에 덧붙인 것을 구분해 보세요.",
            },
            {
                "real": {"sender": "상황 카드", "text": "주차장 정산기 화면에 뜨는 결제 QR.",
                         "why": "기계가 직접 화면에 보여 주는 QR이에요."},
                "fake": {"sender": "상황 카드", "text": "주차장 정산기 위에 테이프로 덧붙인 ‘간편 결제 QR’ 스티커.",
                         "why": "원래 기계 위에 덧붙인 QR은 바꿔치기한 것일 수 있어요."},
                "clue": "화면에 뜬 것과 테이프로 붙인 것의 차이는?",
            },
            {
                "real": {"sender": "상황 카드", "text": "박물관 전시 안내판에 인쇄된 오디오 가이드 QR. 찍으면 박물관 이름의 페이지가 열려요.",
                         "why": "기관이 직접 만든 안내판이고, 돈이나 정보를 요구하지 않아요."},
                "fake": {"sender": "상황 카드", "text": "자동차 앞유리에 붙은 ‘주차 위반 과태료 · QR로 즉시 납부하면 20% 감면’ 스티커.",
                         "why": "누구나 붙일 수 있는 스티커이고, 할인으로 바로 돈을 내게 해요."},
                "clue": "할인을 내세워 바로 돈을 내게 하는 쪽은?",
            },
        ],
    },
    {
        "title": "공짜·당첨이라는 미끼",
        "icon": "🎁",
        "lesson": "응모한 적 없는 당첨이나 공짜 선물이 정보·인증·결제를 요구하면 멈춰요.",
        "note": {
            "message": "축하합니다! ○○마트 10주년 이벤트에 당첨되셨습니다. 경품 무선 이어폰 배송을 위해 배송비 3,000원 결제와 주소 입력 부탁드립니다.",
            "parts": [
                ("당첨되셨습니다", "응모한 기억이 없어도 기뻐서 경계를 풀게 해요."),
                ("배송비 3,000원 결제", "적은 금액이라 부담 없어 보이지만, 결제 정보를 빼내려는 목적일 수 있어요."),
                ("주소 입력", "개인정보를 모아 다음 사기에 이용할 수 있어요."),
            ],
            "defense": "응모한 적 없는 당첨은 의심하고, 그 회사의 공식 앱이나 고객센터에서 이벤트가 있는지 확인해요.",
        },
        "pairs": [
            {
                "real": {"sender": "○○편의점 앱 (직접 설치)", "text": "응모하신 이벤트 결과가 나왔어요. 앱의 ‘내 쿠폰함’에서 확인하세요.",
                         "why": "내가 응모한 이벤트이고, 앱 안에서 확인하라고 해요."},
                "fake": {"sender": "문자 (저장 안 됨)", "text": "○○마트 10주년 이벤트 당첨! 경품 배송비 3,000원 결제와 주소 입력 부탁드립니다.",
                         "why": "응모한 적 없는 당첨인데 결제와 주소를 요구해요."},
                "clue": "응모한 기억이 있는 쪽은?",
            },
            {
                "real": {"sender": "○○도서관 (저장된 번호)", "text": "독서 퀴즈 상품은 다음 방문 때 안내 데스크에서 받아 가세요.",
                         "why": "참여한 행사이고, 직접 방문해서 받는 방식이에요."},
                "fake": {"sender": "SNS 메시지", "text": "팔로워 감사 이벤트 1등 당첨! 상품 발송을 위해 신분증 사진과 계좌번호를 보내 주세요.",
                         "why": "경품을 받는 데 신분증과 계좌번호는 필요하지 않아요."},
                "clue": "경품을 받는 데 신분증이 필요할까요?",
            },
            {
                "real": {"sender": "○○통신사 앱 (직접 설치)", "text": "이번 달 멤버십 무료 영화 쿠폰이 지급됐어요. 앱에서 확인하세요.",
                         "why": "내가 쓰는 통신사 앱 안의 혜택 안내예요."},
                "fake": {"sender": "문자 (저장 안 됨)", "text": "무료 기프티콘이 도착했어요! 받으려면 링크에서 휴대폰 본인인증을 해 주세요.",
                         "why": "선물을 핑계로 본인인증을 시켜 정보를 빼내려 해요."},
                "clue": "선물을 받으려면 본인인증부터 하라는 쪽은?",
            },
            {
                "real": {"sender": "학교 알림 앱", "text": "체육대회 경품 추첨 결과는 내일 학급 게시판에 공지됩니다.",
                         "why": "보낸 곳이 확실하고, 아무것도 요구하지 않아요."},
                "fake": {"sender": "메신저", "text": "축하해! 룰렛 이벤트 최신폰 당첨! 친구 5명을 초대하면 바로 발송돼.",
                         "why": "친구 초대를 조건으로 걸어 같은 사기를 퍼뜨리게 해요."},
                "clue": "친구 초대를 조건으로 거는 이유는 뭘까요?",
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
    .rv-msg .body {font-size:1.02rem; line-height:1.6; word-break:break-all;}
    .rv-tag {display:inline-block; font-weight:800; font-size:.85rem; margin-bottom:4px;}
    .rv-note {background:#FFF7ED; border:2px dashed #FDBA74; border-radius:16px; padding:14px 16px; color:#172B3A;}
    .rv-note .msg {background:#fff; border-radius:12px; padding:10px 12px; margin:6px 0 10px; border:1px solid #FED7AA;}
    .rv-mark {background:#FEF08A; padding:0 3px; border-radius:4px; font-weight:700;}
    .rv-clock {font-weight:800; color:#B45309;}
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(text):
    return html.escape(str(text))


# ─────────────────────────────────────
# 게임 상태
# ─────────────────────────────────────

def new_game():
    return {
        "started": False,
        "timer": True,          # 시간 제한 사용 여부
        "cleared": [],          # 깬 스테이지 번호
        "stage": None,          # 현재 스테이지 번호
        "phase": "note",        # note(수법 해부) / river(강 건너기) / clear / fail
        "order": [],            # 이번 도전의 칸 순서
        "sides": [],            # 칸마다 진짜 돌이 🅰(왼쪽)인지
        "pos": 0,               # 건넌 칸 수
        "lives": LIVES,
        "pauses": PAUSES_PER_STAGE,
        "paused": False,        # 지금 칸에서 '잠깐!'을 눌렀는지
        "deadline": 0.0,        # 지금 칸의 돌이 가라앉는 시각
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
    g["phase"] = "note"
    g["feedback"] = None


def begin_step(g):
    g["paused"] = False
    g["deadline"] = time.time() + TIME_LIMIT


def go_river():
    g = game()
    count = len(STAGES[g["stage"]]["pairs"])
    g["order"] = random.sample(range(count), count)
    g["sides"] = [random.random() < 0.5 for _ in range(count)]
    g["pos"] = 0
    g["lives"] = LIVES
    g["pauses"] = PAUSES_PER_STAGE
    g["feedback"] = None
    g["phase"] = "river"
    begin_step(g)


def current_pair(g):
    return STAGES[g["stage"]]["pairs"][g["order"][g["pos"]]]


def press_pause():
    g = game()
    if g["pauses"] > 0 and not g["paused"] and not g["feedback"]:
        g["pauses"] -= 1
        g["paused"] = True


def record(g, correct, timeout=False):
    bucket = g["stats"]["paused" if g["paused"] else "rushed"]
    bucket[0] += 1 if correct else 0
    bucket[1] += 1
    g["feedback"] = {"correct": correct, "timeout": timeout, "pair": current_pair(g)}
    if correct:
        g["pos"] += 1
    else:
        g["lives"] -= 1


def choose(side_a):
    g = game()
    if g["feedback"] or g["phase"] != "river":
        return
    real_is_a = g["sides"][g["pos"]]
    record(g, correct=(side_a == real_is_a))


def sink():
    """시간이 다 되면 돌이 가라앉아요. 고르지 않은 것도 틀린 것으로 셉니다."""
    g = game()
    if not g["feedback"] and g["phase"] == "river":
        record(g, correct=False, timeout=True)


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


def marked_message(message, parts):
    text = esc(message)
    for part, _ in parts:
        text = text.replace(esc(part), f'<span class="rv-mark">{esc(part)}</span>', 1)
    return text


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
    show_mascot("hint", "급할수록 속기 쉬워요. 헷갈리면 잠깐! 멈춰요.")
    st.markdown(
        "### 🌊 미션: 강을 건너 안전한 곳으로!\n"
        f"스테이지는 **{len(STAGES)}개**예요. 중고거래, 고액 알바, 투자방, QR코드, 공짜 미끼처럼 "
        "일상에서 마주치는 수법을 하나씩 다뤄요.\n\n"
        "1. **🕵️ 수법 해부 노트** — 완성된 가짜 문자를 뜯어보며 숨은 수법을 미리 알아봐요.\n"
        "2. **🌊 두 갈래 징검다리** — 한 칸마다 돌이 두 개 나와요. 하나는 진짜, 하나는 가짜예요. "
        "**안전한 돌**을 골라 밟아요.\n"
        f"3. **⏳ 가라앉는 돌** — {TIME_LIMIT}초 안에 고르지 않으면 돌이 가라앉아요.\n"
        f"4. **✋ 잠깐! 버튼** — 스테이지마다 {PAUSES_PER_STAGE}번 쓸 수 있어요. 누르면 시간이 멈추고 단서가 보여요.\n\n"
        f"틀리거나 돌이 가라앉으면 목숨이 하나 줄어요. (목숨 {LIVES}개)\n\n"
        "마지막에는 **잠깐!을 쓰고 고른 판단**과 **바로 고른 판단**의 정답률을 비교해 보여 줘요."
    )
    st.toggle(
        "⏳ 시간 제한 켜기 (끄면 천천히 할 수 있어요)",
        value=True,
        key="rv_timer_toggle",
    )
    st.caption(
        "모든 문자·기관명·상황은 교육용 가상 자료예요. "
        "게임 속 ‘진짜’도 실제로는 헷갈리면 앱이나 저장된 번호로 다시 확인하는 게 가장 좋아요."
    )
    st.button("🌊 강가로 가기", type="primary", on_click=start)


def show_map(g):
    done = len(g["cleared"])
    if done == 0:
        show_mascot("welcome", "첫 번째 강부터 건너 볼까요? 헷갈리면 잠깐!을 아끼지 마세요.", width=90)
    elif done < len(STAGES):
        show_mascot("welcome", f"벌써 {done}개의 강을 건넜어요! 다음 강도 함께 가요.", width=90)
    st.markdown(f"### 🗺️ 스테이지 지도 · {done} / {len(STAGES)} 통과")
    st.progress(done / len(STAGES))
    left, right = st.columns([3, 1])
    left.caption(f"⏳ 시간 제한: {'켜짐' if g['timer'] else '꺼짐'}")
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
                st.markdown(f"**{mark} STAGE {index + 1} · {stage['icon']} {stage['title']}**")
                st.caption(stage["lesson"] if unlocked else "앞 스테이지를 통과하면 열려요.")
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
        show_mascot("trophy", "모든 강을 건넜어요! 이제 진짜와 가짜를 가려내는 눈이 생겼어요.")
        st.success("🏅 **피싱 감별사 배지 획득!**")
        st.markdown("#### ✋ 멈춘 판단 vs 바로 고른 판단")
        show_stats(g)
        st.markdown(
            "**기억해요**\n"
            "- 중고거래는 앱 안에서만 대화하고 결제해요.\n"
            "- 현금 전달·통장 대여 알바는 범죄 가담이 될 수 있어요.\n"
            "- ‘원금 보장’, ‘확정 수익’ 투자는 없어요.\n"
            "- 누가 붙였는지 모르는 QR코드는 찍기 전에 한 번 더 생각해요.\n"
            "- 공짜라면서 정보·인증·결제를 요구하면 멈춰요.\n"
            "- 그리고 무엇보다, 헷갈리면 **잠깐!**"
        )
        st.button("🔄 처음부터 다시", on_click=restart_all)


def show_note(stage):
    note = stage["note"]
    show_mascot("detective", "먼저 이 가짜 문자에 어떤 수법이 숨어 있는지 뜯어봐요.", width=100)
    st.markdown(f"### 🕵️ 수법 해부 노트 · {stage['icon']} {stage['title']}")
    st.markdown(
        f'<div class="rv-note"><b>교육용 가짜 문자</b>'
        f'<div class="msg">{marked_message(note["message"], note["parts"])}</div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    for part, why in note["parts"]:
        st.markdown(f"- **‘{part}’** — {why}")
    st.info(f"🛡️ **이렇게 막아요** · {note['defense']}")
    st.button("🌊 강 건너러 가기", type="primary", on_click=go_river)
    st.button("🗺️ 지도로 돌아가기", on_click=back_to_map)


@st.fragment(run_every=1)
def countdown():
    """1초마다 남은 시간을 보여 주고, 시간이 다 되면 돌을 가라앉혀요."""
    g = game()
    if g["phase"] != "river" or g["feedback"] or g["paused"] or not g["timer"]:
        return
    left = g["deadline"] - time.time()
    if left <= 0:
        sink()
        st.rerun()
    seconds = max(0, int(left + 0.999))
    st.progress(max(0.0, min(1.0, left / TIME_LIMIT)))
    st.markdown(f'<span class="rv-clock">⏳ {seconds}초 뒤 돌이 가라앉아요</span>', unsafe_allow_html=True)


def show_feedback(g):
    feedback = g["feedback"]
    pair = feedback["pair"]
    if feedback["timeout"]:
        st.error("🫧 꼬르륵… 시간이 다 되어 돌이 가라앉았어요. 목숨이 하나 줄었어요.")
        show_mascot("suspicious", "급하면 판단이 흐려져요. 다음엔 잠깐!으로 시간을 멈춰 봐요.", width=80)
    elif feedback["correct"]:
        st.success("✅ 안전한 돌을 밟았어요! 한 칸 앞으로!")
        if g["pos"] >= len(STAGES[g["stage"]]["pairs"]):
            show_mascot("shield", "마지막 돌까지 안전하게 지켜 냈어요!", width=80)
    else:
        st.error("💦 풍덩! 가짜 돌을 밟았어요. 목숨이 하나 줄었어요.")

    left, right = st.columns(2)
    with left:
        st.markdown(card_html(pair["real"], "✅ 진짜", "real"), unsafe_allow_html=True)
        st.caption(pair["real"]["why"])
    with right:
        st.markdown(card_html(pair["fake"], "🚨 가짜", "fake"), unsafe_allow_html=True)
        st.caption(pair["fake"]["why"])
    st.button("다음 ➡️", type="primary", on_click=next_step)


def show_river(g, stage):
    total = len(stage["pairs"])
    st.markdown(f"### 🌊 STAGE {g['stage'] + 1} · {stage['title']}")
    st.markdown(
        f"**목숨** {'❤️' * g['lives']}{'🤍' * (LIVES - g['lives'])}  ·  "
        f"**✋ 잠깐!** {g['pauses']} / {PAUSES_PER_STAGE}  ·  "
        f"**건넌 칸** {g['pos']} / {total}"
    )
    st.markdown(river_html(g["pos"], total), unsafe_allow_html=True)

    if g["feedback"]:
        show_feedback(g)
        return

    pair = current_pair(g)
    real_is_a = g["sides"][g["pos"]]
    stone_a, stone_b = (pair["real"], pair["fake"]) if real_is_a else (pair["fake"], pair["real"])

    st.markdown(f"#### 칸 {g['pos'] + 1} · 어느 돌이 안전할까요?")

    if g["paused"]:
        show_mascot("stop", f"잠깐! 시간이 멈췄어요. 단서 · {pair['clue']}", width=90)
    elif g["timer"]:
        countdown()

    left, right = st.columns(2)
    with left:
        st.markdown(card_html(stone_a, "🅰 돌"), unsafe_allow_html=True)
        st.button("🅰 이 돌을 밟는다", use_container_width=True, on_click=choose, args=(True,), key=f"rv_a_{g['pos']}")
    with right:
        st.markdown(card_html(stone_b, "🅱 돌"), unsafe_allow_html=True)
        st.button("🅱 이 돌을 밟는다", use_container_width=True, on_click=choose, args=(False,), key=f"rv_b_{g['pos']}")

    if not g["paused"]:
        st.button(
            f"✋ 잠깐! (남은 횟수 {g['pauses']})",
            on_click=press_pause,
            disabled=g["pauses"] <= 0,
            key=f"rv_pause_{g['pos']}",
        )
        st.caption("잠깐!을 누르면 시간이 멈추고 단서가 하나 보여요.")


def show_clear(g, stage):
    show_mascot("escape", "건너편에 도착했어요!", width=100)
    st.markdown(river_html(len(stage["pairs"]), len(stage["pairs"])), unsafe_allow_html=True)
    st.success(f"🎉 STAGE {g['stage'] + 1} 통과! 남은 목숨 {'❤️' * g['lives']}")
    st.write(f"**이번 수법:** {stage['lesson']}")
    with st.expander("✋ 지금까지의 판단 기록 보기"):
        show_stats(g)
    st.button("🗺️ 지도에서 다음 스테이지로", type="primary", on_click=back_to_map)


def show_fail(g, stage):
    show_mascot("retry", "괜찮아요. 수법 노트를 다시 보고, 이번엔 잠깐!도 써 봐요.", width=100)
    st.error(f"💦 STAGE {g['stage'] + 1}에서 목숨을 모두 잃었어요.")
    st.write(f"**다시 떠올려 봐요:** {stage['lesson']}")
    st.button("🕵️ 수법 노트 다시 보기", type="primary", on_click=open_stage, args=(g["stage"],))
    st.button("🗺️ 지도로 돌아가기", on_click=back_to_map)


# ─────────────────────────────────────
# 화면
# ─────────────────────────────────────

st.title("🌊 잠깐! · 진짜·가짜 강 건너기")
st.write("두 갈래 징검다리에서 **안전한 돌**을 골라 강을 건너요. 헷갈리면 **✋ 잠깐!**")
st.caption("교육용 가상 게임입니다. 실제 문자 발송, 링크 접속, 결제는 일어나지 않아요.")

g = game()

if not g["started"]:
    show_intro()
elif g["stage"] is None:
    show_map(g)
else:
    stage = STAGES[g["stage"]]
    if g["phase"] == "note":
        show_note(stage)
    elif g["phase"] == "river":
        show_river(g, stage)
    elif g["phase"] == "clear":
        show_clear(g, stage)
    else:
        show_fail(g, stage)
