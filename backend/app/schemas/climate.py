from typing import List, Optional
from pydantic import BaseModel

class ClimateTrendPoint(BaseModel):
    label: str  # Month name: January - December
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    total_rainfall: float
    rainfall_days: int

class ClimateResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    period: str = "2021 - 2023"  # Standard authoritative baseline
    historical_period: str = "2021-01-01 to 2023-12-31 (ERA5 High-Resolution Reanalysis)"
    parameter: str = "all"  # "temperature", "rainfall", "all"
    data: List[ClimateTrendPoint]
    annual_mean_temp: float
    annual_total_rainfall: float
    wettest_month: str
    warmest_month: str
    rain_day_threshold_mm: float = 1.0
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    source: str = "ECMWF ERA5 Atmospheric Reanalysis / Open-Meteo Archive"
    updated_at: str
