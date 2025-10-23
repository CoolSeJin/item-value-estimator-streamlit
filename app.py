import streamlit as st
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io
import base64

# -------------------------------
# 1️⃣ API 키 설정
# -------------------------------
try:
    # Streamlit Cloud의 "Secrets"에 OPENAI_API_KEY 등록 필수
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("⚠️ API 키 설정 중 오류가 발생했습니다. Secrets에 OPENAI_API_KEY가 설정되었는지 확인해주세요.")
    st.stop()

st.set_page_config(page_title="AI 시세 분석기", page_icon="💰", layout="centered")
st.title("💰 AI 기반 아이템 시세 분석기")
st.write("사진과 설명을 업로드하면 AI가 자동으로 시세를 예측하고, 향후 변동까지 분석해드려요!")

# -------------------------------
# 2️⃣ 이미지 처리 함수
# -------------------------------
def encode_image(image_file):
    """이미지를 base64로 인코딩"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def validate_image_with_ai(image_base64, item_description):
    """AI를 통해 이미지가 상품과 관련 있는지 검증"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "당신은 이미지 검증 전문가입니다. 사용자가 업로드한 이미지가 설명된 상품과 일치하는지, 상품 시세 분석에 적합한 이미지인지 평가해주세요. 부적절한 이미지(풍경, 사람 얼굴, 텍스트만 있는 이미지 등)인 경우 거부해야 합니다."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"다음 상품 설명에 해당하는 적절한 상품 이미지인지 평가해주세요:\n{item_description}\n\n이 이미지가 상품 시세 분석에 적합하면 '적합'이라고만 답변하고, 부적절한 이미지이면 '부적합: [이유]' 형식으로 답변해주세요."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"이미지 검증 중 오류: {str(e)}"

# -------------------------------
# 3️⃣ 이미지 업로드 및 입력
# -------------------------------
uploaded_file = st.file_uploader("상품 사진을 업로드하세요", type=["jpg", "jpeg", "png"])
item_description = st.text_area("상품 설명을 입력하세요 (브랜드, 상태, 모델명 등)", height=100)
item_type = st.selectbox("상품 카테고리", ["전자기기", "의류", "신발", "가방", "가구", "도서", "기타"])

if uploaded_file and item_description:
    # 이미지 표시
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 상품", use_container_width=True)
    
    # -------------------------------
    # 4️⃣ 이미지 검증
    # -------------------------------
    with st.spinner("이미지를 검증 중입니다..."):
        # 파일 포인터를 처음으로 되돌림
        uploaded_file.seek(0)
        image_base64 = encode_image(uploaded_file)
        validation_result = validate_image_with_ai(image_base64, item_description)
        
        if "부적합" in validation_result:
            st.error(f"❌ {validation_result}")
            st.warning("📸 상품을 명확히 보여주는 사진으로 다시 업로드해주세요.")
            st.info("💡 추천 사진: 상품 전체가 선명하게 보이는 사진, 배경이 깔끔한 사진, 여러 각도에서 찍은 사진")
            st.stop()
        elif "오류" in validation_result:
            st.error(validation_result)
            st.stop()
    
    # -------------------------------
    # 5️⃣ AI 시세 분석
    # -------------------------------
    with st.spinner("AI가 시세를 분석 중입니다..."):
        try:
            # 이미지와 텍스트를 함께 사용한 분석
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 숙련된 중고 시세 분석 전문가입니다. 이미지와 설명을 바탕으로 정확한 시세를 예측해주세요."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"""
다음 상품의 시세를 분석해주세요:

카테고리: {item_type}
설명: {item_description}

다음 내용을 포함해서 분석해주세요:
1. 예상 평균 시세 (원 단위)
2. 가격에 영향을 주는 요소 (브랜드, 상태, 희귀성 등)
3. 현재 시장 추세 (가격이 오를지/떨어질지)
4. 거래 시 유의사항

분석 결과는 다음과 같은 형식으로 제공해주세요:
💰 예상 시세: [가격]원
📊 분석 근거: [2-3문장]
📈 시장 전망: [1-2문장]
💡 거래 팁: [1-2문장]
                            """},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            ai_result = response.choices[0].message.content

            # -------------------------------
            # 6️⃣ 결과 출력
            # -------------------------------
            st.subheader("📊 AI 시세 분석 결과")
            st.write(ai_result)

            # -------------------------------
            # 7️⃣ 시세 그래프 시뮬레이션
            # -------------------------------
            st.subheader("📈 예상 시세 추이")
            
            # 더 현실적인 가격 범위 설정
            np.random.seed(42)
            months = np.arange(1, 13)
            
            # 상품 카테고리별 기본 가격대 설정
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
            
            # 계절성 변동 반영 (의류, 신발 등)
            seasonal_effect = 1.0
            if item_type in ["의류", "신발"]:
                seasonal_pattern = [1.1, 1.0, 0.9, 0.8, 0.9, 1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 1.0]
                seasonal_effect = np.array([seasonal_pattern[i] for i in range(12)])
            
            trend = np.linspace(base_price * 0.9, base_price * 1.1, 12)
            noise = np.random.normal(0, base_price * 0.05, 12)
            prices = trend * seasonal_effect + noise

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(months, prices, marker="o", linewidth=2, color="#FF6B6B")
            ax.fill_between(months, prices * 0.95, prices * 1.05, alpha=0.2, color="#FF6B6B")
            ax.set_title(f"'{item_type}' 카테고리 평균 시세 추이 (예상)", fontsize=14, fontweight='bold')
            ax.set_xlabel("개월", fontsize=12)
            ax.set_ylabel("가격 (원)", fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.ticklabel_format(style='plain', axis='y')
            
            # y축 형식을 원화로 설정
            import matplotlib.ticker as ticker
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}원'))
            
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error("⚠️ 시세 분석 중 오류가 발생했습니다.")
            st.error(f"오류 내용: {str(e)}")
            st.info("잠시 후 다시 시도해주세요.")

else:
    st.info("📸 상품 사진과 설명을 모두 입력하면 정확한 시세를 분석합니다.")
    st.write("---")
    st.subheader("📸 좋은 사진 예시")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**명확한 전체샷**")
        st.info("상품 전체가 선명하게")
    with col2:
        st.write("**다양한 각도**")
        st.info("전후좌우 모두 촬영")
    with col3:
        st.write("**상태 확인**")
        st.info("흠집이나 손상 부분")
