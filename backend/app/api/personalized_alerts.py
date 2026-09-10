import datetime
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.deps import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.personalized_alert import (
    UserAlertLocation,
    PushSubscription,
    OfficialAlert,
    AlertGeometry,
    UserAlertDelivery,
)
from app.services.alerts.push_service import push_service
from app.services.alerts.personalized_alert_service import personalized_alert_service
from app.services.alerts.alert_monitor_worker import alert_monitor_worker

router = APIRouter(prefix="/alerts", tags=["personalized_alerts"])
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

# --- Schemas ---
class AlertLocationCreate(BaseModel):
    latitude: float
    longitude: float
    location_name: str
    locality: Optional[str] = None
    village: Optional[str] = None
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    timezone: str = "Asia/Kolkata"
    accuracy: Optional[float] = None
    source: str = "gps"
    label: str = "Primary"
    is_primary: bool = True
    is_active: bool = True

class AlertLocationUpdate(BaseModel):
    label: Optional[str] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None

class PushSubscribePayload(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    user_agent: Optional[str] = None

class TestAlertPayload(BaseModel):
    hazard_type: str = "Heavy Rain"
    severity: str = "Warning"
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    is_inside_user_area: bool = True
    is_update: bool = False
    custom_polygon: Optional[List[List[float]]] = None

# --- Endpoints ---

@router.post("/location")
def save_alert_location(
    data: AlertLocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves or updates a user's consented alert location.
    If is_primary is True, demotes any other primary location.
    """
    if data.is_primary:
        db.query(UserAlertLocation).filter(
            UserAlertLocation.user_id == current_user.id,
            UserAlertLocation.is_primary == True
        ).update({"is_primary": False})

    # Check if exact coordinates already registered for this user
    existing = db.query(UserAlertLocation).filter(
        UserAlertLocation.user_id == current_user.id,
        UserAlertLocation.latitude == data.latitude,
        UserAlertLocation.longitude == data.longitude
    ).first()

    if existing:
        existing.location_name = data.location_name
        existing.district = data.district
        existing.state = data.state
        existing.country = data.country
        existing.timezone = data.timezone
        existing.accuracy = data.accuracy
        existing.source = data.source
        existing.label = data.label
        existing.is_primary = data.is_primary
        existing.is_active = data.is_active
        existing.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    new_loc = UserAlertLocation(
        user_id=current_user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        location_name=data.location_name,
        locality=data.locality,
        village=data.village,
        mandal=data.mandal,
        district=data.district,
        state=data.state,
        country=data.country,
        timezone=data.timezone,
        accuracy=data.accuracy,
        source=data.source,
        label=data.label,
        is_primary=data.is_primary,
        is_active=data.is_active
    )
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@router.get("/my-location")
def get_user_alert_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all registered alert locations for the authenticated user.
    """
    locations = db.query(UserAlertLocation).filter(
        UserAlertLocation.user_id == current_user.id
    ).order_by(UserAlertLocation.is_primary.desc(), UserAlertLocation.created_at.desc()).all()

    # Check push subscription status
    has_push = db.query(PushSubscription).filter(
        PushSubscription.user_id == current_user.id,
        PushSubscription.is_active == True
    ).first() is not None

    return {
        "locations": locations,
        "total": len(locations),
        "push_enabled": has_push,
        "monitoring_active": any(l.is_active for l in locations)
    }

@router.put("/location/{location_id}")
def update_alert_location(
    location_id: int,
    data: AlertLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    loc = db.query(UserAlertLocation).filter(
        UserAlertLocation.id == location_id,
        UserAlertLocation.user_id == current_user.id
    ).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Alert location not found")

    if data.label is not None:
        loc.label = data.label
    if data.is_active is not None:
        loc.is_active = data.is_active
    if data.is_primary is not None:
        if data.is_primary:
            db.query(UserAlertLocation).filter(
                UserAlertLocation.user_id == current_user.id,
                UserAlertLocation.id != location_id
            ).update({"is_primary": False})
        loc.is_primary = data.is_primary

    loc.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(loc)
    return loc

@router.delete("/location/{location_id}")
def delete_alert_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    loc = db.query(UserAlertLocation).filter(
        UserAlertLocation.id == location_id,
        UserAlertLocation.user_id == current_user.id
    ).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Alert location not found")
    db.delete(loc)
    db.commit()
    return {"message": "Location removed from alert monitoring"}

@router.get("/active")
def get_active_location_alerts(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    district: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Returns active official alerts that spatially intersect the user's coordinates/district.
    Uses authenticated user's primary alert location if lat/lon are not explicitly provided.
    """
    target_lat = lat
    target_lon = lon
    target_district = district
    target_state = state

    if (target_lat is None or target_lon is None) and current_user:
        primary_loc = db.query(UserAlertLocation).filter(
            UserAlertLocation.user_id == current_user.id,
            UserAlertLocation.is_primary == True,
            UserAlertLocation.is_active == True
        ).first()
        if primary_loc:
            target_lat = primary_loc.latitude
            target_lon = primary_loc.longitude
            target_district = primary_loc.district or primary_loc.location_name
            target_state = primary_loc.state

    if target_lat is None or target_lon is None:
        # Default fallback
        target_lat = 16.3067
        target_lon = 80.4365
        target_district = "Guntur District"
        target_state = "Andhra Pradesh"

    alerts = personalized_alert_service.get_active_alerts_for_location(
        db=db,
        latitude=target_lat,
        longitude=target_lon,
        district=target_district,
        state=target_state
    )

    return {
        "location": {
            "latitude": target_lat,
            "longitude": target_lon,
            "district": target_district,
            "state": target_state
        },
        "has_active_alerts": len(alerts) > 0,
        "count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@router.get("/history")
def get_alert_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns historical delivered alerts for the authenticated user.
    """
    deliveries = db.query(UserAlertDelivery).filter(
        UserAlertDelivery.user_id == current_user.id
    ).order_by(UserAlertDelivery.sent_at.desc()).limit(limit).all()

    return {
        "deliveries": [
            {
                "id": d.id,
                "alert_id": d.alert_id,
                "hazard_type": d.hazard_type,
                "severity": d.severity,
                "title": d.title,
                "message": d.message,
                "delivery_type": d.delivery_type,
                "status": d.status,
                "match_type": d.match_type,
                "sent_at": d.sent_at.isoformat() if d.sent_at else None
            }
            for d in deliveries
        ],
        "total": len(deliveries)
    }

@router.get("/status")
def get_monitor_status(db: Session = Depends(get_db)):
    """
    Returns monitoring engine status, last run time, and statistics.
    """
    total_locations = db.query(UserAlertLocation).filter(UserAlertLocation.is_active == True).count()
    total_subscriptions = db.query(PushSubscription).filter(PushSubscription.is_active == True).count()
    active_warnings = db.query(OfficialAlert).filter(OfficialAlert.is_active == True).count()

    return {
        "status": alert_monitor_worker.last_status,
        "is_running": alert_monitor_worker.is_running,
        "last_run": alert_monitor_worker.last_run.isoformat() if alert_monitor_worker.last_run else None,
        "monitored_user_locations": total_locations,
        "active_push_subscriptions": total_subscriptions,
        "active_official_warnings": active_warnings,
        "last_stats": alert_monitor_worker.last_stats
    }

@router.post("/test")
async def trigger_test_alert(
    payload: TestAlertPayload,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    DEVELOPMENT/SIMULATION ONLY:
    Creates a simulated official alert, tests spatial matching against user's location,
    dispatches Web Push, and verifies deduplication.
    """
    # 1. Resolve user location
    user_id = current_user.id if current_user else 1
    user_loc = None
    if current_user:
        user_loc = db.query(UserAlertLocation).filter(
            UserAlertLocation.user_id == current_user.id,
            UserAlertLocation.is_active == True
        ).first()

    u_lat = user_loc.latitude if user_loc else 16.2246  # Vadlamudi coordinates
    u_lon = user_loc.longitude if user_loc else 80.5589

    sim_id = f"SIM-ALERT-{int(datetime.datetime.utcnow().timestamp())}" if not payload.is_update else "SIM-ALERT-PERSISTENT"

    # Define warning polygon based on whether user is affected
    if payload.is_inside_user_area:
        # Create small polygon around user location (+/- 0.05 degrees ~ 5km)
        poly = [
            [u_lat - 0.05, u_lon - 0.05],
            [u_lat - 0.05, u_lon + 0.05],
            [u_lat + 0.05, u_lon + 0.05],
            [u_lat + 0.05, u_lon - 0.05]
        ]
        affected_name = f"Area surrounding {user_loc.location_name if user_loc else 'Vadlamudi'}"
    else:
        # Polygon far away from user location (+5.0 degrees away)
        poly = [
            [u_lat + 4.9, u_lon + 4.9],
            [u_lat + 4.9, u_lon + 5.1],
            [u_lat + 5.1, u_lon + 5.1],
            [u_lat + 5.1, u_lon + 4.9]
        ]
        affected_name = "Distant Region (Non-affecting simulation)"

    if payload.custom_polygon:
        poly = payload.custom_polygon

    # Create official alert record in DB
    existing_alert = db.query(OfficialAlert).filter(OfficialAlert.id == sim_id).first()
    if not existing_alert:
        test_alert = OfficialAlert(
            id=sim_id,
            source="NDMA / SACHET Simulation Agency",
            hazard_type=payload.hazard_type,
            title=payload.title or f"Simulated {payload.severity} {payload.hazard_type} Warning",
            description=payload.description or f"Meteorological simulation of {payload.hazard_type} for test verification.",
            severity=payload.severity,
            status="Update" if payload.is_update else "Actual",
            issued_at=datetime.datetime.utcnow(),
            effective_from=datetime.datetime.utcnow(),
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=4),
            affected_area=affected_name,
            district=user_loc.district if (user_loc and payload.is_inside_user_area) else "Distant District",
            state=user_loc.state if user_loc else "Andhra Pradesh",
            country="India",
            instructions=payload.instructions or "Move to sturdy shelter and disconnect electrical equipment.",
            is_active=True
        )
        db.add(test_alert)
        db.flush()

        geom = AlertGeometry(
            alert_id=sim_id,
            geometry_type="polygon",
            coordinates_json=json.dumps(poly),
            centroid_lat=u_lat if payload.is_inside_user_area else u_lat + 5.0,
            centroid_lon=u_lon if payload.is_inside_user_area else u_lon + 5.0,
            radius_km=15.0
        )
        db.add(geom)
    else:
        test_alert = existing_alert
        test_alert.status = "Update"
        test_alert.title = f"Updated Simulated {payload.severity} {payload.hazard_type} Warning"
        test_alert.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(test_alert)

    # Evaluate match
    is_affected, match_type, dist = personalized_alert_service.evaluate_spatial_match(
        user_lat=u_lat,
        user_lon=u_lon,
        user_district=user_loc.district if user_loc else "Guntur District",
        user_state=user_loc.state if user_loc else "Andhra Pradesh",
        geometries=test_alert.geometries,
        alert_district=test_alert.district,
        alert_state=test_alert.state
    )

    dispatched = False
    delivery_status = "not_affected"

    if is_affected and user_loc:
        dispatched = personalized_alert_service.dispatch_alert_to_user(
            db=db,
            user_id=user_id,
            alert=test_alert,
            location=user_loc,
            match_type=match_type,
            language=current_user.preferred_language if current_user else "en"
        )
        delivery_status = "delivered" if dispatched else "duplicate_suppressed"

    return {
        "alert_id": sim_id,
        "is_inside_user_area": payload.is_inside_user_area,
        "spatial_match": is_affected,
        "match_type": match_type,
        "distance_km": dist,
        "delivery_status": delivery_status,
        "user_coordinates": {"latitude": u_lat, "longitude": u_lon},
        "simulated_polygon": poly,
        "message": (
            "User location verified INSIDE warning area: Push notification dispatched."
            if is_affected and dispatched
            else "Duplicate alert detected: Notification suppressed." if is_affected and not dispatched
            else "User location is OUTSIDE warning area: Notification safely withheld as designed."
        )
    }

# --- Notifications Push Router ---

@notifications_router.get("/vapid-public-key")
def get_vapid_public_key():
    """
    Returns public VAPID key to configure browser PushManager.subscribe()
    """
    return {"publicKey": push_service.get_public_key()}

@notifications_router.post("/subscribe")
def subscribe_push_notification(
    payload: PushSubscribePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registers or refreshes browser Web Push subscription for authenticated user.
    """
    existing = db.query(PushSubscription).filter(
        PushSubscription.endpoint == payload.endpoint
    ).first()

    if existing:
        existing.user_id = current_user.id
        existing.p256dh = payload.p256dh
        existing.auth = payload.auth
        existing.user_agent = payload.user_agent
        existing.is_active = True
        existing.updated_at = datetime.datetime.utcnow()
        db.commit()
        return {"message": "Push subscription updated", "id": existing.id}

    new_sub = PushSubscription(
        user_id=current_user.id,
        endpoint=payload.endpoint,
        p256dh=payload.p256dh,
        auth=payload.auth,
        user_agent=payload.user_agent,
        is_active=True
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return {"message": "Push subscription registered", "id": new_sub.id}

@notifications_router.delete("/subscribe")
def unsubscribe_push_notification(
    endpoint: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(PushSubscription).filter(
        PushSubscription.endpoint == endpoint,
        PushSubscription.user_id == current_user.id
    ).first()
    if sub:
        sub.is_active = False
        db.commit()
    return {"message": "Push subscription deactivated"}
