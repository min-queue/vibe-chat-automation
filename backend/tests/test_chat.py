import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_endpoint_success():
    """채팅 엔드포인트 성공 테스트"""
    with patch('app.routers.chat.search_products') as mock_search:
        mock_search.return_value = "아이폰 15 검색 결과입니다."
        
        response = client.post(
            "/chat/",
            json={"message": "아이폰 15"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "아이폰 15" in data["response"]
        mock_search.assert_called_once_with("아이폰 15")


def test_chat_endpoint_empty_message():
    """빈 메시지로 채팅 엔드포인트 테스트"""
    with patch('app.routers.chat.search_products') as mock_search:
        mock_search.return_value = "검색어를 입력해주세요."
        
        response = client.post(
            "/chat/",
            json={"message": ""}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "검색어를 입력해주세요" in data["response"]


def test_chat_endpoint_agent_error():
    """Agent 에러 발생 시 테스트"""
    with patch('app.routers.chat.search_products') as mock_search:
        mock_search.side_effect = Exception("Agent 오류")
        
        response = client.post(
            "/chat/",
            json={"message": "test"}
        )
        
        assert response.status_code == 500
        assert "검색 중 오류가 발생했습니다" in response.json()["detail"]


def test_chat_endpoint_invalid_json():
    """잘못된 JSON 요청 테스트"""
    response = client.post(
        "/chat/",
        json={}
    )
    
    assert response.status_code == 422


def test_chat_invalid_request():
    """잘못된 채팅 요청 테스트"""
    response = client.post(
        "/chat",
        json={}
    )
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_error_handling():
    """채팅 엔드포인트 에러 처리 테스트"""
    # 빈 메시지 테스트
    response = client.post("/chat/", json={"message": ""})
    assert response.status_code == 422


def test_get_chat_history_success():
    """채팅 히스토리 조회 성공 테스트"""
    response = client.get("/chat/history")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    # 기본 limit=50 확인
    assert len(data) <= 50
    
    # 각 메시지 구조 확인
    if data:
        message = data[0]
        assert "message" in message
        assert "timestamp" in message


def test_get_chat_history_with_pagination():
    """채팅 히스토리 페이지네이션 테스트"""
    response = client.get("/chat/history?limit=5&offset=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) <= 5


def test_get_chat_history_limit_validation():
    """채팅 히스토리 limit 유효성 검사 테스트"""
    # limit 초과 테스트
    response = client.get("/chat/history?limit=150")
    assert response.status_code == 422
    
    # 음수 offset 테스트
    response = client.get("/chat/history?offset=-1")
    assert response.status_code == 422 