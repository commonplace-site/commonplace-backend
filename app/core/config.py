from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
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