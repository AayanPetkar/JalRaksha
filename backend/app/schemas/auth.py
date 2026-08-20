import re
from pydantic import BaseModel, Field, field_validator

class UserRegister(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    full_name: str = Field(..., min_length=2, max_length=100, example="Aayan Sharma")
    preferred_language: str = Field(default="mr", example="mr")
    password: str = Field(..., min_length=6, example="Secret123!")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean_v = re.sub(r"\s+", "", v)
        if not re.match(r"^\+?[1-9]\d{7,14}$", clean_v):
            raise ValueError("Invalid phone number format. Must be E.164 compatible.")
        return clean_v

    @field_validator("preferred_language")
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in ["mr", "hi", "en"]:
            raise ValueError("Language must be one of 'mr' (Marathi), 'hi' (Hindi), or 'en' (English).")
        return v


class UserLogin(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    password: str = Field(..., example="Secret123!")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    phone_number: str
    full_name: str
    preferred_language: str
