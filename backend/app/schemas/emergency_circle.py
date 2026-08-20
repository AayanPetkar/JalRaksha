import uuid
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class EmergencyCirclePreferenceOut(BaseModel):
    notify_on_prepare: bool = False
    notify_on_critical: bool = True
    notify_on_distress: bool = True

    class Config:
        from_attributes = True


class EmergencyCirclePreferenceCreate(BaseModel):
    notify_on_prepare: bool = False
    notify_on_critical: bool = True
    notify_on_distress: bool = True


class EmergencyContactCreate(BaseModel):
    contact_name: str = Field(..., min_length=2, max_length=100, example="Father")
    contact_phone: str = Field(..., example="+919811122233")
    relationship: Optional[str] = Field(None, example="Father")
    preferences: Optional[EmergencyCirclePreferenceCreate] = None


class EmergencyContactUpdate(BaseModel):
    contact_name: Optional[str] = Field(None, min_length=2, max_length=100)
    contact_phone: Optional[str] = None
    relationship: Optional[str] = None
    preferences: Optional[EmergencyCirclePreferenceCreate] = None


class EmergencyContactOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    contact_name: str
    contact_phone: str
    relationship: Optional[str] = None
    is_verified: bool = False
    preferences: Optional[EmergencyCirclePreferenceOut] = None

    class Config:
        from_attributes = True


class ImSafeRequest(BaseModel):
    latitude: Optional[float] = Field(None, example=19.0760)
    longitude: Optional[float] = Field(None, example=72.8777)
    custom_message: Optional[str] = Field(None, example="Reached Community Hall safely.")


class NeedHelpRequest(BaseModel):
    latitude: float = Field(..., example=19.0760)
    longitude: float = Field(..., example=72.8777)
    distress_type: str = Field(default="TRAPPED_WATER", example="TRAPPED_WATER")
