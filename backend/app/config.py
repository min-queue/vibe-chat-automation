import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings:
    """애플리케이션 설정"""
    
    # 서버 설정
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 개발/운영 환경
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings() 