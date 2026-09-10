import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(50), default="General User", nullable=False)
    country = Column(String(100), default="India")
    state = Column(String(100), default="Andhra Pradesh")
    preferred_language = Column(String(10), default="en")
    default_location = Column(String(255), default="Guntur, Andhra Pradesh")
    phone_number = Column(String(20), nullable=True, index=True)
    phone_country_code = Column(String(10), default="+91")
    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    alert_locations = relationship("UserAlertLocation", back_populates="user", cascade="all, delete-orphan")
    push_subscriptions = relationship("PushSubscription", back_populates="user", cascade="all, delete-orphan")
    alert_deliveries = relationship("UserAlertDelivery", back_populates="user", cascade="all, delete-orphan")
    sms_deliveries = relationship("UserAlertSmsDelivery", back_populates="user", cascade="all, delete-orphan")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(20), default="system")  # "light", "dark", "system"
    language = Column(String(10), default="en")
    temperature_unit = Column(String(10), default="celsius")  # "celsius", "fahrenheit"
    wind_unit = Column(String(10), default="kmh")  # "kmh", "ms"
    severe_alerts = Column(Boolean, default=True)
    forecast_notifications = Column(Boolean, default=True)
    sms_alerts_enabled = Column(Boolean, default=False)
    sms_alert_categories = Column(Text, default='["Severe Weather", "Flood", "Cyclone", "Thunderstorm", "Extreme Rain", "Heatwave"]')

    user = relationship("User", back_populates="preferences")


    user = relationship("User", back_populates="preferences")
