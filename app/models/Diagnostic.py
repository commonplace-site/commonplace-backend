from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from app.db.database import BASE

class DiagnosticResult(BASE):
    __tablename__ = "diagnostic_results"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    score = Column(Integer)
    level = Column(String)
    learning_content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
