import asyncio
import json
import logging
import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.personalized_alert import UserAlertLocation, OfficialAlert, AlertGeometry
from app.models.user import User
from app.services.alerts.sachet_provider import sachet_provider
from app.services.alerts.personalized_alert_service import personalized_alert_service

logger = logging.getLogger("alert_monitor_worker")

class AlertMonitorWorker:
    def __init__(self):
        self.interval_seconds = 300  # 5 minutes
        self.is_running = False
        self.last_run: Optional[datetime.datetime] = None
        self.last_status: str = "operational"
        self.last_stats: Dict[str, Any] = {
            "alerts_fetched": 0,
            "locations_evaluated": 0,
            "deliveries_dispatched": 0
        }

    async def ingest_official_alerts(self, db: Session) -> int:
        """
        Fetches official alerts from SACHET NDMA & IMD feeds, normalizes them,
        and synchronizes with the official_alerts table.
        """
        raw_alerts, status = await sachet_provider.fetch_all_alerts()
        nowcasts = await sachet_provider.fetch_imd_nowcasts()
        self.last_status = status

        total_ingested = 0
        all_items = raw_alerts + nowcasts

        for raw in all_items:
            try:
                parsed = sachet_provider.parse_alert_item(raw)
                alert_id = parsed["id"]
                if not alert_id:
                    continue

                # Check if exists
                existing = db.query(OfficialAlert).filter(OfficialAlert.id == alert_id).first()
                is_expired = parsed.get("is_expired", False)

                # Parse times
                issued_at = None
                expires_at = None
                try:
                    s_str = parsed.get("start_time", "").replace(" IST", "")
                    e_str = parsed.get("end_time", "").replace(" IST", "")
                    if s_str and "Immediate" not in s_str:
                        issued_at = datetime.datetime.strptime(s_str, "%a %b %d %H:%M:%S %Y")
                    if e_str and "not specified" not in e_str:
                        expires_at = datetime.datetime.strptime(e_str, "%a %b %d %H:%M:%S %Y")
                except Exception:
                    pass

                instructions_text = "; ".join(parsed.get("safety_precautions", []))

                if not existing:
                    new_alert = OfficialAlert(
                        id=alert_id,
                        source=parsed.get("source", "SACHET / NDMA"),
                        hazard_type=parsed.get("category", "Severe Weather"),
                        title=parsed.get("title", "Weather Alert"),
                        description=parsed.get("description", ""),
                        severity=parsed.get("severity", "Warning"),
                        status="Actual",
                        issued_at=issued_at or datetime.datetime.utcnow(),
                        effective_from=issued_at or datetime.datetime.utcnow(),
                        expires_at=expires_at,
                        affected_area=parsed.get("location", ""),
                        district=parsed.get("location", ""),
                        country="India",
                        instructions=instructions_text,
                        is_active=not is_expired,
                        raw_data=json.dumps(raw)
                    )
                    db.add(new_alert)
                    db.flush()

                    # Add centroid/radius geometry if available
                    c_lat = parsed.get("centroid_lat")
                    c_lon = parsed.get("centroid_lon")
                    rad_km = parsed.get("radius_km", 35.0)

                    geom = AlertGeometry(
                        alert_id=alert_id,
                        geometry_type="circle" if (c_lat and c_lon) else "district",
                        centroid_lat=c_lat,
                        centroid_lon=c_lon,
                        radius_km=rad_km
                    )
                    db.add(geom)
                    total_ingested += 1
                else:
                    # Update status and expiry
                    existing.is_active = not is_expired
                    if expires_at:
                        existing.expires_at = expires_at
                    total_ingested += 1

            except Exception as e:
                logger.debug(f"Error ingesting alert item: {e}")

        db.commit()
        return total_ingested

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Executes a single end-to-end monitoring and delivery cycle.
        """
        logger.info("Executing Disaster Alert Monitoring Cycle...")
        db: Session = SessionLocal()
        deliveries_count = 0
        locations_count = 0

        try:
            # 1. Ingest latest official warnings
            alerts_count = await self.ingest_official_alerts(db)

            # 2. Query active consented user alert locations
            active_locations = db.query(UserAlertLocation).filter(
                UserAlertLocation.is_active == True
            ).all()
            locations_count = len(active_locations)

            # 3. Query active official alerts
            now = datetime.datetime.utcnow()
            active_alerts = db.query(OfficialAlert).filter(
                OfficialAlert.is_active == True,
                (OfficialAlert.expires_at == None) | (OfficialAlert.expires_at >= now)
            ).all()

            # 4. Check each user location
            for loc in active_locations:
                user = db.query(User).filter(User.id == loc.user_id).first()
                user_lang = user.preferred_language if user else "en"

                for alert in active_alerts:
                    is_affected, match_type, dist = personalized_alert_service.evaluate_spatial_match(
                        user_lat=loc.latitude,
                        user_lon=loc.longitude,
                        user_district=loc.district or loc.location_name,
                        user_state=loc.state,
                        geometries=alert.geometries,
                        alert_district=alert.district,
                        alert_state=alert.state
                    )

                    if is_affected:
                        dispatched = personalized_alert_service.dispatch_alert_to_user(
                            db=db,
                            user_id=loc.user_id,
                            alert=alert,
                            location=loc,
                            match_type=match_type,
                            language=user_lang
                        )
                        if dispatched:
                            deliveries_count += 1

            self.last_run = datetime.datetime.utcnow()
            self.last_stats = {
                "alerts_fetched": alerts_count,
                "locations_evaluated": locations_count,
                "deliveries_dispatched": deliveries_count,
                "timestamp": self.last_run.isoformat()
            }
            logger.info(f"Monitoring cycle complete: {self.last_stats}")
            return self.last_stats

        except Exception as e:
            logger.error(f"Error during alert monitoring cycle: {e}")
            self.last_status = "error"
            return {"error": str(e)}
        finally:
            db.close()

    async def start_loop(self):
        """
        Long-running background task that repeats every 5 minutes.
        """
        self.is_running = True
        logger.info("Disaster Alert Monitor Worker started.")
        # Run first cycle shortly after boot
        await asyncio.sleep(5)
        while self.is_running:
            try:
                await self.run_cycle()
            except Exception as e:
                logger.error(f"Worker iteration failure: {e}")
            await asyncio.sleep(self.interval_seconds)

    def stop(self):
        self.is_running = False

alert_monitor_worker = AlertMonitorWorker()
