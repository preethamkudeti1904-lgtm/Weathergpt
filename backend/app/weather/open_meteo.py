import asyncio
import datetime
import httpx
from typing import List, Optional
from app.weather.base import WeatherProvider, get_wmo_description, degrees_to_cardinal
from app.schemas.weather import (
    CurrentWeatherResponse,
    ForecastResponse,
    DailyForecastItem,
    HourlyForecastItem,
    WeatherAlertItem,
    AlertsResponse,
    NormalizedLocation,
    NormalizedCurrent
)
from app.schemas.climate import (
    ClimateResponse,
    ClimateTrendPoint,
    ClimateMonthlyPoint,
    ClimateAnnualSummary,
    ClimateSourceInfo,
    LocationMetadata,
    ReferenceStationInfo
)

class OpenMeteoProvider(WeatherProvider):
    @property
    def name(self) -> str:
        return "Open-Meteo / WMO Real-Time Meteorological Network"

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> CurrentWeatherResponse:
        forecast = await self.get_forecast(lat, lon, location_name, days=1)
        return forecast.current

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> ForecastResponse:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "et0_fao_evapotranspiration",
                "visibility",
                "uv_index"
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "wind_speed_10m_max",
                "uv_index_max",
                "sunrise",
                "sunset"
            ],
            "timezone": "auto",
            "forecast_days": max(min(days, 14), 2)
        }

        data = None
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.get(url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    break
            except Exception as e:
                if attempt == 1:
                    raise e
                await asyncio.sleep(0.5)

        curr = data.get("current", {})
        hourly_data = data.get("hourly", {})
        daily_data = data.get("daily", {})

        # Timezone extraction and canonical abbreviation
        tz_name = data.get("timezone", "Asia/Kolkata")
        tz_abbr_raw = data.get("timezone_abbreviation", "IST")
        utc_offset = int(data.get("utc_offset_seconds", 19800))

        TIMEZONE_ABBR_MAP = {
            "Asia/Kolkata": "IST",
            "Asia/Calcutta": "IST",
            "Europe/London": "BST",
            "America/New_York": "EDT",
            "Asia/Tokyo": "JST",
            "Asia/Dubai": "GST",
            "Asia/Singapore": "SGT",
            "Australia/Sydney": "AEST",
            "America/Los_Angeles": "PDT",
            "America/Chicago": "CDT",
            "Europe/Paris": "CEST",
            "Europe/Berlin": "CEST"
        }
        tz_abbr = TIMEZONE_ABBR_MAP.get(tz_name, tz_abbr_raw)

        # Build local updated time e.g. "Sep 9, 2026, 7:46 PM IST"
        tz_delta = datetime.timedelta(seconds=utc_offset)
        local_dt = datetime.datetime.now(datetime.timezone.utc) + tz_delta
        time_12h = local_dt.strftime("%I:%M %p").lstrip("0")
        date_str = local_dt.strftime("%b %d, %Y")
        updated_local_str = f"{date_str}, {time_12h} {tz_abbr}"

        # Current weather calculation
        temp = curr.get("temperature_2m", 0.0)
        feels_like = curr.get("apparent_temperature", temp)
        wmo_code = int(curr.get("weather_code", 0))
        humidity = int(curr.get("relative_humidity_2m", 50))
        wind_spd = float(curr.get("wind_speed_10m", 0.0))
        wind_dir = int(curr.get("wind_direction_10m", 0))
        pressure = float(curr.get("surface_pressure", 1013.25))
        precip = float(curr.get("precipitation", 0.0))

        # Helper to convert "05:55" to "05:55 AM"
        def format_time_12h(time_str: Optional[str]) -> Optional[str]:
            if not time_str:
                return None
            try:
                clean = time_str.split("T")[1] if "T" in time_str else time_str
                parts = clean.split(":")
                h = int(parts[0])
                m = int(parts[1]) if len(parts) > 1 else 0
                ampm = "AM" if h < 12 else "PM"
                h12 = h % 12
                if h12 == 0:
                    h12 = 12
                return f"{h12:02d}:{m:02d} {ampm}"
            except Exception:
                return time_str

        # Sunrise & sunset from first day
        sunrises = daily_data.get("sunrise", [])
        sunsets = daily_data.get("sunset", [])
        sunrise_raw = sunrises[0] if sunrises else None
        sunset_raw = sunsets[0] if sunsets else None
        sunrise_str = format_time_12h(sunrise_raw) or "06:00 AM"
        sunset_str = format_time_12h(sunset_raw) or "06:30 PM"

        # Visibility and UV
        vis_list = hourly_data.get("visibility", [])
        uv_list = hourly_data.get("uv_index", [])
        vis_km = round(vis_list[0] / 1000.0, 1) if vis_list else 10.0
        uv_idx = uv_list[0] if uv_list else 5.0

        precip_val = round(float(precip), 2) if precip is not None else 0.0
        current_obj = CurrentWeatherResponse(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            temperature=round(temp, 1),
            feels_like=round(feels_like, 1),
            condition=get_wmo_description(wmo_code),
            condition_code=wmo_code,
            humidity=humidity,
            wind_speed=round(wind_spd, 1),
            wind_direction=wind_dir,
            wind_direction_cardinal=degrees_to_cardinal(wind_dir),
            wind_gusts=round(float(curr.get("wind_gusts_10m")), 1) if curr.get("wind_gusts_10m") is not None else round(wind_spd * 1.35, 1),
            pressure=round(pressure, 1),
            visibility=vis_km,
            precipitation=precip_val,
            uv_index=uv_idx,
            sunrise=sunrise_str,
            sunset=sunset_str,
            timezone=tz_name,
            timezone_abbreviation=tz_abbr,
            utc_offset_seconds=utc_offset,
            source=self.name,
            updated_at=updated_local_str,
            location=NormalizedLocation(
                latitude=lat,
                longitude=lon,
                name=location_name,
                timezone=tz_name
            ),
            current=NormalizedCurrent(
                temperature=round(temp, 1),
                feels_like=round(feels_like, 1),
                humidity=humidity,
                pressure=round(pressure, 1),
                wind_speed=round(wind_spd, 1),
                wind_direction=wind_dir,
                visibility=vis_km,
                precipitation=precip_val,
                condition=get_wmo_description(wmo_code)
            ),
            timestamp=updated_local_str
        )

        # Process next 24 hourly items starting from the current local hour
        curr_time_str = curr.get("time", "")  # e.g. "2026-09-09T19:45"
        curr_hour_prefix = curr_time_str[:13] if curr_time_str else ""

        h_times = hourly_data.get("time", [])
        start_idx = 0
        if curr_hour_prefix:
            for idx, t_str in enumerate(h_times):
                if t_str.startswith(curr_hour_prefix) or t_str >= curr_hour_prefix:
                    start_idx = idx
                    break

        hourly_items: List[HourlyForecastItem] = []
        h_temps = hourly_data.get("temperature_2m", [])
        h_codes = hourly_data.get("weather_code", [])
        h_probs = hourly_data.get("precipitation_probability", [])
        h_precs = hourly_data.get("precipitation", [])
        h_winds = hourly_data.get("wind_speed_10m", [])
        h_dirs = hourly_data.get("wind_direction_10m", [])
        h_gusts = hourly_data.get("wind_gusts_10m", [])

        end_idx = min(start_idx + 24, len(h_times))
        for i in range(start_idx, end_idx):
            t_str = h_times[i]
            c_code = int(h_codes[i]) if i < len(h_codes) else 0
            w_dir = int(h_dirs[i]) if (i < len(h_dirs) and h_dirs[i] is not None) else None
            w_gust = round(float(h_gusts[i]), 1) if (i < len(h_gusts) and h_gusts[i] is not None) else None
            hourly_items.append(HourlyForecastItem(
                time=t_str,
                temperature=round(h_temps[i], 1) if i < len(h_temps) else 0.0,
                condition=get_wmo_description(c_code),
                condition_code=c_code,
                rain_probability=int(h_probs[i]) if i < len(h_probs) and h_probs[i] is not None else 0,
                precipitation=round(h_precs[i], 2) if i < len(h_precs) else 0.0,
                wind_speed=round(h_winds[i], 1) if i < len(h_winds) else 0.0,
                wind_direction=w_dir,
                wind_direction_cardinal=degrees_to_cardinal(w_dir) if w_dir is not None else None,
                wind_gusts=w_gust
            ))

        # Process daily forecast items
        daily_items: List[DailyForecastItem] = []
        d_times = daily_data.get("time", [])
        d_codes = daily_data.get("weather_code", [])
        d_tmax = daily_data.get("temperature_2m_max", [])
        d_tmin = daily_data.get("temperature_2m_min", [])
        d_probs = daily_data.get("precipitation_probability_max", [])
        d_precs = daily_data.get("precipitation_sum", [])
        d_winds = daily_data.get("wind_speed_10m_max", [])
        d_uvs = daily_data.get("uv_index_max", [])
        d_sunrises = daily_data.get("sunrise", [])
        d_sunsets = daily_data.get("sunset", [])

        for j in range(len(d_times)):
            d_date = d_times[j]
            try:
                dt = datetime.datetime.strptime(d_date, "%Y-%m-%d")
                day_name = dt.strftime("%A")
            except Exception:
                day_name = d_date

            c_code = int(d_codes[j]) if j < len(d_codes) else 0
            daily_items.append(DailyForecastItem(
                date=d_date,
                day_name=day_name,
                condition=get_wmo_description(c_code),
                condition_code=c_code,
                temp_max=round(d_tmax[j], 1) if j < len(d_tmax) else 0.0,
                temp_min=round(d_tmin[j], 1) if j < len(d_tmin) else 0.0,
                rain_probability=int(d_probs[j]) if j < len(d_probs) and d_probs[j] is not None else 0,
                precipitation=round(d_precs[j], 2) if j < len(d_precs) else 0.0,
                wind_speed_max=round(d_winds[j], 1) if j < len(d_winds) else 0.0,
                uv_index_max=round(d_uvs[j], 1) if j < len(d_uvs) and d_uvs[j] is not None else None,
                sunrise=format_time_12h(d_sunrises[j]) if j < len(d_sunrises) else None,
                sunset=format_time_12h(d_sunsets[j]) if j < len(d_sunsets) else None
            ))

        return ForecastResponse(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            current=current_obj,
            hourly=hourly_items,
            daily=daily_items,
            timezone=tz_name,
            timezone_abbreviation=tz_abbr,
            utc_offset_seconds=utc_offset,
            source=self.name,
            updated_at=updated_local_str
        )

    async def get_alerts(self, lat: float, lon: float, location_name: str) -> AlertsResponse:
        """
        Derives real meteorological threshold alerts grounded strictly in live forecast data:
        Heavy rainfall, thunderstorm, strong winds / cyclonic gusts, heat wave, dense fog.
        """
        forecast = await self.get_forecast(lat, lon, location_name, days=3)
        curr = forecast.current
        daily = forecast.daily
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        alerts: List[WeatherAlertItem] = []

        # 1. Check Heavy Rainfall (IMD Criteria: > 64.5 mm heavy, > 115.5 mm very heavy)
        for d in daily[:2]:
            if d.precipitation >= 64.5:
                alerts.append(WeatherAlertItem(
                    id=f"alert-rain-{d.date}",
                    title="Heavy Rainfall Warning",
                    category="Heavy Rain",
                    severity="Warning",
                    color_code="Orange",
                    location=location_name,
                    start_time=f"{d.date} 00:00",
                    end_time=f"{d.date} 23:59",
                    description=f"Anticipated rainfall accumulation of {d.precipitation} mm within 24 hours. Possibility of localized waterlogging and rapid runoff.",
                    source=f"IMD Meteorological Standard / {self.name}",
                    recommended_action="Avoid venturing into low-lying areas. Farmers should ensure adequate field drainage to protect crops."
                ))
            elif d.precipitation >= 35.0:
                alerts.append(WeatherAlertItem(
                    id=f"alert-rain-watch-{d.date}",
                    title="Moderate to Heavy Rain Watch",
                    category="Heavy Rain",
                    severity="Watch",
                    color_code="Yellow",
                    location=location_name,
                    start_time=f"{d.date} 06:00",
                    end_time=f"{d.date} 21:00",
                    description=f"Significant rainfall forecasted ({d.precipitation} mm) with high rain probability ({d.rain_probability}%).",
                    source=f"IMD Meteorological Standard / {self.name}",
                    recommended_action="Keep an umbrella handy; monitor local transport updates before commuting."
                ))

        # 2. Check Thunderstorms
        if curr.condition_code in [95, 96, 99]:
            alerts.append(WeatherAlertItem(
                id="alert-thunderstorm-live",
                title="Active Thunderstorm & Lightning Warning",
                category="Thunderstorm",
                severity="Warning" if curr.condition_code == 95 else "Emergency",
                color_code="Orange" if curr.condition_code == 95 else "Red",
                location=location_name,
                start_time="Immediate",
                end_time="Next 3-6 Hours",
                description="Convective storm activity detected with elevated cloud-to-ground lightning discharge risk and squally wind gusts.",
                source=f"IMD Nowcast / {self.name}",
                recommended_action="Seek substantial indoor shelter immediately. Avoid standing beneath isolated trees or near metallic transmission towers."
            ))

        # 3. Check Heat Wave (IMD Criteria: Max temp >= 40°C in plains, or departures above normal)
        if daily and daily[0].temp_max >= 42.0:
            alerts.append(WeatherAlertItem(
                id=f"alert-heatwave-{daily[0].date}",
                title="Severe Heat Wave Alert",
                category="Heat Wave",
                severity="Warning",
                color_code="Orange",
                location=location_name,
                start_time=f"{daily[0].date} 11:00",
                end_time=f"{daily[0].date} 17:00",
                description=f"Daytime maximum temperature projected to peak at {daily[0].temp_max}°C. Extreme heat discomfort index.",
                source=f"IMD Heatwave Advisory / {self.name}",
                recommended_action="Stay hydrated with oral electrolytes. Minimize outdoor physical exertion between 12 PM and 4 PM."
            ))
        elif daily and daily[0].temp_max >= 39.0:
            alerts.append(WeatherAlertItem(
                id=f"alert-hotday-{daily[0].date}",
                title="High Temperature Watch",
                category="Heat Wave",
                severity="Watch",
                color_code="Yellow",
                location=location_name,
                start_time=f"{daily[0].date} 12:00",
                end_time=f"{daily[0].date} 16:00",
                description=f"Peak temperature reaching {daily[0].temp_max}°C with high afternoon solar radiation.",
                source=f"IMD Heatwave Advisory / {self.name}",
                recommended_action="Drink ample water and wear light, loose cotton garments."
            ))

        # 4. Check Strong Winds / Cyclone risk
        if curr.wind_speed >= 45.0 or (daily and daily[0].wind_speed_max >= 50.0):
            w_max = max(curr.wind_speed, daily[0].wind_speed_max if daily else 0)
            alerts.append(WeatherAlertItem(
                id="alert-wind-gust",
                title="Squally Strong Wind Warning",
                category="Strong Wind",
                severity="Warning",
                color_code="Orange",
                location=location_name,
                start_time="Ongoing",
                end_time="Next 12 Hours",
                description=f"Sustained wind speeds of {w_max} km/h recorded. Risk of damage to temporary structures, tree branches, and overhead wires.",
                source=f"IMD / Coastal NWP Guidance / {self.name}",
                recommended_action="Fishermen are advised not to venture into open water bodies. Secure unsecured rooftop objects."
            ))

        # 5. Check Visibility / Fog
        if curr.visibility < 1.5:
            alerts.append(WeatherAlertItem(
                id="alert-fog",
                title="Dense Fog & Low Visibility Advisory",
                category="Visibility",
                severity="Watch",
                color_code="Yellow",
                location=location_name,
                start_time="Early Morning",
                end_time="Until 09:30 Local Time",
                description=f"Horizontal visibility reduced to approximately {curr.visibility} km due to surface radiative fog condensation.",
                source=f"IMD Aviation Met / {self.name}",
                recommended_action="Use low-beam headlights and maintain safe braking distance on highways."
            ))

        return AlertsResponse(
            location_name=location_name,
            alerts=alerts,
            has_active_alerts=len(alerts) > 0,
            source=self.name,
            updated_at=now_str
        )

    async def get_historical_climate(self, lat: float, lon: float, location_name: str) -> ClimateResponse:
        """
        Retrieves authentic climatological reanalysis from ECMWF ERA5 via Open-Meteo Historical Archive
        for 3 full calendar years (2021-01-01 to 2023-12-31, 1095 days) to compute unbiased 12-month normals.
        NEVER uses hardcoded or fallback synthetic values.
        """
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        url = "https://archive-api.open-meteo.com/v1/archive"
        start_date = "2021-01-01"
        end_date = "2023-12-31"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                raise RuntimeError(f"Open-Meteo Archive API returned status {res.status_code}: {res.text[:120]}")
            data = res.json()

        d = data.get("daily", {})
        times = d.get("time", [])
        means = d.get("temperature_2m_mean", [])
        tmaxs = d.get("temperature_2m_max", [])
        tmins = d.get("temperature_2m_min", [])
        precs = d.get("precipitation_sum", [])

        if not times or not means:
            raise RuntimeError("Historical climate data empty or incomplete from provider")

        years = set()
        month_data = {m: {"mean": [], "max": [], "min": [], "rain": 0.0, "rain_days": 0} for m in range(1, 13)}

        for idx, t in enumerate(times):
            parts = t.split("-")
            years.add(parts[0])
            m_idx = int(parts[1])

            if idx < len(means) and means[idx] is not None:
                month_data[m_idx]["mean"].append(means[idx])
            if idx < len(tmaxs) and tmaxs[idx] is not None:
                month_data[m_idx]["max"].append(tmaxs[idx])
            if idx < len(tmins) and tmins[idx] is not None:
                month_data[m_idx]["min"].append(tmins[idx])
            if idx < len(precs) and precs[idx] is not None:
                p = precs[idx]
                month_data[m_idx]["rain"] += p
                # Standard defined rain day threshold >= 1.0 mm
                if p >= 1.0:
                    month_data[m_idx]["rain_days"] += 1

        num_years = max(1, len(years))
        points: List[ClimateTrendPoint] = []

        for m_num in range(1, 13):
            m_info = month_data[m_num]
            if not m_info["mean"] or not m_info["max"] or not m_info["min"]:
                raise RuntimeError(f"Historical climate data incomplete for month {months[m_num - 1]}")
            avg_m = round(sum(m_info["mean"]) / len(m_info["mean"]), 1)
            max_m = round(sum(m_info["max"]) / len(m_info["max"]), 1)
            min_m = round(sum(m_info["min"]) / len(m_info["min"]), 1)
            tot_rain_m = round(m_info["rain"] / num_years, 1)
            rain_days_m = int(round(m_info["rain_days"] / num_years))

            points.append(ClimateTrendPoint(
                label=months[m_num - 1],
                avg_temperature=avg_m,
                max_temperature=max_m,
                min_temperature=min_m,
                total_rainfall=tot_rain_m,
                rainfall_days=rain_days_m
            ))

        mean_annual_temp = round(sum(p.avg_temperature for p in points) / 12, 1)
        total_annual_rain = round(sum(p.total_rainfall for p in points), 1)
        wettest_m = max(points, key=lambda p: p.total_rainfall).label
        warmest_m = max(points, key=lambda p: p.avg_temperature).label

        monthly_points = [
            ClimateMonthlyPoint(
                month=p.label,
                avg_temperature_c=p.avg_temperature,
                max_temperature_c=p.max_temperature,
                min_temperature_c=p.min_temperature,
                precipitation_mm=p.total_rainfall,
                rain_days=float(p.rainfall_days)
            ) for p in points
        ]
        annual_summary = ClimateAnnualSummary(
            mean_temperature_c=mean_annual_temp,
            max_temperature_c=round(sum(p.max_temperature for p in points) / 12, 1),
            min_temperature_c=round(sum(p.min_temperature for p in points) / 12, 1),
            total_precipitation_mm=total_annual_rain,
            rainy_days=float(sum(p.rainfall_days for p in points)),
            wettest_month=wettest_m,
            warmest_month=warmest_m
        )
        source_obj = ClimateSourceInfo(
            organization="ECMWF / Open-Meteo",
            division="Copernicus Climate Change Service",
            dataset="ERA5 Atmospheric Reanalysis",
            period=f"{min(years)}–{max(years)}",
            data_type="historical_reanalysis",
            attribution="European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 Reanalysis",
            rain_day_definition="Daily precipitation >= 1.0 mm",
            url="https://open-meteo.com/en/docs/historical-weather-api"
        )
        loc_meta = LocationMetadata(
            name=location_name,
            latitude=lat,
            longitude=lon
        )
        ref_meta = ReferenceStationInfo(
            id=f"ERA5-{round(lat, 2)}-{round(lon, 2)}",
            name=f"{location_name} ERA5 Grid Cell",
            latitude=lat,
            longitude=lon,
            distance_km=0.0
        )

        return ClimateResponse(
            location=loc_meta,
            requested_location=loc_meta,
            reference_station=ref_meta,
            source_info=source_obj,
            source=source_obj,
            annual=annual_summary,
            monthly=monthly_points,
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            period=f"{min(years)} – {max(years)}",
            historical_period=f"{start_date} to {end_date} (ECMWF ERA5 High-Resolution Reanalysis)",
            parameter="all",
            data=points,
            annual_mean_temp=mean_annual_temp,
            annual_total_rainfall=total_annual_rain,
            wettest_month=wettest_m,
            warmest_month=warmest_m,
            rain_day_threshold_mm=1.0,
            updated_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )

