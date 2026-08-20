import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class LocationCreate(BaseModel):
    latitude: float = Field(..., example=19.0760)
    longitude: float = Field(..., example=72.8777)
    accuracy_meters: Optional[float] = Field(None, example=12.5)

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0 degrees.")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0 degrees.")
        return v


class LocationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
