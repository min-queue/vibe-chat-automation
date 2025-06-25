from fastapi import APIRouter, HTTPException, Query
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.agent import search_products
from typing import List
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 엔드포인트 - Agent를 통한 상품 검색"""
    try:
        # Agent를 통한 상품 검색
        response_text = search_products(request.message)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/chat/history", response_model=List[ChatMessage], tags=["채팅"])
async def get_chat_history(
    limit: int = Query(default=50, le=100, description="조회할 메시지 수"),
    offset: int = Query(default=0, ge=0, description="시작 위치")
):
    """
    채팅 히스토리를 조회합니다.
    
    - **limit**: 조회할 메시지 수 (최대 100개)
    - **offset**: 시작 위치 (페이지네이션용)
    """
    # TODO: 실제 데이터베이스에서 채팅 히스토리 조회
    # 현재는 목업 데이터 반환
    mock_history = [
        ChatMessage(
            message=f"테스트 메시지 {i}",
            timestamp=datetime.now() - timedelta(minutes=i*5)
        )
        for i in range(offset, min(offset + limit, 20))
    ]
    
    return mock_history 