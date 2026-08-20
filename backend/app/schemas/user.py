import uuid
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class UserOut(BaseModel):
    id: uuid.UUID
    phone_number: str
    full_name: str
    preferred_language: str
    fcm_token: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferred_language: Optional[str] = Field(None)
    fcm_token: Optional[str] = None

    @field_validator("preferred_language")
    @classmethod
    def validate_lang(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["mr", "hi", "en"]:
            raise ValueError("Language must be one of 'mr' (Marathi), 'hi' (Hindi), or 'en' (English).")
        return v
