import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io

# -------------------------------
# 1️⃣ API 키 설정
# -------------------------------
# Streamlit Cloud의 "Secrets"에 OPENAI_API_KEY 등록 필수
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI 시세 분석기", page_icon="💰", layout="centered")
st.title("💰 AI 기반 아이템 시세 분석기")
st.write("사진과 설명을 업로드하면 AI가 자동으로 시세를 예측하고, 향후 변동까지 분석해드려요!")

# -------------------------------
# 2️⃣ 이미지 업로드
# -------------------------------
uploaded_file = st.file_uploader("상품 사진을 업로드하세요", type=["jpg", "jpeg", "png"])
item_description = st.text_area("상품 설명을 입력하세요 (브랜드, 상태, 모델명 등)", height=100)
item_type = st.selectbox("상품 카테고리", ["전자기기", "의류", "신발", "가방", "기타"])

if uploaded_file and item_description:
    # 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 상품", use_container_width=True)

    # -------------------------------
    # 3️⃣ AI 분석 요청
    # -------------------------------
    with st.spinner("AI가 시세를 분석 중입니다..."):
        prompt = f"""
        다음은 사용자가 올린 상품의 설명입니다.
        카테고리: {item_type}
        설명: {item_description}

        이 상품의 온라인 평균 중고 시세를 예측하고,
        가격에 영향을 준 근거를 간략히 2~3문장으로 설명해주세요.
        또한, 현재 시세가 오를지 떨어질지도 추세를 예측해주세요.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 숙련된 중고 시세 분석 전문가야."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            ai_result = response.choices[0].message.content

            # -------------------------------
            # 4️⃣ 결과 출력
            # -------------------------------
            st.subheader("📊 AI 시세 분석 결과")
            st.write(ai_result)

            # -------------------------------
            # 5️⃣ 시세 그래프 시뮬레이션
            # -------------------------------
            np.random.seed(42)
            months = np.arange(1, 13)
            base_price = np.random.randint(50000, 300000)
            trend = np.linspace(base_price * 0.9, base_price * 1.1, 12)
            noise = np.random.normal(0, base_price * 0.03, 12)
            prices = trend + noise

            fig, ax = plt.subplots()
            ax.plot(months, prices, marker="o", linewidth=2)
            ax.set_title(f"{item_type} 평균 시세 추이 (예상)", fontsize=14)
            ax.set_xlabel("개월")
            ax.set_ylabel("가격 (원)")
            st.pyplot(fig)

        except Exception as e:
            st.error("⚠️ 시세 분석 중 오류가 발생했습니다.")
            st.exception(e)
else:
    st.info("사진과 설명을 모두 입력하면 시세를 분석합니다.")
