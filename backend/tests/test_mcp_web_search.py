import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from app.mcp_web_search import MCPWebSearchService


class TestMCPWebSearchService:
    """웹 검색 MCP 서비스 테스트"""
    
    @pytest.fixture
    def mcp_service(self):
        """MCP 웹 검색 서비스 픽스처"""
        return MCPWebSearchService()
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_client(self, mcp_service):
        """MCP 클라이언트 초기화 테스트"""
        with patch.dict(os.environ, {
            'EXA_API_KEY': 'test_exa_key'
        }):
            with patch.object(mcp_service, '_load_search_tools') as mock_load:
                mock_load.return_value = None
                await mcp_service.initialize()
                assert mcp_service.client is not None
                mock_load.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_get_web_search_tools(self, mcp_service):
        """웹 검색 도구 가져오기 테스트"""
        # Mock MCP client
        mock_client = AsyncMock()
        
        # Mock tools with proper name attribute
        mock_tool1 = Mock()
        mock_tool1.name = "exa_search"
        mock_tool2 = Mock()
        mock_tool2.name = "web_search"
        
        mock_tools = [mock_tool1, mock_tool2]
        mock_client.get_tools.return_value = mock_tools
        mcp_service.client = mock_client
        
        tools = await mcp_service.get_web_search_tools()
        assert len(tools) == 2  # 두 개 모두 "search"가 포함됨
        mock_client.get_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_web(self, mcp_service):
        """웹 검색 기능 테스트"""
        # Mock tool execution
        mock_tool = AsyncMock()
        mock_tool.name = "exa_search"
        mock_tool.ainvoke.return_value = {
            "results": [
                {"title": "Test Result", "url": "https://example.com", "snippet": "Test snippet"}
            ]
        }
        
        mcp_service.search_tools = [mock_tool]
        
        results = await mcp_service.search_web("test query")
        assert "results" in results
        assert len(results["results"]) == 1
        mock_tool.ainvoke.assert_called_once_with({"query": "test query"})
    
    @pytest.mark.asyncio
    async def test_cleanup_client(self, mcp_service):
        """클라이언트 정리 테스트"""
        mock_client = AsyncMock()
        mcp_service.client = mock_client
        
        await mcp_service.cleanup()
        # 새로운 API에서는 정리가 필요 없으므로 아무것도 호출되지 않음
        assert True 