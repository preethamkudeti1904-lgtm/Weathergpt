from typing import Optional
from fastapi import APIRouter, Query
from app.weather.nwp_service import nwp_service

router = APIRouter(prefix="/nwp", tags=["Numerical Weather Prediction (GFS/WRF)"])

@router.get("/status")
async def get_nwp_status():
    return await nwp_service.get_model_status()

@router.get("/gfs")
async def get_gfs_forecast(
    lat: float = Query(default=16.3067),
    lon: float = Query(default=80.4365)
):
    return await nwp_service.get_gfs_forecast(lat=lat, lon=lon)

@router.get("/wrf")
async def get_wrf_forecast(
    lat: float = Query(default=16.3067),
    lon: float = Query(default=80.4365)
):
    return await nwp_service.get_wrf_forecast(lat=lat, lon=lon)
