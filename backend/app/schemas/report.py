import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CitizenReportCreate(BaseModel):
    latitude: float = Field(..., example=19.0780)
    longitude: float = Field(..., example=72.8790)
    description: Optional[str] = Field(None, example="Water logging near bridge")
    disaster_category: str = Field(default="WATER_LOGGING", example="ROAD_BLOCKED")
    photo_url: Optional[str] = Field(None, example="https://storage.jalraksha.org/reports/img_1.jpg")
    voice_note_url: Optional[str] = None

    @field_validator("disaster_category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid_cats = ["WATER_LOGGING", "ROAD_BLOCKED", "BRIDGE_SUBMERGED", "TRAPPED_PERSON", "OTHER"]
        if v not in valid_cats:
            raise ValueError(f"Category must be one of {valid_cats}")
        return v


class CitizenReportOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    latitude: float
    longitude: float
    description: Optional[str] = None
    disaster_category: str
    photo_url: Optional[str] = None
    voice_note_url: Optional[str] = None
    verification_status: str = "UNVERIFIED"
    source_tag: str = "CITIZEN_REPORT"
    created_at: datetime

    class Config:
        from_attributes = True
