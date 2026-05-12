from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.incident import IncidentResponse, IncidentCreate, IncidentUpdate
from auth.jwt_handler import get_current_user
from repositories.incident_repository import IncidentRepository
from services.anomaly_engine import AnomalyEngine

router = APIRouter(prefix="/anomaly", tags=["anomaly"])

@router.post("/detect", response_model=List[IncidentResponse])
def run_detection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Run all detectors against recent logs, create incidents."""
    engine = AnomalyEngine(db)
    detected_incidents = engine.run_all_detectors()
    
    repo = IncidentRepository(db)
    saved_incidents = []
    
    from services.gemini_service import GeminiService
    from models.log import LogEntry
    ai_service = GeminiService()
    
    for inc_in in detected_incidents:
        saved = repo.create_incident(inc_in)
        
        if saved.log_sample and isinstance(saved.log_sample, list):
            sample_logs = db.query(LogEntry).filter(LogEntry.id.in_(saved.log_sample)).all()
            if sample_logs:
                ai_summary = ai_service.summarize_incident(saved, sample_logs)
                saved.ai_analysis = ai_summary
                db.commit()
                db.refresh(saved)
                
        saved_incidents.append(saved)
        
    return saved_incidents

@router.get("/incidents", response_model=List[IncidentResponse])
def get_incidents(
    service: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List incidents with filters."""
    repo = IncidentRepository(db)
    return repo.get_incidents(skip=skip, limit=limit, service=service, status=status)

@router.get("/incidents/{id}", response_model=IncidentResponse)
def get_incident_detail(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Single incident detail."""
    repo = IncidentRepository(db)
    incident = repo.get_incident(id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/incidents/{id}", response_model=IncidentResponse)
def update_incident_status(
    id: str,
    update_in: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update incident status."""
    repo = IncidentRepository(db)
    updated = repo.update_incident_status(id, update_in.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    return updated
