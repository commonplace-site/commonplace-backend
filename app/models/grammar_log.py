from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, UUID, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class GrammarLog(BASE):
    __tablename__= 'grammar_logs'

    id=Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="grammar_logs")
    sentence =Column(Text,nullable=False)
    grammar_issue=Column(Text)
    feedback=Column(Text)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)