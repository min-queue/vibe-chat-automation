import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

# TestClient 인스턴스를 함수 내에서 생성
def get_client():
    return TestClient(app)


class TestMultiturnAPI:
    """멀티턴 API 테스트"""
    
    def test_create_session_endpoint(self):
        """세션 생성 엔드포인트 테스트"""
        client = get_client()
        response = client.post("/sessions/", json={"user_id": "test_user"})
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "user_id" in data
        assert data["user_id"] == "test_user"
        
    def test_get_session_endpoint(self):
        """세션 조회 엔드포인트 테스트"""
        client = get_client()
        # 세션 생성
        create_response = client.post("/sessions/", json={"user_id": "test_user"})
        session_id = create_response.json()["session_id"]
        
        # 세션 조회
        response = client.get(f"/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["user_id"] == "test_user"
        
    def test_get_user_sessions_endpoint(self):
        """사용자 세션 목록 조회 엔드포인트 테스트"""
        client = get_client()
        user_id = "test_user"
        
        # 세션 생성
        client.post("/sessions/", json={"user_id": user_id})
        client.post("/sessions/", json={"user_id": user_id})
        
        # 세션 목록 조회
        response = client.get(f"/users/{user_id}/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        
    def test_chat_endpoint(self):
        """채팅 엔드포인트 테스트"""
        client = get_client()
        # 세션 생성
        create_response = client.post("/sessions/", json={"user_id": "test_user"})
        session_id = create_response.json()["session_id"]
        
        with patch('app.langgraph_agent.DuckDuckGoSearchRun') as mock_search:
            mock_search.return_value.run.return_value = "테스트 검색 결과"
            
            # 채팅
            response = client.post(
                f"/chat/{session_id}",
                json={"message": "테스트 메시지"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data
            
    def test_get_user_memories_endpoint(self):
        """사용자 메모리 조회 엔드포인트 테스트"""
        client = get_client()
        user_id = "test_user"
        
        # 메모리가 있는 상태에서 조회
        response = client.get(f"/users/{user_id}/memories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_delete_session_endpoint(self):
        """세션 삭제 엔드포인트 테스트"""
        client = get_client()
        # 세션 생성
        create_response = client.post("/sessions/", json={"user_id": "test_user"})
        session_id = create_response.json()["session_id"]
        
        # 세션 삭제
        response = client.delete(f"/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_health_check_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        client = get_client()
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy" 