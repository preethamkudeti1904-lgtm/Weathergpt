import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "WeatherGPT"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = Field(default="super-secret-weathergpt-sih-key-change-in-prod-2026", validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database: Default to local SQLite fallback if PostgreSQL is not provided
    DATABASE_URL: str = Field(default="sqlite:///./weathergpt.db", validation_alias="DATABASE_URL")

    # Weather Provider ("open-meteo", "openweather", "weatherapi", "imd")
    WEATHER_PROVIDER: str = Field(default="open-meteo", validation_alias="WEATHER_PROVIDER")
    OPENWEATHER_API_KEY: str = Field(default="", validation_alias="OPENWEATHER_API_KEY")
    WEATHERAPI_KEY: str = Field(default="", validation_alias="WEATHERAPI_KEY")
    IMD_API_KEY: str = Field(default="", validation_alias="IMD_API_KEY")

    # AI Provider Keys
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    AI_PROVIDER: str = Field(default="auto", validation_alias="AI_PROVIDER")  # "auto", "gemini", "openai", "heuristic"

    # Maps
    GOOGLE_MAPS_API_KEY: str = Field(default="", validation_alias="GOOGLE_MAPS_API_KEY")

    # Controlled Demo Mode
    DEMO_MODE: bool = Field(default=False, validation_alias="DEMO_MODE")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()
