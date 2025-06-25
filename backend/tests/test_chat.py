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