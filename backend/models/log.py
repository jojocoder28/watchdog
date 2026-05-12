import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Text, JSON
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class LogLevel(str, enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"

class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    service_name = Column(String)
    level = Column(Enum(LogLevel))
    message = Column(Text)
    metadata_json = Column(JSON, nullable=True)
