from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.models.chatbot import ChatbotMemoryType
import logging

logger = logging.getLogger(__name__)

class ChatbotVectorStore:
    def __init__(self):
        try:
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                timeout=settings.QDRANT_TIMEOUT
            )
            # Using a multilingual model for better language support
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self._init_collections()
            logger.info("Successfully connected to Qdrant")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise

    def _init_collections(self):
        """Initialize Qdrant collections for different chatbot memory types"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            # Create collections for different memory types if they don't exist
            for memory_type in ChatbotMemoryType:
                collection_name = f"chatbot_{memory_type.value}"
                if collection_name not in collection_names:
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=384,  # Size of the embedding vector
                            distance=models.Distance.COSINE
                        )
                    )
                    logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the multilingual model"""
        try:
            return self.embedding_model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise

    async def store_memory(
        self,
        memory_id: str,
        memory_type: ChatbotMemoryType,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Store a chatbot memory in Qdrant"""
        try:
            collection_name = f"chatbot_{memory_type.value}"
            
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload={
                            "content": content,
                            **metadata
                        }
                    )
                ],
                wait=True  # Wait for the operation to complete
            )
            logger.info(f"Stored memory in collection {collection_name}: {memory_id}")
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            raise

    async def search_similar_memories(
        self,
        query: str,
        memory_type: ChatbotMemoryType,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar memories in a specific collection"""
        try:
            collection_name = f"chatbot_{memory_type.value}"
            
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)

            # Build filter conditions
            filter_conditions = filter_conditions or {}
            must_conditions = []
            
            for key, value in filter_conditions.items():
                if value is not None:
                    must_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

            # Perform search
            search_filter = models.Filter(must=must_conditions) if must_conditions else None
            
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=0.7  # Only return results with similarity score > 0.7
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "content": point.payload["content"],
                    "metadata": {k: v for k, v in point.payload.items() if k != "content"}
                }
                for point in results
            ]
        except Exception as e:
            logger.error(f"Failed to search memories: {str(e)}")
            raise

    async def search_conversation_context(
        self,
        conversation_id: str,
        memory_type: ChatbotMemoryType,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for conversation context"""
        return await self.search_similar_memories(
            query=conversation_id,
            memory_type=memory_type,
            filter_conditions={"conversation_id": conversation_id},
            limit=limit
        )

    async def search_user_history(
        self,
        user_id: str,
        business_id: str,
        memory_type: ChatbotMemoryType,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for user's conversation history"""
        return await self.search_similar_memories(
            query=user_id,
            memory_type=memory_type,
            filter_conditions={
                "user_id": user_id,
                "business_id": business_id
            },
            limit=limit
        )

    async def delete_memory(
        self,
        memory_id: str,
        memory_type: ChatbotMemoryType
    ):
        """Delete a memory from Qdrant"""
        try:
            collection_name = f"chatbot_{memory_type.value}"
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[memory_id]
                ),
                wait=True  # Wait for the operation to complete
            )
            logger.info(f"Deleted memory from collection {collection_name}: {memory_id}")
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            raise 