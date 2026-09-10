from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
import datetime
from app.database.session import Base

class AlertRecord(Base):
    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(100), unique=True, index=True)
    source = Column(String(100), index=True)  # e.g., NDMA, IMD, CWC, INCOIS, SDMA, MeteoAlarm
    event = Column(String(100), index=True)   # e.g., Flood, Heavy Rain, Thunderstorm
    severity = Column(String(50))             # Extreme, Severe, Moderate, Minor
    urgency = Column(String(50))              # Immediate, Expected, Future
    certainty = Column(String(50))            # Observed, Likely, Possible
    severity_color = Column(String(20))       # Red, Orange, Yellow, Green
    
    # Geospatial
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_description = Column(Text, nullable=True)
    area_covered_sqkm = Column(Float, nullable=True)
    
    # Temporal
    issued_at = Column(DateTime, nullable=True)
    effective_at = Column(DateTime, nullable=True)
    onset_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    duration_text = Column(String(100), nullable=True)
    
    # Advisory content
    headline = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    instruction = Column(Text, nullable=True)
    safety_precautions = Column(Text, nullable=True)  # JSON or newline-separated
    
    raw_source_reference = Column(Text, nullable=True)
    status = Column(String(50), default="Actual")  # Actual, Exercise, Test, Cancel
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
