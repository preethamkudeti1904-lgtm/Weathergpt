from typing import Optional, Union
from fastapi import APIRouter, HTTPException, Query
from app.weather.service import weather_service
from app.services.climate.historical_year_service import historical_year_service
from app.schemas.climate import ClimateResponse, HistoricalYearResponse

router = APIRouter(prefix="/climate", tags=["Climate Analysis"])

@router.get("/historical", response_model=HistoricalYearResponse)
async def get_historical_climate_year(
    location: Optional[str] = Query(default=None),
    latitude: Optional[float] = Query(default=None),
    longitude: Optional[float] = Query(default=None),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    year: int = Query(default=2023, ge=1950, le=2025)
):
    """
    Retrieves location-specific historical meteorological data for a specific calendar year.
    Returns 12 monthly observations (Jan-Dec) and annual summary metrics calculated strictly from that year's data.
    """
    try:
        resolved_lat = latitude if latitude is not None else lat
        resolved_lon = longitude if longitude is not None else lon

        if resolved_lat is not None and not (-90.0 <= resolved_lat <= 90.0):
            raise HTTPException(status_code=400, detail="Latitude must be between -90.0 and 90.0 degrees.")
        if resolved_lon is not None and not (-180.0 <= resolved_lon <= 180.0):
            raise HTTPException(status_code=400, detail="Longitude must be between -180.0 and 180.0 degrees.")
        if not (1950 <= year <= 2026):
            raise HTTPException(status_code=400, detail=f"Year {year} is out of valid range (1950-2026).")

        lat_r, lon_r, loc_display = await weather_service.resolve_coordinates(location or "Nagavarappadu", resolved_lat, resolved_lon)
        
        return await historical_year_service.get_year_data(
            lat=lat_r,
            lon=lon_r,
            location_name=loc_display,
            year=year
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve historical climate data: {str(e)}"
        )

@router.get("/history")
async def get_climate_history(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh"),
    latitude: Optional[float] = Query(default=None),
    longitude: Optional[float] = Query(default=None),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    year: Optional[int] = Query(default=None)
):
    """
    Retrieves either:
    1. Single-year historical meteorological data if 'year' is provided.
    2. Authoritative IMD 30-year climatological normals (1991–2020) if 'year' is omitted.
    """
    try:
        resolved_lat = latitude if latitude is not None else lat
        resolved_lon = longitude if longitude is not None else lon
        lat_r, lon_r, loc_display = await weather_service.resolve_coordinates(location, resolved_lat, resolved_lon)

        if year is not None:
            return await historical_year_service.get_year_data(
                lat=lat_r,
                lon=lon_r,
                location_name=loc_display,
                year=year
            )
        return await weather_service.get_historical_climate(location=loc_display, lat=lat_r, lon=lon_r)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Climate analysis temporarily unavailable: {str(e)}"
        )
