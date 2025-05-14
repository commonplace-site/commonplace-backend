from enum import Enum
from typing import Dict, Any
from datetime import datetime

class SourceType(Enum):
    USER = "user"
    GPT = "gpt"
    SYSTEM = "system"
    AALAM = "aalam"

class SourceRegistry:
    _sources: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_source(
        cls,
        source_id: str,
        source_type: SourceType,
        metadata: Dict[str, Any] = None
    ):
        """Register a new data source"""
        cls._sources[source_id] = {
            "type": source_type,
            "registered_at": datetime.utcnow(),
            "metadata": metadata or {}
        }

    @classmethod
    def get_source_info(cls, source_id: str) -> Dict[str, Any]:
        """Get information about a registered source"""
        return cls._sources.get(source_id, {
            "type": SourceType.SYSTEM,
            "registered_at": datetime.utcnow(),
            "metadata": {}
        })

    @classmethod
    def track_submission(
        cls,
        source_id: str,
        content_type: str,
        metadata: Dict[str, Any] = None
    ):
        """Track a content submission from a source"""
        if source_id not in cls._sources:
            cls.register_source(source_id, SourceType.SYSTEM)
            
        source_info = cls._sources[source_id]
        if "submissions" not in source_info:
            source_info["submissions"] = []
            
        source_info["submissions"].append({
            "content_type": content_type,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }) 