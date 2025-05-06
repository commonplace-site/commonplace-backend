from pydantic import BaseSettings

class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID:str
    AWS_SECRET_ACCESS_KEY:str
    AWS_REGION:str
    AWS_BUCKET_NAME:str
    class Config:
        env_file=".env"