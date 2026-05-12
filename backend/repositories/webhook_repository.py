from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.webhook_history import WebhookHistory, WebhookStatus
from schemas.webhook_history import WebhookHistoryCreate
from datetime import datetime

class WebhookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_webhook_history(self, wh_in: WebhookHistoryCreate) -> WebhookHistory:
        db_wh = WebhookHistory(**wh_in.model_dump())
        self.db.add(db_wh)
        self.db.commit()
        self.db.refresh(db_wh)
        return db_wh

    def update_webhook_status(self, id: str, status: WebhookStatus, response_code: Optional[int] = None, response_body: Optional[str] = None, increment_attempt: bool = False) -> Optional[WebhookHistory]:
        wh = self.db.query(WebhookHistory).filter(WebhookHistory.id == id).first()
        if not wh:
            return None
        wh.status = status
        wh.last_attempt_at = datetime.utcnow()
        if response_code is not None:
            wh.response_code = response_code
        if response_body is not None:
            wh.response_body = response_body
        if increment_attempt:
            wh.attempt_count += 1
        self.db.commit()
        self.db.refresh(wh)
        return wh

    def get_webhook_history(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[WebhookHistory]:
        query = self.db.query(WebhookHistory)
        if status:
            try:
                query = query.filter(WebhookHistory.status == WebhookStatus(status))
            except Exception:
                pass
        return query.order_by(WebhookHistory.created_at.desc()).offset(skip).limit(limit).all()

    def get_failed_webhooks(self) -> List[WebhookHistory]:
        return self.db.query(WebhookHistory).filter(WebhookHistory.status == WebhookStatus.FAILED).all()
        
    def get_stats(self) -> Dict[str, Any]:
        total = self.db.query(WebhookHistory).count()
        failures = self.db.query(WebhookHistory).filter(WebhookHistory.status == WebhookStatus.FAILED).count()
        successes = self.db.query(WebhookHistory).filter(WebhookHistory.status == WebhookStatus.SENT).count()
        
        # In SQLite, avg() returns None for empty sets
        avg_retry_res = self.db.query(func.avg(WebhookHistory.attempt_count)).scalar()
        avg_retry = float(avg_retry_res) if avg_retry_res is not None else 0.0
        
        rate = (successes / total * 100) if total > 0 else 0.0
        return {
            "success_rate": rate,
            "failure_count": failures,
            "avg_retry_count": avg_retry
        }
