import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class UserAlertLocation(Base):
    __tablename__ = "user_alert_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(255), nullable=False)
    locality = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    mandal = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), default="India")
    timezone = Column(String(50), default="Asia/Kolkata")
    accuracy = Column(Float, nullable=True)
    source = Column(String(50), default="gps")  # gps, search, map, saved
    label = Column(String(100), default="Primary")  # Primary, Home, Farm, College, Other
    is_primary = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)  # User can toggle monitoring on/off
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="alert_locations")
    deliveries = relationship("UserAlertDelivery", back_populates="location", cascade="all, delete-orphan")


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, unique=True, nullable=False, index=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    user_agent = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="push_subscriptions")


class OfficialAlert(Base):
    __tablename__ = "official_alerts"

    id = Column(String(150), primary_key=True, index=True)  # CAP Identifier
    source = Column(String(100), nullable=False, index=True)  # SACHET, NDMA, IMD, CWC, INCOIS, etc.
    hazard_type = Column(String(100), nullable=False, index=True)  # Thunderstorm, Heavy Rain, Flood, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(50), default="Warning")  # INFO, LOW, MODERATE, HIGH, SEVERE, EXTREME
    status = Column(String(50), default="Actual")  # Actual, Update, Test, Cancel
    issued_at = Column(DateTime, nullable=True)
    effective_from = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    affected_area = Column(Text, nullable=True)
    district = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    country = Column(String(100), default="India")
    instructions = Column(Text, nullable=True)
    source_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    raw_data = Column(Text, nullable=True)  # Stored JSON string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    geometries = relationship("AlertGeometry", back_populates="alert", cascade="all, delete-orphan")
    deliveries = relationship("UserAlertDelivery", back_populates="alert", cascade="all, delete-orphan")


class AlertGeometry(Base):
    __tablename__ = "alert_geometries"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(150), ForeignKey("official_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    geometry_type = Column(String(50), default="polygon")  # polygon, multipolygon, circle, district
    coordinates_json = Column(Text, nullable=True)  # JSON string of [[lat, lon], ...]
    centroid_lat = Column(Float, nullable=True)
    centroid_lon = Column(Float, nullable=True)
    radius_km = Column(Float, nullable=True)

    # Relationship
    alert = relationship("OfficialAlert", back_populates="geometries")


class UserAlertDelivery(Base):
    __tablename__ = "user_alert_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id = Column(String(150), ForeignKey("official_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("user_alert_locations.id", ondelete="SET NULL"), nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    delivery_type = Column(String(50), default="push")  # push, in_app, sms
    status = Column(String(50), default="sent")  # sent, delivered, failed, read
    hazard_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    match_type = Column(String(50), default="polygon")  # polygon, radius, district, test

    # Relationships
    user = relationship("User", back_populates="alert_deliveries")
    alert = relationship("OfficialAlert", back_populates="deliveries")
    location = relationship("UserAlertLocation", back_populates="deliveries")
