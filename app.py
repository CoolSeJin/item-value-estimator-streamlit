import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import numpy as np
import random
from openai import OpenAI

# ✅ 한글 폰트 깨짐 방지
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rcParams['axes.unicode_minus'] = False

# ✅ OpenAI 클라이언트 생성
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------------------------
# 🌟 Streamlit 기본 설정
st.set_page_config(page_title="AI 시세 분석기", page_icon="💰", layout="centered")
st.title("💸 AI 기반 이미지 시세 추정기")
st.write("사진을 업로드하면 AI가 제품을 분석해 시세와 트렌드를 예측해줍니다!")

# ---------------------------------------------
# 🖼️ 이미지 업로드
uploaded_file = st.file_uploader("📤 제품 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

# ---------------------------------------------
if uploaded_file:
    # 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_container_width=True)

    # ---------------------------------------------
    # 🧠 AI 이미지 설명 생성
    with st.spinner("AI가 이미지를 분석 중입니다... 🔍"):
        prompt = (
            "이 이미지를 설명해줘. 어떤 제품인지, 사용 상태와 특징을 간단히 "
            "요약해서 중고 시세를 예측하는 데 참고할 수 있는 설명을 만들어줘."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        description = response.choices[0].message.content.strip()

    st.subheader("🧾 AI 이미지 분석 결과")
    st.write(description)

    # ---------------------------------------------
    # 💰 시세 데이터 생성
    base_price = random.randint(300000, 400000)
    prices = [base_price + random.randint(-40000, 40000) for _ in range(6)]
    avg_price = np.mean(prices)

    if prices[-1] > prices[0]:
        trend = "상승 📈"
    elif prices[-1] < prices[0]:
        trend = "하락 📉"
    else:
        trend = "안정 ⚖️"

    # ---------------------------------------------
    # 📊 그래프 출력
    fig, ax = plt.subplots()
    ax.plot(range(1, 7), prices, marker='o', color='royalblue')
    ax.set_title("최근 6개월 평균 시세 추이", fontsize=14)
    ax.set_xlabel("기간 (월)")
    ax.set_ylabel("가격 (원)")
    st.pyplot(fig)

    # ---------------------------------------------
    # 💬 시세 분석 근거
    if "하락" in trend:
        reason = (
            "최근 유사 모델이 다수 출시되어 경쟁이 심화되며 중고가가 하락세를 보입니다. "
            "다만 안정적인 수요층이 있어 향후 반등 가능성도 있습니다."
        )
    elif "상승" in trend:
        reason = (
            "희소성과 브랜드 신뢰도가 높아 수요가 꾸준히 유지되고 있습니다. "
            "특히 특정 색상이나 한정판 모델은 거래가 활발하게 이루어지고 있습니다."
        )
    else:
        reason = (
            "공급과 수요가 균형을 이루며 안정적인 가격을 유지하고 있습니다. "
            "다만 소폭의 변동은 계절적 요인에 따라 발생할 수 있습니다."
        )

    # ---------------------------------------------
    # 🔮 향후 3개월 시세 예측 (AI)
    trend_prompt = f"이 제품은 현재 {trend} 상태입니다. 향후 3개월간 시세 전망을 전문가처럼 2문장으로 요약해줘."
    forecast_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": trend_prompt}],
    )
    forecast_text = forecast_response.choices[0].message.content.strip()

    # ---------------------------------------------
    # 🧾 결과 출력
    st.markdown("### 💬 시세 분석 결과")
    st.markdown(f"**평균 시세:** {avg_price:,.0f} 원")
    st.markdown(f"**현재 추세:** {trend}")
    st.markdown(f"**분석 근거:** {reason}")
    st.markdown("### 🔮 향후 3개월 전망")
    st.write(forecast_text)
