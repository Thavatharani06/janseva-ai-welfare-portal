import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    scheme_id = Column(String(36), ForeignKey("schemes.id"), nullable=False)
    status = Column(String(50), default="draft")  # draft | documents_pending | form_generated | submitted
    journey_step = Column(String(50), default="eligibility_verified")
    form_data = Column(JSON, nullable=True)
    missing_docs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")
    uploaded_documents = relationship("UploadedDocument", back_populates="application", cascade="all, delete-orphan")
    generated_form = relationship("GeneratedForm", back_populates="application", uselist=False, cascade="all, delete-orphan")

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # Aadhaar | Community Cert | Income Cert
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    ocr_extracted_text = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="uploaded_documents")

class GeneratedForm(Base):
    __tablename__ = "generated_forms"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    pdf_path = Column(String(512), nullable=False)
    form_fields = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="generated_form")
