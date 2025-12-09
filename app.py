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


def safe_rerun():
    """streamlit 버전에 따라 rerun을 안전하게 호출"""
    if hasattr(st, "rerun"):
        st.rerun()


init_session_state()


def get_cart_total():
    """장바구니 총합 계산"""
    return sum(item["price"] for item in st.session_state.cart)


def render_mission_page():
    st.title("🧩 1. 미션 선택하기")
    st.write("학생이 오늘 수행할 **쇼핑 미션**과 **예산**을 선택하는 화면입니다.")

    st.subheader("미션을 골라주세요")

    option_labels = []
    label_to_mission = {}
    for name, budget in MISSIONS.items():
        label = f"{name} (예산: {budget:,}원)"
        option_labels.append(label)
        label_to_mission[label] = (name, budget)

    selected_label = st.radio(
        "원하는 미션을 선택하세요.",
        option_labels,
        index=None,
        horizontal=False,
    )

    if st.button("✅ 미션 선택 완료"):
        if selected_label is None:
            st.warning("먼저 미션을 선택해주세요.")
        else:
            mission_name, budget = label_to_mission[selected_label]
            st.session_state.mission = mission_name
            st.session_state.budget = budget
            st.session_state.cart = []  # 미션 바꿀 때 장바구니 초기화
            st.session_state.reason = ""
            st.session_state.reason_submitted = False
            st.session_state.step = 2
            st.success(f"'{mission_name}' 미션이 선택되었습니다! 이제 쇼핑을 시작해볼까요?")


def render_shopping_page():
    st.title("🛒 2. 쇼핑 화면")
    st.write("여러 가지 물품 중에서 원하는 상품을 선택하고 **장바구니에 담을 수 있는 화면**입니다.")

    if st.session_state.mission is None or st.session_state.budget is None:
        st.warning("먼저 미션을 선택해주세요.")
        if st.button("미션 선택 화면으로 돌아가기"):
            st.session_state.step = 1
        return

    # 상단에 미션 및 예산 정보 표시
    total = get_cart_total()
    remaining = st.session_state.budget - total

    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.metric("선택한 미션", st.session_state.mission)
    with info_col2:
        st.metric("총 예산", f"{st.session_state.budget:,}원")
    with info_col3:
        st.metric("현재 사용 금액", f"{total:,}원")

    if remaining >= 0:
        st.success(f"남은 예산: {remaining:,}원")
    else:
        st.error(f"예산을 {abs(remaining):,}원 초과했습니다! 일부 상품을 빼야 할 수도 있어요.")

    st.markdown("---")
    st.subheader("상품 목록")

    # 상품을 3열 그리드 형태로 보여주기 (이모지 사용)
    cols = st.columns(3)
    for idx, item in enumerate(ITEMS):
        col = cols[idx % 3]
        with col:
            # 이모지를 크게 표시
            st.markdown(
                f"<div style='font-size: 50px; text-align: center;'>{item['emoji']}</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"<p style='text-align:center;'><b>{item['name']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>가격: {item['price']:,}원</p>", unsafe_allow_html=True)
            if st.button("담기", key=f"add_{item['id']}"):
                st.session_state.cart.append(item)
                # 최신 Streamlit에서는 st.rerun() 사용
                safe_rerun()

    st.markdown("---")
    st.subheader("🧺 장바구니")

    if not st.session_state.cart:
        st.info("아직 장바구니에 담긴 물건이 없습니다. 원하는 상품의 **'담기' 버튼**을 눌러보세요.")
    else:
        # 장바구니 요약 (동일 상품 수량 합치기)
        summary = {}
        for item in st.session_state.cart:
            name = item["name"]
            price = item["price"]
            if name not in summary:
                summary[name] = {
                    "품명": name,
                    "수량": 0,
                    "단가(원)": price,
                    "합계(원)": 0,
                }
            summary[name]["수량"] += 1
            summary[name]["합계(원)"] += price

        st.table(list(summary.values()))
        st.write(f"**총 합계:** {total:,}원")
        st.write(f"**남은 예산:** {remaining:,}원")

    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ 미션 다시 선택하기"):
            st.session_state.step = 1
            safe_rerun()

    with col2:
        if st.button("💳 구매하기"):
            if not st.session_state.cart:
                st.warning("장바구니가 비어 있습니다. 먼저 상품을 담아주세요.")
            else:
                st.session_state.step = 3
                st.success("구매 화면으로 이동합니다.")
                safe_rerun()


def render_result_page():
    st.title("📦 3. 결과 화면")
    st.write("학생이 **구매한 물품을 모아보고**, **구매 이유를 제출하는 화면**입니다.")

    if st.session_state.mission is None or st.session_state.budget is None:
        st.warning("먼저 미션을 선택하고 쇼핑을 진행해주세요.")
        if st.button("미션 선택 화면으로 돌아가기"):
            st.session_state.step = 1
            safe_rerun()
        return

    total = get_cart_total()
    remaining = st.session_state.budget - total

    st.subheader("미션 및 예산 요약")
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.metric("미션", st.session_state.mission)
    with info_col2:
        st.metric("총 예산", f"{st.session_state.budget:,}원")
    with info_col3:
        st.metric("실제 사용 금액", f"{total:,}원")

    if remaining >= 0:
        st.success(f"남은 예산: {remaining:,}원")
    else:
        st.error(f"예산을 {abs(remaining):,}원 초과했습니다.")

    st.markdown("---")
    st.subheader("🧺 내가 구매한 물품")

    if not st.session_state.cart:
        st.info("구매한 물품이 없습니다. 쇼핑 화면으로 돌아가 상품을 담아주세요.")
        if st.button("쇼핑 화면으로 돌아가기"):
            st.session_state.step = 2
            safe_rerun()
        return

    # 장바구니 요약 테이블
    summary = {}
    for item in st.session_state.cart:
        name = item["name"]
        price = item["price"]
        if name not in summary:
            summary[name] = {
                "품명": name,
                "수량": 0,
                "단가(원)": price,
                "합계(원)": 0,
            }
        summary[name]["수량"] += 1
        summary[name]["합계(원)"] += price

    st.table(list(summary.values()))
    st.write(f"**총 사용 금액:** {total:,}원")

    st.markdown("---")
    st.subheader("📝 구매 이유 작성하기")

    st.write("왜 이런 물건들을 선택했는지, 예산을 어떻게 사용했는지 자유롭게 적어보세요.")
    st.session_state.reason = st.text_area(
        "구매 이유를 적어보세요.",
        value=st.session_state.reason,
        height=150
    )

    if st.button("📨 제출"):
        if not st.session_state.reason.strip():
            st.warning("구매 이유를 먼저 작성해주세요.")
        else:
            st.session_state.reason_submitted = True
            st.success("구매 이유가 성공적으로 제출되었습니다!")

    if st.session_state.reason_submitted:
        st.markdown("#### 제출된 구매 이유")
        st.info(st.session_state.reason)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ 쇼핑 화면으로 돌아가기"):
            st.session_state.step = 2
            safe_rerun()
    with col2:
        if st.button("🔄 처음부터 다시 하기"):
            # 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            safe_rerun()


# 현재 step에 따라 화면 렌더링
if st.session_state.step == 1:
    render_mission_page()
elif st.session_state.step == 2:
    render_shopping_page()
elif st.session_state.step == 3:
    render_result_page()
else:
    # 혹시 모를 오류 대비
    st.session_state.step = 1
    render_mission_page()
