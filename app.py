import streamlit as st
import pandas as pd
import numpy as np # 예시를 위해 추가. 실제 사용시 필요에 따라 변경.

# 웹 앱의 기본 설정
st.set_page_config(page_title="물건 값어치 추정기", layout="wide")

# 제목
st.title("🛒 내 물건의 값어치는 얼마일까?")
st.markdown("---")

# 사진 업로드 및 설명 입력 섹션
with st.container():
    st.header("1. 물건 정보 입력")
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("물건 사진을 업로드하세요", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)
    
    with col2:
        item_description = st.text_area(
            "물건에 대해 설명해주세요",
            placeholder="예) 아이폰 14 프로 미드나이트 색상. 사용한 지 1년 됐고, 외관에 작은 스크래치 2~3개 있어요.",
            height=150
        )

# 가치 추정 버튼
if st.button("값어치 추정하기", type="primary"):
    if uploaded_file is not None and item_description:
        with st.spinner('AI가 물건을 분석하고 가치를 추정 중입니다...'):
            # 여기에 실제 AI 모델 추론 코드 또는 가격 API 호출 코드가 들어갑니다.
            # 현재는 임의의 결과를 반환하는 예시로 대체합니다.
            
            # 가상의 추정 가격 생성 (실제 구현시 제거)
            estimated_value = np.random.randint(50000, 500000)
            reasons = [
                "업로드된 이미지에서 '스마트폰'이 확인되었습니다.",
                "설명에 포함된 키워드 '아이폰', '1년'을 바탕으로 시장 평균 가격을 참고하였습니다.",
                "중고 거래 플랫폼의 유사 모델 평균 가격 데이터를 적용했습니다."
            ]
            
        # 결과 표시 섹션
        st.success("분석이 완료되었습니다!")
        st.markdown("---")
        
        st.header("📊 추정 값어치")
        st.metric(label="예상 가격", value=f"{estimated_value:,}원")
        
        st.header("🔍 이렇게 추정했어요")
        for i, reason in enumerate(reasons, 1):
            st.write(f"{i}. {reason}")
            
    else:
        st.error("사진과 물건 설명을 모두 입력해주세요!")
