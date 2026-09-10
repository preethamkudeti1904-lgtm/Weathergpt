from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.weather.service import weather_service
from app.schemas.climate import ClimateResponse

router = APIRouter(prefix="/climate", tags=["Climate Analysis"])

@router.get("/history", response_model=ClimateResponse)
async def get_climate_history(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None)
):
    try:
        return await weather_service.get_historical_climate(location=location, lat=lat, lon=lon)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Climate analysis temporarily unavailable: {str(e)}"
        )
