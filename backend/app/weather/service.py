import time
import datetime
import httpx
from typing import Dict, Any, Optional, Tuple, List
from app.core.config import settings
from app.weather.base import WeatherProvider
from app.weather.open_meteo import OpenMeteoProvider
from app.weather.openweather import OpenWeatherMapProvider
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, AlertsResponse, WeatherAlertItem, AIRiskAssessment
from app.schemas.climate import ClimateResponse
from app.schemas.location import LocationSearchItem
from app.services.alerts.sachet_provider import sachet_provider
from app.services.alerts.global_provider import global_alert_provider
from app.services.alerts.geospatial import evaluate_alert_spatial_match
from app.services.risk.hazard_engine import hazard_risk_engine


# Well-known Indian and international locations with accurate lat/lon for instant lookups
PRESET_LOCATIONS: Dict[str, Tuple[float, float, str, str]] = {
    "guntur": (16.3067, 80.4365, "Guntur", "Andhra Pradesh"),
    "vijayawada": (16.5062, 80.6480, "Vijayawada", "Andhra Pradesh"),
    "visakhapatnam": (17.6868, 83.2185, "Visakhapatnam", "Andhra Pradesh"),
    "amaravati": (16.5417, 80.5158, "Amaravati", "Andhra Pradesh"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad", "Telangana"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru", "Karnataka"),
    "chennai": (13.0827, 80.2707, "Chennai", "Tamil Nadu"),
    "delhi": (28.6139, 77.2090, "New Delhi", "Delhi"),
    "new delhi": (28.6139, 77.2090, "New Delhi", "Delhi"),
    "mumbai": (19.0760, 72.8777, "Mumbai", "Maharashtra"),
    "pune": (18.5204, 73.8567, "Pune", "Maharashtra"),
    "kolkata": (22.5726, 88.3639, "Kolkata", "West Bengal"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad", "Gujarat"),
    "jaipur": (26.9124, 75.7873, "Jaipur", "Rajasthan"),
    "lucknow": (26.8467, 80.9462, "Lucknow", "Uttar Pradesh"),
    "bhopal": (23.2599, 77.4126, "Bhopal", "Madhya Pradesh"),
    "thiruvananthapuram": (8.5241, 76.9366, "Thiruvananthapuram", "Kerala"),
    "kochi": (9.9312, 76.2673, "Kochi", "Kerala"),
    "guwahati": (26.1445, 91.7362, "Guwahati", "Assam"),
    "bhubaneswar": (20.2961, 85.8245, "Bhubaneswar", "Odisha"),
    "patna": (25.5941, 85.1376, "Patna", "Bihar"),
    "chandigarh": (30.7333, 76.7794, "Chandigarh", "Punjab"),
    "srinagar": (34.0837, 74.7973, "Srinagar", "Jammu and Kashmir"),
    "london": (51.5074, -0.1278, "London", "United Kingdom"),
    "new york": (40.7128, -74.0060, "New York", "United States"),
    "tokyo": (35.6762, 139.6503, "Tokyo", "Japan"),
    "singapore": (1.3521, 103.8198, "Singapore", "Singapore"),
    "dubai": (25.2048, 55.2708, "Dubai", "United Arab Emirates")
}

class WeatherService:
    def __init__(self):
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.cache_ttl = 180  # 3 minutes cache

    def _get_provider(self) -> WeatherProvider:
        if settings.WEATHER_PROVIDER == "openweather" and settings.OPENWEATHER_API_KEY:
            return OpenWeatherMapProvider(settings.OPENWEATHER_API_KEY)
        return OpenMeteoProvider()

    async def geocode(self, query: str) -> List[LocationSearchItem]:
        query_clean = query.strip().lower()
        query_first = query_clean.split(",")[0].strip()
        results: List[LocationSearchItem] = []

        # 1. Search OpenStreetMap Nominatim first for exact town/village/city boundaries
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"format": "json", "q": query, "addressdetails": 1, "limit": 5}
            headers = {"User-Agent": "WeatherGPT-IMD-Geospatial/2.0"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, params=params, headers=headers)
                if res.status_code == 200:
                    for item in res.json():
                        addr = item.get("address", {})
                        p_name = (
                            addr.get("village") or addr.get("suburb") or addr.get("town") or
                            addr.get("city") or addr.get("municipality") or item.get("name") or query
                        )
                        state = addr.get("state") or addr.get("region") or ""
                        country = addr.get("country", "India")
                        raw_dist = addr.get("state_district") or addr.get("district") or addr.get("county") or ""
                        district = f"{raw_dist} District" if raw_dist and "district" not in raw_dist.lower() else raw_dist
                        parts = [p for p in [p_name, district, state] if p]
                        disp = ", ".join(parts) if parts else item.get("display_name", p_name)
                        lat = float(item["lat"])
                        lon = float(item["lon"])
                        if not any(abs(r.latitude - lat) < 0.01 and abs(r.longitude - lon) < 0.01 for r in results):
                            results.append(LocationSearchItem(
                                name=p_name,
                                state=state,
                                country=country,
                                latitude=lat,
                                longitude=lon,
                                display_name=disp
                            ))
        except Exception:
            pass

        # 2. Check preset dictionary ONLY if user explicitly entered exact preset name
        for key, (lat, lon, name, state) in PRESET_LOCATIONS.items():
            if query_first == key or query_clean == key:
                if not any(r.name.lower() == name.lower() for r in results):
                    results.insert(0, LocationSearchItem(
                        name=name,
                        state=state,
                        country="India" if state not in ["United Kingdom", "United States", "Japan", "Singapore", "United Arab Emirates"] else state,
                        latitude=lat,
                        longitude=lon,
                        display_name=f"{name}, {state}"
                    ))

        # 3. Also search Open-Meteo Geocoding API for global coverage
        try:
            url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": query_first, "count": 5, "language": "en", "format": "json"}
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json().get("results", [])
                    for item in data:
                        name = item.get("name")
                        admin1 = item.get("admin1") or item.get("country", "")
                        c_name = item.get("country", "India")
                        lat = item.get("latitude")
                        lon = item.get("longitude")
                        disp = f"{name}, {admin1}, {c_name}" if admin1 else f"{name}, {c_name}"
                        if not any(abs(r.latitude - lat) < 0.05 and abs(r.longitude - lon) < 0.05 for r in results):
                            results.append(LocationSearchItem(
                                name=name,
                                state=admin1,
                                country=c_name,
                                latitude=lat,
                                longitude=lon,
                                display_name=disp
                            ))
        except Exception:
            pass

        return results[:8]

    async def resolve_coordinates(self, location_name: str, lat: Optional[float] = None, lon: Optional[float] = None) -> Tuple[float, float, str]:
        # 1. Exact coordinates take absolute priority (Section 3: GPS is source of truth)
        if lat is not None and lon is not None and abs(lat) > 0.0001:
            return lat, lon, location_name or f"{lat:.4f}°, {lon:.4f}°"

        # 2. Match preset locations only on EXACT city name, not arbitrary substrings
        clean = (location_name or "Guntur").strip().lower()
        clean_first = clean.split(",")[0].strip()
        for key, (plat, plon, pname, pstate) in PRESET_LOCATIONS.items():
            if clean_first == key or clean == key:
                return plat, plon, f"{pname}, {pstate}"

        # 3. Geocode searched place name (e.g. "Vadlamudi, Andhra Pradesh")
        items = await self.geocode(location_name)
        if items:
            best = items[0]
            return best.latitude, best.longitude, best.display_name

        return 16.3067, 80.4365, "Guntur, Andhra Pradesh"

    async def get_current_weather(self, location: str, lat: Optional[float] = None, lon: Optional[float] = None) -> CurrentWeatherResponse:
        lat_r, lon_r, loc_display = await self.resolve_coordinates(location, lat, lon)
        cache_key = f"current_{round(lat_r, 4)}_{round(lon_r, 4)}"
        now = time.time()

        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return val

        provider = self._get_provider()
        res = await provider.get_current_weather(lat_r, lon_r, loc_display)
        
        if settings.DEMO_MODE:
            res.source = "DEMO DATA: Synthetic Simulation (Development Mode)"

        self._cache[cache_key] = (now, res)
        return res

    async def get_forecast(self, location: str, lat: Optional[float] = None, lon: Optional[float] = None, days: int = 7) -> ForecastResponse:
        lat_r, lon_r, loc_display = await self.resolve_coordinates(location, lat, lon)
        cache_key = f"forecast_{round(lat_r, 4)}_{round(lon_r, 4)}_{days}"
        now = time.time()

        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return val

        provider = self._get_provider()
        res = await provider.get_forecast(lat_r, lon_r, loc_display, days=days)

        if settings.DEMO_MODE:
            res.source = "DEMO DATA: Synthetic Simulation (Development Mode)"
            res.current.source = res.source

        self._cache[cache_key] = (now, res)
        return res

    async def get_alerts(self, location: str, lat: Optional[float] = None, lon: Optional[float] = None) -> AlertsResponse:
        lat_r, lon_r, loc_display = await self.resolve_coordinates(location, lat, lon)
        cache_key = f"alerts_v2_{round(lat_r, 4)}_{round(lon_r, 4)}"
        now = time.time()

        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return val

        # 1. Reverse geocode to get administrative hierarchy (Country, State, District, City)
        geo_info = await self.reverse_geocode(lat_r, lon_r)
        country = geo_info.get("country", "India")
        state = geo_info.get("state")
        district = geo_info.get("district")
        city = geo_info.get("name")

        # 2. Get forecast data for risk engine evaluation
        forecast = await self.get_forecast(loc_display, lat=lat_r, lon=lon_r, days=3)
        current_weather = forecast.current if forecast else None

        direct_alerts: List[WeatherAlertItem] = []
        regional_alerts: List[WeatherAlertItem] = []
        service_status = "operational"
        service_message = None
        source_label = "SACHET / NDMA / IMD Warning Network" if (country == "India" or "india" in (country or "").lower()) else "Authoritative Warning Agency / WMO"

        is_india = (country == "India" or "india" in (country or "").lower() or (6.0 <= lat_r <= 37.5 and 68.0 <= lon_r <= 97.5))

        if is_india:
            # 3. Query SACHET Official Disaster Portal Feeds
            sachet_raw_alerts, s_status = await sachet_provider.fetch_all_alerts()
            nowcasts = await sachet_provider.fetch_imd_nowcasts()
            service_status = s_status

            all_parsed: List[Dict[str, Any]] = []
            for item in sachet_raw_alerts:
                parsed = sachet_provider.parse_alert_item(item)
                if not parsed.get("is_expired"):
                    all_parsed.append(parsed)

            for nc in nowcasts:
                parsed_nc = sachet_provider.parse_alert_item(nc)
                if not parsed_nc.get("is_expired"):
                    all_parsed.append(parsed_nc)

            # 4. Geospatial Matching for every active alert
            for alert_dict in all_parsed:
                match_res = evaluate_alert_spatial_match(
                    user_lat=lat_r,
                    user_lon=lon_r,
                    district=district,
                    state=state,
                    city=city,
                    alert_centroid_lat=alert_dict.get("centroid_lat"),
                    alert_centroid_lon=alert_dict.get("centroid_lon"),
                    alert_radius_km=alert_dict.get("radius_km"),
                    alert_polygon=None,
                    area_description=alert_dict.get("location")
                )

                item_obj = WeatherAlertItem(
                    id=alert_dict["id"],
                    title=alert_dict["title"],
                    category=alert_dict["category"],
                    severity=alert_dict["severity"],
                    color_code=alert_dict["color_code"],
                    urgency=alert_dict.get("urgency", "Immediate"),
                    certainty=alert_dict.get("certainty", "Likely"),
                    location=alert_dict["location"],
                    start_time=alert_dict["start_time"],
                    end_time=alert_dict["end_time"],
                    duration_text=alert_dict.get("duration_text"),
                    description=alert_dict["description"],
                    source=alert_dict["source"],
                    recommended_action=alert_dict["recommended_action"],
                    safety_precautions=alert_dict.get("safety_precautions", []),
                    centroid_lat=alert_dict.get("centroid_lat"),
                    centroid_lon=alert_dict.get("centroid_lon"),
                    radius_km=alert_dict.get("radius_km"),
                    distance_km=match_res.get("distance_km"),
                    is_direct_match=match_res.get("is_direct"),
                    raw_source=alert_dict.get("raw_source", "NDMA_SACHET")
                )

                if match_res["is_direct"]:
                    direct_alerts.append(item_obj)
                elif match_res["is_regional"]:
                    regional_alerts.append(item_obj)

            if not direct_alerts and not regional_alerts:
                if service_status == "operational":
                    service_status = "no_alerts_found"
                    service_message = f"Official disaster warning feeds verified; no active warnings for {district or city or loc_display}."
            elif service_status == "temporarily_unavailable":
                service_message = "Official disaster warning feed temporarily unavailable."

        else:
            # 5. International Warning Provider
            global_alerts_raw = await global_alert_provider.get_alerts(lat_r, lon_r, loc_display, country)
            for ga in global_alerts_raw:
                direct_alerts.append(WeatherAlertItem(
                    id=ga["id"],
                    title=ga["title"],
                    category=ga["category"],
                    severity=ga["severity"],
                    color_code=ga["color_code"],
                    urgency=ga.get("urgency", "Expected"),
                    certainty=ga.get("certainty", "Likely"),
                    location=ga["location"],
                    start_time=ga["start_time"],
                    end_time=ga["end_time"],
                    duration_text=ga.get("duration_text"),
                    description=ga["description"],
                    source=ga["source"],
                    recommended_action=ga["recommended_action"],
                    safety_precautions=ga.get("safety_precautions", []),
                    centroid_lat=ga.get("centroid_lat"),
                    centroid_lon=ga.get("centroid_lon"),
                    radius_km=ga.get("radius_km"),
                    distance_km=0.0,
                    is_direct_match=True,
                    raw_source="GLOBAL_AUTHORITY"
                ))

            if not direct_alerts:
                service_status = "no_alerts_found"
                service_message = f"No active meteorological warnings reported by regional authority for {loc_display}."

        # Sort direct alerts by severity: Emergency -> Warning -> Watch -> Information
        severity_order = {"Emergency": 0, "Warning": 1, "Watch": 2, "Information": 3}
        direct_alerts.sort(key=lambda a: severity_order.get(a.severity, 4))
        regional_alerts.sort(key=lambda a: (a.distance_km or 999.0))

        # 6. Deterministic Hazard Risk Engine Evaluation
        has_official = len(direct_alerts) > 0
        top_severity = direct_alerts[0].severity if direct_alerts else (regional_alerts[0].severity if regional_alerts else None)
        risk_data = hazard_risk_engine.compute_risk(
            forecast_daily=forecast.daily if forecast else [],
            forecast_hourly=forecast.hourly if forecast else [],
            current_weather=current_weather,
            has_official_warning=has_official,
            official_warning_severity=top_severity
        )
        ai_risk = AIRiskAssessment(**risk_data)

        # 7. Assembled Response
        active_list = direct_alerts if direct_alerts else regional_alerts
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%b %d, %Y, %I:%M %p UTC")

        res = AlertsResponse(
            location_name=loc_display,
            country=country,
            state=state,
            district=district,
            alerts=active_list,
            direct_alerts=direct_alerts,
            regional_alerts=regional_alerts,
            has_active_alerts=len(direct_alerts) > 0,
            ai_risk_assessment=ai_risk,
            service_status=service_status,
            service_message=service_message,
            source=source_label,
            updated_at=now_str
        )

        self._cache[cache_key] = (now, res)
        return res

    async def get_historical_climate(self, location: str, lat: Optional[float] = None, lon: Optional[float] = None) -> ClimateResponse:
        """
        Retrieves location-specific historical climate analysis using exact latitude and longitude coordinates.
        Uses composite cache key containing coordinates, period, and source per Section 17.
        """
        lat_r, lon_r, loc_display = await self.resolve_coordinates(location, lat, lon)
        cache_key = f"climate_{round(lat_r, 4)}_{round(lon_r, 4)}_2021_2023_era5"
        now = time.time()

        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < 86400:
                return val

        geo_info = await self.reverse_geocode(lat_r, lon_r)
        country = geo_info.get("country", "India")
        state = geo_info.get("state")
        city = geo_info.get("name")

        provider = self._get_provider()
        res = await provider.get_historical_climate(lat_r, lon_r, loc_display)
        res.city = city
        res.state = state
        res.country = country

        self._cache[cache_key] = (now, res)
        return res

    async def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Reverse geocodes exact coordinates into specific human-readable locality,
        following priority hierarchy (locality > village > suburb > town > city > district).
        Never falls back to Guntur or nearest preset when coordinates are elsewhere.
        """
        # Primary: OpenStreetMap Nominatim with zoom 18 (high precision locality/village)
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"format": "json", "lat": lat, "lon": lon, "zoom": 18, "addressdetails": 1}
        headers = {"User-Agent": "WeatherGPT-IMD-Geospatial/2.0"}
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.get(url, params=params, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    addr = data.get("address", {})

                    # Strict priority hierarchy (Section 5)
                    place_name = (
                        addr.get("village") or
                        addr.get("suburb") or
                        addr.get("neighbourhood") or
                        addr.get("hamlet") or
                        addr.get("locality") or
                        addr.get("amenity") or
                        addr.get("isolated_dwelling") or
                        addr.get("town") or
                        addr.get("city_district") or
                        addr.get("subdistrict") or
                        addr.get("municipality") or
                        addr.get("city") or
                        addr.get("postal_town") or
                        data.get("name") or
                        ""
                    )

                    raw_district = addr.get("state_district") or addr.get("district") or addr.get("county") or ""
                    district = f"{raw_district} District" if raw_district and "district" not in raw_district.lower() else raw_district
                    state = addr.get("state") or addr.get("region") or ""
                    country = addr.get("country", "India")
                    city = addr.get("city") or addr.get("town") or place_name

                    if place_name:
                        parts = [p for p in [place_name, district, state] if p]
                        display = ", ".join(parts) if parts else place_name
                        return {
                            "name": place_name,
                            "city": city,
                            "district": district,
                            "state": state,
                            "country": country,
                            "display_name": display,
                            "full_address": data.get("display_name", display),
                            "latitude": lat,
                            "longitude": lon
                        }
        except Exception:
            pass

        # Secondary: BigDataCloud Client Reverse Geocoder (reliable, fast global fallback)
        try:
            bdc_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(bdc_url)
                if res.status_code == 200:
                    bdc = res.json()
                    locality = bdc.get("locality") or bdc.get("city") or bdc.get("principalSubdivision") or ""
                    state = bdc.get("principalSubdivision") or ""
                    country = bdc.get("countryName", "India")
                    admin_levels = [a.get("name") for a in bdc.get("localityInfo", {}).get("administrative", [])]
                    raw_district = next((a for a in admin_levels if "district" in a.lower()), "")
                    district = raw_district or (admin_levels[2] if len(admin_levels) > 2 else "")

                    if locality:
                        parts = [p for p in [locality, district, state] if p]
                        display = ", ".join(parts) if parts else locality
                        return {
                            "name": locality,
                            "city": bdc.get("city") or locality,
                            "district": district,
                            "state": state,
                            "country": country,
                            "display_name": display,
                            "full_address": display,
                            "latitude": lat,
                            "longitude": lon
                        }
        except Exception:
            pass

        # Coordinate fallback: NEVER return fake Guntur preset
        coord_name = f"{lat:.4f}°, {lon:.4f}°"
        return {
            "name": coord_name,
            "city": coord_name,
            "district": "",
            "state": "",
            "country": "India",
            "display_name": coord_name,
            "full_address": coord_name,
            "latitude": lat,
            "longitude": lon
        }

weather_service = WeatherService()

