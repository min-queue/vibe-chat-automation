from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="Chat API",
    description="간단한 채팅 API 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Chat API Server"}


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy"} 