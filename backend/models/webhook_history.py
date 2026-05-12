import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON, Enum
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class WebhookStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class WebhookHistory(Base):
    __tablename__ = "webhook_history"
    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("alerts.id"))
    target_type = Column(String) # Slack, Discord, Email
    endpoint_url = Column(String, nullable=True)
    payload_json = Column(JSON)
    status = Column(Enum(WebhookStatus), default=WebhookStatus.PENDING)
    attempt_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
