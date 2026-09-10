import time
import datetime
import httpx
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.services.safety.guidance import get_safety_precautions

logger = logging.getLogger("sachet_provider")

class SachetAlertProvider:
    """
    Official Disaster Warning Provider for India using SACHET (National Disaster Alert Portal - NDMA).
    Integrates authorized sources including IMD, CWC, INCOIS, and State DDMAs.
    Implements HTTP ETag client-side caching in compliance with SACHET CAP Integration Guide.
    """
    def __init__(self):
        self.base_url = "https://sachet.ndma.gov.in/cap_public_website"
        self._cached_alerts: List[Dict[str, Any]] = []
        self._cached_nowcasts: List[Dict[str, Any]] = []
        self._etag_all_alerts: Optional[str] = None
        self._etag_nowcasts: Optional[str] = None
        self._last_fetch_time: float = 0.0
        self._cache_ttl_seconds: float = 180.0  # 3 minutes cache to avoid hammering SACHET servers
        self.last_status: str = "operational"  # operational, temporarily_unavailable, no_alerts_found

    async def fetch_all_alerts(self) -> Tuple[List[Dict[str, Any]], str]:
        """
        Retrieves active official disaster alerts from SACHET.
        Uses ETag change detection (If-None-Match -> 304 Not Modified).
        """
        now = time.time()
        # Serve from memory cache if within TTL
        if self._cached_alerts and (now - self._last_fetch_time < self._cache_ttl_seconds):
            return self._cached_alerts, self.last_status

        url = f"{self.base_url}/FetchAllAlertDetails"
        headers = {
            "User-Agent": "WeatherGPT-IMD-Platform/1.0 (CAP-XML Agency Consumer)",
            "Accept": "application/json, text/plain, */*"
        }
        if self._etag_all_alerts:
            headers["If-None-Match"] = self._etag_all_alerts

        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(url, headers=headers)
                
                # Case A: 304 Not Modified — Content unchanged, use cached data
                if res.status_code == 304:
                    self._last_fetch_time = now
                    self.last_status = "operational"
                    return self._cached_alerts, self.last_status

                # Case B: 200 OK — Updated content received
                if res.status_code == 200:
                    new_etag = res.headers.get("ETag")
                    if new_etag:
                        self._etag_all_alerts = new_etag
                    
                    data = res.json()
                    if isinstance(data, list):
                        self._cached_alerts = data
                        self._last_fetch_time = now
                        self.last_status = "operational"
                        return self._cached_alerts, self.last_status

        except Exception as e:
            logger.warning(f"SACHET FetchAllAlertDetails error: {e}")
            if self._cached_alerts:
                # Fallback to stale cached data during temporary glitch
                return self._cached_alerts, "operational"
            self.last_status = "temporarily_unavailable"
            return [], "temporarily_unavailable"

        return self._cached_alerts, self.last_status

    async def fetch_imd_nowcasts(self) -> List[Dict[str, Any]]:
        """
        Retrieves active district-level IMD Nowcast warnings from SACHET.
        """
        now = time.time()
        if self._cached_nowcasts and (now - self._last_fetch_time < self._cache_ttl_seconds):
            return self._cached_nowcasts

        url = f"{self.base_url}/FetchIMDNowcastAlerts"
        headers = {
            "User-Agent": "WeatherGPT-IMD-Platform/1.0",
            "Accept": "application/json, text/plain, */*"
        }
        if self._etag_nowcasts:
            headers["If-None-Match"] = self._etag_nowcasts

        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 304:
                    return self._cached_nowcasts
                if res.status_code == 200:
                    new_etag = res.headers.get("ETag")
                    if new_etag:
                        self._etag_nowcasts = new_etag
                    data = res.json()
                    nowcasts = data.get("nowcastDetails", [])
                    if isinstance(nowcasts, list):
                        self._cached_nowcasts = nowcasts
                        return self._cached_nowcasts
        except Exception as e:
            logger.warning(f"SACHET FetchIMDNowcastAlerts error: {e}")

        return self._cached_nowcasts

    def parse_alert_item(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a raw SACHET alert into standard CAP attributes.
        """
        identifier = str(raw.get("identifier") or raw.get("alert_id_sdma_autoinc") or f"sachet-{int(time.time()*1000)}")
        event = raw.get("disaster_type") or raw.get("event_category") or "Severe Weather"
        source = raw.get("alert_source") or raw.get("source") or "IMD / NDMA"
        warning_msg = raw.get("warning_message") or raw.get("events") or ""
        area_desc = raw.get("area_description") or ""
        severity_color = (raw.get("severity_color") or "yellow").capitalize()

        # Severity standard
        severity = "Warning"
        if severity_color == "Red":
            severity = "Emergency"
        elif severity_color == "Orange":
            severity = "Warning"
        elif severity_color == "Yellow":
            severity = "Watch"
        else:
            severity = "Information"

        # Centroid parsing
        centroid_lat = None
        centroid_lon = None
        centroid_str = raw.get("centroid")
        if centroid_str and isinstance(centroid_str, str) and "," in centroid_str:
            try:
                parts = centroid_str.split(",")
                # Centroid format in SACHET is longitude,latitude
                centroid_lon = float(parts[0].strip())
                centroid_lat = float(parts[1].strip())
            except Exception:
                pass
        elif raw.get("location") and isinstance(raw.get("location"), dict):
            coords = raw.get("location", {}).get("coordinates")
            if coords and len(coords) == 2:
                centroid_lon = float(coords[0])
                centroid_lat = float(coords[1])

        # Time parsing
        start_time_str = raw.get("effective_start_time") or "Immediate"
        end_time_str = raw.get("effective_end_time") or "Duration not specified by issuing authority"
        
        # Calculate duration text if parseable
        duration_text = "Validity specified by issuing authority"
        try:
            # Example format: "Wed Sep 09 20:47:00 IST 2026"
            dt_start = datetime.datetime.strptime(start_time_str.replace(" IST", ""), "%a %b %d %H:%M:%S %Y")
            dt_end = datetime.datetime.strptime(end_time_str.replace(" IST", ""), "%a %b %d %H:%M:%S %Y")
            diff_hours = round((dt_end - dt_start).total_seconds() / 3600.0, 1)
            duration_text = f"{diff_hours} hours"
        except Exception:
            pass

        # Expiration check
        is_expired = False
        try:
            now_dt = datetime.datetime.now()
            dt_end = datetime.datetime.strptime(end_time_str.replace(" IST", ""), "%a %b %d %H:%M:%S %Y")
            if now_dt > dt_end:
                is_expired = True
        except Exception:
            pass

        # Area radius approximation from area_covered_sqkm
        area_sqkm = None
        try:
            area_sqkm = float(raw.get("area_covered", 0))
        except Exception:
            pass
        radius_km = (area_sqkm / 3.14159) ** 0.5 if area_sqkm and area_sqkm > 0 else 35.0

        precautions = get_safety_precautions(event)

        return {
            "id": identifier,
            "title": f"{event} Alert",
            "category": event,
            "severity": severity,
            "color_code": severity_color,
            "urgency": "Expected" if "Next" in warning_msg or "likely" in warning_msg.lower() else "Immediate",
            "certainty": raw.get("severity_level") or "Likely",
            "location": area_desc or "Regional Area",
            "start_time": start_time_str,
            "end_time": end_time_str,
            "duration_text": duration_text,
            "description": warning_msg or f"Official meteorological warning issued by {source}.",
            "source": f"SACHET / {source}",
            "recommended_action": precautions[0] if precautions else "Follow instructions from local disaster authorities.",
            "safety_precautions": precautions,
            "centroid_lat": centroid_lat,
            "centroid_lon": centroid_lon,
            "radius_km": round(radius_km, 1),
            "is_expired": is_expired,
            "raw_source": "NDMA_SACHET_CAP"
        }

sachet_provider = SachetAlertProvider()
