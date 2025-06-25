import os
import asyncio
from typing import List, Dict, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPWebSearchService:
    """MCP 웹 검색 서비스"""
    
    def __init__(self):
        self.client: Optional[MultiServerMCPClient] = None
        self.search_tools: List = []
    
    async def initialize(self) -> None:
        """MCP 클라이언트 초기화"""
        exa_api_key = os.getenv("EXA_API_KEY")
        
        if not exa_api_key:
            raise ValueError("EXA_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # Exa MCP 서버만 우선 연동 (심플하게 시작)
        self.client = MultiServerMCPClient({
            "exa": {
                "command": "npx",
                "args": ["-y", "exa-mcp-server"],
                "env": {"EXA_API_KEY": exa_api_key},
                "transport": "stdio"
            }
        })
        
        # 웹 검색 도구 로드
        await self._load_search_tools()
    
    async def _load_search_tools(self) -> None:
        """웹 검색 도구 로드"""
        if not self.client:
            return
            
        tools = await self.client.get_tools()
        self.search_tools = [tool for tool in tools if "search" in tool.name.lower()]
    
    async def get_web_search_tools(self) -> List:
        """웹 검색 도구 반환"""
        if not self.search_tools:
            await self._load_search_tools()
        return self.search_tools
    
    async def search_web(self, query: str) -> Dict[str, Any]:
        """웹 검색 실행"""
        if not self.search_tools:
            await self._load_search_tools()
        
        if not self.search_tools:
            return {"results": [], "error": "검색 도구를 사용할 수 없습니다."}
        
        try:
            # 첫 번째 검색 도구 사용
            search_tool = self.search_tools[0]
            result = await search_tool.ainvoke({"query": query})
            return result
        except Exception as e:
            return {"results": [], "error": f"검색 중 오류 발생: {str(e)}"}
    
    async def cleanup(self) -> None:
        """리소스 정리"""
        # 새로운 API에서는 별도 정리가 필요 없음
        pass 