from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WeatherEvidence(BaseModel):
    current_temp: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    relative_humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    wind_gust: Optional[float] = None
    precipitation_next_24h: Optional[float] = None
    precipitation_probability_24h: Optional[int] = None
    precipitation_7d_total: Optional[float] = None
    soil_moisture_estimate: Optional[str] = "Uninstrumented (Calculated from weather and crop water demand)"
    evapotranspiration_et0: Optional[float] = None
    cloud_cover: Optional[int] = None
    uv_index: Optional[float] = None

class AdvisoryItem(BaseModel):
    id: str
    category: str  # Irrigation, Spraying, Rainfall, Fertilizer, Pest Risk, Disease Risk, Temperature Stress, Wind, Harvest, Drainage
    title: str
    priority: str  # Critical, High, Moderate, Low, Information
    reason: str
    weather_evidence: WeatherEvidence
    recommendation: str
    time_window: str
    confidence: str  # High, Medium, Low
    confidence_reason: str
    source: str
    generated_at: str

class FieldOperationWindow(BaseModel):
    day: str  # Today, Tomorrow, Day 3
    date: str
    time_slot: str  # e.g. "06:00 - 10:00 (Local Time)"
    status: str  # Favorable, Marginal, Unfavorable
    suitability_score: int  # 0 to 100
    rain_risk_percent: int
    wind_speed_kmh: float
    temperature_c: float
    recommended_operations: List[str]
    caution_notes: Optional[str] = None

class MeteorologicalObservations(BaseModel):
    current_temperature: str
    daytime_high: str
    nighttime_low: str
    relative_humidity: str
    wind_speed: str
    wind_direction: str
    next_24h_expected_rainfall: str
    next_24h_rain_probability: str
    seven_day_cumulative_rainfall: str
    soil_moisture_status: str
    uv_index: str
    source: str
    observation_time: str
    forecast_time: str

class OfficialBulletin(BaseModel):
    issuing_authority: str
    bulletin_title: str
    target_area: str
    validity_period: str
    summary: str
    source_url: Optional[str] = None
    disclaimer: str

class ClimateContext(BaseModel):
    historical_period: str
    monthly_mean_temp: Optional[float] = None
    monthly_normal_rainfall: Optional[float] = None
    wettest_month: Optional[str] = None
    warmest_month: Optional[str] = None
    source: str

class AdvisoryResponse(BaseModel):
    location: Dict[str, Any]
    crop: str
    crop_display_name: str
    growth_stage: str
    growth_stage_display_name: str
    language: str
    meteorological_observations: MeteorologicalObservations
    climate_context: Optional[ClimateContext] = None
    advisories: List[AdvisoryItem]
    field_operation_windows: List[FieldOperationWindow]
    official_bulletin: OfficialBulletin
    data_freshness: Dict[str, str]
    triggered_rules_count: int
    system_disclaimer: str
