import uuid
from typing import Optional, List
from pydantic import BaseModel, Field

class SafeZoneOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str # 'OFFICIAL_SHELTER', 'RELIEF_CENTER', 'COMMUNITY_HALL', 'EVACUATION_CENTER'
    capacity: int
    current_occupancy: int
    is_active: bool
    is_verified: bool
    distance_meters: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = None
    district: Optional[str] = None
    source_tag: str = "OFFICIAL_DATA"

    class Config:
        from_attributes = True
