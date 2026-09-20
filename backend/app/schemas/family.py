from pydantic import BaseModel
from typing import Optional

class FamilyMemberCreate(BaseModel):
    full_name: str
    relationship_type: str  # spouse | child | parent | sibling | other
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    is_dependent: Optional[bool] = True

class FamilyMemberResponse(BaseModel):
    id: str
    full_name: str
    relationship_type: str
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    is_dependent: bool

    class Config:
        from_attributes = True
