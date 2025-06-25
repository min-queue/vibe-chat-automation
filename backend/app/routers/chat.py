from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.agent import search_products

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/chat/", response_model=ChatResponse, tags=["채팅"])
async def chat(request: ChatRequest):
    """
    사용자의 메시지를 받아 응답을 생성합니다.
    
    - **message**: 사용자의 입력 메시지
    """
    try:
        # 의도적인 버그: undefined_variable 참조
        print(undefined_variable)  # NameError 발생 예정
        
        # AI 에이전트를 통한 상품 검색
        search_result = search_products(request.message)
        
        if search_result:
            response_text = f"다음 상품을 찾았습니다: {search_result}"
        else:
            response_text = "죄송합니다. 관련 상품을 찾을 수 없습니다."
        
        return ChatResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}") 