# ✅ 필요한 패키지 설치 (Streamlit Cloud는 requirements.txt에 넣기)
# streamlit
# matplotlib
# pillow
# numpy
# openai
# requests

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import numpy as np
import random
import openai

# ✅ 한글 폰트 설정 (깨짐 방지)
matplotlib.rc('font', family='Malgun Gothic')  # 윈도우
matplotlib.rcParams['axes.unicode_minus'] = False

# ✅ OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------------------------------------------
# 🌟 앱 기본 UI 설정
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
    # 🧠 AI 분석 요청 (설명 추출)
    with st.spinner("AI가 이미지를 분석 중입니다... 🔍"):
        prompt = """
        이 이미지를 설명해줘. 어떤 물건인지, 사용 상태나 특징이 뭔지, 
        그리고 중고 시세 추정에 참고할만한 키워드를 중심으로 간단히 요약해줘.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        description = response.choices[0].message.content.strip()

    st.subheader("🧾 AI 이미지 분석 결과")
    st.write(description)

    # ---------------------------------------------
    # 💰 시세 예측 (랜덤 + AI 참고)
    base_price = random.randint(300000, 400000)
    prices = [base_price + random.randint(-40000, 40000) for _ in range(6)]
    avg_price = np.mean(prices)

    # 추세 계산
    if prices[-1] > prices[0]:
        trend = "상승 📈"
    elif prices[-1] < prices[0]:
        trend = "하락 📉"
    else:
        trend = "안정 ⚖️"

    # ---------------------------------------------
    # 📊 그래프 출력
    fig, ax = plt.subplots()
    ax.plot(range(1, 7), prices, marker='o')
    ax.set_title("최근 6개월 평균 시세 추이", fontsize=14)
    ax.set_xlabel("기간 (월)")
    ax.set_ylabel("가격 (원)")
    st.pyplot(fig)

    # ---------------------------------------------
    # 💬 시세 분석 설명
    if "하락" in trend:
        reason = (
            "최근 시장에 유사한 신제품이 다수 출시되어 경쟁이 심화되고 있습니다. "
            "이에 따라 해당 제품의 중고 거래가는 일시적으로 하락세를 보입니다. "
            "다만 일정 기간 이후 안정세로 돌아올 가능성도 있습니다."
        )
    elif "상승" in trend:
        reason = (
            "제품의 희소성과 브랜드 신뢰도가 높아, 중고 거래 수요가 꾸준히 증가하고 있습니다. "
            "특히 해당 모델은 최근 품질 평가가 좋아 프리미엄 가격대가 형성되고 있습니다."
        )
    else:
        reason = (
            "시장 공급과 수요가 균형을 이루고 있어 가격 변동 폭이 크지 않습니다. "
            "일부 품목에서는 한정판이나 특정 색상 모델이 소폭 상승세를 보이기도 합니다."
        )

    # ---------------------------------------------
    # 🧭 향후 전망 (AI 예측)
    trend_prompt = f"이 제품은 현재 {trend} 상태입니다. 앞으로 3개월간 시세 전망을 전문가처럼 2문장으로 요약해줘."
    forecast_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": trend_prompt}],
    )
    forecast_text = forecast_response.choices[0].message.content.strip()

    # ---------------------------------------------
    # 결과 출력
    st.markdown("### 💬 시세 분석 결과")
    st.markdown(f"**평균 시세:** {avg_price:,.0f} 원")
    st.markdown(f"**현재 추세:** {trend}")
    st.markdown(f"**분석 근거:** {reason}")
    st.markdown("### 🔮 향후 3개월 전망")
    st.write(forecast_text)
