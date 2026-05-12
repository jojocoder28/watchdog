from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SystemSettingsUpdate(BaseModel):
    anomaly_threshold_error_rate: Optional[float] = None
    gemini_model_version: Optional[str] = None
    default_webhook_url: Optional[str] = None
    gemini_api_key: Optional[str] = None
    jwt_expire_minutes: Optional[int] = None
    error_threshold: Optional[int] = None
    critical_threshold: Optional[int] = None
    latency_threshold_ms: Optional[int] = None
    slack_enabled: Optional[bool] = None
    discord_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    environment: Optional[str] = None

class SystemSettingsResponse(BaseModel):
    id: int
    anomaly_threshold_error_rate: float
    gemini_model_version: str
    default_webhook_url: Optional[str] = None
    gemini_api_key: Optional[str] = None
    jwt_expire_minutes: int
    error_threshold: int
    critical_threshold: int
    latency_threshold_ms: int
    slack_enabled: bool
    discord_enabled: bool
    email_enabled: bool
    environment: str
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
