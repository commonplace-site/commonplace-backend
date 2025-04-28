from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship



class ScrapingSource(BASE):
    __tablename__ = 'scraping_sources'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Add relationship to ScrapedContent
    contents = relationship("ScrapedContent", back_populates="source")