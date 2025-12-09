import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="예산 쇼핑 미션",
    page_icon="🛒",
    layout="wide"
)

# 미션(예산) 설정: 이름과 예산 금액(원)
MISSIONS = {
    "절약 여행 준비": 30000,
    "학교 축제 준비": 50000,
    "새 학기 준비": 70000,
}

# 쇼핑할 상품 목록 (품명, 가격, 이모지)
ITEMS = [
    {
        "id": "notebook_set",
        "name": "줄 공책 3권 세트",
        "price": 3000,
        "emoji": "📒",
    },
    {
        "id": "pen_set",
        "name": "볼펜 5개 세트",
        "price": 4000,
        "emoji": "🖊️",
    },
    {
        "id": "highlighter",
        "name": "형광펜 4색 세트",
        "price": 3500,
        "emoji": "🖍️",
    },
    {
        "id": "backpack",
        "name": "기본 학생 가방",
        "price": 25000,
        "emoji": "🎒",
    },
    {
        "id": "tumbler",
        "name": "보온 텀블러",
        "price": 12000,
        "emoji": "☕",
    },
    {
        "id": "snack_pack",
        "name": "간식 모둠 세트",
        "price": 8000,
        "emoji": "🍪",
    },
    {
        "id": "powerbank",
        "name": "휴대용 보조 배터리",
        "price": 18000,
        "emoji": "🔋",
    },
    {
        "id": "earphone",
        "name": "유선 이어폰",
        "price": 10000,
        "emoji": "🎧",
    },
    {
        "id": "folder_file",
        "name": "파일/화일 세트",
        "price": 5000,
        "emoji": "📁",
    },
]

# 세션 상태 초기화 함수
def init_session_state():
    defaults = {
        "step": 1,  # 1: 미션 선택, 2: 쇼핑, 3: 결과
        "mission": None,
        "budget": None,
        "cart": [],  # 담은 상품들 리스트
        "reason": "",
        "reason_submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


def get_cart_total():
    """장바구니 총합 계산"""
    return sum(item["price"] for item in st.session_state.cart)


def render_mi_
