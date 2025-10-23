# -*- coding: utf-8 -*-
import os
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
# ✅ UTF-8 환경 설정
# -------------------------
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# -------------------------
# 한글 폰트 설정
# -------------------------
plt.rcParams['axes.unicode_minus'] = False

def set_korean_font():
    candidates = ['Malgun Gothic', 'AppleGothic', 'NanumGothic', 'Noto Sans CJK KR', 'DejaVu Sans']
    available = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in available:
            plt.rcParams['font.family'] = c
            return
    plt.rcParams['font.family'] = 'DejaVu Sans'

set_korean_font()

# -------------------------
# OpenAI 설정
# -------------------------
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ API 키 설정 중 오류가 발생했습니다. Secrets에 OPENAI_API_KEY가 등록되어 있는지 확인하세요.")
    st.stop()

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="AI 시세 분석기", 
    page_icon="💰", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("💰 AI 기반 아이템 시세 분석기")
st.caption("사진과 설명을 업로드하면 AI가 자동으로 시세를 예측합니다.")

# -------------------------
# 유틸리티 함수
# -------------------------
def encode_image_to_base64(image_file):
    """이미지를 Base64로 인코딩"""
    try:
        image_file.seek(0)
        data = image_file.read()
        return base64.b64encode(data).decode('ascii')
    except Exception as e:
        st.error(f"이미지 인코딩 오류: {str(e)}")
        return None

def validate_image(pil_image):
    """이미지 유효성 검사"""
    w, h = pil_image.size
    if w < 100 or h < 100:
        return False, "이미지 해상도가 너무 낮습니다."
    if w * h > 10000000:
        return False, "이미지 크기가 너무 큽니다."
    return True, ""

def extract_price_from_analysis(analysis_text):
    """AI 분석 결과에서 가격 정보 추출"""
    try:
        import re
        match = re.search(r'Estimated Price:\s*([\d,]+)\s*KRW', analysis_text)
        if match:
            price_str = match.group(1).replace(',', '')
            return int(price_str)
        match = re.search(r'([\d,]+)\s*KRW', analysis_text)
        if match:
            price_str = match.group(1).replace(',', '')
            return int(price_str)
        return None
    except:
        return None

# -------------------------
# AI 분석 함수
# -------------------------
def analyze_price_with_ai(item_description, item_type, image_base64=None):
    """AI를 이용한 시세 분석"""
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

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]

        # 이미지가 있는 경우 멀티모달 분석
        if image_base64:
            messages = [
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            model = "gpt-4o"
        else:
            model = "gpt-4o-mini"

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=600
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"AI 분석 중 오류 발생: {str(e)}")

# -------------------------
# 차트 생성 함수
# -------------------------
def create_price_chart(item_type, estimated_price=None):
    """시세 추이 차트 생성"""
    try:
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
        
        if estimated_price:
            base_price = estimated_price
            base_price = max(min_price * 0.8, min(max_price * 1.2, base_price))
        else:
            base_price = np.random.randint(min_price, max_price)

        trend = np.linspace(base_price * 0.95, base_price * 1.05, 12)
        noise = np.random.normal(0, base_price * 0.03, 12)
        prices = np.maximum(trend + noise, min_price * 0.5)

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(months, prices, marker="o", linewidth=2, color="#FF6B6B")
        ax.fill_between(months, prices * 0.97, prices * 1.03, alpha=0.15, color="#FFE66D")
        ax.set_title(f"'{item_type}' 카테고리 시세 추이 (예상)", fontsize=14, fontweight='bold')
        ax.set_xlabel("월")
        ax.set_ylabel("가격 (원)")
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"차트 생성 오류: {str(e)}")
        return None

# -------------------------
# 사이드바
# -------------------------
with st.sidebar:
    st.header("ℹ️ 사용 방법")
    st.markdown("""
    1. **상품 사진** 업로드 (선택)
    2. **상품 설명** 입력 (필수)
    3. **카테고리** 선택
    4. **시세 분석 시작** 버튼 클릭
    """)
    
    st.header("📊 분석 항목")
    st.markdown("""
    - 예상 시세
    - 분석 근거
    - 시장 전망
    - 거래 팁
    - 시세 추이 차트
    """)

# -------------------------
# 메인 콘텐츠
# -------------------------

# 사용자 입력
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📷 상품 사진 업로드 (선택)", 
        type=["jpg", "jpeg", "png"],
        help="상품 사진을 업로드하면 더 정확한 분석이 가능합니다"
    )

with col2:
    item_type = st.selectbox(
        "📂 카테고리", 
        ["전자기기", "의류", "신발", "가방", "가구", "도서", "기타"]
    )

item_description = st.text_area(
    "📝 상품 설명", 
    height=120, 
    placeholder="예: 아이폰 14 프로 256GB, 사용 1년, 외관 양호, 배터리 건강 90%, 모든 기능 정상 작동"
)

# 이미지 처리
pil_image = None
image_base64 = None
use_image = False

if uploaded_file:
    try:
        pil_image = Image.open(uploaded_file).convert("RGB")
        st.image(pil_image, caption="업로드된 상품 이미지", use_container_width=True)
        
        # 이미지 검증
        ok, reason = validate_image(pil_image)
        if not ok:
            st.warning(f"⚠️ {reason}")
            if st.button("이미지 무시하고 텍스트만 분석하기"):
                use_image = False
            else:
                st.stop()
        else:
            use_image = True
            image_base64 = encode_image_to_base64(uploaded_file)
            if image_base64:
                st.success("✅ 이미지 분석이 가능합니다!")
            else:
                st.warning("⚠️ 이미지 처리에 실패했습니다. 텍스트만으로 분석합니다.")
                use_image = False
                
    except Exception as e:
        st.error(f"이미지 불러오기 오류: {str(e)}")
        use_image = False

# 분석 시작 버튼
if not item_description.strip():
    st.info("📝 상품 설명을 입력해주세요. 더 자세한 설명일수록 정확한 분석이 가능합니다.")
    st.stop()

analyze_button = st.button("🔍 시세 분석 시작", type="primary", use_container_width=True)

# AI 분석 실행
if analyze_button:
    with st.spinner("🤖 AI가 시세를 분석 중입니다... 잠시만 기다려주세요."):
        try:
            final_image_base64 = image_base64 if use_image else None
            
            ai_result = analyze_price_with_ai(
                item_description, 
                item_type, 
                final_image_base64
            )
            
            # 결과 표시
            st.success("✅ 분석이 완료되었습니다!")
            st.subheader("📊 AI 시세 분석 결과")
            
            # 결과 파싱 및 표시
            result_lines = ai_result.split('\n')
            for line in result_lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Estimated Price:'):
                    st.markdown(f"### 💰 {line}")
                elif line.startswith('Analysis Basis:'):
                    st.markdown(f"**📈 {line}**")
                    st.write(line.replace('Analysis Basis:', '').strip())
                elif line.startswith('Market Outlook:'):
                    st.markdown(f"**🔮 {line}**")
                    st.write(line.replace('Market Outlook:', '').strip())
                elif line.startswith('Trading Tips:'):
                    st.markdown(f"**💡 {line}**")
                    st.write(line.replace('Trading Tips:', '').strip())
                elif ':' in line and not line.startswith(' '):
                    # 기타 제목 있는 내용
                    parts = line.split(':', 1)
                    st.markdown(f"**{parts[0]}:**")
                    if len(parts) > 1:
                        st.write(parts[1].strip())
                else:
                    st.write(line)
            
            # 가격 정보 추출
            estimated_price = extract_price_from_analysis(ai_result)
            
            # 시세 추이 차트
            st.subheader("📈 예상 시세 추이")
            chart = create_price_chart(item_type, estimated_price)
            if chart:
                st.pyplot(chart)
                
                if estimated_price:
                    st.info(f"💡 분석된 예상 가격: **{estimated_price:,.0f}원** 기준으로 시세 추이를 시뮬레이션했습니다.")
                else:
                    st.info("💡 해당 카테고리의 일반적인 시세 추이를 보여드립니다.")
            
            # 분석 방법 안내
            with st.expander("🔍 이 분석은 어떻게 진행되었나요?"):
                if use_image:
                    st.write("✅ **이미지 + 텍스트 분석**: 상품의 외관, 상태, 모델 등을 이미지로 확인하여 더 정확한 분석을 진행했습니다.")
                else:
                    st.write("📝 **텍스트 분석**: 입력하신 설명을 기반으로 분석했습니다. 이미지를 추가하면 더 정확한 분석이 가능합니다.")
                    
        except Exception as e:
            st.error("❌ 시세 분석 중 오류가 발생했습니다.")
            st.error(f"오류 내용: {str(e)}")

# -------------------------
# 푸터
# -------------------------
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💡 사용 팁")
    st.markdown("""
    - **상품 설명을 자세히** 입력하세요
    - **실제 사진**을 업로드하면 정확도 ↑
    - **정확한 카테고리**를 선택하세요
    """)

with col2:
    st.markdown("### ⚠️ 주의사항")
    st.markdown("""
    - AI 예측으로 실제 가격과 다를 수 있습니다
    - 중요한 거래는 여러 자료를 참고하세요
    - 참고용으로만 활용해주세요
    """)

st.caption("© 2024 AI 시세 분석기 - 모든 권리 보유")
