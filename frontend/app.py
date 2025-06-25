import streamlit as st
import requests
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="상품 검색 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 상수 설정
BACKEND_URL = "http://localhost:8000/chat/"
REQUEST_TIMEOUT = 5 if os.getenv("STREAMLIT_TESTING") else 30  # 테스트 환경에서는 짧은 타임아웃

def call_backend_api(message: str) -> str:
    """백엔드 API 호출 함수"""
    try:
        with st.spinner("AI가 상품을 검색 중입니다..."):
            response = requests.post(
                BACKEND_URL,
                json={"message": message},
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("response", "응답을 받을 수 없습니다.")
            else:
                return f"서버 오류가 발생했습니다. (상태 코드: {response.status_code})"
                
    except requests.exceptions.ConnectionError:
        return "백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."
    except requests.exceptions.Timeout:
        return "요청 시간이 초과되었습니다. 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"요청 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"예상치 못한 오류가 발생했습니다: {str(e)}"

def display_response_with_stream(response: str):
    """응답을 스트리밍 방식으로 표시"""
    # 테스트 환경에서는 스트리밍 효과 생략
    if os.getenv("STREAMLIT_TESTING"):
        st.markdown(response)
        return response
    
    placeholder = st.empty()
    displayed_text = ""
    
    for char in response:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(0.02)  # 타이핑 효과
    
    return response

# 메인 앱 UI
st.title("🤖 상품 검색 챗봇")
st.markdown("안녕하세요! 찾고 계신 상품에 대해 질문해주세요.")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("상품에 대해 질문해주세요!"):
    # 빈 메시지 체크
    if not prompt.strip():
        st.warning("메시지를 입력해주세요.")
    else:
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 어시스턴트 응답 생성 및 표시
        with st.chat_message("assistant"):
            response = call_backend_api(prompt)
            # 스트리밍 효과로 응답 표시
            final_response = display_response_with_stream(response)
            
        # 어시스턴트 응답을 세션 상태에 저장
        st.session_state.messages.append({"role": "assistant", "content": final_response})

# 사이드바에 추가 정보
with st.sidebar:
    st.header("💡 사용법")
    st.markdown("""
    1. 아래 채팅창에 찾고 싶은 상품명을 입력하세요
    2. AI가 웹에서 상품 정보를 검색합니다
    3. 검색 결과와 추천 상품을 확인하세요
    
    **예시 질문:**
    - "iPhone 15 Pro 가격 알려줘"
    - "노트북 추천해줘"
    - "무선 이어폰 비교해줘"
    """)
    
    if st.button("채팅 기록 삭제"):
        st.session_state.messages = []
        st.rerun() 