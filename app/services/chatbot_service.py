from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.chatbot import ChatbotMemory, ChatbotMemorySchema, ChatbotMemoryType, ConversationContext
from app.core.chatbot_vector_store import ChatbotVectorStore
from uuid import uuid4
from datetime import datetime
from fastapi import Depends
from app.db.dependencies import get_db

class ChatbotService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.vector_store = ChatbotVectorStore()

    async def create_conversation(
        self,
        user_id: str,
        business_id: str,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid4())
        context = ConversationContext(
            id=conversation_id,
            user_id=user_id,
            business_id=business_id,
            context=initial_context or {},
            created_at=datetime.utcnow()
        )
        self.db.add(context)
        self.db.commit()
        return conversation_id

    async def store_memory(
        self,
        memory: ChatbotMemorySchema,
        current_user: Any
    ) -> Dict[str, Any]:
        """Store a chatbot memory"""
        # Generate embedding for the memory content
        embedding = await self.vector_store.generate_embedding(memory.content)
        
        # Store in vector database
        memory_id = str(uuid4())
        await self.vector_store.store_memory(
            memory_id=memory_id,
            memory_type=memory.type,
            content=memory.content,
            embedding=embedding,
            metadata={
                "user_id": str(current_user.id),
                "business_id": memory.business_id,
                "conversation_id": memory.conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Store in SQL database
        db_memory = ChatbotMemory(
            id=memory_id,
            user_id=str(current_user.id),
            business_id=memory.business_id,
            conversation_id=memory.conversation_id,
            type=memory.type,
            content=memory.content,
            metadata=memory.metadata
        )
        self.db.add(db_memory)
        self.db.commit()
        
        return {
            "memory_id": memory_id,
            "type": memory.type,
            "content": memory.content,
            "metadata": memory.metadata
        }

    async def get_conversation_context(
        self,
        conversation_id: str,
        memory_type: Optional[ChatbotMemoryType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation context"""
        # Get context from vector store
        filter_conditions = {"conversation_id": conversation_id}
        if memory_type:
            filter_conditions["type"] = memory_type
            
        memories = await self.vector_store.search_similar_memories(
            query="",  # Empty query to get all memories
            memory_type=memory_type,
            filter_conditions=filter_conditions,
            limit=limit
        )
        
        return memories

    async def get_user_history(
        self,
        user_id: str,
        business_id: str,
        memory_type: Optional[ChatbotMemoryType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's conversation history"""
        filter_conditions = {
            "user_id": user_id,
            "business_id": business_id
        }
        if memory_type:
            filter_conditions["type"] = memory_type
            
        memories = await self.vector_store.search_similar_memories(
            query="",  # Empty query to get all memories
            memory_type=memory_type,
            filter_conditions=filter_conditions,
            limit=limit
        )
        
        return memories

    async def search_similar_memories(
        self,
        query: str,
        memory_type: Optional[ChatbotMemoryType] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar memories"""
        memories = await self.vector_store.search_similar_memories(
            query=query,
            memory_type=memory_type,
            filter_conditions=filter_conditions or {},
            limit=limit
        )
        
        return memories 