
import streamlit as st
import pandas as pd

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/seoul.csv"
)


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자 형식으로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 필요한 데이터만 사용
    df = df.dropna(subset=["날짜", "평균기온"]).copy()

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    return df


df = load_data()


# -----------------------------
# 연평균 기온 계산
# -----------------------------
annual = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

annual.columns = ["연도", "연평균 기온"]

# 연평균 기온이 실제로 존재하는 연도만 사용
annual = annual.dropna()

# 데이터의 마지막 연도 확인
latest_year = int(annual["연도"].max())

# 현재 데이터의 마지막 해가 완전한 연도인지 확인
last_year_count = df[df["연도"] == latest_year].shape[0]

# 윤년 여부를 고려한 해당 연도의 날짜 수
days_in_latest_year = (
    366
    if pd.Timestamp(f"{latest_year}-12-31").is_leap_year
    else 365
)

# 마지막 연도가 완전하지 않으면 제외
if last_year_count < days_in_latest_year:
    annual = annual[annual["연도"] < latest_year]

# 최근 100개의 완전한 연도만 선택
annual = annual.tail(100).copy()


# -----------------------------
# 화면
# -----------------------------
st.title("🌡️ 서울의 100년간 연평균 기온 변화")

st.markdown(
    """
    서울의 일별 평균기온 데이터를 이용해 **연평균 기온**을 계산하고,
    최근 100년 동안 기온이 어떻게 변화해 왔는지 그래프로 나타냈습니다.
    """
)

st.divider()


# -----------------------------
# 간단한 요약 정보
# -----------------------------
start_year = int(annual["연도"].min())
end_year = int(annual["연도"].max())

oldest_temp = annual.iloc[0]["연평균 기온"]
latest_temp = annual.iloc[-1]["연평균 기온"]
change = latest_temp - oldest_temp

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "분석 기간",
        f"{start_year}~{end_year}년"
    )

with col2:
    st.metric(
        "시작 연도의 평균기온",
        f"{oldest_temp:.1f} ℃"
    )

with col3:
    st.metric(
        "마지막 연도의 평균기온",
        f"{latest_temp:.1f} ℃",
        delta=f"{change:+.1f} ℃"
    )


st.subheader("📈 연평균 기온 변화")

# Streamlit 기본 차트
chart_data = annual.set_index("연도")[["연평균 기온"]]

st.line_chart(
    chart_data,
    y="연평균 기온",
    x_label="연도",
    y_label="연평균 기온 (℃)",
    use_container_width=True
)


st.caption(
    f"※ {start_year}년부터 {end_year}년까지의 완전한 연도 "
    "100개를 사용했습니다."
)


# -----------------------------
# 데이터 표
# -----------------------------
with st.expander("📋 연평균 기온 데이터 보기"):
    display_df = annual.copy()
    display_df["연평균 기온"] = display_df["연평균 기온"].round(2)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


st.divider()

st.caption(
    "데이터 출처: 기상청 서울 지점(108) 관측자료 / "
    "greatsong/modudata의 seoul.csv"
)
