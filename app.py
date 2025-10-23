# -*- coding: utf-8 -*-
import sys
# 안정적으로 stdout utf-8 설정 (일부 환경에서만 필요)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from PIL import Image
import io
import base64
import matplotlib.ticker as ticker
import traceback

# -------------------------
# 한글 폰트 자동 설정 시도
# -------------------------
plt.rcParams['axes.unicode_minus'] = False
def set_korean_font():
    # 우선 후보 목록
    candidates = ['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'Noto Sans CJK JP', 'Noto Sans CJK KR']
    available = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in available:
            plt.rcParams['font.family'] = c
            return c
    # 없으면 기본 폰트 유지
    return None

font_used = set_korean_font()

# -------------------------------
# 1️⃣ API 키 설정
# -------------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("⚠️ API 키 설정 중 오류가 발생했습니다. Secrets에 OPENAI_API_KEY가 설정되었는지 확인해주세요.")
    st.stop()

st.set_page_config(page_title="AI 시세 분석기", page_icon="💰", layout="centered")
st.title("AI 기반 아이템 시세 분석기")
st.write("사진과 설명을 업로드하면 AI가 자동으로 시세를 예측합니다. (현재 버전은 설명 기반 분석입니다)")

# -------------------------------
# 이미지 인코딩 (base64)
# -------------------------------
def encode_image_to_base64(image_file):
    try:
        image_file.seek(0)
        data = image_file.read()
        # base64 문자열은 ASCII 범위 문자를 사용하므로 ascii로 디코딩해도 무방합니다
        return base64.b64encode(data).decode('ascii')
    except Exception as e:
        return None

# -------------------------------
# 이미지 검증 (간단) - 로컬에서만 사용
# -------------------------------
def simple_image_is_suitable(pil_image):
    # 아주 간단한 기준: 가로 세로 크기 체크
    w, h = pil_image.size
    if w < 100 or h < 100:
        return False, "이미지 해상도가 너무 낮습니다."
    return True, ""

# -------------------------------
# 3️⃣ UI: 업로드 및 입력
# -------------------------------
uploaded_file = st.file_uploader("상품 사진을 업로드하세요 (선택)", type=["jpg", "jpeg", "png"])
item_description = st.text_area("상품 설명을 입력하세요 (브랜드 상태 모델명 등)", height=120)
item_type = st.selectbox("상품 카테고리", ["전자기기", "의류", "신발", "가방", "가구", "도서", "기타"])

if not item_description:
    st.info("상품 설명을 입력하면 더 정확한 분석이 가능합니다.")
    st.stop()

# 이미지가 업로드 됐을 때 보여주기
pil_image = None
if uploaded_file:
    try:
        pil_image = Image.open(uploaded_file).convert("RGB")
        st.image(pil_image, caption="업로드된 상품 이미지", use_container_width=True)
    except Exception as e:
        st.error("이미지를 불러오는 중 오류가 발생했습니다.")
        st.error(str(e))
        pil_image = None

# -------------------------------
# 4️⃣ (선택) 간단 이미지 검증
# -------------------------------
if pil_image:
    ok, reason = simple_image_is_suitable(pil_image)
    if not ok:
        st.warning(f"이미지 검증 문제: {reason}")
        if not st.button("이미지 무시하고 계속 진행"):
            st.stop()
        else:
            st.info("이미지 검증을 건너뛰고 진행합니다.")

# -------------------------------
# 5️⃣ AI 시세 분석 (텍스트 기반)
# -------------------------------
with st.spinner("AI가 시세를 분석하고 있습니다..."):
    try:
        # 중요한 점: 시스템/사용자 메시지에 이모지나 특수문자를 제거해서 전송합니다.
        system_message = (
            "You are an experienced used price analysis expert. "
            "Based on the product description and category provide an estimated average used price in KRW. "
            "Respond in this exact format:\n"
            "Estimated Price: [price] KRW\n"
            "Analysis Basis: [2-3 sentences]\n"
            "Market Outlook: [1-2 sentences]\n"
            "Trading Tips: [1-2 sentences]\n"
        )

        user_prompt = (
            f"Category: {item_type}\n"
            f"Description: {item_description}\n\n"
            "Please estimate price and give short basis outlook and tips."
        )

        # 여기서는 이미지 데이터 또는 데이터 URL을 채팅 메시지에 넣지 않습니다.
        # (이미지를 분석하려면 외부에 업로드한 URL을 넣거나 OpenAI의 이미지 전용 API를 사용하세요.)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=600
        )

        # 응답 추출 안전하게
        ai_result = ""
        try:
            ai_result = response.choices[0].message.content
        except Exception:
            # SDK 반환 형식이 약간 다를 수 있으니 안전하게 변환
            ai_result = str(response)

        # 출력
        st.subheader("AI 시세 분석 결과")
        st.code(ai_result)

    except Exception as e:
        # 예외 메시지 utf-8로 안전하게 변환해서 보여주기
        err_text = "".join(traceback.format_exception_only(type(e), e)).strip()
        try:
            err_text = err_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except Exception:
            err_text = str(err_text)
        st.error("⚠️ 시세 분석 중 오류가 발생했습니다.")
        st.error(f"오류 내용: {err_text}")
        # 내부 디버그 로그 (개발용)
        # st.text(traceback.format_exc())
        st.stop()

# -------------------------------
# 6️⃣ 시뮬레이션 차트 (설명 기반 추정치)
# -------------------------------
try:
    st.subheader("예상 시세 추이 (시뮬레이션)")

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
    title_text = f"{item_type} 카테고리 시세 추이 (예상)"
    ax.set_title(title_text)
    ax.set_xlabel("월")
    ax.set_ylabel("가격 (원)")
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    st.pyplot(fig)
except Exception as e:
    st.warning("차트 생성 중 오류가 발생했습니다.")
    st.warning(str(e))

# -------------------------------
# 추가 안내: 이미지 기반 분석이 필요하면
# -------------------------------
st.markdown("---")
st.markdown("**이미지 기반 AI 분석이 필요하면** 아래 중 하나를 권장합니다.")
st.markdown("1. 이미지를 외부 호스팅(예: Imgur, S3 등)에 업로드하고 그 이미지 URL을 '설명'에 포함해 주세요.\n2. 또는 OpenAI 이미지 전용 API(멀티모달)를 사용하도록 코드를 변경해야 합니다. 필요하면 예시 코드를 제공해 드립니다.")
