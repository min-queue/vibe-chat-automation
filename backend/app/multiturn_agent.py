import os
from typing import Optional, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.store.base import BaseStore

from app.memory_system import memory_system
from app.session_manager import session_manager


class MultiturnAgent:
    """멀티턴 대화를 지원하는 에이전트"""
    
    def __init__(self):
        """멀티턴 에이전트 초기화"""
        self.memory_system = memory_system
        self.session_manager = session_manager
        
        # LLM 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # 검색 도구 초기화
        self.search_tool = DuckDuckGoSearchRun()
        
    def get_conversation_context(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """사용자의 대화 컨텍스트 조회"""
        return self.memory_system.search_memories(user_id, limit=limit)
        
    def create_enhanced_prompt(self, query: str, context: List[Dict[str, Any]]) -> str:
        """컨텍스트를 포함한 향상된 프롬프트 생성"""
        base_prompt = """
        당신은 상품 최저가 검색 전문 어시스턴트입니다.
        사용자가 요청한 상품에 대해 판매 사이트가 나오도록 검색어를 수정하고 웹 검색을 상품리스트를 찾고, 
        한국어로 유용하고 정확한 상품 최저가 정보와 구매 링크를 제공해주세요.
        """
        
        if context:
            context_info = "\n\n이전 대화 정보:\n"
            for memory in context:
                context_info += f"- {memory['content']}\n"
            
            base_prompt += context_info
            
        base_prompt += f"\n\n현재 질문: {query}"
        
        return base_prompt
        
    def search_with_memory(self, user_id: str, session_id: str, query: str) -> str:
        """메모리를 활용한 검색"""
        try:
            # 사용자 컨텍스트 조회
            context = self.get_conversation_context(user_id)
            
            # 향상된 프롬프트 생성
            enhanced_query = self.create_enhanced_prompt(query, context)
            
            # 웹 검색 수행
            search_result = self.search_tool.run(enhanced_query)
            
            # LLM으로 결과 정리
            response = self.llm.invoke([
                {"role": "system", "content": enhanced_query},
                {"role": "user", "content": f"검색 결과: {search_result}"}
            ])
            
            # 대화 메모리 저장
            self.save_conversation_memory(user_id, query, response.content)
            
            return response.content
            
        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {str(e)}"
            
    def save_conversation_memory(self, user_id: str, query: str, response: str) -> str:
        """대화 메모리 저장"""
        conversation_text = f"질문: {query}\n답변: {response}"
        return self.memory_system.save_memory(user_id, conversation_text, "conversation")
        
    def save_preference_memory(self, user_id: str, preference: str) -> str:
        """사용자 선호도 메모리 저장"""
        return self.memory_system.save_memory(user_id, preference, "preference")
        
    def create_session(self, user_id: str) -> str:
        """새 세션 생성"""
        return self.session_manager.create_session(user_id)
        
    def get_session_config(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 설정 조회"""
        return self.session_manager.get_session_config(session_id)


# 전역 멀티턴 에이전트 인스턴스
multiturn_agent = MultiturnAgent() 