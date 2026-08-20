import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class DistressEventOut(BaseModel):
    user_id: uuid.UUID
    user_name: str
    user_phone: str
    latitude: float
    longitude: float
    distress_type: str
    created_at: datetime


class AdminOverviewOut(BaseModel):
    active_alert_level: str = "CRITICAL"
    total_affected_villages: int = 1
    total_population_exposed: int = 14200
    unverified_reports_count: int = 1
    active_distress_signals_count: int = 1
