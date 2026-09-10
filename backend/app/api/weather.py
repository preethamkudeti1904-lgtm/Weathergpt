from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.weather.service import weather_service
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, AlertsResponse

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh", description="City or place name"),
    lat: Optional[float] = Query(default=None, description="Latitude"),
    lon: Optional[float] = Query(default=None, description="Longitude")
):
    try:
        return await weather_service.get_current_weather(location=location, lat=lat, lon=lon)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather data temporarily unavailable: {str(e)}"
        )

@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    days: int = Query(default=7, ge=1, le=14)
):
    try:
        return await weather_service.get_forecast(location=location, lat=lat, lon=lon, days=days)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Weather forecast temporarily unavailable: {str(e)}"
        )

@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None)
):
    try:
        return await weather_service.get_alerts(location=location, lat=lat, lon=lon)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Alert data temporarily unavailable: {str(e)}"
        )
