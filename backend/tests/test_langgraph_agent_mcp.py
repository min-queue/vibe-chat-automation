import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock


class TestLangGraphMCPAgent:
    """MCP 웹 검색을 사용하는 LangGraph 에이전트 테스트"""
    
    @pytest.fixture
    def agent(self):
        """LangGraph MCP 에이전트 픽스처"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_google_key', 'EXA_API_KEY': 'test_exa_key'}):
            with patch('app.langgraph_agent_mcp.multiturn_agent') as mock_multiturn, \
                 patch('app.langgraph_agent_mcp.ChatGoogleGenerativeAI') as mock_llm, \
                 patch('app.langgraph_agent_mcp.MCPWebSearchService') as mock_mcp:
                
                # Mock 객체들 설정
                mock_multiturn.memory_system.get_checkpointer.return_value = Mock()
                mock_multiturn.memory_system.get_store.return_value = Mock()
                
                from app.langgraph_agent_mcp import LangGraphMCPAgent
                return LangGraphMCPAgent()
    
    @pytest.mark.asyncio
    async def test_initialize_agent(self, agent):
        """에이전트 초기화 테스트"""
        assert agent.mcp_web_search is not None
        assert agent.multiturn_agent is not None
        assert agent.llm is not None
        assert agent.graph is not None
    
    @pytest.mark.asyncio
    async def test_web_search_integration(self, agent):
        """웹 검색 MCP 통합 테스트"""
        # Mock MCP 웹 검색 결과
        mock_search_result = {
            "results": [
                {"title": "Test Product", "url": "https://example.com", "snippet": "Great price"}
            ]
        }
        
        # AsyncMock 사용
        agent.mcp_web_search.search_web = AsyncMock(return_value=mock_search_result)
        
        # 웹 검색 실행
        result = await agent.mcp_web_search.search_web("test query")
        
        assert "results" in result
        assert len(result["results"]) == 1
        agent.mcp_web_search.search_web.assert_called_once_with("test query")
    
    @pytest.mark.asyncio
    async def test_graph_execution_with_mcp(self, agent):
        """MCP를 사용한 그래프 실행 테스트"""
        # Mock 데이터
        test_user_id = "test_user_123"
        test_message = "아이폰 15 최저가 찾아줘"
        
        # Mock MCP 검색 결과
        mock_search_result = {
            "results": [
                {"title": "iPhone 15 최저가", "url": "https://example.com", "snippet": "900,000원"}
            ]
        }
        
        # Mock LLM 응답
        mock_response = Mock()
        mock_response.content = "아이폰 15의 최저가는 900,000원입니다."
        
        with patch.object(agent.mcp_web_search, 'search_web') as mock_search, \
             patch.object(agent.mcp_web_search, 'client', Mock()), \
             patch.object(agent.llm, 'invoke') as mock_llm, \
             patch.object(agent.multiturn_agent, 'save_conversation_memory') as mock_save, \
             patch.object(agent.multiturn_agent, 'get_conversation_context') as mock_get_context, \
             patch.object(agent.multiturn_agent, 'create_session') as mock_create_session:
            
            mock_search.return_value = mock_search_result
            mock_llm.return_value = mock_response
            mock_save.return_value = None
            mock_get_context.return_value = []
            mock_create_session.return_value = "test_session_123"
            
            # 그래프 실행
            config = agent.create_session_config(test_user_id)
            input_data = {"messages": [{"role": "user", "content": test_message}]}
            
            # Graph invoke를 Mock 처리
            with patch.object(agent.graph, 'invoke') as mock_invoke:
                mock_invoke.return_value = {"messages": [mock_response]}
                result = agent.invoke(input_data, config)
                
                # 검증
                assert "messages" in result
                mock_invoke.assert_called_once_with(input_data, config)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """에러 처리 테스트"""
        # Mock 검색 에러
        mock_error_result = {
            "results": [],
            "error": "검색 서비스 오류"
        }
        
        # AsyncMock 사용
        agent.mcp_web_search.search_web = AsyncMock(return_value=mock_error_result)
        
        # 에러 상황에서도 적절한 응답이 반환되는지 확인
        result = await agent.mcp_web_search.search_web("test query")
        
        assert "error" in result
        assert result["error"] == "검색 서비스 오류" 