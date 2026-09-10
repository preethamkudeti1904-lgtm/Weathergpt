from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from app.schemas.weather import CurrentWeatherResponse, ForecastResponse, AlertsResponse
from app.schemas.climate import ClimateResponse

WMO_CODE_MAP = {
    0: ("Clear sky", "Sunny"),
    1: ("Mainly clear", "Partly Cloudy"),
    2: ("Partly cloudy", "Partly Cloudy"),
    3: ("Overcast", "Overcast"),
    45: ("Foggy", "Fog"),
    48: ("Depositing rime fog", "Fog"),
    51: ("Light drizzle", "Drizzle"),
    53: ("Moderate drizzle", "Drizzle"),
    55: ("Dense drizzle", "Drizzle"),
    56: ("Light freezing drizzle", "Freezing Rain"),
    57: ("Dense freezing drizzle", "Freezing Rain"),
    61: ("Slight rain", "Rain"),
    62: ("Moderate rain", "Rain"),
    63: ("Moderate rain", "Rain"),
    65: ("Heavy rain", "Heavy Rain"),
    66: ("Light freezing rain", "Freezing Rain"),
    67: ("Heavy freezing rain", "Freezing Rain"),
    71: ("Slight snow fall", "Snow"),
    73: ("Moderate snow fall", "Snow"),
    75: ("Heavy snow fall", "Snow"),
    77: ("Snow grains", "Snow"),
    80: ("Slight rain showers", "Showers"),
    81: ("Moderate rain showers", "Showers"),
    82: ("Violent rain showers", "Heavy Showers"),
    85: ("Slight snow showers", "Snow Showers"),
    86: ("Heavy snow showers", "Snow Showers"),
    95: ("Thunderstorm", "Thunderstorm"),
    96: ("Thunderstorm with slight hail", "Thunderstorm Hail"),
    99: ("Thunderstorm with heavy hail", "Severe Thunderstorm"),
}

def get_wmo_description(code: int) -> str:
    return WMO_CODE_MAP.get(code, ("Unknown", "Cloudy"))[0]

def degrees_to_cardinal(deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((deg + 11.25) / 22.5) % 16
    return dirs[ix]

class WeatherProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> CurrentWeatherResponse:
        pass

    @abstractmethod
    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> ForecastResponse:
        pass

    @abstractmethod
    async def get_alerts(self, lat: float, lon: float, location_name: str) -> AlertsResponse:
        pass

    @abstractmethod
    async def get_historical_climate(self, lat: float, lon: float, location_name: str) -> ClimateResponse:
        pass
