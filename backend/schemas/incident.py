from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from models.incident import IncidentStatus, IncidentSeverity

class IncidentBase(BaseModel):
    title: str
    incident_type: str
    status: IncidentStatus = IncidentStatus.OPEN
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    confidence_score: Optional[float] = None
    affected_service: Optional[str] = None
    start_time: Optional[datetime] = None
    log_sample: Optional[List[str]] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None

class IncidentResponse(IncidentBase):
    id: str
    ai_analysis: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
