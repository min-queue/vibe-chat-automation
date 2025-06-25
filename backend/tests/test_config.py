import pytest
from app.config import settings


def test_settings_defaults():
    """기본 설정값 테스트"""
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert isinstance(settings.DEBUG, bool)


def test_settings_types():
    """설정값 타입 테스트"""
    assert isinstance(settings.HOST, str)
    assert isinstance(settings.PORT, int)
    assert isinstance(settings.DEBUG, bool) 