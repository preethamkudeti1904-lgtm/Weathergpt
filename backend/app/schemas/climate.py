from datetime import datetime, timezone
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

class ClimateTrendPoint(BaseModel):
    label: str  # Month name: January - December
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    total_rainfall: float
    rainfall_days: int

class ClimateMonthlyPoint(BaseModel):
    month: str
    avg_temperature_c: float
    max_temperature_c: float
    min_temperature_c: float
    precipitation_mm: float
    rain_days: float

class ClimateAnnualSummary(BaseModel):
    mean_temperature_c: float
    max_temperature_c: float
    min_temperature_c: float
    total_precipitation_mm: float
    rainy_days: float
    wettest_month: str
    warmest_month: str

class ReferenceStationInfo(BaseModel):
    id: str
    name: str
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    distance_km: float

class ClimateSourceInfo(BaseModel):
    organization: str = "India Meteorological Department (IMD)"
    division: Optional[str] = "National Data Centre (NDC) / Climate Application Group, Pune"
    dataset: str = "IMD Climatological Normals (1991–2020)"
    period: str = "1991–2020"
    data_type: str = "climatological_normal"
    attribution: str = "Government of India, Ministry of Earth Sciences (MoES) / IMD"
    rain_day_definition: str = "Daily precipitation >= 2.5 mm (Official IMD Standard)"
    url: Optional[str] = "https://mausam.imd.gov.in"

class LocationMetadata(BaseModel):
    name: str
    latitude: float
    longitude: float

class ClimateResponse(BaseModel):
    # Structured official hierarchy per Section 6
    location: Optional[LocationMetadata] = None
    requested_location: Optional[LocationMetadata] = None
    reference_station: Optional[ReferenceStationInfo] = None
    source_info: Optional[ClimateSourceInfo] = None
    source: Union[ClimateSourceInfo, str] = "India Meteorological Department (IMD)"
    annual: Optional[ClimateAnnualSummary] = None
    monthly: Optional[List[ClimateMonthlyPoint]] = None

    # Legacy & backwards-compatible properties
    location_name: str
    latitude: float
    longitude: float
    period: str = "1991–2020"
    historical_period: Optional[str] = "1991–2020 (IMD 30-Year Climatological Normals)"
    parameter: str = "all"
    data: List[ClimateTrendPoint]
    annual_mean_temp: float
    annual_total_rainfall: float
    wettest_month: Optional[str] = None
    warmest_month: Optional[str] = None
    rain_day_threshold_mm: float = 2.5
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class HistoricalYearMonthly(BaseModel):
    month: str
    avg_temperature: float
    max_temperature: float
    min_temperature: float
    rainfall: float
    rainy_days: int

class HistoricalYearSummary(BaseModel):
    annual_average_temperature: float
    annual_rainfall: float
    highest_temperature: float
    lowest_temperature: float
    warmest_month: str
    coldest_month: str
    wettest_month: str
    driest_month: str
    total_rainy_days: int

class HistoricalSource(BaseModel):
    name: str
    station: str
    station_id: Optional[str] = None
    distance_km: float
    dataset: Optional[str] = None
    data_coverage: Optional[str] = None
    observation_type: Optional[str] = None
    rain_day_definition: Optional[str] = None
    attribution: Optional[str] = None

class HistoricalYearResponse(BaseModel):
    location: LocationMetadata
    year: int
    source: HistoricalSource
    monthly: List[HistoricalYearMonthly]
    summary: HistoricalYearSummary
    available_years: Optional[List[int]] = None
    climatological_normal: Optional[Dict[str, Any]] = None
