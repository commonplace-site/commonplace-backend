from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.utils import get_current_user
from app.services.chatbot_service import ChatbotService
from app.models.chatbot import (
    ChatbotMemorySchema,
    ChatbotMemoryType,
    ConversationContext
)
from app.schemas.common import ResponseSchema
from app.core.chatbot_vector_store import ChatbotVectorStore
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post("/conversations", response_model=ResponseSchema)
async def create_conversation(
    business_id: str,
    initial_context: Optional[Dict[str, Any]] = None,
    current_user: Any = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends()
) -> ResponseSchema:
    """Create a new conversation"""
    conversation_id = await chatbot_service.create_conversation(
        user_id=str(current_user.id),
        business_id=business_id,
        initial_context=initial_context
    )
    return ResponseSchema(
        success=True,
        data={"conversation_id": conversation_id}
    )

@router.post("/memories", response_model=ResponseSchema)
async def store_memory(
    memory: ChatbotMemorySchema,
    current_user: Any = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends()
) -> ResponseSchema:
    """Store a chatbot memory"""
    stored_memory = await chatbot_service.store_memory(memory, current_user)
    return ResponseSchema(
        success=True,
        data=stored_memory
    )

@router.get("/conversations/{conversation_id}/context", response_model=ResponseSchema)
async def get_conversation_context(
    conversation_id: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends()
) -> ResponseSchema:
    """Get conversation context"""
    context = await chatbot_service.get_conversation_context(
        conversation_id=conversation_id,
        memory_type=memory_type,
        limit=limit
    )
    return ResponseSchema(
        success=True,
        data=context
    )

@router.get("/users/{user_id}/history", response_model=ResponseSchema)
async def get_user_history(
    user_id: str,
    business_id: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user: Any = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends()
) -> ResponseSchema:
    """Get user's conversation history"""
    history = await chatbot_service.get_user_history(
        user_id=user_id,
        business_id=business_id,
        memory_type=memory_type,
        limit=limit
    )
    return ResponseSchema(
        success=True,
        data=history
    )

@router.get("/memories/search", response_model=ResponseSchema)
async def search_similar_memories(
    query: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    business_id: Optional[str] = None,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    limit: int = Query(5, ge=1, le=50),
    current_user: Any = Depends(get_current_user),
    chatbot_service: ChatbotService = Depends()
) -> ResponseSchema:
    """Search for similar memories"""
    filter_conditions = {}
    if business_id:
        filter_conditions["business_id"] = business_id
    if user_id:
        filter_conditions["user_id"] = user_id
    if conversation_id:
        filter_conditions["conversation_id"] = conversation_id

    memories = await chatbot_service.search_similar_memories(
        query=query,
        memory_type=memory_type,
        filter_conditions=filter_conditions,
        limit=limit
    )
    return ResponseSchema(
        success=True,
        data=memories
    )

# Test endpoint to check Qdrant connection
@router.get("/test/connection", response_model=ResponseSchema)
async def test_qdrant_connection(
    vector_store: ChatbotVectorStore = Depends()
) -> ResponseSchema:
    """Test Qdrant connection and list collections"""
    try:
        collections = vector_store.client.get_collections()
        return ResponseSchema(
            success=True,
            data={
                "message": "Successfully connected to Qdrant",
                "collections": [col.name for col in collections.collections]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Qdrant: {str(e)}"
        )

# Test endpoint to store a test memory
@router.post("/test/store", response_model=ResponseSchema)
async def test_store_memory(
    content: str,
    memory_type: ChatbotMemoryType = ChatbotMemoryType.USER_MESSAGE,
    vector_store: ChatbotVectorStore = Depends()
) -> ResponseSchema:
    """Test storing a memory in Qdrant"""
    try:
        memory_id = str(uuid4())
        embedding = await vector_store.generate_embedding(content)
        
        await vector_store.store_memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            metadata={
                "test": True,
                "timestamp": str(datetime.utcnow())
            }
        )
        
        return ResponseSchema(
            success=True,
            data={
                "message": "Successfully stored test memory",
                "memory_id": memory_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store memory: {str(e)}"
        )

# Test endpoint to search memories
@router.get("/test/search", response_model=ResponseSchema)
async def test_search_memories(
    query: str,
    memory_type: Optional[ChatbotMemoryType] = None,
    limit: int = Query(5, ge=1, le=50),
    vector_store: ChatbotVectorStore = Depends()
) -> ResponseSchema:
    """Test searching memories in Qdrant"""
    try:
        results = await vector_store.search_similar_memories(
            query=query,
            memory_type=memory_type or ChatbotMemoryType.USER_MESSAGE,
            limit=limit
        )
        
        return ResponseSchema(
            success=True,
            data={
                "message": "Successfully searched memories",
                "results": results
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search memories: {str(e)}"
        ) 