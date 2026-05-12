from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List, Dict
from datetime import datetime
from app.db.models import UserRole, LogLevel, IncidentStatus, IncidentSeverity

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.SRE

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LogCreate(BaseModel):
    service_name: str
    level: LogLevel
    message: str
    metadata_json: Optional[Dict[str, Any]] = None

class LogResponse(LogCreate):
    id: str
    timestamp: datetime

    model_config = {"from_attributes": True}

class GenerateLogsRequest(BaseModel):
    count: int = 100
    error_ratio: float = 0.1

class GenerateLogsResponse(BaseModel):
    generated_count: int

class IncidentBase(BaseModel):
    title: str
    status: IncidentStatus = IncidentStatus.OPEN
    severity: IncidentSeverity = IncidentSeverity.MEDIUM

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None

class IncidentResponse(IncidentBase):
    id: str
    ai_analysis: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class AlertResponse(BaseModel):
    id: str
    incident_id: str
    log_id: Optional[str] = None
    rule_triggered: str
    created_at: datetime

    model_config = {"from_attributes": True}

class SystemSettingsUpdate(BaseModel):
    anomaly_threshold_error_rate: Optional[float] = None
    gemini_model_version: Optional[str] = None
    default_webhook_url: Optional[str] = None

class SystemSettingsResponse(BaseModel):
    id: int
    anomaly_threshold_error_rate: float
    gemini_model_version: str
    default_webhook_url: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}

class WebhookTestRequest(BaseModel):
    url: str
    payload: Dict[str, Any]
