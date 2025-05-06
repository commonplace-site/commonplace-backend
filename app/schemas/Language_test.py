from typing import Optional
from pydantic import BaseModel


class LanguageTestSection(BaseModel):
    section: str  # P1, P2, or P3
    question_type: str
    topic: str
    language_level: str
    rubric_score: Optional[float]