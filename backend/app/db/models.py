import uuid
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey, Integer, Text, Float, JSON
from datetime import datetime
from app.db.database import Base
import enum

def generate_uuid():
    return str(uuid.uuid4())

class UserRole(str, enum.Enum):
    SRE = "SRE"
    DEVOPS = "DevOps"
    LEAD = "Lead"

class LogLevel(str, enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    DEBUG = "DEBUG"

class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"

class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.SRE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    service_name = Column(String)
    level = Column(Enum(LogLevel))
    message = Column(Text)
    metadata_json = Column(JSON, nullable=True)
    
class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"))
    log_id = Column(String, ForeignKey("logs.id"), nullable=True)
    rule_triggered = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class WebhookHistory(Base):
    __tablename__ = "webhook_history"
    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"))
    endpoint_url = Column(String)
    payload = Column(JSON)
    status_code = Column(Integer)
    response_body = Column(Text)
    triggered_at = Column(DateTime, default=datetime.utcnow)

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, default=1)
    anomaly_threshold_error_rate = Column(Float, default=5.0)
    gemini_model_version = Column(String, default="gemini-1.5-flash")
    default_webhook_url = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
