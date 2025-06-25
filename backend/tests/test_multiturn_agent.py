import pytest
from unittest.mock import Mock, patch
from app.multiturn_agent import MultiturnAgent


class TestMultiturnAgent:
    """멀티턴 에이전트 테스트"""
    
    def test_agent_creation(self):
        """에이전트 생성 테스트"""
        agent = MultiturnAgent()
        assert agent is not None
        assert agent.memory_system is not None
        
    def test_search_with_memory(self):
        """메모리를 활용한 검색 테스트"""
        agent = MultiturnAgent()
        user_id = "test_user"
        session_id = "test_session"
        query = "피자 최저가"
        
        # 이전 대화 메모리 추가
        agent.memory_system.save_memory(user_id, "사용자가 이탈리아 음식을 좋아함", "preference")
        
        with patch('app.multiturn_agent.DuckDuckGoSearchRun') as mock_search:
            mock_search.return_value.run.return_value = "피자 검색 결과"
            
            result = agent.search_with_memory(user_id, session_id, query)
            assert result is not None
            assert isinstance(result, str)
            
    def test_save_conversation_memory(self):
        """대화 메모리 저장 테스트"""
        agent = MultiturnAgent()
        user_id = "test_user"
        query = "치킨 최저가 알려줘"
        response = "치킨 최저가 정보: ..."
        
        memory_id = agent.save_conversation_memory(user_id, query, response)
        assert memory_id is not None
        
        # 저장된 메모리 확인
        memories = agent.memory_system.search_memories(user_id)
        assert len(memories) > 0
        
    def test_get_conversation_context(self):
        """대화 컨텍스트 조회 테스트"""
        agent = MultiturnAgent()
        user_id = "test_user"
        
        # 테스트 메모리 추가
        agent.memory_system.save_memory(user_id, "이전 질문: 피자 가격", "conversation")
        agent.memory_system.save_memory(user_id, "사용자 취향: 매운 음식 좋아함", "preference")
        
        context = agent.get_conversation_context(user_id)
        assert context is not None
        assert len(context) > 0
        
    def test_memory_integration(self):
        """메모리 통합 테스트"""
        agent = MultiturnAgent()
        user_id = "test_user"
        
        # 이전 대화 저장
        agent.memory_system.save_memory(user_id, "피자를 좋아합니다", "preference")
        
        # 컨텍스트 조회
        context = agent.get_conversation_context(user_id)
        assert any("피자" in memory["content"] for memory in context) 