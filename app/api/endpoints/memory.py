from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.memory import MemoryCreate, MemoryRead, MemoryQuery, MemoryResponse
from app.services.memory_service import MemoryService
from app.core.auth import get_current_user

router = APIRouter()
memory_service = MemoryService()

@router.post("/write", response_model=MemoryResponse)
async def write_memory(
    memory: MemoryCreate,
    current_user: str = Depends(get_current_user)
):
    if memory.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to write memory for this user")
    
    memory_obj = await memory_service.write_memory(memory)
    return MemoryResponse(
        id=str(memory_obj.id),
        user_id=memory_obj.user_id,
        type=memory_obj.type,
        tags=memory_obj.tags,
        content=memory_obj.content,
        date=memory_obj.date
    )

@router.get("/read", response_model=List[MemoryResponse])
async def read_memories(
    filters: MemoryRead = Depends(),
    current_user: str = Depends(get_current_user)
):
    if filters.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to read memories for this user")
    
    memories = await memory_service.read_memories(filters)
    return [
        MemoryResponse(
            id=str(memory.id),
            user_id=memory.user_id,
            type=memory.type,
            tags=memory.tags,
            content=memory.content,
            date=memory.date
        )
        for memory in memories
    ]

@router.post("/query", response_model=List[MemoryResponse])
async def query_memories(
    query: MemoryQuery,
    current_user: str = Depends(get_current_user)
):
    if query.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to query memories for this user")
    
    memories = await memory_service.query_memories(query)
    return [
        MemoryResponse(
            id=str(memory.id),
            user_id=memory.user_id,
            type=memory.type,
            tags=memory.tags,
            content=memory.content,
            date=memory.date,
            similarity_score=memory.similarity_score
        )
        for memory in memories
    ]

@router.post("/boot", response_model=List[MemoryResponse])
async def boot_memory(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to access boot context for this user")
    
    memories = await memory_service.get_boot_context(user_id)
    return [
        MemoryResponse(
            id=str(memory.id),
            user_id=memory.user_id,
            type=memory.type,
            tags=memory.tags,
            content=memory.content,
            date=memory.date
        )
        for memory in memories
    ] 