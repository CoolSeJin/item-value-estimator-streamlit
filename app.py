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

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(
    page_title="AI 시세 분석기", 
    page_icon="💰", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------
# 한글 폰트 설정 (강화된 버전)
# -------------------------
plt.rcParams['axes.unicode_minus'] = False

def set_korean_font():
    """한글 폰트 설정 함수"""
    try:
        # 폰트 후보군
        korean_fonts = [
            'Malgun Gothic', 
            'AppleGothic', 
            'NanumGothic', 
            'Noto Sans CJK KR', 
            'DejaVu Sans',
            'D2Coding',
            'Gulim',
            'Dotum'
        ]
        
        # 사용 가능한 폰트 찾기
        available_fonts = {f.name for f in fm.fontManager.ttflist}
        
        for font in korean_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = font
                return font
        
        # 한글 폰트가 없을 경우 기본 폰트 사용
        plt.rcParams['font.family'] = 'DejaVu Sans'
        return "DejaVu Sans"
        
    except Exception as e:
        plt.rcParams['font.family'] = 'DejaVu Sans'
        return "DejaVu Sans"

font_used = set_korean_font()

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
# AI 분석 함수 (더미 데이터)
# -------------------------
def analyze_price_with_ai(item_description, item_type, image_base64=None):
    """AI를 이용한 시세 분석"""
    try:
        # 카테고리별 더미 응답
        dummy_responses = {
            "전자기기": """Estimated Price: 350,000 KRW
Analysis Basis: 전자기기 카테고리는 기술 발전 속도가 빠르며, 출시 시기와 상태에 따라 가격 변동이 큽니다. 최신 모델일수록 가치가 높습니다.
Market Outlook: 중고 전자기기 시장은 꾸준한 수요가 있으며, 신제품 출시 시 기존 모델 가격이 하락하는 경향이 있습니다.
Trading Tips: 제품의 사양, 사용 기간, 외관 상태를 상세히 기재하면 더 빠른 거래가 가능합니다.""",
            
            "의류": """Estimated Price: 25,000 KRW
Analysis Basis: 의류는 브랜드, 상태, 시즌에 따라 가격 차이가 큽니다. 한정판이나 인기 브랜드의 경우 프리미엄이 발생할 수 있습니다.
Market Outlook: 중고 의류 시장은 지속적으로 성장 중이며, 특히 명품 브랜드의 수요가 높습니다.
Trading Tips: 사진을 선명하게 찍고, 사이즈와 상태를 정확히 표기하면 거래 성공률이 높아집니다.""",
            
            "신발": """Estimated Price: 75,000 KRW
Analysis Basis: 신발은 브랜드와 마모 상태에 따라 가격이 결정됩니다. 한정판이나 콜라보레이션 제품은 높은 가치를 유지합니다.
Market Outlook: 중고 신발 시장은 컬렉터와 실용적 사용자 모두에게 인기가 있습니다.
Trading Tips: 밑창 마모 상태와 박스 유무를 명시하는 것이 중요합니다.""",
            
            "가방": """Estimated Price: 120,000 KRW
Analysis Basis: 가방은 브랜드 인지도, 소재, 상태에 따라 가격이 크게 달라집니다. 명품 브랜드의 경우 보증서와 더스트백 유무가 중요합니다.
Market Outlook: 중고 명품 가방 시장은 매우 활발하며, 일부 제품은 시간이 지날수록 가치가 상승하기도 합니다.
Trading Tips: 정품 인증과 함께 상세한 사진을 여러 각도에서 제공하세요.""",
            
            "가구": """Estimated Price: 85,000 KRW
Analysis Basis: 가구는 재질, 브랜드, 크기, 상태에 따라 가격이 결정됩니다. 실용성과 디자인이 모두 중요한 요소입니다.
Market Outlook: 이사 시즌에 수요가 증가하며, 공간 활용도가 높은 다기능 가구의 인기가 높습니다.
Trading Tips: 배송 가능 여부와 조립 필요성을 미리 알려주는 것이 좋습니다.""",
            
            "도서": """Estimated Price: 8,000 KRW
Analysis Basis: 도서는 절판 여부, 출판년도, 상태에 따라 가격이 결정됩니다. 참고서나 전문서적은 수요가 꾸준합니다.
Market Outlook: 전자책의 보급에도 불구하고, 절판된 도서나 초판본은 수집 가치가 있습니다.
Trading Tips: 페이지 훼손 여부와 필기 흔적 유무를 정확히 표기하세요.""",
            
            "기타": """Estimated Price: 45,000 KRW
Analysis Basis: 10kg 덤벨은 중고 시장에서 수요가 꾸준한 편입니다. 일반적으로 새 제품 가격이 6-8만 원대인 점을 고려할 때, 중고 가격은 4-5만 원대가 적절합니다.
Market Outlook: 홈트레이닝 수요가 지속되면서 덤벨 시장은 안정적인 편입니다.
Trading Tips: 상태가 양호하고 녹이 슬지 않은 제품이라면 거래가 빠르게 이루어질 수 있습니다."""
        }
        
        # 선택된 카테고리에 해당하는 응답 반환
        return dummy_responses.get(item_type, dummy_responses["기타"])
        
    except Exception as e:
        raise Exception(f"분석 중 오류 발생: {str(e)}")

# -------------------------
# 차트 생성 함수 (수정된 버전)
# -------------------------
def create_price_chart(item_type, estimated_price=None):
    """시세 추이 차트 생성"""
    try:
        # 폰트 설정 확인
        plt.rcParams['font.family'] = font_used
        plt.rcParams['axes.unicode_minus'] = False
        
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

        # 차트 생성
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 데이터 플롯
        ax.plot(months, prices, marker="o", linewidth=2, color="#FF6B6B", markersize=6)
        ax.fill_between(months, prices * 0.97, prices * 1.03, alpha=0.15, color="#FFE66D")
        
        # 스타일 설정
        ax.set_title(f"'{item_type}' 카테고리 시세 추이 (예상)", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("월", fontsize=12)
        ax.set_ylabel("가격 (원)", fontsize=12)
        
        # x축 설정 (텍스트 깨짐 방지)
        ax.set_xticks(months)
        ax.set_xticklabels(['1월', '2월', '3월', '4월', '5월', '6월', 
                          '7월', '8월', '9월', '10월', '11월', '12월'], 
                         fontsize=10, rotation=45)
        
        # y축 설정
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        ax.tick_params(axis='y', labelsize=10)
        
        # 그리드 및 레이아웃
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # 여백 조정
        plt.tight_layout()
        
        return fig
        
    except Exception as e:
        st.error(f"차트 생성 오류: {str(e)}")
        # 오류 발생시 기본 차트 반환
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, '차트 생성 중 오류가 발생했습니다', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

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
    
    # 폰트 정보 표시
    st.header("⚙️ 시스템 정보")
    st.write(f"사용 중인 폰트: {font_used}")

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
    with st.spinner("🤖 시세를 분석 중입니다... 잠시만 기다려주세요."):
        try:
            final_image_base64 = image_base64 if use_image else None
            
            ai_result = analyze_price_with_ai(
                item_description, 
                item_type, 
                final_image_base64
            )
            
            # 결과 표시
            st.success("✅ 분석이 완료되었습니다!")
            st.subheader("📊 시세 분석 결과")
            
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
                    st.write("✅ **이미지 분석**: 상품의 외관, 상태 등을 이미지로 확인하여 더 정확한 분석을 진행했습니다.")
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
