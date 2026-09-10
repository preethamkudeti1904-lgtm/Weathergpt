import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

class PhoneOtp(Base):
    __tablename__ = "phone_otps"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")


class UserAlertSmsDelivery(Base):
    __tablename__ = "user_alert_sms_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id = Column(String(150), ForeignKey("official_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("user_alert_locations.id", ondelete="SET NULL"), nullable=True)
    phone_number = Column(String(20), nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    status = Column(String(50), default="SENT")  # QUEUED, SENDING, SENT, DELIVERED, FAILED
    hazard_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    provider_message_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sms_deliveries")
    alert = relationship("OfficialAlert")
    location = relationship("UserAlertLocation")
