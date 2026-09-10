import asyncio
import json
import logging
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.personalized_alert import UserAlertLocation, OfficialAlert
from app.models.sms_alert import UserAlertSmsDelivery
from app.models.user import User, UserPreference
from app.services.sms.service import sms_service
from app.services.alerts.personalized_alert_service import personalized_alert_service
from app.services.alerts.alert_monitor_worker import alert_monitor_worker

logger = logging.getLogger("disaster_sms_worker")

class DisasterSmsWorker:
    def __init__(self):
        self.interval_seconds = 300  # 5 minutes
        self.is_running = False
        self.last_run: Optional[datetime.datetime] = None
        self.last_status: str = "operational"
        self.last_stats: Dict[str, Any] = {
            "users_evaluated": 0,
            "sms_dispatched": 0,
            "duplicates_suppressed": 0
        }

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Evaluates active official warnings against all phone-verified users with SMS alerts enabled.
        """
        logger.info("Executing Disaster SMS Worker cycle...")
        db: Session = SessionLocal()
        sms_sent_count = 0
        duplicates_count = 0
        users_count = 0

        try:
            # 1. Ensure official warnings are ingested
            await alert_monitor_worker.ingest_official_alerts(db)

            # 2. Query active official alerts
            now = datetime.datetime.utcnow()
            active_alerts = db.query(OfficialAlert).filter(
                OfficialAlert.is_active == True,
                (OfficialAlert.expires_at == None) | (OfficialAlert.expires_at >= now)
            ).all()

            if not active_alerts:
                logger.info("No active official warnings found for SMS dispatch.")
                self.last_run = now
                return {"status": "no_active_alerts", "sms_dispatched": 0}

            # 3. Query all users with phone_verified == True and SMS alerts enabled
            eligible_users = (
                db.query(User)
                .join(UserPreference, User.id == UserPreference.user_id)
                .filter(
                    User.phone_verified == True,
                    User.phone_number != None,
                    UserPreference.sms_alerts_enabled == True
                )
                .all()
            )
            users_count = len(eligible_users)

            for user in eligible_users:
                # Parse user's category preferences
                allowed_categories = []
                try:
                    if user.preferences and user.preferences.sms_alert_categories:
                        allowed_categories = json.loads(user.preferences.sms_alert_categories)
                except Exception:
                    pass

                # Get user's primary active alert location
                loc = db.query(UserAlertLocation).filter(
                    UserAlertLocation.user_id == user.id,
                    UserAlertLocation.is_active == True,
                    UserAlertLocation.is_primary == True
                ).first()

                if not loc:
                    # Fallback to first active location
                    loc = db.query(UserAlertLocation).filter(
                        UserAlertLocation.user_id == user.id,
                        UserAlertLocation.is_active == True
                    ).first()

                if not loc:
                    continue

                for alert in active_alerts:
                    # Check category filter if specified
                    if allowed_categories and not any(cat.lower() in alert.hazard_type.lower() for cat in allowed_categories):
                        continue

                    # Geospatial point-in-polygon matching
                    is_affected, match_type, dist = personalized_alert_service.evaluate_spatial_match(
                        user_lat=loc.latitude,
                        user_lon=loc.longitude,
                        user_district=loc.district or loc.location_name,
                        user_state=loc.state,
                        geometries=alert.geometries,
                        alert_district=alert.district,
                        alert_state=alert.state
                    )

                    if not is_affected:
                        continue

                    # Deduplication check
                    existing = db.query(UserAlertSmsDelivery).filter(
                        UserAlertSmsDelivery.user_id == user.id,
                        UserAlertSmsDelivery.alert_id == alert.id,
                        UserAlertSmsDelivery.location_id == loc.id
                    ).order_by(UserAlertSmsDelivery.sent_at.desc()).first()

                    is_update = False
                    if existing:
                        if alert.status == "Update":
                            update_delivery = db.query(UserAlertSmsDelivery).filter(
                                UserAlertSmsDelivery.user_id == user.id,
                                UserAlertSmsDelivery.alert_id == alert.id,
                                UserAlertSmsDelivery.message.like("%UPDATE%")
                            ).first()
                            if not update_delivery:
                                is_update = True
                            else:
                                duplicates_count += 1
                                continue
                        else:
                            duplicates_count += 1
                            continue

                    # Format message
                    valid_until = alert.expires_at.strftime("%I:%M %p IST") if alert.expires_at else "Until further notice"
                    sms_text = sms_service.format_disaster_sms(
                        hazard=alert.hazard_type,
                        severity=alert.severity,
                        location_name=loc.location_name,
                        valid_until=valid_until,
                        source=alert.source,
                        language=user.preferred_language or "en",
                        is_update=is_update
                    )

                    # Send SMS via provider
                    res = await sms_service.send_sms(user.phone_number, sms_text)

                    delivery = UserAlertSmsDelivery(
                        user_id=user.id,
                        alert_id=alert.id,
                        location_id=loc.id,
                        phone_number=user.phone_number,
                        sent_at=datetime.datetime.utcnow(),
                        status=res.get("status", "SENT"),
                        hazard_type=alert.hazard_type,
                        severity=alert.severity,
                        message=sms_text,
                        provider_message_id=res.get("message_id"),
                        error_message=res.get("error")
                    )
                    db.add(delivery)
                    db.commit()
                    sms_sent_count += 1

                    logger.info(
                        f"SMS Alert: {alert.id} | User: {user.id} | Phone: {user.phone_number} | "
                        f"Status: {res.get('status')} | ID: {res.get('message_id')}"
                    )

            self.last_run = datetime.datetime.utcnow()
            self.last_stats = {
                "users_evaluated": users_count,
                "sms_dispatched": sms_sent_count,
                "duplicates_suppressed": duplicates_count,
                "timestamp": self.last_run.isoformat()
            }
            logger.info(f"Disaster SMS cycle complete: {self.last_stats}")
            return self.last_stats

        except Exception as e:
            logger.error(f"Error in Disaster SMS Worker cycle: {e}")
            self.last_status = "error"
            return {"error": str(e)}
        finally:
            db.close()

    async def start_loop(self):
        """
        Long-running background task that monitors official alerts and dispatches SMS alerts.
        """
        self.is_running = True
        logger.info("Disaster SMS Worker background loop initialized.")
        await asyncio.sleep(8)
        while self.is_running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Disaster SMS worker loop error: {e}")
            await asyncio.sleep(self.interval_seconds)

    def stop(self):
        self.is_running = False

disaster_sms_worker = DisasterSmsWorker()
