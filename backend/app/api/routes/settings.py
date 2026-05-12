from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SystemSettings, User, UserRole
from app.schemas.schemas import SystemSettingsResponse, SystemSettingsUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=SystemSettingsResponse)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/", response_model=SystemSettingsResponse)
def update_settings(settings_in: SystemSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    if current_user.role not in [UserRole.LEAD, UserRole.DEVOPS]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    if settings_in.anomaly_threshold_error_rate is not None:
        settings.anomaly_threshold_error_rate = settings_in.anomaly_threshold_error_rate
    if settings_in.gemini_model_version is not None:
        settings.gemini_model_version = settings_in.gemini_model_version
    if settings_in.default_webhook_url is not None:
        settings.default_webhook_url = settings_in.default_webhook_url
        
    db.commit()
    db.refresh(settings)
    return settings
