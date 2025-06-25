import pytest
from unittest.mock import Mock
from app.session_service import SessionService


class TestSessionService:
    """세션 관리 서비스 테스트"""
    
    def test_service_creation(self):
        """서비스 생성 테스트"""
        service = SessionService()
        assert service is not None
        assert service.langgraph_agent is not None
        
    def test_create_user_session(self):
        """사용자 세션 생성 테스트"""
        service = SessionService()
        user_id = "test_user"
        
        session_info = service.create_user_session(user_id)
        
        assert session_info is not None
        assert "session_id" in session_info
        assert "user_id" in session_info
        assert session_info["user_id"] == user_id
        
    def test_get_session_info(self):
        """세션 정보 조회 테스트"""
        service = SessionService()
        user_id = "test_user"
        
        session_info = service.create_user_session(user_id)
        session_id = session_info["session_id"]
        
        retrieved_info = service.get_session_info(session_id)
        
        assert retrieved_info is not None
        assert retrieved_info["session_id"] == session_id
        assert retrieved_info["user_id"] == user_id
        
    def test_get_user_sessions(self):
        """사용자 세션 목록 조회 테스트"""
        service = SessionService()
        user_id = "test_user"
        
        # 여러 세션 생성
        session1 = service.create_user_session(user_id)
        session2 = service.create_user_session(user_id)
        
        sessions = service.get_user_sessions(user_id)
        
        assert len(sessions) >= 2
        session_ids = [s["session_id"] for s in sessions]
        assert session1["session_id"] in session_ids
        assert session2["session_id"] in session_ids
        
    def test_get_user_memories(self):
        """사용자 메모리 조회 테스트"""
        service = SessionService()
        user_id = "test_user"
        
        # 메모리 추가
        service.langgraph_agent.multiturn_agent.save_conversation_memory(
            user_id, "테스트 질문", "테스트 답변"
        )
        
        memories = service.get_user_memories(user_id)
        
        assert memories is not None
        assert len(memories) > 0
        
    def test_delete_session(self):
        """세션 삭제 테스트"""
        service = SessionService()
        user_id = "test_user"
        
        session_info = service.create_user_session(user_id)
        session_id = session_info["session_id"]
        
        # 세션 삭제
        result = service.delete_session(session_id)
        assert result is True
        
        # 삭제된 세션 조회 시도
        deleted_session = service.get_session_info(session_id)
        assert deleted_session is None 