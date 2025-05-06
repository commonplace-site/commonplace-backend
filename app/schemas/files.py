from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class FileOut(BaseModel):
    id: str
    filename: str
    s3_url: str
    audio_type:str
    file_url:str
    transcription_text:Optional[str]
    topic:str
    question_type:str
    language_level:str
    rubric_score:Optional[float]
    uploaded_by: str
    created_at:datetime
     
    class config:
        orm_mode=True

class AudioTag(BaseModel):
    s3_key: str
    topic: str
    level: int
    question_type: str
    rubric_score: int