import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True, default=generate_uuid)
    incident_id = Column(String, ForeignKey("incidents.id"))
    log_id = Column(String, ForeignKey("logs.id"), nullable=True)
    rule_triggered = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
