from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.location import SavedLocation
from app.schemas.location import LocationSearchItem, SavedLocationCreate, SavedLocationOut
from app.weather.service import weather_service

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/search", response_model=List[LocationSearchItem])
async def search_locations(q: str = Query(..., min_length=1, description="Location name or partial search term")):
    return await weather_service.geocode(q)

@router.get("/reverse")
async def reverse_geocode(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    return await weather_service.reverse_geocode(lat=lat, lon=lon)

@router.get("/saved", response_model=List[SavedLocationOut])
def get_saved_locations(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    if not user:
        # Default preset locations for guest preview
        return [
            SavedLocationOut(
                id=1,
                user_id=0,
                location_name="Guntur",
                state="Andhra Pradesh",
                country="India",
                latitude=16.3067,
                longitude=80.4365,
                is_default=True
            ),
            SavedLocationOut(
                id=2,
                user_id=0,
                location_name="Hyderabad",
                state="Telangana",
                country="India",
                latitude=17.3850,
                longitude=78.4867,
                is_default=False
            ),
            SavedLocationOut(
                id=3,
                user_id=0,
                location_name="Vijayawada",
                state="Andhra Pradesh",
                country="India",
                latitude=16.5062,
                longitude=80.6480,
                is_default=False
            )
        ]
    return db.query(SavedLocation).filter(SavedLocation.user_id == user.id).all()

@router.post("/save", response_model=SavedLocationOut)
def save_location(
    loc_in: SavedLocationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if loc_in.is_default:
        db.query(SavedLocation).filter(SavedLocation.user_id == user.id).update({"is_default": False})

    loc = SavedLocation(
        user_id=user.id,
        location_name=loc_in.location_name,
        state=loc_in.state,
        country=loc_in.country or "India",
        latitude=loc_in.latitude,
        longitude=loc_in.longitude,
        is_default=loc_in.is_default or False
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return SavedLocationOut.model_validate(loc)

@router.delete("/{location_id}")
def delete_saved_location(
    location_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    loc = db.query(SavedLocation).filter(SavedLocation.id == location_id, SavedLocation.user_id == user.id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Saved location not found")
    db.delete(loc)
    db.commit()
    return {"message": "Location removed from saved list"}
