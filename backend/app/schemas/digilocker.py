from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DigiLockerConnectUrlResponse(BaseModel):
    authorization_url: str
    state: str
    enabled: bool
    environment: str

class DigiLockerCallbackRequest(BaseModel):
    code: str
    state: str

class DigiLockerDocumentResponse(BaseModel):
    id: str
    doc_type: str
    name: str
    uri: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    verification_status: str

    class Config:
        from_attributes = True

class DigiLockerStatusResponse(BaseModel):
    is_connected: bool
    connection_status: str  # connected | disconnected | expired | not_configured
    connected_at: Optional[datetime] = None
    provider: str = "digilocker"
    verified_documents_count: int = 0
    documents: List[DigiLockerDocumentResponse] = []
    message: str
