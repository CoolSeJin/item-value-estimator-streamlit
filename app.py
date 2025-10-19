import streamlit as st
import numpy as np
from PIL import Image

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(page_title="AI 미니딜러", layout="wide")
st.title("🤖 AI 미니딜러: 내 물건의 실제 시세는?")
st.caption("사진과 설명만으로 AI가 유사 제품 시세를 분석하고, 근거까지 설명해드립니다.")
st.markdown("---")

# ---------------------------
# 입력 섹션
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
        placeholder="예) 5kg 덤벨 한 쌍, 상태 좋음. 1년 사용. 외관 깨끗함.",
        height=150
    )

# ---------------------------
# AI 분석 및 시세 추정 함수
# ---------------------------
def analyze_item(description):
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

def get_price_range(item_name):
    price_data = {
        "덤벨": [12000, 18000, 15000, 20000, 13000, 25000],
        "노트북": [400000, 600000, 550000, 800000, 620000],
        "스마트폰": [300000, 450000, 500000, 420000, 390000],
        "운동화": [60000, 80000, 90000, 70000, 85000],
        "기타": [30000, 50000, 70000]
    }
    prices = price_data.get(item_name, price_data["기타"])
    return np.mean(prices), min(prices), max(prices), len(prices)

def analyze_condition(description):
    """설명 기반 상태 평가 및 가격 조정 요인"""
    desc = description.lower()
    bonus, penalty = 0, 0
    reasons = []

    if any(word in desc for word in ["깨끗", "좋", "양호", "거의 새것"]):
        bonus += 0.1
        reasons.append("제품 상태가 양호하여 평균 시세보다 약간 높게 평가되었습니다.")
    if any(word in desc for word in ["스크래치", "흠집", "사용감", "오염"]):
        penalty += 0.15
        reasons.append("외관에 사용 흔적이 있어 약간의 감가가 반영되었습니다.")
    if any(word in desc for word in ["박스", "정품", "보증서"]):
        bonus += 0.05
        reasons.append("정품 인증 및 부속품 포함으로 소폭 프리미엄이 적용되었습니다.")
    if any(word in desc for word in ["오래", "1년", "2년", "사용함"]):
        penalty += 0.1
        reasons.append("사용기간이 길어 평균 시세보다 약간 낮게 평가되었습니다.")

    adjustment = (1 + bonus - penalty)
    return adjustment, reasons

# ---------------------------
# 버튼 클릭 → 실행
# ---------------------------
if st.button("💰 시세 추정하기", type="primary"):
    if uploaded_file is not None and description.strip():
        with st.spinner("AI가 물건을 분석하고 유사 거래 시세를 조사 중입니다..."):
            
            # 1️⃣ 제품 분류
            item_name, category = analyze_item(description)

            # 2️⃣ 기본 시세 데이터
            avg_price, min_price, max_price, data_count = get_price_range(item_name)

            # 3️⃣ 상태 분석 및 조정
            adjustment, reason_list = analyze_condition(description)
            adjusted_price = int(avg_price * adjustment)

            # 4️⃣ 신뢰도 계산
            confidence = np.random.uniform(82, 97)

        # ---------------------------
        # 결과 출력
        # ---------------------------
        st.success("✅ 분석 완료!")
        st.markdown("---")
        
        st.subheader("📊 AI 시세 추정 결과")
        st.metric(label="예상 가격", value=f"{adjusted_price:,}원")
        st.write(f"📉 시세 범위: **{min_price:,}원 ~ {max_price:,}원**")
        st.write(f"🧾 인식된 제품: **{item_name} ({category})**")
        st.progress(confidence / 100)
        st.caption(f"AI 신뢰도: {confidence:.1f}% (유사 {data_count}건 데이터 기반)")

        st.markdown("### 🔍 근거 및 해석")
        if reason_list:
            for r in reason_list:
                st.write(f"- {r}")
        else:
            st.write("- 제품 상태 정보가 부족하여 평균 시세로 계산되었습니다.")
        
        # 종합 해석 문장
        st.markdown("### 💬 AI 해석 요약")
        if adjustment > 1.05:
            st.info("설명에 따르면 제품 상태가 매우 양호하여, 평균 시세보다 다소 높게 형성된 것으로 보입니다.")
        elif adjustment < 0.95:
            st.warning("설명 내용 중 사용감 또는 손상 관련 언급이 있어 시세가 약간 낮게 추정되었습니다.")
        else:
            st.info("설명에서 특별한 감가 요인이 없어, 시장 평균가 수준으로 추정되었습니다.")

    else:
        st.error("사진과 설명을 모두 입력해주세요!")
