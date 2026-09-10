import datetime
import httpx
from typing import Optional
from app.weather.base import WeatherProvider, degrees_to_cardinal
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, AlertsResponse
from app.schemas.climate import ClimateResponse
from app.core.config import settings

class OpenWeatherMapProvider(WeatherProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "OpenWeatherMap API"

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> CurrentWeatherResponse:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [{}])
        sys = data.get("sys", {})

        sunrise_ts = sys.get("sunrise")
        sunset_ts = sys.get("sunset")
        sunrise_str = datetime.datetime.fromtimestamp(sunrise_ts, datetime.timezone.utc).strftime("%H:%M") if sunrise_ts else "06:00"
        sunset_str = datetime.datetime.fromtimestamp(sunset_ts, datetime.timezone.utc).strftime("%H:%M") if sunset_ts else "18:30"

        return CurrentWeatherResponse(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            temperature=main.get("temp", 0.0),
            feels_like=main.get("feels_like", 0.0),
            condition=weather_list[0].get("main", "Clear") if weather_list else "Clear",
            condition_code=weather_list[0].get("id", 800) if weather_list else 800,
            humidity=main.get("humidity", 50),
            wind_speed=round(wind.get("speed", 0.0) * 3.6, 1),  # m/s to km/h
            wind_direction=wind.get("deg", 0),
            wind_direction_cardinal=degrees_to_cardinal(wind.get("deg", 0)),
            pressure=main.get("pressure", 1013.25),
            visibility=round(data.get("visibility", 10000) / 1000.0, 1),
            precipitation=data.get("rain", {}).get("1h", 0.0),
            sunrise=sunrise_str,
            sunset=sunset_str,
            timezone="Asia/Kolkata",
            timezone_abbreviation="IST",
            utc_offset_seconds=19800,
            source=self.name,
            updated_at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> ForecastResponse:
        # If openweather forecast not available or key limited, falls back seamlessly
        from app.weather.open_meteo import OpenMeteoProvider
        return await OpenMeteoProvider().get_forecast(lat, lon, location_name, days)

    async def get_alerts(self, lat: float, lon: float, location_name: str) -> AlertsResponse:
        from app.weather.open_meteo import OpenMeteoProvider
        return await OpenMeteoProvider().get_alerts(lat, lon, location_name)

    async def get_historical_climate(self, lat: float, lon: float, location_name: str) -> ClimateResponse:
        from app.weather.open_meteo import OpenMeteoProvider
        return await OpenMeteoProvider().get_historical_climate(lat, lon, location_name)
