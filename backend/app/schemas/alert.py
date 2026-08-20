import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AlertOut(BaseModel):
    id: uuid.UUID
    village_id: uuid.UUID
    alert_level: str # 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    title: str
    message_en: str
    message_mr: Optional[str] = None
    message_hi: Optional[str] = None
    source_tag: str = "OFFICIAL_DATA"
    issued_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
