from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class GrammarLog(BASE):
    __tablename__= 'grammar_logs'

    id=Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    sentence =Column(Text,nullable=False)
    grammar_issue=Column(Text)
    feedback=Column(Text)
    created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)