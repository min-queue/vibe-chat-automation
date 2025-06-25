from typing import Dict, List, Optional, Any
from datetime import datetime

from app.langgraph_agent import langgraph_agent


class SessionService:
    """세션 관리 서비스"""
    
    def __init__(self):
        """세션 서비스 초기화"""
        self.langgraph_agent = langgraph_agent
        
    def create_user_session(self, user_id: str) -> Dict[str, Any]:
        """사용자 세션 생성"""
        session_id = self.langgraph_agent.multiturn_agent.create_session(user_id)
        
        session_info = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat()
        }
        
        return session_info
        
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보 조회"""
        session = self.langgraph_agent.multiturn_agent.session_manager.get_session(session_id)
        if not session:
            return None
            
        return {
            "session_id": session["session_id"],
            "user_id": session["user_id"],
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat()
        }
        
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 모든 세션 조회"""
        sessions = self.langgraph_agent.multiturn_agent.session_manager.get_user_sessions(user_id)
        
        return [
            {
                "session_id": session["session_id"],
                "user_id": session["user_id"],
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat()
            }
            for session in sessions
        ]
        
    def get_user_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 메모리 조회"""
        return self.langgraph_agent.multiturn_agent.get_conversation_context(user_id, limit)
        
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        return self.langgraph_agent.multiturn_agent.session_manager.delete_session(session_id)
        
    def chat_with_memory(self, user_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """메모리를 활용한 채팅"""
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
        
        input_data = {
            "messages": [{"role": "user", "content": message}]
        }
        
        result = self.langgraph_agent.invoke(input_data, config)
        
        # 결과 포맷팅
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            return {
                "response": last_message.content,
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "response": "응답을 생성할 수 없습니다.",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
    def stream_chat_with_memory(self, user_id: str, session_id: str, message: str):
        """메모리를 활용한 스트리밍 채팅"""
        config = {
            "configurable": {
                "thread_id": session_id,
                "user_id": user_id
            }
        }
        
        input_data = {
            "messages": [{"role": "user", "content": message}]
        }
        
        return self.langgraph_agent.stream(input_data, config, stream_mode="values")


# 전역 세션 서비스 인스턴스
session_service = SessionService() 