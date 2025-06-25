import uuid
from typing import Dict, List, Optional, Any
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver


class MemorySystem:
    """멀티턴 대화를 위한 메모리 시스템"""
    
    def __init__(self):
        """메모리 시스템 초기화"""
        self.store = InMemoryStore()
        self.checkpointer = InMemorySaver()
        
    def get_user_namespace(self, user_id: str) -> tuple:
        """사용자별 네임스페이스 생성"""
        return (user_id, "memories")
        
    def save_memory(self, user_id: str, content: str, memory_type: str = "conversation") -> str:
        """메모리 저장"""
        namespace = self.get_user_namespace(user_id)
        memory_id = str(uuid.uuid4())
        memory_data = {
            "content": content,
            "type": memory_type
        }
        
        self.store.put(namespace, memory_id, memory_data)
        return memory_id
        
    def get_memory(self, user_id: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """특정 메모리 조회"""
        namespace = self.get_user_namespace(user_id)
        result = self.store.get(namespace, memory_id)
        return result.value if result else None
        
    def search_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 메모리 검색"""
        namespace = self.get_user_namespace(user_id)
        results = self.store.search(namespace)
        
        # 최근 메모리부터 반환 (limit 적용)
        memories = []
        for item in results[-limit:]:
            memories.append({
                "id": item.key,
                "content": item.value["content"],
                "type": item.value["type"],
                "created_at": item.created_at,
                "updated_at": item.updated_at
            })
        
        return memories
        
    def get_store(self) -> InMemoryStore:
        """스토어 인스턴스 반환"""
        return self.store
        
    def get_checkpointer(self) -> InMemorySaver:
        """체크포인터 인스턴스 반환"""
        return self.checkpointer


# 전역 메모리 시스템 인스턴스
memory_system = MemorySystem() 