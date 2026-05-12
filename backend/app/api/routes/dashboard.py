from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import LogEntry, Incident, IncidentStatus, User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    total_logs = db.query(LogEntry).count()
    active_incidents = db.query(Incident).filter(Incident.status != IncidentStatus.RESOLVED).count()
    
    total_errors = db.query(LogEntry).filter(LogEntry.level == "ERROR").count()
    error_rate = (total_errors / total_logs * 100) if total_logs > 0 else 0
    
    return {
        "total_logs": total_logs,
        "active_incidents": active_incidents,
        "error_rate": round(error_rate, 2)
    }
