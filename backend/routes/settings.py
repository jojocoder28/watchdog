from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.system_settings import SystemSettings
from schemas.system_settings import SystemSettingsResponse, SystemSettingsUpdate
from auth.jwt_handler import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=SystemSettingsResponse)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.post("/", response_model=SystemSettingsResponse)
def update_settings(settings_in: SystemSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    if current_user.role not in ["Lead", "DevOps", "SRE"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    update_data = settings_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
        
    db.commit()
    db.refresh(settings)
    return settings
