from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryResponse(BaseModel):
    id: str
    name: str
    name_ta: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class AliasResponse(BaseModel):
    id: str
    alias: str
    language_code: str

    class Config:
        from_attributes = True

class SchemeResponse(BaseModel):
    id: str
    category_id: Optional[str] = None
    title: str
    title_ta: Optional[str] = None
    code: str
    ministry: Optional[str] = None
    official_website: Optional[str] = None
    helpline_number: Optional[str] = None
    legal_summary: str
    simple_summary: str
    eli10_summary: str
    min_age: int
    max_age: int
    max_income: Optional[float] = None
    gender_restriction: Optional[str] = None
    target_community: Optional[str] = None
    target_occupation: Optional[str] = None
    state_district_scope: Optional[str] = None
    required_documents: Optional[List[str]] = None
    category: Optional[CategoryResponse] = None
    aliases: List[AliasResponse] = []

    class Config:
        from_attributes = True

class AliasResolveResponse(BaseModel):
    query: str
    matched_scheme: Optional[SchemeResponse] = None
    confidence: float
    matched_alias: str
