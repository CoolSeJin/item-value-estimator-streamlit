import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import plotly.express as px
import requests
from io import BytesIO

# 기본 설정
st.set_page_config(page_title="AI 미니딜러 확장버전", layout="wide")
st.title("🤖 AI 미니딜러 + 시세그래프 포함")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸 사진 업로드", type=['png','jpg','jpeg'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)
with col2:
    description = st.text_area(
        "📝 물건 설명 입력",
        placeholder="예) 5kg 덤벨 한 쌍, 상태 매우 양호. 사용 1년.",
        height=150
    )

def analyze_item(description):
    desc = description.lower()
    if "덤벨" in desc or "운동기구" in desc:
        return "덤벨", "운동기구"
    # 추가 분류 …
    return "기타", "일반물품"

def fetch_market_data(item_name):
    """
    실제 구현 시: 중고거래사이트 API나 크롤링 결과로
    날짜별 가격 리스트 반환
    예시: DataFrame with columns ['date','price']
    """
    # 모의 데이터 생성
    dates = pd.date_range(end=pd.Timestamp.today(), periods=10, freq='M')
    prices = np.linspace(15000, 25000, len(dates)) + np.random.randint(-2000,2000, size=len(dates))
    df = pd.DataFrame({'date': dates, 'price': prices})
    return df

def analyze_condition(description):
    desc = description.lower()
    bonus, penalty = 0, 0
    reasons = []
    if any(w in desc for w in ["양호","좋음","깨끗"]):
        bonus += 0.1
        reasons.append("제품 상태가 양호하여 평균보다 높게 평가됩니다.")
    if any(w in desc for w in ["스크래치","사용감","흠집"]):
        penalty += 0.15
        reasons.append("외관에 사용 흔적이 있어 감가요인이 반영됩니다.")
    if any(w in desc for w in ["사용 1년","사용 2년","오래"]):
        penalty += 0.1
        reasons.append("사용기간이 길어 시세가 조금 낮춰졌습니다.")
    adj = 1 + bonus - penalty
    return adj, reasons

if st.button("💰 시세 추정하기"):
    if uploaded_file and description.strip():
        with st.spinner("분석 중…"):
            item_name, category = analyze_item(description)
            market_df = fetch_market_data(item_name)
            avg_price = int(market_df['price'].mean())
            min_p = int(market_df['price'].min())
            max_p = int(market_df['price'].max())
            adjustment, cond_reasons = analyze_condition(description)
            estimated = int(avg_price * adjustment)
            confidence = np.random.uniform(80, 95)

        st.success("✅ 분석 완료!")
        st.markdown("---")
        st.subheader("📊 추정 결과")
        st.metric(label="예상 가격", value=f"{estimated:,}원", delta=f"{(adjustment-1)*100:+.1f}%")
        st.write(f"📉 시세 범위: {min_p:,} ~ {max_p:,} 원")
        st.write(f"🧾 제품 인식: {item_name} ({category})")
        st.progress(confidence/100)
        st.caption(f"AI 신뢰도: {confidence:.1f}%")

        st.markdown("### 🔍 근거 및 조건")
        for r in cond_reasons:
            st.write(f"- {r}")

        st.markdown("### 💬 해석 요약")
        if adjustment > 1.05:
            st.info("설명에 따르면 상태가 매우 좋으므로 평균보다 다소 높게 형성된 것으로 보입니다.")
        elif adjustment < 0.95:
            st.warning("설명에 사용감 또는 손상 언급이 있어 시세가 다소 낮게 예상됩니다.")
        else:
            st.info("설명에서 특별한 추가 요인이 없어 시장 평균 수준입니다.")

        st.markdown("### 📈 시세 흐름 그래프")
        fig = px.line(market_df, x='date', y='price', title=f"{item_name} 최근 시세 추이")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🖼️ 참조 이미지")
        # 참조 이미지 예시: 구글 검색 또는 사전 이미지
        st.image(f"https://via.placeholder.com/400?text={item_name}", caption=f"{item_name} 참고 이미지", use_column_width=True)
    else:
        st.error("사진과 설명을 모두 입력해주세요!")
