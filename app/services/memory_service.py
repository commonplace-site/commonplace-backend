from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.database import get_db
from app.models.memory import Memory, MemorySchema, MemoryType
from app.core.vector_store import VectorStore
from app.core.cache import Cache
from app.core.security import check_permissions

class MemoryService:
    def __init__(
        self,
        db: Session = Depends(get_db),
        vector_store: VectorStore = Depends(),
        cache: Cache = Depends()
    ):
        self.db = db
        self.vector_store = vector_store
        self.cache = cache

    # async def write_memory(self, memory: MemorySchema, current_user: UserProfile) -> Memory:
    #     """Write a memory object to both PostgreSQL and Qdrant"""
    #     # Check permissions
    #     check_permissions(current_user, memory.business_id, "write")

    #     # Create memory in PostgreSQL
    #     db_memory = Memory(
    #         business_id=memory.business_id,
    #         user_id=memory.user_id,
    #         type=memory.type,
    #         tags=memory.tags,
    #         content=memory.content,
    #         date=memory.date,
    #         metadata=memory.metadata
    #     )
    #     self.db.add(db_memory)
    #     self.db.commit()
    #     self.db.refresh(db_memory)

    #     # Store in vector database if embedding exists
    #     if memory.embedding:
    #         await self.vector_store.store_memory(
    #             memory_id=str(db_memory.id),
    #             embedding=memory.embedding,
    #             metadata={
    #                 "type": memory.type,
    #                 "business_id": str(memory.business_id),
    #                 "user_id": memory.user_id,
    #                 "tags": memory.tags
    #             }
    #         )

    #     # Invalidate relevant caches
    #     await self.cache.invalidate_memory_cache(memory.business_id)

    #     return db_memory

    # async def read_memory(
    #     self,
    #     type: Optional[MemoryType] = None,
    #     tags: Optional[List[str]] = None,
    #     business_id: Optional[UUID] = None,
    #     start_date: Optional[datetime] = None,
    #     end_date: Optional[datetime] = None,
    #     pagination: dict = None,
    #     current_user: UserProfile = None
    # ) -> List[Memory]:
    #     """Read memory objects with filtering"""
    #     # Check permissions
    #     if business_id:
    #         check_permissions(current_user, business_id, "read")

    #     # Try to get from cache first
    #     cache_key = f"memory:read:{type}:{tags}:{business_id}:{start_date}:{end_date}:{pagination}"
    #     cached_result = await self.cache.get(cache_key)
    #     if cached_result:
    #         return cached_result

    #     # Query from database
    #     query = self.db.query(Memory)
        
    #     if type:
    #         query = query.filter(Memory.type == type)
    #     if tags:
    #         query = query.filter(Memory.tags.overlap(tags))
    #     if business_id:
    #         query = query.filter(Memory.business_id == str(business_id))
    #     if start_date:
    #         query = query.filter(Memory.date >= start_date)
    #     if end_date:
    #         query = query.filter(Memory.date <= end_date)

    #     # Apply pagination
    #     if pagination:
    #         query = query.offset(pagination.offset).limit(pagination.limit)

    #     results = query.all()

    #     # Cache results
    #     await self.cache.set(cache_key, results, expire=300)  # Cache for 5 minutes

    #     return results

    #  async def query_memory(
    #     self,
    #     query: str,
    #     type: Optional[MemoryType] = None,
    #     business_id: Optional[UUID] = None,
    #     pagination: dict = None,
    #     current_user: UserProfile = None
    # ) -> List[Memory]:
    #     """Semantic search across memory objects"""
    #     # Check permissions
    #     if business_id:
    #         check_permissions(current_user, business_id, "read")

    #     # Generate embedding for query
    #     query_embedding = await self.vector_store.generate_embedding(query)

    #     # Search in vector store
    #     vector_results = await self.vector_store.search(
    #         query_embedding,
    #         filter_conditions={
    #             "type": type.value if type else None,
    #             "business_id": str(business_id) if business_id else None
    #         },
    #         limit=pagination.limit if pagination else 10
    #     )

    #     # Get full memory objects from PostgreSQL
    #     memory_ids = [result["id"] for result in vector_results]
    #     memories = self.db.query(Memory).filter(Memory.id.in_(memory_ids)).all()

    #     return memories

    # # async def boot_memory(self, current_user: UserProfile) -> dict:
        """Get session context and recent memory objects"""
        # Get user's recent memories
        # recent_memories = await self.read_memory(
        #     business_id=current_user.business_id,
        #     pagination={"limit": 10, "offset": 0},
        #     current_user=current_user
        # )

        # # Get user's profile
        # user_profile = await self.read_memory(
        #     type=MemoryType.USER_PROFILE,
        #     business_id=current_user.business_id,
        #     current_user=current_user
        # )

        # return {
        #     "recent_memories": recent_memories,
        #     "user_profile": user_profile[0] if user_profile else None
        # } 