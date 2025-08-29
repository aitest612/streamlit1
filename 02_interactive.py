# 2회차: 인터랙티브 요소 및 데이터 시각화
# 파일명: session2_interactive.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import seaborn as sns

# 페이지 설정
st.set_page_config(
    page_title="인터랙티브 데이터 분석",
    page_icon="🎮",
    layout="wide"
)

# 타이틀
st.title("🎮 인터랙티브 데이터 분석 대시보드")
st.markdown("사용자 입력에 따라 실시간으로 변화하는 차트를 체험해보세요!")
st.markdown("---")

# 샘플 데이터 생성
@st.cache_data
def create_sales_data():
    np.random.seed(42)
    
    # 날짜 범위 생성
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    data = []
    products = ['노트북', '스마트폰', '태블릿', '이어폰', '마우스']
    regions = ['서울', '부산', '대구', '인천', '광주']
    
    for date in dates:
        for product in products:
            for region in regions:
                sales = np.random.poisson(20) + np.random.randint(0, 50)
                price = np.random.normal(100, 20) + np.random.randint(50, 200)
                data.append({
                    '날짜': date,
                    '제품': product,
                    '지역': region,
                    '판매량': sales,
                    '가격': max(10, int(price)),
                    '매출': sales * max(10, int(price))
                })
    
    return pd.DataFrame(data)

df = create_sales_data()

# 사이드바 - 필터 옵션
st.sidebar.title("🎛️ 필터 옵션")
st.sidebar.markdown("원하는 조건을 선택하여 데이터를 필터링하세요.")

# 날짜 범위 선택
date_range = st.sidebar.date_input(
    "📅 날짜 범위 선택",
    value=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
    min_value=datetime(2023, 1, 1),
    max_value=datetime(2023, 12, 31)
)

# 제품 선택
selected_products = st.sidebar.multiselect(
    "🛍️ 제품 선택",
    options=df['제품'].unique(),
    default=df['제품'].unique()
)

# 지역 선택
selected_regions = st.sidebar.multiselect(
    "🗺️ 지역 선택",
    options=df['지역'].unique(),
    default=df['지역'].unique()
)

# 매출 범위 슬라이더
sales_range = st.sidebar.slider(
    "💰 매출 범위 (만원)",
    min_value=int(df['매출'].min()),
    max_value=int(df['매출'].max()),
    value=(int(df['매출'].min()), int(df['매출'].max()))
)

# 데이터 필터링
if len(date_range) == 2:
    filtered_df = df[
        (df['날짜'] >= pd.Timestamp(date_range[0])) &
        (df['날짜'] <= pd.Timestamp(date_range[1])) &
        (df['제품'].isin(selected_products)) &
        (df['지역'].isin(selected_regions)) &
        (df['매출'] >= sales_range[0]) &
        (df['매출'] <= sales_range[1])
    ]
else:
    filtered_df = df

# 메인 대시보드
st.header("📊 실시간 분석 결과")

# KPI 메트릭
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['매출'].sum()
    avg_sales = df['매출'].sum() / 365  # 일평균
    change = ((total_sales / len(filtered_df)) - avg_sales) / avg_sales * 100 if len(filtered_df) > 0 else 0
    st.metric(
        "총 매출", 
        f"₩{total_sales:,.0f}", 
        f"{change:+.1f}%"
    )

with col2:
    total_quantity = filtered_df['판매량'].sum()
    avg_quantity = df['판매량'].sum() / 365
    qty_change = ((total_quantity / len(filtered_df)) - avg_quantity) / avg_quantity * 100 if len(filtered_df) > 0 else 0
    st.metric(
        "총 판매량", 
        f"{total_quantity:,}개", 
        f"{qty_change:+.1f}%"
    )

with col3:
    avg_price = filtered_df['가격'].mean() if len(filtered_df) > 0 else 0
    overall_avg_price = df['가격'].mean()
    price_change = (avg_price - overall_avg_price) / overall_avg_price * 100
    st.metric(
        "평균 가격", 
        f"₩{avg_price:,.0f}", 
        f"{price_change:+.1f}%"
    )

with col4:
    unique_products = filtered_df['제품'].nunique()
    st.metric(
        "제품 종류", 
        f"{unique_products}개",
        "📦"
    )

st.markdown("---")

# 인터랙티브 차트 섹션
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("📈 시계열 매출 추이")
    
    # 차트 타입 선택
    chart_type = st.selectbox(
        "차트 타입 선택",
        ["선 그래프", "막대 그래프", "영역 차트"]
    )
    
    # 월별 매출 집계
    monthly_sales = filtered_df.groupby(filtered_df['날짜'].dt.to_period('M'))['매출'].sum().reset_index()
    monthly_sales['날짜'] = monthly_sales['날짜'].astype(str)
    
    if chart_type == "선 그래프":
        fig = px.line(monthly_sales, x='날짜', y='매출', 
                     title="월별 매출 추이", markers=True)
    elif chart_type == "막대 그래프":
        fig = px.bar(monthly_sales, x='날짜', y='매출', 
                    title="월별 매출 추이")
    else:
        fig = px.area(monthly_sales, x='날짜', y='매출', 
                     title="월별 매출 추이")
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("🥧 제품별 매출 비율")
    
    # 색상 팔레트 선택
    color_palette = st.selectbox(
        "색상 팔레트 선택",
        ["기본", "파스텔", "비비드", "다크"]
    )
    
    color_maps = {
        "기본": px.colors.qualitative.Set1,
        "파스텔": px.colors.qualitative.Pastel,
        "비비드": px.colors.qualitative.Vivid,
        "다크": px.colors.qualitative.Dark24
    }
    
    product_sales = filtered_df.groupby('제품')['매출'].sum().reset_index()
    
    fig_pie = px.pie(product_sales, values='매출', names='제품',
                     title="제품별 매출 분포",
                     color_discrete_sequence=color_maps[color_palette])
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

# 지역별 분석
st.markdown("---")
st.subheader("🗺️ 지역별 상세 분석")

region_tab1, region_tab2 = st.tabs(["📊 지역별 비교", "🔥 히트맵"])

with region_tab1:
    # 분석 기준 선택
    analysis_metric = st.radio(
        "분석 기준 선택",
        ["매출", "판매량", "평균 가격"],
        horizontal=True
    )
    
    region_analysis = filtered_df.groupby(['지역', '제품'])[analysis_metric.replace('평균 ', '')].agg(
        'sum' if analysis_metric != '평균 가격' else 'mean'
    ).reset_index()
    
    fig_bar = px.bar(region_analysis, x='지역', y=analysis_metric.replace('평균 ', ''), 
                     color='제품', title=f"지역별 {analysis_metric} 비교",
                     barmode='group')
    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

with region_tab2:
    # 히트맵 데이터 준비
    heatmap_data = filtered_df.groupby(['지역', '제품'])['매출'].sum().unstack(fill_value=0)
    
    fig_heatmap = px.imshow(heatmap_data.values,
                           x=heatmap_data.columns,
                           y=heatmap_data.index,
                           title="지역별 제품별 매출 히트맵",
                           color_continuous_scale="Viridis")
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# 고급 인터랙티브 기능
st.markdown("---")
st.header("🎯 고급 인터랙티브 기능")

advanced_col1, advanced_col2 = st.columns(2)

with advanced_col1:
    st.subheader("🎚️ 동적 필터링")
    
    # 실시간 필터링
    min_sales = st.number_input("최소 판매량", min_value=0, value=0)
    max_price = st.number_input("최대 가격", min_value=0, value=int(df['가격'].max()))
    
    # 조건부 필터링
    dynamic_filter = filtered_df[
        (filtered_df['판매량'] >= min_sales) & 
        (filtered_df['가격'] <= max_price)
    ]
    
    st.write(f"필터 조건에 맞는 데이터: **{len(dynamic_filter):,}건**")
    
    if len(dynamic_filter) > 0:
        st.dataframe(dynamic_filter.head(10))
    else:
        st.warning("조건에 맞는 데이터가 없습니다.")

with advanced_col2:
    st.subheader("📈 상관관계 분석")
    
    # 변수 선택
    x_var = st.selectbox("X축 변수", ['판매량', '가격', '매출'], key='x_var')
    y_var = st.selectbox("Y축 변수", ['판매량', '가격', '매출'], key='y_var')
    
    if x_var != y_var:
        fig_scatter = px.scatter(filtered_df, x=x_var, y=y_var, 
                                color='제품', size='매출',
                                hover_data=['지역'],
                                title=f"{x_var} vs {y_var} 상관관계")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 상관계수 계산
        correlation = filtered_df[x_var].corr(filtered_df[y_var])
        st.metric("상관계수", f"{correlation:.3f}")
    else:
        st.warning("다른 변수를 선택해주세요.")

# 실시간 데이터 업데이트 시뮬레이션
st.markdown("---")
st.subheader("⚡ 실시간 업데이트 시뮬레이션")

if st.button("🔄 데이터 새로고침"):
    # 캐시 클리어하고 새 데이터 생성
    st.cache_data.clear()
    st.experimental_rerun()

# 데이터 다운로드
st.markdown("---")
st.subheader("💾 데이터 다운로드")

col1, col2, col3 = st.columns(3)

with col1:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📄 CSV 다운로드",
        data=csv,
        file_name=f"filtered_sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col2:
    # 요약 통계
    summary_stats = filtered_df.describe()
    summary_csv = summary_stats.to_csv()
    st.download_button(
        label="📊 통계 요약 다운로드",
        data=summary_csv,
        file_name=f"sales_summary_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with col3:
    # 현재 필터 설정 저장
    filter_settings = {
        "날짜_시작": str(date_range[0]) if len(date_range) == 2 else "",
        "날짜_종료": str(date_range[1]) if len(date_range) == 2 else "",
        "선택된_제품": selected_products,
        "선택된_지역": selected_regions,
        "매출_최소": sales_range[0],
        "매출_최대": sales_range[1]
    }
    
    import json
    filter_json = json.dumps(filter_settings, ensure_ascii=False, indent=2)
    st.download_button(
        label="⚙️ 필터 설정 저장",
        data=filter_json,
        file_name=f"filter_settings_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

# 세션 상태 데모
st.markdown("---")
st.subheader("💾 세션 상태 관리")

# 세션 상태 초기화
if 'view_count' not in st.session_state:
    st.session_state.view_count = 0
if 'favorite_products' not in st.session_state:
    st.session_state.favorite_products = []

# 방문 카운터
st.session_state.view_count += 1
st.write(f"페이지 방문 횟수: **{st.session_state.view_count}회**")

# 즐겨찾기 기능
selected_for_favorite = st.multiselect(
    "즐겨찾는 제품을 선택하세요:",
    options=df['제품'].unique(),
    default=st.session_state.favorite_products
)

if st.button("즐겨찾기 저장"):
    st.session_state.favorite_products = selected_for_favorite
    st.success(f"즐겨찾기에 {len(selected_for_favorite)}개 제품이 저장되었습니다!")

if st.session_state.favorite_products:
    st.write("현재 즐겨찾기:", ", ".join(st.session_state.favorite_products))

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🎮 인터랙티브 데이터 분석 완료! 🎮</p>
        <p><em>사용자 입력에 반응하는 동적 대시보드</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)