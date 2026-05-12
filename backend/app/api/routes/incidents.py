from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Incident, User
from app.schemas.schemas import IncidentResponse, IncidentUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse])
def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents

@router.get("/{id}", response_model=IncidentResponse)
def get_incident(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{id}", response_model=IncidentResponse)
def update_incident(id: str, incident_in: IncidentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident_in.status:
        incident.status = incident_in.status
    if incident_in.severity:
        incident.severity = incident_in.severity
        
    db.commit()
    db.refresh(incident)
    return incident
