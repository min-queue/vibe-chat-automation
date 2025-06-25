import pytest
import uuid
from app.session_manager import SessionManager


class TestSessionManager:
    """세션 관리자 테스트"""
    
    def test_session_creation(self):
        """세션 생성 테스트"""
        manager = SessionManager()
        user_id = "test_user"
        
        session_id = manager.create_session(user_id)
        assert session_id is not None
        assert isinstance(session_id, str)
        
    def test_get_session(self):
        """세션 조회 테스트"""
        manager = SessionManager()
        user_id = "test_user"
        
        session_id = manager.create_session(user_id)
        session = manager.get_session(session_id)
        
        assert session is not None
        assert session["user_id"] == user_id
        assert session["session_id"] == session_id
        
    def test_session_isolation(self):
        """세션 격리 테스트"""
        manager = SessionManager()
        
        user1_session = manager.create_session("user1")
        user2_session = manager.create_session("user2")
        
        assert user1_session != user2_session
        
        session1 = manager.get_session(user1_session)
        session2 = manager.get_session(user2_session)
        
        assert session1["user_id"] == "user1"
        assert session2["user_id"] == "user2"
        
    def test_get_user_sessions(self):
        """사용자별 세션 목록 조회 테스트"""
        manager = SessionManager()
        user_id = "test_user"
        
        session1 = manager.create_session(user_id)
        session2 = manager.create_session(user_id)
        
        sessions = manager.get_user_sessions(user_id)
        assert len(sessions) == 2
        assert session1 in [s["session_id"] for s in sessions]
        assert session2 in [s["session_id"] for s in sessions]
        
    def test_session_config_generation(self):
        """세션 설정 생성 테스트"""
        manager = SessionManager()
        user_id = "test_user"
        
        session_id = manager.create_session(user_id)
        config = manager.get_session_config(session_id)
        
        assert config is not None
        assert config["configurable"]["thread_id"] == session_id
        assert config["configurable"]["user_id"] == user_id 