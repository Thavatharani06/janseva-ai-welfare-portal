import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class DigiLockerConnection(Base):
    __tablename__ = "digilocker_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    provider = Column(String(50), default="digilocker", nullable=False)
    external_user_id = Column(String(255), nullable=True)
    connection_status = Column(String(50), default="connected", nullable=False)  # connected | disconnected | expired | not_configured
    
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)

    connected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="digilocker_connection")
    documents = relationship("DigiLockerDocument", back_populates="connection", cascade="all, delete-orphan")


class DigiLockerDocument(Base):
    __tablename__ = "digilocker_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    connection_id = Column(String(36), ForeignKey("digilocker_connections.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    doc_type = Column(String(100), nullable=False)  # AADHAAR | DRIVING_LICENSE | INCOME_CERTIFICATE | CASTE_CERTIFICATE | DOMICILE_CERTIFICATE | DISABILITY_CERTIFICATE | CLASS_X_MARKSHEET
    name = Column(String(255), nullable=False)
    uri = Column(String(255), nullable=True)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    
    # Store normalized non-sensitive extracted metadata
    extracted_data = Column(Text, nullable=True)  # JSON string
    verification_status = Column(String(50), default="VERIFIED_OFFICIAL", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    connection = relationship("DigiLockerConnection", back_populates="documents")
    user = relationship("User", back_populates="digilocker_documents")
