import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent


def create_agent():
    """LangGraph React Agent를 생성합니다."""
    # Gemini LLM 모델 초기화
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # DuckDuckGo 검색 Tool 초기화
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    
    # 시스템 프롬프트 설정
    system_prompt = """
    당신은 상품 최저가 검색 전문 어시스턴트입니다.
    사용자가 요청한 상품에 대해 판매 사이트가 나오도록 검색어를 수정하고 웹 검색을 상품리스트를 찾고, 
    한국어로 유용하고 정확한 상품 최저가 정보와 구매 링크를 제공해주세요.
    
    검색 결과를 바탕으로:
    1. 상품명과 가격 정보
    2. 구매 가능한 쇼핑몰 또는 사이트 링크
    
    위 정보들을 포함하여 친절하고 상세하게 답변해주세요.
    """
    
    # React Agent 생성
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt
    )
    
    return agent


def search_products(query: Optional[str]) -> str:
    """상품 검색 함수"""
    if not query or query.strip() == "":
        return "검색어를 입력해주세요."
    
    try:
        agent = create_agent()
        
        # Agent 실행
        result = agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        # 결과에서 마지막 메시지 내용 추출
        if result and "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            return last_message.content
        else:
            return "검색 결과를 가져올 수 없습니다."
            
    except Exception as e:
        return f"검색 중 오류가 발생했습니다: {str(e)}" 