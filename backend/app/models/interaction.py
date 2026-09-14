import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    explanation_level = Column(String(20), default="simple")  # legal | simple | eli10
    response = Column(Text, nullable=False)
    sources_json = Column(JSON, nullable=True)
    scam_flagged = Column(Boolean, default=False)
    scam_reason = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.92)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_histories")

class VoiceConversation(Base):
    __tablename__ = "voice_conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    language = Column(String(10), default="ta")
    audio_url = Column(String(512), nullable=True)
    transcript = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    tts_url = Column(String(512), nullable=True)
    confidence_score = Column(Float, default=0.90)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="voice_conversations")

class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=120.0)
    confidence_score = Column(Float, default=0.90)
    error_log = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # info | alert | application_update
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    chat_id = Column(String(36), nullable=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
