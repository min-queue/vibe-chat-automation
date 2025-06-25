from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "안녕하세요! 무엇을 도와드릴까요?",
                "timestamp": "2024-01-01T12:00:00"
            }
        }


class ChatMessage(BaseModel):
    """채팅 메시지 모델"""
    message: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "안녕하세요!",
                "timestamp": "2024-01-01T12:00:00"
            }
        } 