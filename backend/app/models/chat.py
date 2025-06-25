from pydantic import BaseModel


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    message: str


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str 