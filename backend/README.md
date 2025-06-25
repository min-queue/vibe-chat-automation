# TASK-003: LangGraph Agent 구현 완료

## 개요
LangGraph를 사용한 React Agent 구현이 완료되었습니다. 이 Agent는 DuckDuckGo 검색을 통해 상품 정보를 찾고, Gemini LLM을 사용하여 사용자에게 유용한 정보를 제공합니다.

## 구현된 기능

### 1. LangGraph React Agent
- **create_react_agent** 함수를 사용한 단일 턴 Agent
- **Gemini-2.0-flash** 모델 연동
- **DuckDuckGo Search Tool** 통합
- 한국어 상품 검색 전용 시스템 프롬프트

### 2. FastAPI 통합
- `/chat/` 엔드포인트를 통한 Agent 호출
- 에러 핸들링 및 HTTP 예외 처리
- JSON 요청/응답 처리

### 3. 테스트 커버리지
- Agent 생성 및 실행 테스트
- 상품 검색 함수 테스트
- FastAPI 엔드포인트 테스트
- 에러 상황 테스트

## 설정 방법

### 1. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# AI 모델 API 키 (필수)
GOOGLE_API_KEY=your_google_api_key_here

# LangSmith 모니터링 (선택사항)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=vibe-coding-w2-1
```

### 2. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python run.py
```

## API 사용법

### 상품 검색
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "아이폰 15"}'
```

### 응답 예시
```json
{
  "response": "아이폰 15에 대한 상품 정보를 찾았습니다...(검색 결과)"
}
```

## 테스트 실행
```bash
# 모든 테스트 실행
python -m pytest tests/ -v

# Agent 테스트만 실행
python -m pytest tests/test_agent.py -v

# API 테스트만 실행
python -m pytest tests/test_chat.py -v
```

## 기술 스택
- **LangGraph**: React Agent 프레임워크
- **Google Gemini**: LLM 모델
- **DuckDuckGo Search**: 웹 검색 Tool
- **FastAPI**: 웹 API 프레임워크
- **pytest**: 테스트 프레임워크

## 구현 특징
- **단일 턴 처리**: 메모리 없이 각 요청을 독립적으로 처리
- **간단한 구조**: 과도한 모듈화 없이 심플한 아키텍처
- **TDD 개발**: 테스트 우선 개발 방식 적용
- **에러 핸들링**: 안정적인 예외 처리 