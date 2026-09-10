import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.session import engine, Base
import app.models  # Ensures all models are registered with Base

# Import API Routers
from app.api.auth import router as auth_router
from app.api.weather import router as weather_router
from app.api.chat import router as chat_router
from app.api.locations import router as locations_router
from app.api.climate import router as climate_router
from app.api.advisory import router as advisory_router
from app.api.nwp import router as nwp_router
from app.api.personalized_alerts import router as personalized_alerts_router, notifications_router
from app.api.sms_alerts import router as sms_alerts_router
from app.services.alerts.alert_monitor_worker import alert_monitor_worker
from app.services.alerts.disaster_sms_worker import disaster_sms_worker
import asyncio

# Create database tables automatically
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[Database Warning] Table initialization note: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="Conversational AI for Weather Forecasting, Alerts & Climate Information - IMD / MoES SIH Platform",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits dev and production origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(weather_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(locations_router, prefix=settings.API_V1_STR)
app.include_router(climate_router, prefix=settings.API_V1_STR)
app.include_router(advisory_router, prefix=settings.API_V1_STR)
app.include_router(nwp_router, prefix=settings.API_V1_STR)
app.include_router(personalized_alerts_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(sms_alerts_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(alert_monitor_worker.start_loop())
    asyncio.create_task(disaster_sms_worker.start_loop())


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "Conversational AI for Weather Forecasting, Alerts & Climate Information",
        "version": settings.VERSION,
        "status": "Operational",
        "demo_mode": settings.DEMO_MODE,
        "weather_provider": settings.WEATHER_PROVIDER,
        "documentation": f"{settings.API_V1_STR}/docs"
    }

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": "connected",
        "weather_service": "active",
        "ai_engine": "ready"
    }

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An error occurred: {str(exc)}"}
    )
