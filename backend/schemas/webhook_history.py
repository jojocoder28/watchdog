from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from models.webhook_history import WebhookStatus

class WebhookHistoryBase(BaseModel):
    alert_id: str
    target_type: str
    endpoint_url: Optional[str] = None
    payload_json: Dict[str, Any]

class WebhookHistoryCreate(WebhookHistoryBase):
    status: WebhookStatus = WebhookStatus.PENDING

class WebhookHistoryResponse(WebhookHistoryBase):
    id: str
    status: WebhookStatus
    attempt_count: int
    last_attempt_at: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class WebhookStats(BaseModel):
    success_rate: float
    failure_count: int
    avg_retry_count: float
