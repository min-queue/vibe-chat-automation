import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_read_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json() 