import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import random
import io
import openai
import matplotlib.font_manager as fm

# 🔹 폰트 설정 (한글 깨짐 방지용)
plt.rc('font', family='Malgun Gothic')  # Windows용
plt.rc('axes', unicode_minus=False)

# 🔹 OpenAI API Key 설정 (Streamlit Cloud에서는 Secrets 관리 기능 이용)
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
# 이미지 인식 (AI)
# -----------------------------
def identify_item_with_ai(image_bytes):
    try:
        result = openai.chat.completions.create(
            model="gpt-4o-mini",
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
# 시세 데이터 (임시 예시)
# -----------------------------
def get_price_samples():
    base = random.randint(200000, 1000000)
    return [int(base * (1 + random.uniform(-0.1, 0.15))) for _ in range(6)]

# -----------------------------
# 실행 로직
# -----------------------------
if uploaded_file and item_description:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_container_width=True)

    with st.spinner("🔍 AI가 이미지를 분석 중입니다..."):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        item_type = identify_item_with_ai(image_bytes.getvalue())

    st.success(f"**AI 분석 결과:** {item_type}")

    prices = get_price_samples()
    months = np.arange(1, len(prices) + 1)

    avg_price = int(np.mean(prices))
    trend = "상승 📈" if prices[-1] > prices[-2] else "하락 📉"

    # 그래프
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(months, prices, marker='o', linewidth=2)
    ax.set_title(f"{item_type} 최근 6개월 시세 추이", fontsize=14)
    ax.set_xlabel("개월")
    ax.set_ylabel("시세 (원)")
    ax.grid(True)
    st.pyplot(fig)

    # 시세 설명
    reasons = [
        "최근 리셀 시장에서 거래량이 증가해 시세가 상승 중입니다.",
        "신제품 출시 영향으로 가격이 조정되는 추세입니다.",
        "사용감이 적고 브랜드 인지도가 높아 안정적인 시세를 유지하고 있습니다.",
        "계절 트렌드 요인으로 단기적인 변동이 예상됩니다."
    ]
    reason = random.choice(reasons)

    st.subheader("💬 시세 분석 결과")
    st.markdown(f"**품목:** {item_type}")
    st.markdown(f"**평균 시세:** {avg_price:,} 원")
    st.markdown(f"**현재 추세:** {trend}")
    st.markdown(f"**분석 근거:** {reason}")

else:
    st.info("이미지와 설명을 업로드하면 AI 분석이 시작됩니다!")

st.markdown("---")
st.caption("© 2025 Mini 딜러 AI – 이미지 인식 + 실시간 시세 예측 데모")
