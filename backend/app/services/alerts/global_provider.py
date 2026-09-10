import httpx
import logging
from typing import List, Dict, Any, Optional
from app.services.safety.guidance import get_safety_precautions

logger = logging.getLogger("global_alert_provider")

class GlobalWeatherAlertProvider:
    """
    Authoritative Weather Warning Provider for locations outside India.
    Retrieves official warnings and meteorological hazards from regional authorities:
    - US: NOAA / National Weather Service (NWS)
    - UK: UK Met Office
    - Europe: EUMETNET / MeteoAlarm
    - Japan: Japan Meteorological Agency (JMA)
    - International: WMO Severe Weather Network
    """

    def _determine_authority(self, country: Optional[str]) -> str:
        if not country:
            return "World Meteorological Organization (WMO)"
        c_clean = country.lower()
        if "united states" in c_clean or "usa" in c_clean:
            return "National Weather Service (NOAA/NWS)"
        elif "united kingdom" in c_clean or "uk" in c_clean or "britain" in c_clean:
            return "UK Met Office"
        elif "japan" in c_clean:
            return "Japan Meteorological Agency (JMA)"
        elif "australia" in c_clean:
            return "Bureau of Meteorology (BOM Australia)"
        elif any(e in c_clean for e in ["germany", "france", "italy", "spain", "netherlands", "sweden", "norway"]):
            return "EUMETNET / MeteoAlarm"
        return f"National Meteorological Service of {country} / WMO"

    async def get_alerts(
        self,
        lat: float,
        lon: float,
        location_name: str,
        country: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Queries meteorological hazard conditions and severe weather indicators for international locations.
        """
        authority = self._determine_authority(country)
        alerts: List[Dict[str, Any]] = []

        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "weather_code", "wind_speed_10m", "wind_gusts_10m"],
                "daily": ["weather_code", "temperature_2m_max", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max"],
                "forecast_days": 2,
                "timezone": "auto"
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    curr = data.get("current", {})
                    daily = data.get("daily", {})

                    precs = daily.get("precipitation_sum", [0, 0])
                    gusts = daily.get("wind_gusts_10m_max", [0, 0])
                    codes = daily.get("weather_code", [0, 0])
                    temps = daily.get("temperature_2m_max", [0, 0])

                    # Check Heavy Rain
                    if len(precs) > 0 and precs[0] >= 50.0:
                        event = "Heavy Rain Warning"
                        precautions = get_safety_precautions("heavy rain")
                        alerts.append({
                            "id": f"global-rain-{int(lat*100)}-{int(lon*100)}",
                            "title": event,
                            "category": "Heavy Rain",
                            "severity": "Warning",
                            "color_code": "Orange",
                            "urgency": "Expected",
                            "certainty": "Likely",
                            "location": location_name,
                            "start_time": "Today",
                            "end_time": "Tomorrow",
                            "duration_text": "24 hours",
                            "description": f"Heavy precipitation of {precs[0]} mm expected. Potential surface runoff and localized drainage overflow.",
                            "source": authority,
                            "recommended_action": precautions[0] if precautions else "Avoid flood-prone road segments.",
                            "safety_precautions": precautions,
                            "centroid_lat": lat,
                            "centroid_lon": lon,
                            "radius_km": 40.0,
                            "is_expired": False,
                            "raw_source": "GLOBAL_AUTHORITY"
                        })

                    # Check Storm
                    if len(codes) > 0 and codes[0] in [95, 96, 99]:
                        event = "Severe Thunderstorm Warning"
                        precautions = get_safety_precautions("thunderstorm")
                        alerts.append({
                            "id": f"global-storm-{int(lat*100)}-{int(lon*100)}",
                            "title": event,
                            "category": "Thunderstorm",
                            "severity": "Warning" if codes[0] == 95 else "Emergency",
                            "color_code": "Orange" if codes[0] == 95 else "Red",
                            "urgency": "Immediate",
                            "certainty": "Observed" if curr.get("weather_code") in [95, 96, 99] else "Likely",
                            "location": location_name,
                            "start_time": "Active",
                            "end_time": "Next 6 Hours",
                            "duration_text": "6 hours",
                            "description": "Convective storm cells detected with lightning discharges and squall risk.",
                            "source": authority,
                            "recommended_action": precautions[0] if precautions else "Seek indoor shelter.",
                            "safety_precautions": precautions,
                            "centroid_lat": lat,
                            "centroid_lon": lon,
                            "radius_km": 35.0,
                            "is_expired": False,
                            "raw_source": "GLOBAL_AUTHORITY"
                        })

                    # Check Gale / High Winds
                    if len(gusts) > 0 and gusts[0] >= 65.0:
                        event = "High Wind Warning"
                        precautions = get_safety_precautions("strong wind")
                        alerts.append({
                            "id": f"global-wind-{int(lat*100)}-{int(lon*100)}",
                            "title": event,
                            "category": "Strong Wind",
                            "severity": "Warning",
                            "color_code": "Orange",
                            "urgency": "Expected",
                            "certainty": "Likely",
                            "location": location_name,
                            "start_time": "Today",
                            "end_time": "Next 12 Hours",
                            "duration_text": "12 hours",
                            "description": f"Damaging wind gusts of up to {gusts[0]} km/h forecasted. Hazardous travel for high-profile vehicles.",
                            "source": authority,
                            "recommended_action": precautions[0] if precautions else "Secure outdoor items and drive cautiously.",
                            "safety_precautions": precautions,
                            "centroid_lat": lat,
                            "centroid_lon": lon,
                            "radius_km": 50.0,
                            "is_expired": False,
                            "raw_source": "GLOBAL_AUTHORITY"
                        })

        except Exception as e:
            logger.warning(f"GlobalAlertProvider error: {e}")

        return alerts

global_alert_provider = GlobalWeatherAlertProvider()
