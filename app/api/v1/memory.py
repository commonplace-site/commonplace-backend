from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.core.utils import get_current_user
from app.models.memory import Memory, MemorySchema, MemoryType

from app.services.memory_service import MemoryService
from app.schemas.common import PaginationParams

router = APIRouter()

@router.post("/write", response_model=MemorySchema)
async def write_memory(
    memory: MemorySchema,
    current_user = Depends(get_current_user),
    memory_service: MemoryService = Depends()
):
    """Store any data type as memory object"""
    return await memory_service.write_memory(memory, current_user)

@router.get("/read", response_model=List[MemorySchema])
async def read_memory(
    type: Optional[MemoryType] = None,
    tags: Optional[List[str]] = Query(None),
    business_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    pagination: PaginationParams = Depends(),
    current_user = Depends(get_current_user),
    memory_service: MemoryService = Depends()
):
    """Read memory objects with filtering"""
    return await memory_service.read_memory(
        type=type,
        tags=tags,
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
        pagination=pagination,
        current_user=current_user
    )

@router.post("/query", response_model=List[MemorySchema])
async def query_memory(
    query: str,
    type: Optional[MemoryType] = None,
    business_id: Optional[UUID] = None,
    pagination: PaginationParams = Depends(),
    current_user = Depends(get_current_user),
    memory_service: MemoryService = Depends()
):
    """Semantic search across memory objects"""
    return await memory_service.query_memory(
        query=query,
        type=type,
        business_id=business_id,
        pagination=pagination,
        current_user=current_user
    )

@router.get("/boot", response_model=dict)
async def boot_memory(
    current_user = Depends(get_current_user),
    memory_service: MemoryService = Depends()
):
    """Get session context and recent memory objects"""
    return await memory_service.boot_memory(current_user) 