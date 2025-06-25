import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime


class SessionManager:
    """사용자 세션 관리자"""
    
    def __init__(self):
        """세션 관리자 초기화"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        
    def create_session(self, user_id: str) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        self.sessions[session_id] = session_data
        
        # 사용자별 세션 목록에 추가
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        return session_id
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보 조회"""
        if session_id in self.sessions:
            # 마지막 활동 시간 업데이트
            self.sessions[session_id]["last_activity"] = datetime.now()
            return self.sessions[session_id]
        return None
        
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 모든 세션 조회"""
        if user_id not in self.user_sessions:
            return []
            
        sessions = []
        for session_id in self.user_sessions[user_id]:
            if session_id in self.sessions:
                sessions.append(self.sessions[session_id])
        
        return sessions
        
    def get_session_config(self, session_id: str) -> Optional[Dict[str, Any]]:
        """LangGraph 설정 생성"""
        session = self.get_session(session_id)
        if not session:
            return None
            
        return {
            "configurable": {
                "thread_id": session_id,
                "user_id": session["user_id"]
            }
        }
        
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        user_id = session["user_id"]
        
        # 세션 삭제
        del self.sessions[session_id]
        
        # 사용자 세션 목록에서 제거
        if user_id in self.user_sessions:
            self.user_sessions[user_id] = [
                s for s in self.user_sessions[user_id] if s != session_id
            ]
            
        return True


# 전역 세션 관리자 인스턴스
session_manager = SessionManager() 