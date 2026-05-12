import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Text, Float, JSON
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"

class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    incident_type = Column(String)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    confidence_score = Column(Float, nullable=True)
    affected_service = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    log_sample = Column(JSON, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
