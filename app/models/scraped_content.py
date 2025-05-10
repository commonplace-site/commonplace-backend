# from datetime import datetime
# from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
# from app.db.database import BASE
# from sqlalchemy.orm import relationship


# class ScrapedContent(BASE):
#     __tablename__ = 'scraped_contents'

#     id = Column(BigInteger, primary_key=True)
#     source_id = Column(BigInteger, ForeignKey('scraping_sources.id'), nullable=False, index=True)
#     title = Column(String(255))
#     summary = Column(Text)
#     full_text = Column(Text)
#     level_flag = Column(String(50))
#     created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

#     source = relationship("ScrapingSource", back_populates="contents")
