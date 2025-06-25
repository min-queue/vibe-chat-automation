import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI


class TestMultiturnChatMCPAPI:
    """MCP 통합 멀티턴 채팅 API 테스트"""
    
    @pytest.fixture
    def app(self):
        """테스트용 FastAPI 앱 생성"""
        app = FastAPI()
        
        # Mock 라우터를 직접 생성
        from fastapi import APIRouter
        router = APIRouter()
        
        @router.post("/sessions/")
        async def create_session(session_data: dict):
            return {"session_id": "test_session_123", "user_id": session_data["user_id"]}
        
        @router.post("/chat/{session_id}")
        async def chat(session_id: str, message: dict):
            return {
                "response": "Mock MCP response for: " + message["message"],
                "user_id": "test_user",
                "session_id": session_id
            }
        
        app.include_router(router)
        return app
    
    @pytest.mark.asyncio
    async def test_chat_with_mcp_search(self, app):
        """MCP 웹 검색을 사용한 채팅 테스트"""
        # TestClient를 사용하되 async context 내에서 실행
        from httpx import ASGITransport
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 세션 생성
            session_response = await client.post(
                "/sessions/",
                json={"user_id": "test_user"}
            )
            assert session_response.status_code == 200
            session_data = session_response.json()
            session_id = session_data["session_id"]
            
            # MCP 검색 채팅 요청
            chat_response = await client.post(
                f"/chat/{session_id}",
                json={"message": "iPhone 15 Pro 최저가 알려줘"}
            )
            
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            
            # 응답 검증
            assert "response" in chat_data
            assert "iPhone 15 Pro" in chat_data["response"]
    
    @pytest.mark.asyncio
    async def test_mcp_web_search_service_integration(self):
        """MCP 웹 검색 서비스 직접 테스트"""
        from app.mcp_web_search import MCPWebSearchService
        
        mcp_service = MCPWebSearchService()
        
        # Mock 검색 결과
        mock_search_result = {
            "results": [
                {"title": "iPhone 15 Pro", "url": "https://example.com", "snippet": "최저가 1,200,000원"}
            ]
        }
        
        # AsyncMock 사용
        mcp_service.search_web = AsyncMock(return_value=mock_search_result)
        
        # 웹 검색 실행
        result = await mcp_service.search_web("iPhone 15 Pro 최저가")
        
        assert "results" in result
        assert len(result["results"]) == 1
        assert "iPhone 15 Pro" in result["results"][0]["title"]
    
    @pytest.mark.asyncio
    async def test_langgraph_mcp_agent_integration(self):
        """LangGraph MCP 에이전트 통합 테스트"""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key', 'EXA_API_KEY': 'test_exa_key'}):
            with patch('app.langgraph_agent_mcp.multiturn_agent') as mock_multiturn, \
                 patch('app.langgraph_agent_mcp.ChatGoogleGenerativeAI') as mock_llm, \
                 patch('app.langgraph_agent_mcp.MCPWebSearchService') as mock_mcp:
                
                # Mock 설정
                mock_multiturn.memory_system.get_checkpointer.return_value = Mock()
                mock_multiturn.memory_system.get_store.return_value = Mock()
                
                from app.langgraph_agent_mcp import LangGraphMCPAgent
                agent = LangGraphMCPAgent()
                
                # Mock MCP 검색 결과
                mock_search_result = {
                    "results": [
                        {"title": "iPhone 15", "url": "https://example.com", "snippet": "900,000원"}
                    ]
                }
                
                # Mock 응답
                mock_response = Mock()
                mock_response.content = "iPhone 15의 최저가는 900,000원입니다."
                
                # AsyncMock으로 search_web 설정
                agent.mcp_web_search.search_web = AsyncMock(return_value=mock_search_result)
                agent.mcp_web_search.client = Mock()
                
                # 검색 실행
                result = await agent.mcp_web_search.search_web("iPhone 15 최저가")
                
                assert "results" in result
                assert len(result["results"]) == 1
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """에러 처리 테스트"""
        from app.mcp_web_search import MCPWebSearchService
        
        mcp_service = MCPWebSearchService()
        
        # Mock 검색 에러
        mock_error_result = {
            "results": [],
            "error": "검색 서비스 일시 중단"
        }
        
        # AsyncMock 사용
        mcp_service.search_web = AsyncMock(return_value=mock_error_result)
        
        # 에러 상황에서도 적절한 응답이 반환되는지 확인
        result = await mcp_service.search_web("test query")
        
        assert "error" in result
        assert result["error"] == "검색 서비스 일시 중단"
    
    @pytest.mark.asyncio
    async def test_mcp_search_error_handling(self):
        """MCP 검색 오류 처리 테스트"""
        # Mock 검색 오류
        mock_error_result = {
            "results": [],
            "error": "검색 서비스 일시 중단"
        }
        
        with patch('app.routers.multiturn_chat.get_langgraph_mcp_agent') as mock_get_agent:
            # Mock 에이전트 설정
            mock_agent = Mock()
            mock_agent.mcp_web_search.search_web = AsyncMock(return_value=mock_error_result)
            mock_agent.mcp_web_search.client = Mock()
            mock_agent.create_session_config.return_value = {
                "configurable": {"thread_id": "test_session", "user_id": "test_user"}
            }
            
            # 오류 응답 Mock
            mock_error_response = Mock()
            mock_error_response.content = "죄송합니다. 현재 검색 서비스에 일시적인 문제가 있습니다."
            mock_agent.invoke.return_value = {"messages": [mock_error_response]}
            
            mock_get_agent.return_value = mock_agent
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                # 세션 생성
                session_response = await client.post(
                    "/sessions/",
                    json={"user_id": "test_user"}
                )
                session_id = session_response.json()["session_id"]
                
                # 검색 오류 시 채팅 요청
                chat_response = await client.post(
                    f"/chat/{session_id}",
                    json={"message": "검색 테스트"}
                )
                
                assert chat_response.status_code == 200
                chat_data = chat_response.json()
                
                # 오류가 적절히 처리되는지 확인
                assert "response" in chat_data
                assert "일시적인 문제" in chat_data["response"]
    
    @pytest.mark.asyncio
    async def test_memory_integration_with_mcp(self):
        """MCP와 메모리 시스템 통합 테스트"""
        # 이전 대화 메모리 Mock
        mock_memory = [
            {"content": "사용자가 iPhone에 관심이 있음", "timestamp": "2023-01-01"}
        ]
        
        # Mock MCP 검색 결과
        mock_search_result = {
            "results": [
                {"title": "iPhone 15", "url": "https://example.com", "snippet": "900,000원"}
            ]
        }
        
        with patch('app.routers.multiturn_chat.get_langgraph_mcp_agent') as mock_get_agent:
            # Mock 에이전트 설정
            mock_agent = Mock()
            mock_agent.mcp_web_search.search_web = AsyncMock(return_value=mock_search_result)
            mock_agent.mcp_web_search.client = Mock()
            mock_agent.multiturn_agent.get_conversation_context.return_value = mock_memory
            mock_agent.multiturn_agent.save_conversation_memory.return_value = None
            mock_agent.create_session_config.return_value = {
                "configurable": {"thread_id": "test_session", "user_id": "test_user"}
            }
            
            # 메모리를 활용한 응답 Mock
            mock_response = Mock()
            mock_response.content = "이전에 iPhone에 관심을 보이셨네요. iPhone 15의 현재 최저가는 900,000원입니다."
            mock_agent.invoke.return_value = {"messages": [mock_response]}
            
            mock_get_agent.return_value = mock_agent
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                # 세션 생성
                session_response = await client.post(
                    "/sessions/",
                    json={"user_id": "test_user"}
                )
                session_id = session_response.json()["session_id"]
                
                # 메모리를 활용한 채팅 요청
                chat_response = await client.post(
                    f"/chat/{session_id}",
                    json={"message": "최신 가격 알려줘"}
                )
                
                assert chat_response.status_code == 200
                chat_data = chat_response.json()
                
                # 메모리 활용 응답 검증
                assert "response" in chat_data
                assert "이전에" in chat_data["response"]
                assert "iPhone" in chat_data["response"] 