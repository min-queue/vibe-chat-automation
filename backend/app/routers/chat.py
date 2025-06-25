from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.agent import search_products

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