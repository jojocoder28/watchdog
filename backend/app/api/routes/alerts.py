from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Alert, User
from app.schemas.schemas import AlertResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def get_alerts(skip: int = 0, limit: int = 100, incident_id: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    query = db.query(Alert)
    if incident_id:
        query = query.filter(Alert.incident_id == incident_id)
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@router.get("/{id}", response_model=AlertResponse)
def get_alert(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
