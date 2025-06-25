from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import multiturn_chat
from app.config import settings  # LangSmith 설정 초기화

app = FastAPI(
    title="Multiturn Chat API",
    description="멀티턴 대화를 지원하는 채팅 API 서버",
    version="2.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 멀티턴 채팅 라우터만 등록
app.include_router(multiturn_chat.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Multiturn Chat API Server"}


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"} 