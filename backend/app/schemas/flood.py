import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RiskFactorOut(BaseModel):
    factor_key: str
    contribution_percentage: float
    value: Optional[float] = None
    unit: Optional[str] = None
    description_en: str
    description_mr: Optional[str] = None
    description_hi: Optional[str] = None

    class Config:
        from_attributes = True


class FloodImpactOut(BaseModel):
    affected_houses_count: int = 0
    affected_farmland_acres: float = 0.0
    affected_schools_count: int = 0
    affected_hospitals_count: int = 0


class FloodRiskOut(BaseModel):
    id: uuid.UUID
    village_id: uuid.UUID
    village_name: str = "Kurla, Mumbai"
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(..., example="CRITICAL") # 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    confidence_score: float = 0.85
    data_freshness_minutes: int = 5
    source_tag: str = "SIMULATED_DEMO_DATA"
    is_demo_data: bool = True
    disclaimer: str = "AI prediction; not an official government warning."
    local_impact: FloodImpactOut
    main_risk_factors: List[RiskFactorOut] = []
    evaluated_at: datetime

    class Config:
        from_attributes = True


class FloodRiskWhyOut(BaseModel):
    risk_id: uuid.UUID
    village_id: uuid.UUID
    risk_score: float
    risk_level: str
    confidence: str = "High"
    data_updated: str = "5 minutes ago"
    source_tag: str = "SIMULATED_DEMO_DATA"
    contributing_factors: List[RiskFactorOut]
