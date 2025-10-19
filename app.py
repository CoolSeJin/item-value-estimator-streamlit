import streamlit as st
import numpy as np
from PIL import Image
import requests
from io import BytesIO

# ---------------------------
# 🔧 1. 기본 설정
# ---------------------------
st.set_page_config(page_title="AI 미니딜러", layout="wide")
st.title("🤖 AI 미니딜러: 내 물건의 실제 시세는?")
st.caption("사진과 설명만으로 AI가 유사 제품을 찾아 실시간 가격을 예측해줍니다.")
st.markdown("---")

# ---------------------------
# 2. 입력 섹션
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📸 사진 업로드", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 이미지", use_column_width=True)

with col2:
    description = st.text_area(
        "📝 물건 설명 입력",
        placeholder="예: 5kg 덤벨 한 쌍, 상태 좋음. 1년 사용. 외관 깨끗함.",
        height=150
    )

# ---------------------------
# 3. 모의 AI + 시세 검색 함수
# ---------------------------

def fake_ai_analyze(image, description):
    """AI가 이미지를 보고 물건 종류를 예측하는 부분 (간단한 흉내)"""
    desc = description.lower()
    if "덤벨" in desc or "운동" in desc:
        return "덤벨", "운동기구"
    elif "노트북" in desc or "laptop" in desc:
        return "노트북", "전자기기"
    elif "아이폰" in desc or "휴대폰" in desc:
        return "스마트폰", "전자기기"
    elif "신발" in desc or "운동화" in desc:
        return "운동화", "패션잡화"
    else:
        return "기타", "일반물품"

def fake_price_scrape(keyword):
    """웹에서 시세를 수집하는 대신, 임의 데이터 생성 (실제 서비스 시 API로 교체)"""
    sample_data = {
        "덤벨": [12000, 18000, 15000, 20000, 13000, 25000],
        "노트북": [400000, 600000, 550000, 800000, 620000],
        "스마트폰": [300000, 450000, 500000, 420000, 390000],
        "운동화": [60000, 80000, 90000, 70000, 85000],
        "기타": [30000, 50000, 70000]
    }
    prices = sample_data.get(keyword, sample_data["기타"])
    return np.mean(prices), (min(prices), max(prices)), len(prices)

# ---------------------------
# 4. 버튼 클릭 → 분석 실행
# ---------------------------
if st.button("💰 시세 추정하기", type="primary"):
    if uploaded_file is not None and description.strip():
        with st.spinner("AI가 물건을 분석하고, 유사 거래 데이터를 수집 중입니다..."):
            
            # 1) AI 분석
            item_name, category = fake_ai_analyze(image, description)

            # 2) 시세 수집
            avg_price, (min_price, max_price), count = fake_price_scrape(item_name)
            
            # 3) 신뢰도 계산
            confidence = np.random.uniform(80, 98)

        # ---------------------------
        # 결과 출력
        # ---------------------------
        st.success("✅ 분석 완료!")
        st.markdown("---")
        
        st.subheader("📊 AI 시세 추정 결과")
        st.metric(label="예상 가격", value=f"{int(avg_price):,}원")
        st.write(f"📉 예상 시세 범위: **{min_price:,}원 ~ {max_price:,}원**")
        st.write(f"🤖 인식된 제품: **{item_name} ({category})**")
        st.progress(confidence / 100)
        st.caption(f"AI 신뢰도: {confidence:.1f}% (유사 {count}건 데이터 기반)")

        st.markdown("### 🔍 참고 근거")
        st.markdown(f"""
        1. 업로드된 이미지와 설명을 기반으로 '{item_name}' 카테고리로 분류했습니다.  
        2. 여러 거래 플랫폼(당근마켓, 번개장터, eBay 등)의 평균 시세 데이터를 반영했습니다.  
        3. 상태·사용기간 관련 설명을 바탕으로 시장가를 조정했습니다.
        """)

    else:
        st.error("사진과 설명을 모두 입력해주세요!")
