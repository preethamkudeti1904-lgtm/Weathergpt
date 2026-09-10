import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class UserPreferenceBase(BaseModel):
    theme: Optional[str] = "system"
    language: Optional[str] = "en"
    temperature_unit: Optional[str] = "celsius"
    wind_unit: Optional[str] = "kmh"
    severe_alerts: Optional[bool] = True
    forecast_notifications: Optional[bool] = True
    sms_alerts_enabled: Optional[bool] = False
    sms_alert_categories: Optional[str] = '["Severe Weather", "Flood", "Cyclone", "Thunderstorm", "Extreme Rain", "Heatwave"]'

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceOut(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str  # Required phone number
    phone_country_code: Optional[str] = "+91"
    password: str
    confirm_password: Optional[str] = None
    country: Optional[str] = "India"
    state: Optional[str] = "Andhra Pradesh"
    preferred_language: Optional[str] = "en"
    user_type: Optional[str] = "General User"
    default_location: Optional[str] = "Guntur, Andhra Pradesh"

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Password must be a string.")
        byte_len = len(v.encode("utf-8"))
        if byte_len > 72:
            raise ValueError("Password is too long. Please use a password of 72 UTF-8 bytes or fewer.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserTypeUpdate(BaseModel):
    user_type: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    user_type: str
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = "+91"
    phone_verified: bool = False
    phone_verified_at: Optional[datetime.datetime] = None
    country: Optional[str] = "India"
    state: Optional[str] = "Andhra Pradesh"
    preferred_language: str
    default_location: Optional[str] = None
    created_at: datetime.datetime
    preferences: Optional[UserPreferenceOut] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

