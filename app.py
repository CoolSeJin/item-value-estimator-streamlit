# -*- coding: utf-8 -*-
import sys
import io
import traceback
import base64
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
from PIL import Image
import streamlit as st
from openai import OpenAI

# -------------------------
# 안정적으로 stdout UTF-8 설정
# -------------------------
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')

# -------------------------
# 한글 폰트 자동 설정
# -------------------------
plt.rcParams['axes.unicode_minus'] = False

def set_korean_font():
    candidates = ['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'Noto Sans CJK KR']
    available = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in available:
            plt.rcParams['font.family'] = c
            return c
    return None

font_used = set_korean_font()

# -------------------------
# OpenAI 클라이언트 설정
# -------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정 중 오류가 발생했습니다. Secrets에 OPENAI_API_KEY가 등록되어 있는지 확인하세요.")
    st.stop()

# -------------------------
# Streamlit 페이지 설정
# -------------------------
st.set_page_config(page_title="AI 시세 분석기", page_icon="💰", layout="centered")
st.title("💰 AI 기반 아이템 시세 분석기")
st.caption("사진과 설명을 업로드하면 AI가 자동으로 시세를 예측합니다. (현재 버전은 텍스트 기반 분석입니다)")

# -------------------------
# 이미지 Base64 인코딩
# -------------------------
def encode_image_to_base64(image_file):
    try:
        image_file.seek(0)
        data = image_file.read()
        return base64.b64encode(data).decode('ascii')
    except Exception as e:
        return None

# -------------------------
# 간단한 이미지 검증
# -------------------------
def simple_image_is_suitable(pil_image):
    w, h = pil_image.size
    if w < 100 or h < 100:
        return False, "이미지 해상도가 너무 낮습니다."
    return True, ""

# -------------------------
# 사용자 입력 UI
# -------------------------
uploaded_file = st.file_uploader("상품 사진을 업로드하세요 (선택)", type=["jpg", "jpeg", "png"])
item_description = st.text_area("상품 설명을 입력하세요 (브랜드, 상태, 모델명 등)", height=120)
item_type = st.selectbox("상품 카테고리", ["전자기기", "의류", "신발", "가방", "가구", "도서", "기타"])

if not item_description:
    st.info("상품 설명을 입력하면 더 정확한 분석이 가능합니다.")
    st.stop()

# 이미지 표시
pil_image = None
if uploaded_file:
    try:
        pil_image = Image.open(uploaded_file).convert("RGB")
        st.image(pil_image, caption="업로드된 상품 이미지", use_container_width=True)
    except Exception as e:
        st.error("이미지를 불러오는 중 오류가 발생했습니다.")
        st.error(str(e))
        pil_image = None

# -------------------------
# 이미지 검증
# -------------------------
if pil_image:
    ok, reason = simple_image_is_suitable(pil_image)
    if not ok:
        st.warning(f"이미지 검증 문제: {reason}")
        if not st.button("이미지 무시하고 계속 진행"):
            st.stop()
        else:
            st.info("이미지 검증을 건너뛰고 진행합니다.")

# -------------------------
# AI 시세 분석
# -------------------------
with st.spinner("AI가 시세를 분석 중입니다..."):
    try:
        system_message = (
            "You are an experienced used price analysis expert. "
            "Based on the product description and category, provide an estimated average used price in KRW. "
            "Respond in the following format:\n"
            "Estimated Price: [price] KRW\n"
            "Analysis Basis: [2-3 sentences]\n"
            "Market Outlook: [1-2 sentences]\n"
            "Trading Tips: [1-2 sentences]\n"
        )

        user_prompt = (
            f"Category: {item_type}\n"
            f"Description: {item_description}\n\n"
            "Please estimate the price and give a brief analysis, outlook, and trading tips."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=600
        )

        ai_result = response.choices[0].message.content.strip()
        st.subheader("📊 AI 시세 분석 결과")
        st.code(ai_result, language="markdown")

    except Exception as e:
        err_text = "".join(traceback.format_exception_only(type(e), e)).strip()
        err_text = err_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        st.error("❌ 시세 분석 중 오류가 발생했습니다.")
        st.error(f"오류 내용: {err_text}")
        st.stop()

# -------------------------
# 시세 추이 차트 (시뮬레이션)
# -------------------------
try:
    st.subheader("📈 예상 시세 추이 (시뮬레이션)")
    np.random.seed(42)
    months = np.arange(1, 13)

    price_ranges = {
        "전자기기": (100000, 500000),
        "의류": (10000, 100000),
        "신발": (30000, 200000),
        "가방": (50000, 300000),
        "가구": (50000, 500000),
        "도서": (5000, 50000),
        "기타": (10000, 200000)
    }

    min_price, max_price = price_ranges.get(item_type, (10000, 200000))
    base_price = np.random.randint(min_price, max_price)
    trend = np.linspace(base_price * 0.95, base_price * 1.05, 12)
    noise = np.random.normal(0, base_price * 0.03, 12)
    prices = trend + noise

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(months, prices, marker="o", linewidth=2)
    ax.fill_between(months, prices * 0.97, prices * 1.03, alpha=0.15)
    ax.set_title(f"{item_type} 카테고리 시세 추이 (예상)")
    ax.set_xlabel("월")
    ax.set_ylabel("가격 (원)")
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    st.pyplot(fig)
except Exception as e:
    st.warning("차트 생성 중 오류가 발생했습니다.")
    st.warning(str(e))

# -------------------------
# 추가 안내
# -------------------------
st.markdown("---")
st.markdown("💡 **이미지 기반 AI 분석을 원한다면**")
st.markdown("1️⃣ 이미지를 외부 호스팅(예: Imgur, S3 등)에 업로드하고, 그 URL을 설명에 포함하세요.  
2️⃣ 또는 OpenAI의 멀티모달 API(`gpt-4o`)로 이미지를 함께 분석하도록 코드를 확장할 수 있습니다. 원하시면 예시 코드도 만들어드릴게요.")
