from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer, String, Text, func
from app.db.database import BASE
from sqlalchemy.orm import relationship


class ScrapingSource(BASE):
    __tablename__ = 'scraping_sources'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    source_url = Column(Text, nullable=False)
    active = Column(Boolean, default=True, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    contents = relationship("ScrapedContent", back_populates="source")
