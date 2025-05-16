from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._init_collection()

    def _init_collection(self):
        """Initialize the Qdrant collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if "memories" not in collection_names:
            self.client.create_collection(
                collection_name="memories",
                vectors_config=models.VectorParams(
                    size=384,  # Size of the embedding vector
                    distance=models.Distance.COSINE
                )
            )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the sentence transformer model"""
        return self.embedding_model.encode(text).tolist()

    async def store_memory(
        self,
        memory_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Store a memory in Qdrant"""
        self.client.upsert(
            collection_name="memories",
            points=[
                models.PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload=metadata
                )
            ]
        )

    async def search(
        self,
        query_embedding: List[float],
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar memories in Qdrant"""
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
            collection_name="memories",
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "metadata": point.payload
            }
            for point in results
        ]

    async def delete_memory(self, memory_id: str):
        """Delete a memory from Qdrant"""
        self.client.delete(
            collection_name="memories",
            points_selector=models.PointIdsList(
                points=[memory_id]
            )
        ) 