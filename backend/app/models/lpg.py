import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class LPGConnection(Base):
    __tablename__ = "lpg_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    consumer_id_masked = Column(String(50), nullable=True)  # e.g. XXXX-XXXX-1234
    consumer_id_hash = Column(String(128), nullable=True)   # Salted SHA-256
    provider = Column(String(100), nullable=True)           # IOCL (Indane) | BPCL (Bharatgas) | HPCL (HP Gas)
    distributor_name = Column(String(255), nullable=True)
    connection_type = Column(String(50), nullable=True)    # PMUY (Ujjwala) | GENERAL
    connection_status = Column(String(50), default="active", nullable=False) # active | inactive | NOT_CONFIGURED | UNAVAILABLE
    
    subsidy_eligible = Column(Boolean, default=True)
    last_refill_date = Column(String(50), nullable=True)
    refill_count = Column(Integer, default=0)
    subsidy_received_amount = Column(Float, nullable=True)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="lpg_connection")
