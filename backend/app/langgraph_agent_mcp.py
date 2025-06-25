import os
import uuid
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.store.base import BaseStore

from app.multiturn_agent import multiturn_agent
from app.mcp_web_search import MCPWebSearchService


class LangGraphMCPAgent:
    """MCP 웹 검색을 사용하는 LangGraph 에이전트"""
    
    def __init__(self):
        """LangGraph MCP 에이전트 초기화"""
        self.multiturn_agent = multiturn_agent
        self.mcp_web_search = MCPWebSearchService()
        
        # LLM 초기화
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # StateGraph 구성
        self.graph = self._build_graph()
        
    async def initialize(self):
        """비동기 초기화"""
        await self.mcp_web_search.initialize()
        
    def _build_graph(self):
        """StateGraph 구성"""
        async def call_model_with_mcp_search(
            state: MessagesState,
            config: RunnableConfig,
            *,
            store: BaseStore = None
        ):
            """MCP 웹 검색을 활용한 모델 호출"""
            user_id = config["configurable"]["user_id"]
            
            # 사용자 메모리 검색
            memories = self.multiturn_agent.get_conversation_context(user_id, limit=3)
            
            # 메모리 정보를 시스템 메시지에 포함
            memory_info = ""
            if memories:
                memory_info = "\n\n이전 대화 정보:\n"
                for memory in memories:
                    memory_info += f"- {memory['content']}\n"
            
            # 현재 사용자 메시지
            last_message = state["messages"][-1]
            current_query = last_message.content
            
            # MCP 웹 검색 수행
            try:
                # MCP 웹 검색 서비스가 초기화되지 않았다면 초기화
                if not self.mcp_web_search.client:
                    await self.mcp_web_search.initialize()
                
                search_result = await self.mcp_web_search.search_web(current_query)
                
                # 검색 결과 포맷팅
                if search_result.get("results"):
                    formatted_results = ""
                    for result in search_result["results"][:3]:  # 상위 3개 결과만 사용
                        formatted_results += f"- {result.get('title', 'N/A')}: {result.get('snippet', 'N/A')}\n"
                        if result.get('url'):
                            formatted_results += f"  링크: {result['url']}\n"
                else:
                    formatted_results = search_result.get("error", "검색 결과가 없습니다.")
                
                # 시스템 프롬프트 구성
                system_prompt = f"""
                당신은 상품 최저가 검색 전문 어시스턴트입니다.
                사용자가 요청한 상품에 대해 웹 검색 결과를 바탕으로 한국어로 유용하고 정확한 상품 최저가 정보와 구매 링크를 제공해주세요.
                {memory_info}
                
                검색 결과:
                {formatted_results}
                """
                
                # LLM 호출
                response = self.llm.invoke([
                    {"role": "system", "content": system_prompt},
                    *state["messages"]
                ])
                
                # 대화 메모리 저장
                self.multiturn_agent.save_conversation_memory(
                    user_id, 
                    current_query, 
                    response.content
                )
                
                return {"messages": [response]}
                
            except Exception as e:
                error_response = f"검색 중 오류가 발생했습니다: {str(e)}"
                return {"messages": [{"role": "assistant", "content": error_response}]}
        
        # StateGraph 빌드
        builder = StateGraph(MessagesState)
        builder.add_node("call_model_with_mcp_search", call_model_with_mcp_search)
        builder.add_edge(START, "call_model_with_mcp_search")
        
        # 컴파일 (메모리 시스템의 store와 checkpointer 사용)
        return builder.compile(
            checkpointer=self.multiturn_agent.memory_system.get_checkpointer(),
            store=self.multiturn_agent.memory_system.get_store()
        )
        
    def invoke(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """그래프 호출"""
        return self.graph.invoke(input_data, config)
        
    def stream(self, input_data: Dict[str, Any], config: Dict[str, Any], stream_mode: str = "values"):
        """그래프 스트리밍"""
        return self.graph.stream(input_data, config, stream_mode=stream_mode)
        
    def create_session_config(self, user_id: str) -> Dict[str, Any]:
        """세션 설정 생성"""
        session_id = self.multiturn_agent.create_session(user_id)
        return {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }


# 전역 LangGraph MCP 에이전트 인스턴스 (지연 초기화)
langgraph_mcp_agent = None

def get_langgraph_mcp_agent():
    """LangGraph MCP 에이전트 싱글톤 생성"""
    global langgraph_mcp_agent
    if langgraph_mcp_agent is None:
        langgraph_mcp_agent = LangGraphMCPAgent()
    return langgraph_mcp_agent 