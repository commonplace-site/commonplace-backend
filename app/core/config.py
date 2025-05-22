from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class ModelSource(str, Enum):
    AALAM = "aalam"
    TEACHER = "teacher"
    MODULE = "module"

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Commonplace Backend"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    

    Notion: str
    synthesia: str
    supabase: str
    ALGORITHM: str


    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # AWS Settings (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    
    # Supabase Settings (Optional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Database Settings (Optional)
    DB_USERNAME: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_DATABASE: Optional[str] = None
    
    # Qdrant Settings
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_TIMEOUT: float = float(os.getenv("QDRANT_TIMEOUT", "10.0"))
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Redis settings (all optional with defaults)
    REDIS_DB: Optional[int] = None
    REDIS_SSL: bool = False
    
    # Audit logging settings
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Aalam specific settings
    AALAM_MODEL: str = "gpt-4"
    AALAM_DEFAULT_CONTEXT: str = "speak"
    AALAM_DEFAULT_VOICE: str = "zh-CN-XiaoxiaoNeural"
    AALAM_DEFAULT_LANGUAGE: str = "zh-CN"
    AALAM_DEFAULT_AUDIO_FORMAT: str = "mp3"
    AALAM_TEMP_DIR: str = "temp_audio"
    
    # Service endpoints
    ROOM_127_ENDPOINT: str
    CODEX_ENDPOINT: str
    SUSPENSE_QUEUE_ENDPOINT: str
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    
    # Qdrant
    QDRANT_HTTP_PORT: int = 6334
    QDRANT_STORAGE_PATH: str = "./qdrant_storage"
    QDRANT_SNAPSHOTS_PATH: str = "./qdrant_snapshots"
    QDRANT_LOGS_PATH: str = "./qdrant_logs"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Security
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    
    # Other settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()