import pytest
import os
from unittest.mock import Mock, patch
from app.langgraph_agent import LangGraphAgent


class TestLangGraphAgent:
    """LangGraph 기반 에이전트 테스트"""
    
    def test_agent_creation(self):
        """에이전트 생성 테스트"""
        agent = LangGraphAgent()
        assert agent is not None
        assert agent.graph is not None
        
    def test_invoke_with_memory(self):
        """메모리를 사용한 에이전트 호출 테스트"""
        agent = LangGraphAgent()
        user_id = "test_user"
        session_id = agent.multiturn_agent.create_session(user_id)
        
        # 이전 대화 메모리 추가
        agent.multiturn_agent.save_preference_memory(user_id, "치킨을 좋아함")
        
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
        
        with patch('app.langgraph_agent.DuckDuckGoSearchRun') as mock_search:
            mock_search.return_value.run.return_value = "치킨 최저가 검색 결과"
            
            result = agent.invoke(
                {"messages": [{"role": "user", "content": "치킨 최저가 알려줘"}]},
                config
            )
            
            assert result is not None
            assert "messages" in result
            
    def test_stream_with_memory(self):
        """메모리를 사용한 스트리밍 테스트"""
        agent = LangGraphAgent()
        user_id = "test_user2"
        session_id = agent.multiturn_agent.create_session(user_id)
        
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
        
        with patch('app.langgraph_agent.DuckDuckGoSearchRun') as mock_search:
            mock_search.return_value.run.return_value = "피자 검색 결과"
            
            stream_results = list(agent.stream(
                {"messages": [{"role": "user", "content": "피자 최저가"}]},
                config,
                stream_mode="values"
            ))
            
            assert len(stream_results) > 0
            
    def test_memory_persistence(self):
        """메모리 지속성 테스트"""
        agent = LangGraphAgent()
        user_id = "test_user3"
        session_id = agent.multiturn_agent.create_session(user_id)
        
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
        
        # 첫 번째 대화
        with patch('app.langgraph_agent.DuckDuckGoSearchRun') as mock_search:
            mock_search.return_value.run.return_value = "햄버거 검색 결과"
            
            agent.invoke(
                {"messages": [{"role": "user", "content": "햄버거 최저가"}]},
                config
            )
        
        # 메모리 확인
        memories = agent.multiturn_agent.get_conversation_context(user_id)
        assert len(memories) > 0
        assert any("햄버거" in memory["content"] for memory in memories) 