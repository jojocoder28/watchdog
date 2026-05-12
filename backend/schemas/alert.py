from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    incident_id: str
    log_id: Optional[str] = None
    rule_triggered: str

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
