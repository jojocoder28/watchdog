from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.log import LogLevel

class LogCreate(BaseModel):
    service_name: str
    level: LogLevel
    message: str
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class LogResponse(LogCreate):
    id: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class LogFilter(BaseModel):
    service: Optional[str] = None
    level: Optional[LogLevel] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class LogStats(BaseModel):
    total_logs: int
    error_rate: float
    counts_by_level: Dict[str, int]
    counts_by_service: Dict[str, int]
