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
# 2️⃣ 이미지 처리 함수 (수정된 버전)
# -------------------------------
def encode_image(image_file):
    """이미지를 base64로 안전하게 인코딩"""
    try:
        # 파일 포인터를 처음으로 되돌림
        image_file.seek(0)
        # 바이너리 데이터 읽기
        image_data = image_file.read()
        # base64로 인코딩 (ASCII-safe)
        encoded_string = base64.b64encode(image_data).decode('ascii')
        return encoded_string
    except Exception as e:
        st.error(f"이미지 처리 중 오류: {str(e)}")
        return None

def validate_image_with_ai(image_base64, item_description):
    """AI를 통해 이미지가 상품과 관련 있는지 검증"""
    try:
        # 시스템 메시지를 ASCII-safe하게 작성
        system_message = """
        You are an image validation expert. Evaluate if the uploaded image matches the described product 
        and is suitable for product price analysis. Reject inappropriate images (landscapes, faces, text-only images, etc.).
        Respond with 'Suitable' only if appropriate, or 'Unsuitable: [reason]' if not.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Product description: {item_description}\n\nIs this image suitable for price analysis of this product? Respond with 'Suitable' or 'Unsuitable: [reason]'."},
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
        return f"Validation error: {str(e)}"

# -------------------------------
# 3️⃣ 이미지 업로드 및 입력
# -------------------------------
uploaded_file = st.file_uploader("상품 사진을 업로드하세요", type=["jpg", "jpeg", "png"])
item_description = st.text_area("상품 설명을 입력하세요 (브랜드, 상태, 모델명 등)", height=100)
item_type = st.selectbox("상품 카테고리", ["전자기기", "의류", "신발", "가방", "가구", "도서", "기타"])

if uploaded_file and item_description:
    # 이미지 표시
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 상품", use_container_width=True)
    except Exception as e:
        st.error(f"이미지를 표시할 수 없습니다: {str(e)}")
        st.stop()
    
    # -------------------------------
    # 4️⃣ 이미지 검증
    # -------------------------------
    with st.spinner("이미지를 검증 중입니다..."):
        image_base64 = encode_image(uploaded_file)
        
        if image_base64 is None:
            st.error("이미지 처리에 실패했습니다. 다른 이미지로 시도해주세요.")
            st.stop()
            
        validation_result = validate_image_with_ai(image_base64, item_description)
        
        if "Unsuitable" in validation_result:
            st.error(f"❌ 부적합한 이미지입니다: {validation_result}")
            st.warning("📸 상품을 명확히 보여주는 사진으로 다시 업로드해주세요.")
            st.info("💡 추천 사진: 상품 전체가 선명하게 보이는 사진, 배경이 깔끔한 사진, 여러 각도에서 찍은 사진")
            st.stop()
        elif "Validation error" in validation_result:
            st.error("이미지 검증 중 오류가 발생했습니다.")
            st.info("계속 진행하시려면 '검증 건너뛰기' 버튼을 눌러주세요.")
            
            if st.button("검증 건너뛰기 및 계속 진행"):
                st.warning("이미지 검증을 건너뛰고 분석을 진행합니다.")
            else:
                st.stop()
        elif "Suitable" in validation_result:
            st.success("✅ 이미지 검증 통과! 적합한 상품 이미지입니다.")
        else:
            st.warning("⚠️ 이미지 검증 결과를 확인할 수 없습니다. 계속 진행합니다.")
    
    # -------------------------------
    # 5️⃣ AI 시세 분석
    # -------------------------------
    with st.spinner("AI가 시세를 분석 중입니다..."):
        try:
            # ASCII-safe한 시스템 메시지
            system_message = """
            You are an experienced used price analysis expert. 
            Predict the average online used price for the product based on the image and description.
            Provide the analysis in the following format:
            💰 Estimated Price: [price] won
            📊 Analysis Basis: [2-3 sentences]
            📈 Market Outlook: [1-2 sentences]
            💡 Trading Tips: [1-2 sentences]
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"""
Category: {item_type}
Description: {item_description}

Please analyze the price and provide insights.
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
            
            trend = np.linspace(base_price * 0.9, base_price * 1.1, 12)
            noise = np.random.normal(0, base_price * 0.05, 12)
            prices = trend + noise

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(months, prices, marker="o", linewidth=2, color="#FF6B6B")
            ax.fill_between(months, prices * 0.95, prices * 1.05, alpha=0.2, color="#FF6B6B")
            ax.set_title(f"Price Trend for {item_type} Category (Estimated)", fontsize=14, fontweight='bold')
            ax.set_xlabel("Month", fontsize=12)
            ax.set_ylabel("Price (KRW)", fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # y축 형식을 설정
            import matplotlib.ticker as ticker
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error("⚠️ 시세 분석 중 오류가 발생했습니다.")
            st.error(f"오류 내용: {str(e)}")
            st.info("잠시 후 다시 시도해주세요.")

else:
    st.info("📸 상품 사진과 설명을 모두 입력하면 정확한 시세를 분석합니다.")
