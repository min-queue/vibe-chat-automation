from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any
import json

from app.session_service import session_service
from app.langgraph_agent_mcp import get_langgraph_mcp_agent

router = APIRouter()


class SessionCreate(BaseModel):
    user_id: str


class ChatMessage(BaseModel):
    message: str


@router.post("/sessions/")
async def create_session(session_data: SessionCreate) -> Dict[str, Any]:
    """새 세션 생성"""
    try:
        session_info = session_service.create_user_session(session_data.user_id)
        return session_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """세션 정보 조회"""
    session_info = session_service.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_info


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    """사용자의 모든 세션 조회"""
    try:
        sessions = session_service.get_user_sessions(user_id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/memories")
async def get_user_memories(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """사용자 메모리 조회"""
    try:
        memories = session_service.get_user_memories(user_id, limit)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """세션 삭제"""
    try:
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/{session_id}")
async def chat(session_id: str, message: ChatMessage) -> Dict[str, Any]:
    """MCP 웹 검색을 활용한 메모리 기반 채팅"""
    try:
        # 세션 정보 조회
        session_info = session_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = session_info["user_id"]
        
        # MCP 에이전트 사용 (기존 세션 서비스 대신)
        try:
            mcp_agent = get_langgraph_mcp_agent()
            
            # MCP 초기화 (필요시)
            if not mcp_agent.mcp_web_search.client:
                await mcp_agent.initialize()
            
            # LangGraph 실행을 위한 설정 구성
            config = mcp_agent.create_session_config(user_id)
            input_data = {"messages": [{"role": "user", "content": message.message}]}
            
            # LangGraph 실행
            result = mcp_agent.invoke(input_data, config)
            
            if "messages" in result and len(result["messages"]) > 0:
                last_message = result["messages"][-1]
                return {
                    "response": last_message.content,
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": session_info.get("created_at", "")
                }
            else:
                return {
                    "response": "죄송합니다. 응답을 생성할 수 없습니다.",
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": session_info.get("created_at", "")
                }
                
        except Exception as mcp_error:
            # MCP 오류 시 기존 세션 서비스로 폴백
            print(f"MCP 오류 발생, 기존 서비스로 폴백: {mcp_error}")
            result = session_service.chat_with_memory(user_id, session_id, message.message)
            return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/{session_id}/stream")
async def stream_chat(session_id: str, message: ChatMessage):
    """메모리를 활용한 스트리밍 채팅 (기존 방식 유지)"""
    try:
        # 세션 정보 조회
        session_info = session_service.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = session_info["user_id"]
        
        def generate_stream():
            try:
                for chunk in session_service.stream_chat_with_memory(user_id, session_id, message.message):
                    if "messages" in chunk and len(chunk["messages"]) > 0:
                        last_message = chunk["messages"][-1]
                        yield f"data: {json.dumps({'content': last_message.content})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(generate_stream(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """헬스체크"""
    return {"status": "healthy"} 