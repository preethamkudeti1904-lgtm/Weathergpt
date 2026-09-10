from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class NormalizedLocation(BaseModel):
    latitude: float
    longitude: float
    name: str
    timezone: Optional[str] = None

class NormalizedCurrent(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    visibility: float
    precipitation: Optional[float] = None
    condition: str

class CurrentWeatherResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    temperature: float
    feels_like: float
    condition: str
    condition_code: int
    humidity: int
    wind_speed: float
    wind_direction: int
    wind_direction_cardinal: str
    wind_gusts: Optional[float] = None
    pressure: float
    visibility: float
    precipitation: Optional[float] = None
    uv_index: Optional[float] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    timezone_abbreviation: Optional[str] = "IST"
    utc_offset_seconds: Optional[int] = 19800
    source: str
    updated_at: str

    # Section 29 Normalized API Structure
    location: Optional[NormalizedLocation] = None
    current: Optional[NormalizedCurrent] = None
    timestamp: Optional[str] = None


class HourlyForecastItem(BaseModel):
    time: str
    temperature: float
    condition: str
    condition_code: int
    rain_probability: int
    precipitation: float
    wind_speed: float
    wind_direction: Optional[int] = None
    wind_direction_cardinal: Optional[str] = None
    wind_gusts: Optional[float] = None

class DailyForecastItem(BaseModel):
    date: str
    day_name: str
    condition: str
    condition_code: int
    temp_max: float
    temp_min: float
    rain_probability: int
    precipitation: float
    wind_speed_max: float
    uv_index_max: Optional[float] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None

class ForecastResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    current: CurrentWeatherResponse
    hourly: List[HourlyForecastItem]
    daily: List[DailyForecastItem]
    timezone: Optional[str] = "Asia/Kolkata"
    timezone_abbreviation: Optional[str] = "IST"
    utc_offset_seconds: Optional[int] = 19800
    source: str
    updated_at: str

class WeatherAlertItem(BaseModel):
    id: str
    title: str
    category: str  # Heavy Rain, Cyclone, Flood, Heat Wave, Thunderstorm, Strong Wind, Visibility
    severity: str  # Information, Watch, Warning, Emergency
    color_code: str  # Green, Yellow, Orange, Red
    urgency: Optional[str] = "Immediate"  # Immediate, Expected, Future
    certainty: Optional[str] = "Likely"  # Observed, Likely, Possible
    location: str
    start_time: str
    end_time: str
    duration_text: Optional[str] = None
    description: str
    source: str
    recommended_action: str
    safety_precautions: Optional[List[str]] = []
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    radius_km: Optional[float] = None
    distance_km: Optional[float] = None
    is_direct_match: Optional[bool] = True
    raw_source: Optional[str] = "NDMA_SACHET"

class AIRiskAssessment(BaseModel):
    score: int
    level: str  # LOW, MODERATE, HIGH, VERY HIGH, EXTREME
    confidence: str  # High, Moderate, Low
    expected_window: str
    reason: str
    hazard_breakdown: Dict[str, float]
    disclaimer: str

class AlertsResponse(BaseModel):
    location_name: str
    country: Optional[str] = "India"
    state: Optional[str] = None
    district: Optional[str] = None
    alerts: List[WeatherAlertItem]  # Primary alerts list for backwards compatibility
    direct_alerts: List[WeatherAlertItem] = []
    regional_alerts: List[WeatherAlertItem] = []
    has_active_alerts: bool = False
    ai_risk_assessment: Optional[AIRiskAssessment] = None
    service_status: str = "operational"  # "operational", "temporarily_unavailable", "no_alerts_found"
    service_message: Optional[str] = None
    source: str
    updated_at: str

