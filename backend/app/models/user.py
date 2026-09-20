import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="citizen", nullable=False)  # citizen | admin
    language_preference = Column(String(10), default="ta", nullable=False)  # ta | en | hi

    # Demographics for eligibility & auto-fill
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # male | female | other
    annual_income = Column(Float, nullable=True)
    district = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    disability_status = Column(Boolean, default=False)
    community = Column(String(50), nullable=True)  # General | OBC | SC | ST | MBC
    marital_status = Column(String(50), nullable=True)  # Single | Married | Widowed | Divorced
    education_level = Column(String(100), nullable=True)
    family_members_count = Column(Integer, default=1)
    property_owner = Column(Boolean, default=False)

    # Security & MFA & Journey State
    mfa_secret = Column(String(255), nullable=True)
    is_mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_recovery_codes = Column(Text, nullable=True)
    is_onboarded = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    voice_conversations = relationship("VoiceConversation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
