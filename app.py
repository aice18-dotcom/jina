import streamlit as st
import random
import math
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(
    page_title="좌표 보물찾기 게임",
    page_icon="🗺️",
    layout="wide"
)

# 좌표 범위 설정 (학생에게도 안내)
X_MIN, X_MAX = -10, 10
Y_MIN, Y_MAX = -10, 10


def init_session_state():
    """세션 상태 기본값 설정"""
    defaults = {
        "step": 1,              # 1: 시작 화면, 2: 게임(지도), 3: 결과 화면
        "treasure_x": None,
        "treasure_y": None,
        "attempts": [],         # 각 시도: dict {x, y, manhattan, euclid}
        "found": False,
        "reflection": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def safe_rerun():
    """버전에 맞게 rerun 안전하게 호출"""
    if hasattr(st, "rerun"):
        st.rerun()


def create_new_treasure():
    """새 보물 좌표 생성"""
    st.session_state.treasure_x = random.randint(X_MIN, X_MAX)
    st.session_state.treasure_y = random.randint(Y_MIN, Y_MAX)
    st.session_state.attempts = []
    st.session_state.found = False


def get_hint_sentence(dx_to_treasure, dy_to_treasure):
    """
    dx_to_treasure: 보물_x - 현재_x
    dy_to_treasure: 보물_y - 현재_y
    학생 위치 기준으로 보물의 방향/거리 문장 생성
    """
    if dx_to_treasure == 0 and dy_to_treasure == 0:
        return "🎉 정확히 보물을 찾았어요!"

    parts = []

    # 좌우 방향
    if dx_to_treasure > 0:
        parts.append(f"오른쪽으로 {dx_to_treasure}칸")
    elif dx_to_treasure < 0:
        parts.append(f"왼쪽으로 {abs(dx_to_treasure)}칸")

    # 위아래 방향
    if dy_to_treasure > 0:
        parts.append(f"위로 {dy_to_treasure}칸")
    elif dy_to_treasure < 0:
        parts.append(f"아래로 {abs(dy_to_treasure)}칸")

    if parts:
        return "보물은 현재 위치에서 " + ", ".join(parts) + " 떨어져 있어요."
    else:
        # 이론상 여기 올 일은 없지만 보호용
        return "보물과의 거리를 계산하는 중 문제가 생겼어요."


def get_xy_match_hint(guess_x, guess_y, tx, ty):
    """x좌표, y좌표가 맞았는지에 대한 힌트"""
    if guess_x == tx and guess_y == ty:
        return "x좌표와 y좌표가 모두 정확합니다!"
    elif guess_x == tx:
        return "x좌표는 맞고, y좌표는 틀렸어요."
    elif guess_y == ty:
        return "y좌표는 맞고, x좌표는 틀렸어요."
    else:
        return "x좌표와 y좌표가 모두 다릅니다."


def draw_coordinate_plane(show_treasure=False):
    """
    정사각형 좌표평면 그리기
    - 가운데 가로축: x축 (y=0)
    - 가운데 세로축: y축 (x=0)
    """
    # 정사각형 비율 유지
    fig, ax = plt.subplots(figsize=(6, 6))

    # 좌우/위아래 대칭 범위 설정 (정사각형)
    ax.set_xlim(X_MIN - 0.5, X_MAX + 0.5)
    ax.set_ylim(Y_MIN - 0.5, Y_MAX + 0.5)
    ax.set_aspect("equal", adjustable="box")

    # 격자선
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)

    # 가운데 x축(y=0), y축(x=0)을 굵게 표시
    ax.axhline(0, linewidth=2)
    ax.axvline(0, linewidth=2)

    # 정수 눈금
    ax.set_xticks(range(X_MIN, X_MAX + 1))
    ax.set_yticks(range(Y_MIN, Y_MAX + 1))

    # 시도한 좌표들 그리기
    attempts = st.session_state.attempts
    if attempts:
        xs = [a["x"] for a in attempts]
        ys = [a["y"] for a in attempts]
        ax.scatter(xs, ys, s=50)
        # 번호 라벨 붙이기
        for i, (x, y) in enumerate(zip(xs, ys), start=1):
            ax.text(x + 0.2, y + 0.2, str(i), fontsize=9)

    # 보물 위치 표시 (결과 화면에서만)
    if show_treasure and st.session_state.treasure_x is not None:
        tx = st.session_state.treasure_x
        ty = st.session_state.treasure_y
        ax.scatter([tx], [ty], marker="*", s=200)
        ax.text(tx + 0.2, ty + 0.2, "보물", fontsize=10)

    ax.set_xlabel("x 좌표")
    ax.set_ylabel("y 좌표")
    return fig


def render_start_page():
    st.title("🗺️ 좌표 보물찾기 게임")
    st.write("좌표평면 위에 숨겨진 **보물의 위치**를 추리해보는 활동입니다.")

    st.markdown(
        f"""
        **게임 규칙**
        - 보물은 정수 좌표 위에 숨겨져 있어요.  
        - 좌표 범위: **x: {X_MIN} ~ {X_MAX}, y: {Y_MIN} ~ {Y_MAX}**  
        - 여러분은 (x, y) 좌표를 입력해서 보물 위치를 추측합니다.  
        - 매 시도마다  
          - 보물이 어느 방향에 있는지  
          - x좌표 / y좌표가 맞았는지  
          - 거리(맨해튼 거리, 유클리드 거리)를 알려줄 거예요.
        """
    )

    st.markdown("---")

    st.subheader("🎯 힌트 예시")
    st.write("- \"x좌표는 2의 배수예요.\"")
    st.write("- \"y좌표는 -3보다 커요.\"")
    st.write("- \"보물은 현재 위치에서 **오른쪽으로 2칸, 위로 1칸** 떨어져 있어요.\"")
    st.write("- \"x좌표는 맞고, y좌표는 틀렸어요.\"")

    if st.button("🎮 새 게임 시작"):
        create_new_treasure()
        st.session_state.step = 2
        safe_rerun()


def render_game_page():
    st.title("📍 보물 좌표 찾기")

    if st.session_state.treasure_x is None or st.session_state.treasure_y is None:
        st.warning("먼저 시작 화면에서 게임을 시작해주세요.")
        if st.button("⬅ 시작 화면으로 돌아가기"):
            st.session_state.step = 1
            safe_rerun()
        return

    tx, ty = st.session_state.treasure_x, st.session_state.treasure_y

    # 왼쪽: 좌표 입력 / 힌트, 오른쪽: 그래프
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("좌표를 입력해서 보물을 찾아보세요!")

        guess_x = st.number_input(
            "x 좌표를 입력하세요",
            min_value=X_MIN,
            max_value=X_MAX,
            value=0,
            step=1,
        )
        guess_y = st.number_input(
            "y 좌표를 입력하세요",
            min_value=Y_MIN,
            max_value=Y_MAX,
            value=0,
            step=1,
        )

        if st.button("📌 이 좌표로 추측하기"):
            # 거리 계산
            dx = guess_x - tx
            dy = guess_y - ty
            manhattan = abs(dx) + abs(dy)
            euclid = math.sqrt(dx ** 2 + dy ** 2)

            dx_to_treasure = tx - guess_x
            dy_to_treasure = ty - guess_y

            hint_direction = get_hint_sentence(dx_to_treasure, dy_to_treasure)
            hint_match = get_xy_match_hint(guess_x, guess_y, tx, ty)

            attempt = {
                "x": guess_x,
                "y": guess_y,
                "manhattan": manhattan,
                "euclid": euclid,
                "hint_direction": hint_direction,
                "hint_match": hint_match,
            }
            st.session_state.attempts.append(attempt)

            if manhattan == 0:
                st.session_state.found = True

            safe_rerun()

        st.markdown("---")
        st.subheader("📜 지금까지의 시도")

        if not st.session_state.attempts:
            st.info("아직 시도한 좌표가 없습니다. 좌표를 입력하고 추측해보세요!")
        else:
            table_data = [
                {
                    "시도 번호": i + 1,
                    "x": a["x"],
                    "y": a["y"],
                    "맨해튼 거리": a["manhattan"],
                    "유클리드 거리(반올림)": round(a["euclid"], 2),
                    "좌표 힌트": a["hint_match"],
                }
                for i, a in enumerate(st.session_state.attempts)
            ]
            st.table(table_data)

            # 마지막 시도에 대한 자세한 힌트
            last = st.session_state.attempts[-1]
            st.markdown("#### 🔍 가장 최근 시도에 대한 힌트")
            st.info(
                f"- 방향 힌트: {last['hint_direction']}\n"
                f"- 좌표 일치 여부: {last['hint_match']}\n"
                f"- 맨해튼 거리: {last['manhattan']}, 유클리드 거리(대략): {round(last['euclid'], 2)}"
            )

    with right_col:
        st.subheader("좌표평면에서 내 시도 보기")
        fig = draw_coordinate_plane(show_treasure=False)
        st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅ 시작 화면으로"):
            st.session_state.step = 1
            safe_rerun()
    with col2:
        if st.button("📊 결과 화면으로 이동"):
            st.session_state.step = 3
            safe_rerun()
    with col3:
        if st.button("🔁 보물 위치만 바꾸고 새로 시작"):
            create_new_treasure()
            safe_rerun()

    if st.session_state.found:
        st.success("🎉 정답 좌표를 맞췄어요! 결과 화면에서 전체 기록을 확인해보세요.")


def render_result_page():
    st.title("📦 보물찾기 결과 정리")

    if st.session_state.treasure_x is None or st.session_state.treasure_y is None:
        st.warning("아직 게임을 시작하지 않았습니다. 시작 화면으로 이동하세요.")
        if st.button("⬅ 시작 화면으로 돌아가기"):
            st.session_state.step = 1
            safe_rerun()
        return

    tx, ty = st.session_state.treasure_x, st.session_state.treasure_y

    st.subheader("🎯 보물의 실제 좌표")
    st.info(f"보물의 위치는 **({tx}, {ty})** 입니다.")

    st.markdown("---")

    st.subheader("📍 좌표평면에서 보기")
    fig = draw_coordinate_plane(show_treasure=True)
    st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📜 전체 시도 기록")

    attempts = st.session_state.attempts
    if not attempts:
        st.info("아직 시도한 좌표가 없습니다. 게임 화면에서 추측을 먼저 해보세요.")
    else:
        table_data = [
            {
                "시도 번호": i + 1,
                "x": a["x"],
                "y": a["y"],
                "맨해튼 거리": a["manhattan"],
                "유클리드 거리(반올림)": round(a["euclid"], 2),
            }
            for i, a in enumerate(attempts)
        ]
        st.table(table_data)

        # 가장 가까운 시도 찾기 (맨해튼 거리 기준)
        best_manhattan = min(attempts, key=lambda a: a["manhattan"])
        best_euclid = min(attempts, key=lambda a: a["euclid"])

        st.markdown("### 🏆 가장 보물에 가까웠던 시도는?")
        st.write(
            f"- **맨해튼 거리 기준**: 좌표 **({best_manhattan['x']}, {best_manhattan['y']})**, "
            f"거리: {best_manhattan['manhattan']}"
        )
        st.write(
            f"- **유클리드 거리 기준**: 좌표 **({best_euclid['x']}, {best_euclid['y']})**, "
            f"거리: {round(best_euclid['euclid'], 2)}"
        )

    st.markdown("---")
    st.subheader("📝 되돌아보기 질문")

    st.write("다음 질문 중 하나를 골라서 적어보게 할 수 있어요:")
    st.write("- 어떤 전략으로 보물 위치를 줄여 나갔나요?")
    st.write("- 좌표와 거리를 함께 보면서 어떤 점을 깨달았나요?")
    st.write("- 다음에 다시 한다면, 처음에는 어디서부터 시도해보고 싶나요?")

    st.session_state.reflection = st.text_area(
        "학생이 스스로 정리할 수 있는 공간",
        value=st.session_state.reflection,
        height=120,
    )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅ 게임 화면으로 돌아가기"):
            st.session_state.step = 2
            safe_rerun()
    with col2:
        if st.button("🏁 완전히 새 게임 시작"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            init_session_state()
            safe_rerun()
    with col3:
        if st.button("⬅ 시작 화면으로"):
            st.session_state.step = 1
            safe_rerun()


# --------- 메인 실행 ---------
init_session_state()

if st.session_state.step == 1:
    render_start_page()
elif st.session_state.step == 2:
    render_game_page()
elif st.session_state.step == 3:
    render_result_page()
else:
    st.session_state.step = 1
    render_start_page()
