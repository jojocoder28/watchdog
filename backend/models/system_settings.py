from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, default=1)
    anomaly_threshold_error_rate = Column(Float, default=5.0)
    gemini_model_version = Column(String, default="gemini-1.5-flash")
    default_webhook_url = Column(String, nullable=True)
    
    gemini_api_key = Column(String, nullable=True)
    jwt_expire_minutes = Column(Integer, default=60)
    error_threshold = Column(Integer, default=50)
    critical_threshold = Column(Integer, default=10)
    latency_threshold_ms = Column(Integer, default=5000)
    slack_enabled = Column(Boolean, default=True)
    discord_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=False)
    environment = Column(String, default="Production")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
