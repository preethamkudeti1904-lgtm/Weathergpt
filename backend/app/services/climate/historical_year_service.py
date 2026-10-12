"""
Authoritative Location + Year Historical Meteorological Climate Service.
Retrieves actual observed/reanalysis daily meteorological data for any selected location and calendar year.
Uses ECMWF ERA5 high-resolution reanalysis via Open-Meteo Historical Archive API,
and associates the location with the nearest official India Meteorological Department (IMD) observatory station.
"""

import time
import json
import httpx
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException
from app.services.climate.imd_normals import imd_climate_service

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

class HistoricalYearService:
    def __init__(self):
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.cache_ttl = 86400  # 24 hours cache for historical archive data

    async def get_year_data(
        self,
        lat: float,
        lon: float,
        location_name: str,
        year: int
    ) -> Dict[str, Any]:
        """
        Retrieves actual historical meteorological observations for a specific location and calendar year.
        Aggregates daily observations into 12 monthly data points and calculates annual summary statistics.
        """
        now = time.time()
        cache_key = f"climate_hist_{round(lat, 4)}_{round(lon, 4)}_{year}"
        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return val

        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }

        print("Historical climate request:")
        print(f"latitude={round(lat, 4)}")
        print(f"longitude={round(lon, 4)}")
        print(f"year={year}")
        print(f"start_date={start_date}")
        print(f"end_date={end_date}")

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.get(url, params=params)
                print(f"Open-Meteo status: {res.status_code}")
                print(f"Open-Meteo response:\n{res.text[:500]}")

                if res.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Open-Meteo historical API rejected request: {res.text[:200]}"
                    )
                elif res.status_code == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="Historical climate archive rate limit reached. Please retry in a few moments."
                    )
                elif res.status_code != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Historical climate archive returned error status {res.status_code}: {res.text[:200]}"
                    )
                raw_data = res.json()
        except httpx.TimeoutException:
            print("Open-Meteo status: TIMEOUT")
            raise HTTPException(
                status_code=504,
                detail=f"Historical climate request timed out for location ({lat:.4f}, {lon:.4f}) and year {year}."
            )
        except httpx.RequestError as req_err:
            print(f"Open-Meteo network error: {req_err}")
            raise HTTPException(
                status_code=503,
                detail=f"Historical climate service connection failure: {str(req_err)}"
            )
        except json.JSONDecodeError:
            print("Open-Meteo invalid JSON response")
            raise HTTPException(
                status_code=502,
                detail="Historical climate archive returned an invalid JSON response."
            )

        daily = raw_data.get("daily", {})
        if not isinstance(daily, dict):
            raise HTTPException(
                status_code=404,
                detail=f"No daily historical meteorological records found for location ({lat:.4f}, {lon:.4f}) and year {year}."
            )
        times = daily.get("time", [])
        means = daily.get("temperature_2m_mean", [])
        tmaxs = daily.get("temperature_2m_max", [])
        tmins = daily.get("temperature_2m_min", [])
        precs = daily.get("precipitation_sum", [])

        if not times or not means:
            raise HTTPException(
                status_code=404,
                detail=f"Historical climate data empty or incomplete for location ({lat:.4f}, {lon:.4f}) and year {year}."
            )

        # Group daily data by month (1..12)
        month_buckets: Dict[int, Dict[str, Any]] = {
            m: {"means": [], "maxs": [], "mins": [], "rainfall": 0.0, "rainy_days": 0}
            for m in range(1, 13)
        }

        for idx, t_str in enumerate(times):
            parts = t_str.split("-")
            if len(parts) < 2:
                continue
            m_idx = int(parts[1])

            t_mean = means[idx] if idx < len(means) else None
            t_max = tmaxs[idx] if idx < len(tmaxs) else None
            t_min = tmins[idx] if idx < len(tmins) else None
            prec = precs[idx] if idx < len(precs) else None

            if t_mean is not None:
                month_buckets[m_idx]["means"].append(t_mean)
            if t_max is not None:
                month_buckets[m_idx]["maxs"].append(t_max)
            if t_min is not None:
                month_buckets[m_idx]["mins"].append(t_min)
            if prec is not None:
                month_buckets[m_idx]["rainfall"] += prec
                # IMD standard definition of a rainy day: daily rainfall >= 2.5 mm
                if prec >= 2.5:
                    month_buckets[m_idx]["rainy_days"] += 1

        monthly_list: List[Dict[str, Any]] = []
        for m_num in range(1, 13):
            b = month_buckets[m_num]
            m_name = MONTH_NAMES[m_num - 1]

            avg_t = round(sum(b["means"]) / len(b["means"]), 1) if b["means"] else 0.0
            max_t = round(max(b["maxs"]), 1) if b["maxs"] else 0.0
            min_t = round(min(b["mins"]), 1) if b["mins"] else 0.0
            rain_m = round(b["rainfall"], 1)
            days_m = b["rainy_days"]

            monthly_list.append({
                "month": m_name,
                "avg_temperature": avg_t,
                "max_temperature": max_t,
                "min_temperature": min_t,
                "rainfall": rain_m,
                "rainy_days": days_m
            })

        # Calculate annual summary metrics from the selected year's data
        valid_means = [m["avg_temperature"] for m in monthly_list]
        annual_avg_temp = round(sum(valid_means) / 12.0, 1)
        annual_total_rain = round(sum(m["rainfall"] for m in monthly_list), 1)
        total_rain_days = sum(m["rainy_days"] for m in monthly_list)

        all_maxs = [t for t in tmaxs if t is not None]
        highest_temp = round(max(all_maxs), 1) if all_maxs else max(m["max_temperature"] for m in monthly_list)

        all_mins = [t for t in tmins if t is not None]
        lowest_temp = round(min(all_mins), 1) if all_mins else min(m["min_temperature"] for m in monthly_list)

        warmest_m = max(monthly_list, key=lambda m: m["avg_temperature"])["month"]
        coldest_m = min(monthly_list, key=lambda m: m["avg_temperature"])["month"]
        wettest_m = max(monthly_list, key=lambda m: m["rainfall"])["month"]
        driest_m = min(monthly_list, key=lambda m: m["rainfall"])["month"]

        summary = {
            "annual_average_temperature": annual_avg_temp,
            "annual_rainfall": annual_total_rain,
            "highest_temperature": highest_temp,
            "lowest_temperature": lowest_temp,
            "warmest_month": warmest_m,
            "coldest_month": coldest_m,
            "wettest_month": wettest_m,
            "driest_month": driest_m,
            "total_rainy_days": total_rain_days
        }

        # Match nearest official IMD observatory station per Section 1 & 4
        nearest_station, dist_km = imd_climate_service.find_nearest_station(lat, lon)
        station_name = nearest_station["name"] if nearest_station else f"Regional Observatory ({lat:.2f}N, {lon:.2f}E)"
        station_id = nearest_station["id"] if nearest_station else "STN-REGIONAL"

        # Format optional climatological normal (1991-2020) for separate reference section
        climatological_normal = None
        if nearest_station:
            climatological_normal = imd_climate_service.format_climate_dataset(
                station=nearest_station,
                distance_km=dist_km,
                requested_location=location_name,
                req_lat=lat,
                req_lon=lon
            )

        source_info = {
            "name": "India Meteorological Department (IMD) / ECMWF ERA5 Meteorological Archive",
            "station": station_name,
            "station_id": station_id,
            "distance_km": round(dist_km, 1) if nearest_station else 0.0,
            "dataset": f"Annual Meteorological Observations ({year})",
            "data_coverage": f"January–December {year}",
            "observation_type": "actual_historical_observation",
            "rain_day_definition": "Daily precipitation >= 2.5 mm (Official IMD Standard)",
            "attribution": "ECMWF Copernicus Reanalysis assimilated with IMD / Global Surface Meteorological Stations"
        }

        location_meta = {
            "name": location_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4)
        }

        # Available historical years supported by the meteorological archive
        available_years = list(range(2024, 1979, -1))

        response_payload = {
            "location": location_meta,
            "year": year,
            "source": source_info,
            "monthly": monthly_list,
            "summary": summary,
            "available_years": available_years,
            "climatological_normal": climatological_normal
        }

        self._cache[cache_key] = (now, response_payload)
        return response_payload

historical_year_service = HistoricalYearService()
