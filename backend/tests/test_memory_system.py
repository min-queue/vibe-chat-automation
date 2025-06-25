import pytest
import uuid
from unittest.mock import Mock
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver


class TestMemorySystem:
    """메모리 시스템 테스트"""
    
    def test_inmemory_store_creation(self):
        """InMemoryStore 생성 테스트"""
        store = InMemoryStore()
        assert store is not None
        
    def test_inmemory_saver_creation(self):
        """InMemorySaver 생성 테스트"""
        saver = InMemorySaver()
        assert saver is not None
        
    def test_store_put_and_get(self):
        """메모리 저장 및 조회 테스트"""
        store = InMemoryStore()
        user_id = "test_user"
        namespace = (user_id, "memories")
        memory_id = str(uuid.uuid4())
        memory_data = {"content": "테스트 메모리", "type": "conversation"}
        
        # 메모리 저장
        store.put(namespace, memory_id, memory_data)
        
        # 메모리 조회
        retrieved = store.get(namespace, memory_id)
        assert retrieved is not None
        assert retrieved.value == memory_data
        
    def test_store_search(self):
        """메모리 검색 테스트"""
        store = InMemoryStore()
        user_id = "test_user"
        namespace = (user_id, "memories")
        
        # 테스트 데이터 저장
        memory1 = {"content": "피자를 좋아합니다", "type": "preference"}
        memory2 = {"content": "커피를 자주 마십니다", "type": "preference"}
        
        store.put(namespace, "mem1", memory1)
        store.put(namespace, "mem2", memory2)
        
        # 검색
        results = store.search(namespace)
        assert len(results) == 2
        
    def test_namespace_isolation(self):
        """네임스페이스 격리 테스트"""
        store = InMemoryStore()
        
        user1_namespace = ("user1", "memories")
        user2_namespace = ("user2", "memories")
        
        memory1 = {"content": "사용자1 메모리"}
        memory2 = {"content": "사용자2 메모리"}
        
        store.put(user1_namespace, "mem1", memory1)
        store.put(user2_namespace, "mem1", memory2)
        
        # 각 사용자별로 격리된 메모리 확인
        user1_results = store.search(user1_namespace)
        user2_results = store.search(user2_namespace)
        
        assert len(user1_results) == 1
        assert len(user2_results) == 1
        assert user1_results[0].value["content"] == "사용자1 메모리"
        assert user2_results[0].value["content"] == "사용자2 메모리" 