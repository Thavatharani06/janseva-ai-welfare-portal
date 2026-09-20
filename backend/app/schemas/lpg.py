from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LPGBindRequest(BaseModel):
    consumer_id: str
    provider: str  # IOCL (Indane) | BPCL (Bharatgas) | HPCL (HP Gas)

class LPGStatusResponse(BaseModel):
    is_connected: bool
    status: str  # active | inactive | NOT_CONFIGURED | UNAVAILABLE | ERROR
    consumer_id_masked: Optional[str] = None
    provider: Optional[str] = None
    distributor_name: Optional[str] = None
    connection_type: Optional[str] = None
    subsidy_eligible: Optional[bool] = None
    last_refill_date: Optional[str] = None
    refill_count: Optional[int] = 0
    subsidy_received_amount: Optional[float] = None
    last_updated: Optional[datetime] = None
    message: str
