from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, BigInteger, Boolean, Column, ForeignKey, Integer,String, Text
from app.db.database import BASE
from sqlalchemy.orm import relationship


class User(BASE):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)

    profile = relationship("Profile", back_populates='user', uselist=False)
    # vocabulary_logs =relationship("VocabularyLog",back_populates="user")
    vocabulary_logs = relationship("VocabularyLog", back_populates="user")
    grammar_logs = relationship("GrammarLog", back_populates="user")
    pronunciation_logs = relationship("PronunciationLog", back_populates="user")
    comprehension_logs = relationship("ComprehensionLog", back_populates="user")
    roleplay_sessions=relationship("RolePlaySession", back_populates="user")
    audio_files = relationship("AudioFile", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")
    role_id = Column(BigInteger, ForeignKey('roles.id'))
    role = relationship("Role", back_populates="users")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# class Profile(BASE):
#     __tablename__ = 'profiles'

#     id = Column(BigInteger, primary_key=True, index=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False,index=True)
#     name = Column(String(100))
#     avatar_url = Column(Text)
#     bio = Column(Text)
#     native_language = Column(String(50))
#     target_language = Column(String(50))
#     user = relationship("User", back_populates="profile")
#     created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
#     updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# class VocabularyLog(BASE):
#     __tablename__ = 'vocabulary_logs'

#     id = Column(BigInteger, primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     word = Column(String(100), nullable=False)
#     meaning = Column(String(255))
#     source = Column(String(100))
#     added_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


# class GrammarLog(BASE):
#     __tablename__= 'grammar_logs'

#     id=Column(BigInteger, primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     sentence =Column(Text,nullable=False)
#     grammar_issue=Column(Text)
#     feedback=Column(Text)
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)


# class PronunciationLog(BASE):
#     __tablename__ ='pronunciation_logs'
#     id=Column(BigInteger,primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     original_text=Column(Text)
#     audio_file_url=Column(Text)
#     ai_feedback=Column(Text)
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)

# class ComprehensionLog(BASE):
#     __tablename__ = 'comprehension_logs'
#     id=Column(BigInteger,primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     material=Column(Text)
#     comprehension_score=Column(Integer)
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)

# class Lesson(BASE):
#     __tablename__ = 'lessons'

#     id=Column(BigInteger,primary_key=True)
#     title=Column(String(255),nullable=False)
#     description=Column(Text)
#     content_url=Column(Text)
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)
#     updated_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)

# class RolePlaySession(BASE):
#     __tablename__='roleplay_sessions'

#     id=Column(BigInteger,primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     scenario=Column(String(255)) 
#     avatar_used=Column(String(100))
#     recording_url =Column(Text)
#     feedback=Column(Text)
#     created_at = Column(TIMESTAMP(timezone=True),default=datetime.utcnow)

# class AudioFile(BASE):

#     __tablename__ = 'audio_files'
#     id=Column(BigInteger,primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     audio_type=Column(String(50))
#     file_url=Column(Text,nullable=False)
#     transcription_text=Column(Text)
#     created_at= Column(TIMESTAMP(timezone=True),default=datetime.utcnow)


# class FeedbackLog(BASE):
#     __tablename__ = 'feedback_logs'

#     id=Column(BigInteger,primary_key=True)
#     user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
#     source = Column(String(50))
#     feedback_text=Column(Text)
#     related_module=Column(String(100))
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)

# class Integration(BASE):
#     __tablename__ = 'integrations'

#     id=Column(BigInteger, primary_key=True)
#     name= Column(String(100), nullable=False)
#     type = Column(String(50))
#     status=Column(Boolean,default=True)
#     usage_count= Column(BigInteger, default=0)
#     usage_limit = Column(BigInteger)
#     base_url=Column(Text)
#     api_key=Column(Text)
#     config=Column(JSON)    
#     last_check_at=Column(TIMESTAMP(timezone=True))
#     created_at=Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


# class LearningModule(BASE):
#     __tablename__ = 'learning_modules'

#     id= Column(BigInteger,primary_key=True)
#     name=Column(String(100),nullable=False)
#     status=Column(String(50),default='pending')
#     active_user=Column(Integer,default=0)
#     last_updated_at =Column(TIMESTAMP(timezone=True))
#     created_at=Column(TIMESTAMP(timezone=True),default=datetime.utcnow)


# class ScrapingSource(BASE):
#     __tablename__ = 'scraping_sources'

#     id = Column(BigInteger, primary_key=True)
#     name = Column(String(100), nullable=False)
#     source_url = Column(Text, nullable=False)
#     active = Column(Boolean, default=True)
#     created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
#     # Add relationship to ScrapedContent
#     contents = relationship("ScrapedContent", back_populates="source")

# class ScrapedContent(BASE):
#     __tablename__ = 'scraped_contents'

#     id = Column(BigInteger, primary_key=True)
#     source_id = Column(BigInteger, ForeignKey('scraping_sources.id'), nullable=False, index=True)
#     title = Column(String(255))
#     summary = Column(Text)
#     full_text = Column(Text)
#     level_flag = Column(String(50))
#     created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
#     # Add relationship to ScrapingSource
#     source = relationship("ScrapingSource", back_populates="contents")
