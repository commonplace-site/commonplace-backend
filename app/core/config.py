from pydantic_settings import BaseSettings
from enum import Enum

class ModelSource(str, Enum):
    AALAM = "aalam"
    TEACHER = "teacher"
    MODULE = "module"

class Settings(BaseSettings):
    # AWS settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str
    
    # Redis settings (all optional with defaults)
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: int | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_SSL: bool = False
    
    # Audit logging settings
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # OpenAI settings
    OPENAI_API_KEY: str
    
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
    DB_USERNAME: str
    DB_HOST: str
    DB_PORT: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DATABASE_URL: str
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # This allows for case-insensitive env var matching

# Create settings instance
settings = Settings()