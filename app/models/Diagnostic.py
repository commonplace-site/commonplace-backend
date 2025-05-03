from sqlalchemy import Column, Integer, String, Text
from app.db.database import BASE

class DiagnosticResult(BASE):
    __tablename__ = "diagnostic_results"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    score = Column(Integer)
    level = Column(String)
    learning_content = Column(Text)