import streamlit as st
import requests
import time
import os
import uuid

# 페이지 설정
st.set_page_config(
    page_title="멀티턴 상품 검색 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 상수 설정
BACKEND_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 5 if os.getenv("STREAMLIT_TESTING") else 30  # 테스트 환경에서는 짧은 타임아웃

def create_session(user_id: str) -> str:
    """새 세션 생성"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/sessions/",
            json={"user_id": user_id},
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()["session_id"]
        else:
            st.error(f"세션 생성 실패: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"세션 생성 중 오류: {str(e)}")
        return None

def call_backend_api(session_id: str, message: str) -> str:
    """백엔드 API 호출 함수 (멀티턴 지원)"""
    try:
        with st.spinner("AI가 상품을 검색 중입니다..."):
            response = requests.post(
                f"{BACKEND_URL}/chat/{session_id}",
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

def get_user_memories(user_id: str) -> list:
    """사용자 메모리 조회"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/{user_id}/memories",
            timeout=REQUEST_TIMEOUT
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

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

# 세션 상태 초기화
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "session_id" not in st.session_state:
    st.session_state.session_id = create_session(st.session_state.user_id)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 메인 앱 UI
st.title("🤖 멀티턴 상품 검색 챗봇")
st.markdown("안녕하세요! 찾고 계신 상품에 대해 질문해주세요.")

# 세션 정보 표시
with st.expander("🔧 세션 정보", expanded=False):
    st.text(f"사용자 ID: {st.session_state.user_id}")
    st.text(f"세션 ID: {st.session_state.session_id}")

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("상품에 대해 질문해주세요!"):
    # 빈 메시지 체크
    if not prompt.strip():
        st.warning("메시지를 입력해주세요.")
    elif not st.session_state.session_id:
        st.error("세션이 생성되지 않았습니다. 페이지를 새로고침해주세요.")
    else:
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 어시스턴트 응답 생성 및 표시
        with st.chat_message("assistant"):
            response = call_backend_api(st.session_state.session_id, prompt)
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
    3. **이전 대화를 기억**하여 연관된 질문에 답합니다
    4. 검색 결과와 추천 상품을 확인하세요
    
    **예시 대화:**
    - "iPhone 15 Pro 가격 알려줘"
    - "방금 찾아준 것 중에서 가장 싼 곳은?"
    - "노트북도 추천해줘"
    - "앞에서 말한 iPhone과 비교해줘"
    """)
    
    # 메모리 상태 표시
    st.header("🧠 대화 메모리")
    if st.session_state.session_id:
        memories = get_user_memories(st.session_state.user_id)
        if memories:
            st.text(f"저장된 메모리: {len(memories)}개")
            with st.expander("메모리 내용 보기"):
                for i, memory in enumerate(memories[:5]):  # 최근 5개만 표시
                    st.text(f"{i+1}. {memory['content'][:50]}...")
        else:
            st.text("아직 저장된 메모리가 없습니다.")
    
    # 세션 관리
    st.header("🔄 세션 관리")
    if st.button("새 세션 시작"):
        st.session_state.session_id = create_session(st.session_state.user_id)
        st.session_state.messages = []
        st.rerun()
        
    if st.button("채팅 기록 삭제"):
        st.session_state.messages = []
        st.rerun() 