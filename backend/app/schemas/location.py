from typing import Optional
from pydantic import BaseModel

class LocationSearchItem(BaseModel):
    name: str
    state: Optional[str] = None
    country: str = "India"
    latitude: float
    longitude: float
    display_name: str

class SavedLocationCreate(BaseModel):
    location_name: str
    state: Optional[str] = None
    country: Optional[str] = "India"
    latitude: float
    longitude: float
    is_default: Optional[bool] = False

class SavedLocationOut(BaseModel):
    id: int
    user_id: int
    location_name: str
    state: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    is_default: bool

    class Config:
        from_attributes = True
