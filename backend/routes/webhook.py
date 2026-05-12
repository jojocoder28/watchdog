from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.incident import Incident, IncidentSeverity
from models.alert import Alert
from models.webhook_history import WebhookHistory
from schemas.webhook_history import WebhookHistoryResponse, WebhookStats
from auth.jwt_handler import get_current_user
from repositories.webhook_repository import WebhookRepository
from services.webhook_service import WebhookService
from services.alert_service import AlertService

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/test")
def manual_test_alert(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Manually trigger a test alert to all channels."""
    incident = Incident(
        title="Test Webhook Alert",
        incident_type="ManualTest",
        severity=IncidentSeverity.CRITICAL,
        affected_service="TestService",
        ai_analysis="This is a manually triggered test alert to verify webhook pipelines."
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    alert_service = AlertService(db)
    alert = alert_service.create_alert_from_incident(incident)
    
    if alert:
        background_tasks.add_task(alert_service.dispatch_alert, alert)
        
    return {"message": "Test alert dispatched to all channels."}

@router.get("/history", response_model=List[WebhookHistoryResponse])
def get_webhook_history(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Paginated history with status filter."""
    repo = WebhookRepository(db)
    return repo.get_webhook_history(skip=skip, limit=limit, status=status)

@router.post("/retry/{id}", response_model=WebhookHistoryResponse)
def retry_webhook(
    id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Retry a failed webhook."""
    wh = db.query(WebhookHistory).filter(WebhookHistory.id == id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Webhook history not found")
        
    svc = WebhookService(db)
    background_tasks.add_task(svc.retry_dispatch, id)
    
    return wh

@router.get("/stats", response_model=WebhookStats)
def get_webhook_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Success rate, failure count, avg retry count."""
    repo = WebhookRepository(db)
    return repo.get_stats()
