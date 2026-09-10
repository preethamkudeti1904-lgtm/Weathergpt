import json
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.deps import get_current_user
from app.models.user import User, UserPreference
from app.models.personalized_alert import UserAlertLocation, OfficialAlert
from app.models.sms_alert import UserAlertSmsDelivery
from app.services.sms.service import sms_service
from app.services.alerts.personalized_alert_service import personalized_alert_service

router = APIRouter(tags=["sms_alerts"])

def mask_phone_number(phone: Optional[str]) -> str:
    if not phone:
        return "No phone number linked"
    clean = phone.strip()
    if len(clean) >= 8:
        return clean[:3] + "******" + clean[-4:]
    return clean

class SmsAlertsSettingsUpdate(BaseModel):
    sms_alerts_enabled: bool
    sms_alert_categories: Optional[List[str]] = None

class TestSmsPayload(BaseModel):
    hazard_type: str = "Heavy Rain"
    severity: str = "Warning"
    is_inside_user_area: bool = True

@router.get("/settings/sms-alerts")
def get_sms_alerts_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns user's disaster SMS configuration, masked phone, verification status, and primary location.
    """
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    categories = ["Severe Weather", "Flood", "Cyclone", "Thunderstorm", "Extreme Rain", "Heatwave"]
    if pref and pref.sms_alert_categories:
        try:
            categories = json.loads(pref.sms_alert_categories)
        except Exception:
            pass

    # Primary alert location
    primary_loc = db.query(UserAlertLocation).filter(
        UserAlertLocation.user_id == current_user.id,
        UserAlertLocation.is_active == True,
        UserAlertLocation.is_primary == True
    ).first()

    loc_data = None
    if primary_loc:
        loc_data = {
            "id": primary_loc.id,
            "name": primary_loc.location_name,
            "latitude": primary_loc.latitude,
            "longitude": primary_loc.longitude,
            "district": primary_loc.district,
            "state": primary_loc.state,
            "source": primary_loc.source
        }

    return {
        "phone_number": current_user.phone_number,
        "masked_phone": mask_phone_number(current_user.phone_number),
        "phone_verified": bool(current_user.phone_verified),
        "phone_verified_at": current_user.phone_verified_at.isoformat() if current_user.phone_verified_at else None,
        "sms_alerts_enabled": bool(pref.sms_alerts_enabled) if pref else False,
        "sms_alert_categories": categories,
        "alert_location": loc_data
    }

@router.post("/settings/sms-alerts")
def update_sms_alerts_settings(
    payload: SmsAlertsSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggles SMS disaster alerts and updates category filters.
    Requires verified phone number to enable.
    """
    if payload.sms_alerts_enabled and not current_user.phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Your mobile phone number must be verified via OTP before disaster SMS alerts can be enabled."
        )

    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    pref.sms_alerts_enabled = payload.sms_alerts_enabled
    if payload.sms_alert_categories is not None:
        pref.sms_alert_categories = json.dumps(payload.sms_alert_categories)

    db.commit()
    db.refresh(pref)

    return {
        "success": True,
        "sms_alerts_enabled": pref.sms_alerts_enabled,
        "sms_alert_categories": json.loads(pref.sms_alert_categories) if pref.sms_alert_categories else []
    }

@router.get("/alerts/sms-history")
def get_sms_alert_history(
    limit: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns historical disaster SMS messages delivered to the user.
    """
    deliveries = db.query(UserAlertSmsDelivery).filter(
        UserAlertSmsDelivery.user_id == current_user.id
    ).order_by(UserAlertSmsDelivery.sent_at.desc()).limit(limit).all()

    return {
        "deliveries": [
            {
                "id": d.id,
                "alert_id": d.alert_id,
                "hazard_type": d.hazard_type,
                "severity": d.severity,
                "phone_number": mask_phone_number(d.phone_number),
                "message": d.message,
                "status": d.status,
                "provider_message_id": d.provider_message_id,
                "sent_at": d.sent_at.isoformat() if d.sent_at else None
            }
            for d in deliveries
        ],
        "total": len(deliveries)
    }

@router.post("/notifications/test-sms")
async def send_test_disaster_sms(
    payload: TestSmsPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DEVELOPMENT/TESTING ONLY:
    Sends a test disaster SMS to user's verified phone, validating the message pipeline and delivery record.
    """
    if not current_user.phone_verified or not current_user.phone_number:
        raise HTTPException(
            status_code=400,
            detail="Cannot send test SMS: Mobile phone number is not verified."
        )

    # Get primary alert location
    loc = db.query(UserAlertLocation).filter(
        UserAlertLocation.user_id == current_user.id,
        UserAlertLocation.is_active == True
    ).first()

    loc_name = loc.location_name if loc else current_user.default_location or "Vadlamudi, Andhra Pradesh"

    if not payload.is_inside_user_area:
        return {
            "success": True,
            "dispatched": False,
            "message": "User location is OUTSIDE warning polygon: Test SMS safely withheld as designed."
        }

    # Format official disaster SMS
    valid_until = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%I:%M %p IST")
    sms_text = sms_service.format_disaster_sms(
        hazard=payload.hazard_type,
        severity=payload.severity,
        location_name=loc_name,
        valid_until=valid_until,
        source="SACHET / NDMA (Verified Test)",
        language=current_user.preferred_language or "en",
        is_update=False
    )

    res = await sms_service.send_sms(current_user.phone_number, sms_text)

    # Log delivery in DB
    delivery = UserAlertSmsDelivery(
        user_id=current_user.id,
        alert_id=f"TEST-SMS-{int(datetime.datetime.utcnow().timestamp())}",
        location_id=loc.id if loc else None,
        phone_number=current_user.phone_number,
        sent_at=datetime.datetime.utcnow(),
        status=res.get("status", "SENT"),
        hazard_type=payload.hazard_type,
        severity=payload.severity,
        message=sms_text,
        provider_message_id=res.get("message_id"),
        error_message=res.get("error")
    )
    db.add(delivery)
    db.commit()

    return {
        "success": res.get("success", False),
        "dispatched": True,
        "provider": res.get("provider"),
        "message_id": res.get("message_id"),
        "phone_number": mask_phone_number(current_user.phone_number),
        "status": res.get("status"),
        "message": "Test disaster SMS dispatched successfully."
    }
