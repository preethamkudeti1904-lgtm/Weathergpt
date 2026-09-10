import time
import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from app.weather.service import weather_service
from app.services.agri.advisory_engine import advisory_engine
from app.services.agri.crop_thresholds import CROPS_REGISTRY, GROWTH_STAGES_REGISTRY
from app.schemas.advisory import AdvisoryResponse

router = APIRouter(prefix="/advisory", tags=["Specialized Advisory"])

# In-memory advisory cache: key -> (timestamp, AdvisoryResponse)
_ADVISORY_CACHE: Dict[str, Any] = {}

@router.get("", response_model=AdvisoryResponse)
@router.get("/", response_model=AdvisoryResponse)
async def get_advisory(
    lat: Optional[float] = Query(default=None, description="Exact latitude"),
    lon: Optional[float] = Query(default=None, description="Exact longitude"),
    location: Optional[str] = Query(default=None, description="Location name or search string"),
    crop: Optional[str] = Query(default="rice", description="Crop name or identifier"),
    growth_stage: Optional[str] = Query(default="vegetative", description="Crop growth stage"),
    language: Optional[str] = Query(default="en", description="Target language code")
):
    """
    Central Weather-Driven Agrometeorological Advisory Endpoint (Section 30).
    Generates location-specific, crop-stage calibrated agricultural guidance
    using exact coordinates, real-time observations, 7-day forecast, and climate history.
    """
    try:
        lat_r, lon_r, loc_display = await weather_service.resolve_coordinates(location, lat, lon)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resolve location coordinates: {str(e)}")

    # Composite cache key (Section 36: lat + lon + crop + growthStage + date)
    today_iso = datetime.datetime.utcnow().strftime("%Y%m%d_%H")
    cache_key = f"adv_{round(lat_r, 4)}_{round(lon_r, 4)}_{crop}_{growth_stage}_{language}_{today_iso}"
    now = time.time()

    if cache_key in _ADVISORY_CACHE:
        ts, cached_val = _ADVISORY_CACHE[cache_key]
        if now - ts < 900:  # 15 minutes TTL
            return cached_val

    # Reverse geocode for accurate locality, district, state
    try:
        geo_info = await weather_service.reverse_geocode(lat_r, lon_r)
    except Exception:
        geo_info = {"name": loc_display, "district": None, "state": None, "country": "India"}

    loc_dict = {
        "name": geo_info.get("name") or loc_display,
        "district": geo_info.get("district") or loc_display.split(",")[0],
        "state": geo_info.get("state") or "Andhra Pradesh",
        "country": geo_info.get("country") or "India",
        "latitude": lat_r,
        "longitude": lon_r,
        "timezone": "Asia/Kolkata",
        "source": "gps" if (lat is not None and lon is not None) else "search"
    }

    # Fetch 7-day forecast with current weather & hourly slices
    try:
        forecast = await weather_service.get_forecast(location=loc_display, lat=lat_r, lon=lon_r, days=7)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Advisory temporarily unavailable because current weather data could not be retrieved: {str(e)}"
        )

    # Fetch climate reanalysis context
    climate_data = None
    try:
        climate_data = await weather_service.get_historical_climate(location=loc_display, lat=lat_r, lon=lon_r)
    except Exception:
        pass  # Climate is contextual; failure will not block operational weather advisory

    current = forecast.current
    loc_dict["timezone"] = forecast.timezone or "Asia/Kolkata"

    # Generate deterministic rule-based advisories
    res = advisory_engine.generate_advisories(
        location=loc_dict,
        current=current,
        forecast=forecast,
        climate=climate_data,
        crop_input=crop,
        growth_stage_input=growth_stage,
        language=language or "en"
    )

    _ADVISORY_CACHE[cache_key] = (now, res)
    return res

@router.get("/crops")
async def get_crop_advisory(
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh"),
    crop: Optional[str] = Query(default="Chilli / Cotton / Paddy"),
    growth_stage: Optional[str] = Query(default="vegetative"),
    language: Optional[str] = Query(default="en")
):
    """
    Backwards-compatible crop advisory endpoint.
    Routes directly through the central weather-driven advisory engine.
    """
    adv_res = await get_advisory(
        lat=lat,
        lon=lon,
        location=location,
        crop=crop,
        growth_stage=growth_stage,
        language=language
    )

    # Structure legacy format for backwards compatibility while including new rich payload
    legacy_recommendations = []
    for adv in adv_res.advisories:
        legacy_recommendations.append({
            "stage": adv.category,
            "action": adv.recommendation,
            "priority": adv.priority,
            "title": adv.title,
            "reason": adv.reason
        })

    return {
        "location": adv_res.location.get("name"),
        "crop_focus": adv_res.crop_display_name,
        "growth_stage": adv_res.growth_stage_display_name,
        "meteorological_observations": adv_res.meteorological_observations.model_dump() if hasattr(adv_res.meteorological_observations, "model_dump") else adv_res.meteorological_observations.dict(),
        "ai_generated_advisory": {
            "disclaimer": adv_res.system_disclaimer,
            "recommendations": legacy_recommendations,
            "pest_disease_risk": next((a.recommendation for a in adv_res.advisories if "Pest" in a.category or "Disease" in a.category), "Low"),
            "spraying_window": next((a.recommendation for a in adv_res.advisories if "Spraying" in a.category), "Moderate")
        },
        "advisories": [a.model_dump() if hasattr(a, "model_dump") else a.dict() for a in adv_res.advisories],
        "field_operation_windows": [w.model_dump() if hasattr(w, "model_dump") else w.dict() for w in adv_res.field_operation_windows],
        "official_bulletin": adv_res.official_bulletin.model_dump() if hasattr(adv_res.official_bulletin, "model_dump") else adv_res.official_bulletin.dict(),
        "climate_context": adv_res.climate_context.model_dump() if adv_res.climate_context and hasattr(adv_res.climate_context, "model_dump") else (adv_res.climate_context.dict() if adv_res.climate_context else None),
        "data_freshness": adv_res.data_freshness
    }

@router.get("/crops-registry")
def get_crops_and_stages_registry():
    """Returns list of supported crops and phonological growth stages."""
    return {
        "crops": CROPS_REGISTRY,
        "growth_stages": GROWTH_STAGES_REGISTRY
    }

@router.get("/disaster")
async def get_disaster_dashboard(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh")
):
    """
    Emergency Weather Dashboard for Disaster Management Authorities.
    """
    forecast = await weather_service.get_forecast(location=location, days=5)
    alerts = await weather_service.get_alerts(location=location)
    curr = forecast.current

    flood_risk = "High Risk" if any(d.precipitation > 50 for d in forecast.daily[:2]) else ("Moderate" if any(d.precipitation > 20 for d in forecast.daily[:2]) else "Normal")
    cyclone_risk = "Active Squall Watch" if curr.wind_speed > 40 else "No Severe Cyclonic Disturbance"

    return {
        "location": location,
        "emergency_status": "ELEVATED ALERT" if alerts.has_active_alerts else "NORMAL OPERATIONS",
        "active_alerts": alerts.alerts,
        "key_risk_indicators": {
            "flood_inundation_risk": flood_risk,
            "cyclonic_wind_status": cyclone_risk,
            "current_wind_speed": f"{curr.wind_speed} km/h",
            "heavy_rainfall_threat": f"{forecast.daily[0].precipitation} mm expected today",
            "atmospheric_pressure": f"{curr.pressure} hPa"
        },
        "response_checklist": [
            "Check municipal stormwater pumping stations and drain culverts",
            "Confirm VHF/wireless communication backup power for emergency control rooms",
            "Coordinate with SDRF/NDRF nodal officers if rainfall exceeds Orange warning thresholds",
            "Monitor low-lying causeways and deploy road safety barricades"
        ],
        "source": curr.source,
        "updated_at": curr.updated_at
    }

@router.get("/aviation")
async def get_aviation_weather(
    location: Optional[str] = Query(default="Guntur, Andhra Pradesh")
):
    """
    Aviation Meteorological Summary (Visibility, Wind, Temperature).
    """
    curr = await weather_service.get_current_weather(location=location)
    
    # Flight category determination
    flight_category = "VFR (Visual Flight Rules)"
    if curr.visibility < 5.0 or curr.condition_code in [95, 96, 99]:
        flight_category = "IFR (Instrument Flight Rules)"
    elif curr.visibility < 8.0:
        flight_category = "MVFR (Marginal VFR)"

    return {
        "location": location,
        "flight_category": flight_category,
        "visibility_km": curr.visibility,
        "surface_wind": {
            "speed_kmh": curr.wind_speed,
            "direction_degrees": curr.wind_direction,
            "direction_cardinal": curr.wind_direction_cardinal
        },
        "temperature_c": curr.temperature,
        "dewpoint_spread_approx_c": round(curr.temperature - ((100 - curr.humidity) / 5), 1),
        "altimeter_setting_hpa": curr.pressure,
        "weather_phenomena": curr.condition,
        "source": curr.source,
        "updated_at": curr.updated_at
    }

@router.get("/marine")
async def get_marine_weather(
    location: Optional[str] = Query(default="Visakhapatnam, Andhra Pradesh")
):
    """
    Marine and Coastal Weather Summary (Wind, Waves, Storms).
    """
    curr = await weather_service.get_current_weather(location=location)
    
    # Estimate sea state based on wind speed (Beaufort scale)
    wind_kts = curr.wind_speed * 0.539957
    if wind_kts < 7:
        sea_state = "Smooth (Wave height: 0.2 - 0.5 m)"
        beaufort = 2
    elif wind_kts < 16:
        sea_state = "Slight to Moderate (Wave height: 0.6 - 1.2 m)"
        beaufort = 4
    elif wind_kts < 27:
        sea_state = "Rough (Wave height: 1.5 - 2.5 m)"
        beaufort = 6
    else:
        sea_state = "Very Rough to High (Wave height: > 3.0 m)"
        beaufort = 8

    return {
        "location": location,
        "wind_speed_kmh": curr.wind_speed,
        "wind_speed_knots": round(wind_kts, 1),
        "wind_direction": curr.wind_direction_cardinal,
        "estimated_sea_state": sea_state,
        "beaufort_force": beaufort,
        "fishermen_warning": "Warning: Avoid venturing into deep sea" if wind_kts > 22 else "No general marine warning",
        "coastal_tide_outlook": "Semi-diurnal cycle normal",
        "source": curr.source,
        "updated_at": curr.updated_at
    }
