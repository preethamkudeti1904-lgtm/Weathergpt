import json
import logging
import datetime
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.personalized_alert import (
    UserAlertLocation,
    OfficialAlert,
    AlertGeometry,
    UserAlertDelivery,
    PushSubscription
)
from app.services.alerts.geospatial import haversine_distance, point_in_polygon
from app.services.alerts.push_service import push_service

logger = logging.getLogger("personalized_alert_service")

def normalize_district_name(name: Optional[str]) -> str:
    if not name:
        return ""
    cleaned = name.lower().strip()
    # Remove words like "district", "dist", "division"
    for term in ["district", "dist.", "dist", "division", "district"]:
        cleaned = cleaned.replace(term, "")
    return cleaned.strip()

class PersonalizedAlertService:
    def evaluate_spatial_match(
        self,
        user_lat: float,
        user_lon: float,
        user_district: Optional[str],
        user_state: Optional[str],
        geometries: List[AlertGeometry],
        alert_district: Optional[str] = None,
        alert_state: Optional[str] = None
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Determines if user coordinates fall inside the warning's affected area.
        Priority:
          1. Polygon / MultiPolygon point-in-polygon check.
          2. Circle / Radius centroid distance check.
          3. Strict normalized district equality fallback (NO loose text matching).
        Returns:
          (is_affected, match_type, distance_km)
        """
        # 1. Evaluate Geometries
        for geom in geometries:
            gtype = (geom.geometry_type or "polygon").lower()
            coords_raw = geom.coordinates_json

            # Polygon or MultiPolygon
            if gtype in ["polygon", "multipolygon"] and coords_raw:
                try:
                    coords = json.loads(coords_raw)
                    if gtype == "polygon":
                        # coords is [[lat, lon], ...]
                        poly = [(float(pt[0]), float(pt[1])) for pt in coords if len(pt) >= 2]
                        if len(poly) >= 3 and point_in_polygon(user_lat, user_lon, poly):
                            return True, "polygon", 0.0
                    elif gtype == "multipolygon":
                        # coords is [[[lat, lon], ...], ...]
                        for poly_pts in coords:
                            poly = [(float(pt[0]), float(pt[1])) for pt in poly_pts if len(pt) >= 2]
                            if len(poly) >= 3 and point_in_polygon(user_lat, user_lon, poly):
                                return True, "multipolygon", 0.0
                except Exception as e:
                    logger.debug(f"Error parsing polygon coordinates: {e}")

            # Circle / Radius
            if gtype == "circle" or (geom.centroid_lat is not None and geom.radius_km is not None):
                if geom.centroid_lat is not None and geom.centroid_lon is not None:
                    dist = haversine_distance(user_lat, user_lon, geom.centroid_lat, geom.centroid_lon)
                    radius = geom.radius_km if geom.radius_km and geom.radius_km > 0 else 35.0
                    if dist <= radius:
                        return True, "circle", round(dist, 1)

        # 2. Strict District Fallback (Section 8: Never use loose text matching)
        norm_user_dist = normalize_district_name(user_district)
        norm_alert_dist = normalize_district_name(alert_district)

        if norm_user_dist and norm_alert_dist:
            if norm_user_dist == norm_alert_dist:
                return True, "district", 0.0

        # State fallback only if warning explicitly designates the whole state
        if user_state and alert_state:
            norm_user_state = user_state.lower().strip()
            norm_alert_state = alert_state.lower().strip()
            if norm_user_state == norm_alert_state and norm_alert_dist in ["all", "entire state", "statewide"]:
                return True, "statewide", 0.0

        return False, "none", None

    def should_deliver_alert(
        self,
        db: Session,
        user_id: int,
        alert: OfficialAlert,
        location_id: Optional[int] = None
    ) -> Tuple[bool, bool]:
        """
        Deduplication engine: Checks if alert has already been sent to this user.
        Returns:
          (should_send, is_update)
        """
        existing = db.query(UserAlertDelivery).filter(
            UserAlertDelivery.user_id == user_id,
            UserAlertDelivery.alert_id == alert.id
        ).order_by(UserAlertDelivery.sent_at.desc()).first()

        if not existing:
            return True, False

        # If alert is marked as Update or has newer content
        if alert.status == "Update":
            update_delivery = db.query(UserAlertDelivery).filter(
                UserAlertDelivery.user_id == user_id,
                UserAlertDelivery.alert_id == alert.id,
                UserAlertDelivery.title.like("%Update%")
            ).first()
            if not update_delivery:
                return True, True

        # Duplicate alert already sent
        return False, False

    def get_active_alerts_for_location(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        district: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active official warnings that geographically intersect the user's location.
        """
        now = datetime.datetime.utcnow()
        # Query active, non-expired alerts
        alerts = db.query(OfficialAlert).filter(
            OfficialAlert.is_active == True,
            (OfficialAlert.expires_at == None) | (OfficialAlert.expires_at >= now)
        ).all()

        results = []
        for alert in alerts:
            is_affected, match_type, dist_km = self.evaluate_spatial_match(
                user_lat=latitude,
                user_lon=longitude,
                user_district=district,
                user_state=state,
                geometries=alert.geometries,
                alert_district=alert.district,
                alert_state=alert.state
            )

            if is_affected:
                results.append({
                    "id": alert.id,
                    "source": alert.source,
                    "hazard_type": alert.hazard_type,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity,
                    "status": alert.status,
                    "issued_at": alert.issued_at.isoformat() if alert.issued_at else None,
                    "effective_from": alert.effective_from.isoformat() if alert.effective_from else None,
                    "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
                    "affected_area": alert.affected_area,
                    "district": alert.district,
                    "state": alert.state,
                    "country": alert.country,
                    "instructions": alert.instructions,
                    "source_url": alert.source_url,
                    "match_type": match_type,
                    "distance_km": dist_km,
                    "why_affects_you": (
                        f"Your coordinates ({latitude:.4f}°, {longitude:.4f}°) fall directly within the official {alert.hazard_type} warning boundary."
                        if match_type in ["polygon", "multipolygon", "circle"]
                        else f"Your registered administrative district ({district or 'Region'}) is explicitly placed under this official {alert.hazard_type} warning."
                    )
                })

        return results

    def dispatch_alert_to_user(
        self,
        db: Session,
        user_id: int,
        alert: OfficialAlert,
        location: UserAlertLocation,
        match_type: str,
        language: str = "en"
    ) -> bool:
        """
        Deduplicates, formats, sends Web Push, and logs delivery record.
        """
        should_send, is_update = self.should_deliver_alert(db, user_id, alert, location.id)
        if not should_send:
            logger.info(f"Skipping duplicate alert {alert.id} for user {user_id}")
            return False

        valid_until = alert.expires_at.strftime("%I:%M %p UTC") if alert.expires_at else "Until further notice"
        title, body = push_service.format_alert_message(
            hazard=alert.hazard_type,
            severity=alert.severity,
            location_name=location.location_name,
            valid_until=valid_until,
            source=alert.source,
            language=language,
            is_update=is_update
        )

        # Get active push subscriptions for user
        subscriptions = db.query(PushSubscription).filter(
            PushSubscription.user_id == user_id,
            PushSubscription.is_active == True
        ).all()

        push_sent = False
        payload = {
            "title": title,
            "body": body,
            "tag": f"alert-{alert.id}",
            "data": {
                "alertId": alert.id,
                "url": "/alerts",
                "hazard": alert.hazard_type,
                "severity": alert.severity
            }
        }

        for sub in subscriptions:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            res = push_service.send_push(sub_info, payload)
            if res:
                push_sent = True
            else:
                logger.debug(f"Push send failed for endpoint {sub.endpoint[:30]}...")

        # Record in user_alert_deliveries
        delivery = UserAlertDelivery(
            user_id=user_id,
            alert_id=alert.id,
            location_id=location.id,
            sent_at=datetime.datetime.utcnow(),
            delivery_type="push" if push_sent else "in_app",
            status="sent" if push_sent else "pending_in_app",
            hazard_type=alert.hazard_type,
            severity=alert.severity,
            title=title,
            message=body,
            match_type=match_type
        )
        db.add(delivery)
        db.commit()

        logger.info(
            f"Alert: {alert.id} | User: {user_id} | Location: ({location.latitude}, {location.longitude}) | "
            f"Match: TRUE | Reason: {match_type} | Notification: {'SENT_PUSH' if push_sent else 'STORED_IN_APP'}"
        )
        return True

personalized_alert_service = PersonalizedAlertService()
