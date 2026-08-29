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
    current_risk_level: str = "LOW"
    current_risk_score: float = 20.0
    active_alerts_count: int = 0
    citizen_reports_count: int = 0
    unverified_reports_count: int = 0
    distress_signals_count: int = 0
    affected_roads_count: int = 0
    operational_safe_zones_count: int = 0
    source_tag: str = "SIMULATED_DEMO_DATA"
