import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    full_name = Column(String(255), nullable=False)
    relationship_type = Column(String(50), nullable=False) # spouse | child | parent | sibling | other
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    occupation = Column(String(100), nullable=True)
    is_dependent = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="family_members")
