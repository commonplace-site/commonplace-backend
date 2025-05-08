from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship




class ScrapingSource(BASE):
    __tablename__ = 'scraped_contents'

    id = Column(BigInteger, primary_key=True)
    source_id = Column(BigInteger, ForeignKey('scraping_sources.id'), nullable=False, index=True)
    title = Column(String(255))                  # Title of the content
    url = Column(String(500))                    # URL of the scraped content
    source = Column(String(255))                 # Source domain or origin
    author = Column(String(255))                 # Author's name
    type = Column(String(100))                   # Type of content (e.g., article, video)
    tags = Column(Text)                          # Comma-separated tags or serialized list
    language = Column(String(50))                # Language of content (e.g., 'en')
    level = Column(String(50))                   # Difficulty level or audience level
    summary = Column(Text)                       # Short summary of the content
    full_text = Column(Text)                     # Full scraped text
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)   # Original publish date
    scraped_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)   # When it was scraped

    scraping_source = relationship("ScrapingSource", back_populates="contents")
    