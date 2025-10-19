pip install streamlit matplotlib pillow numpy openai requests
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import requests
import random
import io

# OpenAI API (CLIP 또는 GPT-4V용)
import openai
openai.api_key = "YOUR_OPENAI_API_KEY"

# -----------------------------
# Streamlit 기본 설정
# -----------------------------
st.set_page_config(page_title="AI 시세 예측 딜러", layout="wide")
st.title("💰 Mini 딜러 : AI 기반 이미지 시세 예측기")
st.write("사진을 올리면 AI가 상품을 인식하고 실시간 시세를 추정합니다.")

# -----------------------------
# 입력 섹션
# -----------------------------
uploaded_file = st.file_uploader("📸 상품 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])
item_description = st.text_area("📝 상품 설명을 입력하세요", placeholder="예: 루이비통 가방, 상태 A급, 사용 6개월 등")

# -----------------------------
# 함수: 이미지 → 품목 예측
# -----------------------------
def identify_item_with_ai(image_bytes):
    """
    OpenAI의 CLIP 또는 GPT-4V 모델로 이미지를 분석해 품목을 예측
    """
    try:
        result = openai.chat.completions.create(
            model="gpt-4o-mini",  # 이미지 인식 가능 모델
            messages=[
                {"role": "system", "content": "너는 이미지를 분석해서 품목 종류를 식별하는 AI야."},
                {"role": "user", "content": [
                    {"type": "text", "text": "이 이미지의 주요 상품은 무엇인가요?"},
                    {"type": "image", "image": image_bytes}
                ]}
            ]
        )
        return result.choices[0].message["content"]
    except Exception as e:
        return "이미지 분석 실패: " + str(e)

# -----------------------------
# 함수: 네이버쇼핑 시세 검색
# -----------------------------
def get_naver_shopping_price(query):
    """
    네이버 쇼핑 OPEN API를 사용하여 상품 시세를 검색 (Demo용 mock 데이터)
    """
    # 실제 연동 시 네이버 개발자 센터의 CLIENT_ID, CLIENT_SECRET 필요
    # 여기서는 임의의 가격을 생성
    base_price = random.randint(100000, 2000000)
    price_samples = [int(base_price * (1 + random.uniform(-0.1, 0.15))) for _ in range(6)]
    return price_samples

# -----------------------------
# 본 실행 로직
# -----------------------------
if uploaded_file and item_description:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_container_width=True)

    with st.spinner("🔍 AI가 이미지를 분석 중입니다..."):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        item_type = identify_item_with_ai(image_bytes.getvalue())

    st.success(f"**AI 분석 결과:** {item_type}")

    # 시세 데이터 가져오기
    prices = get_naver_shopping_price(item_type)
    months = np.arange(1, len(prices)+1)

    avg_price = int(np.mean(prices))
    last_diff = prices[-1] - prices[-2]
    trend = "상승 📈" if last_diff > 0 else "하락 📉"

    # -----------------------------
    # 시세 그래프
    # -----------------------------
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(months, prices, marker='o', linestyle='-', linewidth=2)
    ax.set_title(f"{item_type} 최근 6개월 시세 추이", fontsize=14)
    ax.set_xlabel("지난 개월 수")
    ax.set_ylabel("시세 (원)")
    ax.grid(True)
    st.pyplot(fig)

    # -----------------------------
    # 근거 문장 생성
    # -----------------------------
    reasons = [
        "해당 품목은 최근 리셀 시장에서 거래량이 증가해 시세가 상승하는 경향을 보입니다.",
        "신제품 출시 영향으로 이전 모델의 가격이 조정되고 있습니다.",
        "사용감이 적고 브랜드 인지도 덕분에 안정적인 중고 시세가 유지되고 있습니다.",
        "시즌 트렌드 요인으로 단기적인 가격 변동이 예상됩니다."
    ]

    reason = random.choice(reasons)

    # -----------------------------
    # 결과 출력
    # -----------------------------
    st.subheader("💬 시세 분석 결과")
    st.markdown(f"**품목:** {item_type}")
    st.markdown(f"**평균 시세:** {avg_price:,} 원")
    st.markdown(f"**현재 추세:** {trend}")
    st.markdown(f"**예측 근거:** {reason}")

else:
    st.info("이미지와 설명을 업로드하면 AI 분석이 시작됩니다!")

# -----------------------------
# 푸터
# -----------------------------
st.markdown("---")
st.caption("© 2025 Mini 딜러 AI – 이미지 인식 + 실시간 시세 예측 데모")
