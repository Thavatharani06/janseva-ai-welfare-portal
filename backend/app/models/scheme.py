import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class SchemeCategory(Base):
    __tablename__ = "scheme_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    name_ta = Column(String(100), nullable=True)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    schemes = relationship("Scheme", back_populates="category")

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String(36), ForeignKey("scheme_categories.id"), nullable=True)
    title = Column(String(255), index=True, nullable=False)
    title_ta = Column(String(255), index=True, nullable=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., PMAY-U, PM-KISAN, KMT
    ministry = Column(String(255), nullable=True)
    official_website = Column(String(255), nullable=True)
    helpline_number = Column(String(50), nullable=True)

    # Explanation Modes
    legal_summary = Column(Text, nullable=False)
    simple_summary = Column(Text, nullable=False)
    eli10_summary = Column(Text, nullable=False)

    # Deterministic Rule Limits
    min_age = Column(Integer, default=0)
    max_age = Column(Integer, default=120)
    max_income = Column(Float, nullable=True)  # Max annual income limit in INR
    gender_restriction = Column(String(50), nullable=True)  # All | Female | Male
    disability_required = Column(Boolean, default=False)
    target_community = Column(String(100), nullable=True)  # All | SC/ST | OBC | General
    target_occupation = Column(String(100), nullable=True)  # All | Farmer | Unorganized | Student
    state_district_scope = Column(String(100), default="All India")

    required_documents = Column(JSON, nullable=True)  # ["Aadhaar", "Community Cert", "Income Cert"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("SchemeCategory", back_populates="schemes")
    aliases = relationship("SchemeAlias", back_populates="scheme", cascade="all, delete-orphan")
    eligibility_rules = relationship("EligibilityRule", back_populates="scheme", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="scheme", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="scheme")

class SchemeAlias(Base):
    __tablename__ = "scheme_aliases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id"), nullable=False)
    alias = Column(String(255), index=True, nullable=False)
    language_code = Column(String(10), default="en")  # en | ta | hi

    scheme = relationship("Scheme", back_populates="aliases")

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id"), nullable=False)
    rule_key = Column(String(100), nullable=False)  # e.g., 'income', 'age', 'community'
    operator = Column(String(20), nullable=False)  # '<=', '>=', '==', 'in'
    rule_value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    scheme = relationship("Scheme", back_populates="eligibility_rules")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id"), nullable=True)
    title = Column(String(255), nullable=False)
    go_number = Column(String(100), nullable=True)  # Government Order Number
    document_type = Column(String(50), default="GO")  # GO | GUIDELINE | FORM
    file_path = Column(String(512), nullable=True)
    ocr_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scheme = relationship("Scheme", back_populates="documents")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_content = Column(Text, nullable=False)
    page_number = Column(Integer, default=1)
    metadata_json = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="embeddings")
