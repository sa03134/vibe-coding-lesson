"""
현대자동차 지역 거점 네이버 리뷰 감성 분석 대시보드
====================================================
Streamlit 기반의 리뷰 감성 분석 및 시각화 대시보드입니다.
샘플 데이터 또는 CSV 업로드를 통해 동작합니다.
"""

import io

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import (
    analyze_reviews,
    analyze_sentiment,
    classify_categories,
    extract_keywords,
    generate_summary,
)
from sample_data import BRANCHES, generate_reviews

# ──────────────────────────────────────────────
# 페이지 설정 및 브랜드 스타일링
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="현대자동차 리뷰 감성 분석",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 현대자동차 브랜드 컬러 기반 커스텀 CSS
HYUNDAI_CSS = """
<style>
    /* 현대 브랜드 컬러: Dark Blue #002C5F, Active Blue #00AAD2, White */
    .stApp {
        background-color: #F7F9FC;
    }
    .main-header {
        background: linear-gradient(135deg, #002C5F 0%, #003E7E 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: white;
        font-size: 1.8rem;
        margin: 0;
    }
    .main-header p {
        color: #B0C4DE;
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid #002C5F;
        text-align: center;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #002C5F;
    }
    .metric-card .label {
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    .praise-box {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .improve-box {
        background: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    .review-positive {
        border-left: 3px solid #4CAF50;
        padding-left: 0.8rem;
        margin: 0.5rem 0;
    }
    .review-negative {
        border-left: 3px solid #F44336;
        padding-left: 0.8rem;
        margin: 0.5rem 0;
    }
    .review-neutral {
        border-left: 3px solid #9E9E9E;
        padding-left: 0.8rem;
        margin: 0.5rem 0;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #002C5F 0%, #001A3A 100%);
    }
    div[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    div[data-testid="stSidebar"] label {
        color: white !important;
    }
</style>
"""
st.markdown(HYUNDAI_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────

st.markdown(
    """
<div class="main-header">
    <h1>현대자동차 지역 거점 리뷰 감성 분석 대시보드</h1>
    <p>고객 리뷰 데이터를 AI 감성 분석하여 서비스 개선 인사이트를 도출합니다</p>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 사이드바: 데이터 입력
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 데이터 설정")

    data_source = st.radio(
        "데이터 소스 선택",
        ["샘플 데이터 사용", "CSV 파일 업로드"],
        index=0,
    )

    if data_source == "샘플 데이터 사용":
        selected_branch = st.selectbox(
            "분석할 지점 선택",
            list(BRANCHES.keys()),
        )
        review_count = st.slider("리뷰 수", min_value=10, max_value=100, value=50)

        # 샘플 데이터 로드
        raw_reviews = generate_reviews(selected_branch, review_count)
        branch_info = BRANCHES[selected_branch]

    else:
        st.markdown(
            """
            **CSV 파일 형식 안내:**
            - 필수 컬럼: `text` (리뷰 내용)
            - 선택 컬럼: `author`, `rating`, `date`
            """
        )
        uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

        if uploaded_file is not None:
            df_upload = pd.read_csv(uploaded_file)
            if "text" not in df_upload.columns:
                st.error("CSV 파일에 'text' 컬럼이 필요합니다.")
                st.stop()

            raw_reviews = []
            for i, row in df_upload.iterrows():
                raw_reviews.append(
                    {
                        "id": i + 1,
                        "branch": "업로드된 데이터",
                        "author": row.get("author", f"사용자{i+1}"),
                        "rating": row.get("rating", 3),
                        "text": row["text"],
                        "categories": [],
                        "date": row.get("date", "2025-01-01"),
                    }
                )
            selected_branch = "업로드된 데이터"
            branch_info = {"address": "-", "phone": "-", "rating": "-"}
        else:
            st.info("CSV 파일을 업로드하거나, 샘플 데이터를 사용해주세요.")
            st.stop()

    st.markdown("---")
    st.markdown("### 필터 옵션")

    sentiment_filter = st.multiselect(
        "감성 필터",
        ["긍정", "중립", "부정"],
        default=["긍정", "중립", "부정"],
    )

    category_filter = st.multiselect(
        "카테고리 필터",
        ["서비스", "친절도", "전문성", "시설", "대기시간"],
        default=["서비스", "친절도", "전문성", "시설", "대기시간"],
    )

# ──────────────────────────────────────────────
# 데이터 분석
# ──────────────────────────────────────────────

analyzed = analyze_reviews(raw_reviews)
summary = generate_summary(raw_reviews, analyzed)
keywords = extract_keywords(raw_reviews, top_n=15)

# 필터 적용
filtered = [
    r
    for r in analyzed
    if r["sentiment_label"] in sentiment_filter
    and any(cat in category_filter for cat in r["analyzed_categories"])
]

df = pd.DataFrame(filtered)

# ──────────────────────────────────────────────
# 지점 정보 및 핵심 지표
# ──────────────────────────────────────────────

st.markdown(f"#### {selected_branch}")

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.caption("주소")
    st.write(branch_info["address"])
with col_info2:
    st.caption("연락처")
    st.write(branch_info["phone"])
with col_info3:
    st.caption("네이버 평점")
    st.write(f"⭐ {branch_info['rating']}")

st.markdown("---")

# 핵심 KPI 지표
if not df.empty:
    positive_count = len(df[df["sentiment_label"] == "긍정"])
    negative_count = len(df[df["sentiment_label"] == "부정"])
    neutral_count = len(df[df["sentiment_label"] == "중립"])
    avg_score = df["sentiment_score"].mean()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="value">{len(df)}</div>
            <div class="label">분석된 리뷰</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="value" style="color:#4CAF50">{positive_count}</div>
            <div class="label">긍정 리뷰</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="value" style="color:#F44336">{negative_count}</div>
            <div class="label">부정 리뷰</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with kpi4:
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="value" style="color:#9E9E9E">{neutral_count}</div>
            <div class="label">중립 리뷰</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with kpi5:
        score_color = "#4CAF50" if avg_score >= 60 else "#F44336" if avg_score < 40 else "#FF9800"
        st.markdown(
            f"""
        <div class="metric-card">
            <div class="value" style="color:{score_color}">{avg_score:.1f}</div>
            <div class="label">평균 감성 점수</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # AI 핵심 요약
    # ──────────────────────────────────────────────

    st.markdown("### AI 핵심 요약")

    col_praise, col_improve = st.columns(2)

    with col_praise:
        st.markdown("**칭찬 포인트**")
        for i, point in enumerate(summary["praise_points"], 1):
            st.markdown(
                f'<div class="praise-box">✅ {point}</div>',
                unsafe_allow_html=True,
            )

    with col_improve:
        st.markdown("**개선 필요 포인트**")
        for i, point in enumerate(summary["improvement_points"], 1):
            st.markdown(
                f'<div class="improve-box">⚠️ {point}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ──────────────────────────────────────────────
    # 시각화 섹션
    # ──────────────────────────────────────────────

    st.markdown("### 분석 차트")

    chart_col1, chart_col2 = st.columns(2)

    # 1) 긍정/부정/중립 비율 파이 차트
    with chart_col1:
        sentiment_counts = df["sentiment_label"].value_counts()
        fig_pie = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="감성 분포",
            color=sentiment_counts.index,
            color_discrete_map={
                "긍정": "#4CAF50",
                "부정": "#F44336",
                "중립": "#9E9E9E",
            },
            hole=0.4,
        )
        fig_pie.update_layout(
            font=dict(size=13),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 2) 카테고리별 감성 점수
    with chart_col2:
        cat_data = []
        for _, row in df.iterrows():
            for cat in row["analyzed_categories"]:
                cat_data.append(
                    {"category": cat, "score": row["sentiment_score"]}
                )
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            cat_avg = df_cat.groupby("category")["score"].mean().reset_index()
            cat_avg.columns = ["카테고리", "평균 점수"]

            fig_bar = px.bar(
                cat_avg,
                x="카테고리",
                y="평균 점수",
                title="카테고리별 평균 감성 점수",
                color="평균 점수",
                color_continuous_scale=["#F44336", "#FF9800", "#4CAF50"],
                range_color=[0, 100],
            )
            fig_bar.update_layout(
                yaxis_range=[0, 100],
                font=dict(size=13),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            fig_bar.add_hline(
                y=50,
                line_dash="dash",
                line_color="#999",
                annotation_text="중립 기준선",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # 3) 주요 키워드 바 차트
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        if keywords:
            kw_df = pd.DataFrame(keywords, columns=["키워드", "빈도"])
            fig_kw = px.bar(
                kw_df.head(12),
                x="빈도",
                y="키워드",
                orientation="h",
                title="주요 언급 키워드 TOP 12",
                color="빈도",
                color_continuous_scale=["#B0C4DE", "#002C5F"],
            )
            fig_kw.update_layout(
                yaxis=dict(autorange="reversed"),
                font=dict(size=13),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig_kw, use_container_width=True)

    # 4) 날짜별 감성 추이
    with chart_col4:
        if "date" in df.columns:
            df_date = df.copy()
            df_date["date"] = pd.to_datetime(df_date["date"])
            df_date = df_date.sort_values("date")

            # 월별 집계
            df_date["month"] = df_date["date"].dt.to_period("M").astype(str)
            monthly = (
                df_date.groupby(["month", "sentiment_label"])
                .size()
                .reset_index(name="count")
            )

            fig_trend = px.bar(
                monthly,
                x="month",
                y="count",
                color="sentiment_label",
                title="월별 감성 분포 추이",
                color_discrete_map={
                    "긍정": "#4CAF50",
                    "부정": "#F44336",
                    "중립": "#9E9E9E",
                },
                barmode="stack",
            )
            fig_trend.update_layout(
                xaxis_title="월",
                yaxis_title="리뷰 수",
                font=dict(size=13),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend_title="감성",
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # ──────────────────────────────────────────────
    # 감성 점수 분포 히스토그램
    # ──────────────────────────────────────────────

    st.markdown("### 감성 점수 분포")
    fig_hist = px.histogram(
        df,
        x="sentiment_score",
        nbins=20,
        title="리뷰 감성 점수 분포",
        color="sentiment_label",
        color_discrete_map={
            "긍정": "#4CAF50",
            "부정": "#F44336",
            "중립": "#9E9E9E",
        },
        barmode="overlay",
        opacity=0.7,
    )
    fig_hist.update_layout(
        xaxis_title="감성 점수 (0: 매우 부정 ~ 100: 매우 긍정)",
        yaxis_title="리뷰 수",
        font=dict(size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # ──────────────────────────────────────────────
    # 개별 리뷰 상세 뷰
    # ──────────────────────────────────────────────

    st.markdown("### 개별 리뷰 상세")

    sort_option = st.selectbox(
        "정렬 기준",
        ["최신순", "감성 점수 높은순", "감성 점수 낮은순", "평점 높은순", "평점 낮은순"],
    )

    df_sorted = df.copy()
    if sort_option == "최신순":
        df_sorted = df_sorted.sort_values("date", ascending=False)
    elif sort_option == "감성 점수 높은순":
        df_sorted = df_sorted.sort_values("sentiment_score", ascending=False)
    elif sort_option == "감성 점수 낮은순":
        df_sorted = df_sorted.sort_values("sentiment_score", ascending=True)
    elif sort_option == "평점 높은순":
        df_sorted = df_sorted.sort_values("rating", ascending=False)
    elif sort_option == "평점 낮은순":
        df_sorted = df_sorted.sort_values("rating", ascending=True)

    # 페이지네이션
    reviews_per_page = 10
    total_pages = max(1, (len(df_sorted) + reviews_per_page - 1) // reviews_per_page)
    page = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)

    start_idx = (page - 1) * reviews_per_page
    end_idx = start_idx + reviews_per_page
    page_reviews = df_sorted.iloc[start_idx:end_idx]

    for _, row in page_reviews.iterrows():
        label = row["sentiment_label"]
        css_class = {
            "긍정": "review-positive",
            "부정": "review-negative",
            "중립": "review-neutral",
        }.get(label, "review-neutral")

        badge_color = {
            "긍정": "#4CAF50",
            "부정": "#F44336",
            "중립": "#9E9E9E",
        }.get(label, "#9E9E9E")

        stars = "⭐" * int(row["rating"])
        categories_str = ", ".join(row["analyzed_categories"])

        st.markdown(
            f"""
        <div class="{css_class}">
            <strong>{row['author']}</strong> &nbsp;
            {stars} &nbsp;
            <span style="background:{badge_color};color:white;padding:2px 8px;
                         border-radius:10px;font-size:0.8rem;">
                {label} ({row['sentiment_score']}점)
            </span>
            <span style="color:#888;font-size:0.8rem;margin-left:8px;">
                {row['date']}
            </span>
            <br>
            <span style="color:#333;margin-top:4px;display:inline-block;">
                {row['text']}
            </span>
            <br>
            <span style="color:#666;font-size:0.8rem;">
                분류: {categories_str}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.caption(f"페이지 {page} / {total_pages} (총 {len(df_sorted)}건)")

    st.markdown("---")

    # ──────────────────────────────────────────────
    # 데이터 내보내기
    # ──────────────────────────────────────────────

    st.markdown("### 데이터 내보내기")

    export_df = df[
        [
            "id",
            "author",
            "rating",
            "date",
            "text",
            "sentiment_score",
            "sentiment_label",
            "analyzed_categories",
        ]
    ].copy()
    export_df.columns = [
        "번호",
        "작성자",
        "평점",
        "작성일",
        "리뷰내용",
        "감성점수",
        "감성라벨",
        "분류카테고리",
    ]

    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="분석 결과 CSV 다운로드",
        data=csv_data,
        file_name=f"리뷰분석_{selected_branch}.csv",
        mime="text/csv",
    )

else:
    st.warning("선택한 필터 조건에 해당하는 리뷰가 없습니다. 필터를 조정해주세요.")

# ──────────────────────────────────────────────
# 푸터
# ──────────────────────────────────────────────

st.markdown(
    """
<div style="text-align:center;color:#888;padding:2rem 0 1rem 0;font-size:0.8rem;">
    현대자동차 리뷰 감성 분석 대시보드 | 학습용 프로젝트 | 샘플 데이터 기반
</div>
""",
    unsafe_allow_html=True,
)
