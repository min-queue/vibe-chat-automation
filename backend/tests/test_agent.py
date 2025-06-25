import pytest
from unittest.mock import Mock, patch
from app.agent import create_agent, search_products


@pytest.fixture
def mock_agent():
    """Mock Agent 인스턴스를 반환하는 픽스처"""
    agent = Mock()
    agent.invoke.return_value = {
        "messages": [
            Mock(content="테스트 상품 검색 결과입니다.")
        ]
    }
    return agent


def test_create_agent():
    """Agent 생성 테스트"""
    with patch('app.agent.create_react_agent') as mock_create:
        mock_create.return_value = Mock()
        agent = create_agent()
        assert agent is not None
        mock_create.assert_called_once()


def test_search_products():
    """상품 검색 함수 테스트"""
    with patch('app.agent.create_agent') as mock_create:
        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [
                Mock(content="아이폰 15 관련 상품 검색 결과입니다.")
            ]
        }
        mock_create.return_value = mock_agent
        
        result = search_products("아이폰 15")
        
        assert result is not None
        assert "아이폰 15" in result or "상품 검색" in result
        mock_agent.invoke.assert_called_once()


def test_search_products_with_empty_query():
    """빈 쿼리로 상품 검색 테스트"""
    result = search_products("")
    assert "검색어를 입력해주세요" in result


def test_search_products_with_none_query():
    """None 쿼리로 상품 검색 테스트"""
    result = search_products(None)
    assert "검색어를 입력해주세요" in result


def test_agent_tool_integration():
    """Agent와 Tool 통합 테스트"""
    with patch('app.agent.DuckDuckGoSearchRun') as mock_tool:
        mock_tool.return_value.invoke.return_value = "검색 결과"
        
        with patch('app.agent.create_react_agent') as mock_create:
            mock_agent = Mock()
            mock_create.return_value = mock_agent
            
            agent = create_agent()
            assert agent is not None 