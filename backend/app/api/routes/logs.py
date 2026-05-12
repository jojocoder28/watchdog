from typing import Any, List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import LogEntry, User
from app.schemas.schemas import LogCreate, LogResponse, GenerateLogsRequest, GenerateLogsResponse
from app.api.deps import get_current_user
from app.services.generator import generate_synthetic_logs

router = APIRouter()

@router.post("/upload", response_model=List[LogResponse], status_code=201)
def upload_logs(logs_in: List[LogCreate], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    db_logs = []
    for log_in in logs_in:
        log = LogEntry(**log_in.model_dump())
        db.add(log)
        db_logs.append(log)
    db.commit()
    for log in db_logs:
        db.refresh(log)
    return db_logs

@router.post("/generate", response_model=GenerateLogsResponse)
def generate_logs(req: GenerateLogsRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    count = generate_synthetic_logs(db, req.count, req.error_ratio)
    return {"generated_count": count}

@router.get("/", response_model=List[LogResponse])
def get_logs(skip: int = 0, limit: int = 100, level: Optional[str] = None, service: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Any:
    query = db.query(LogEntry)
    if level:
        query = query.filter(LogEntry.level == level)
    if service:
        query = query.filter(LogEntry.service_name == service)
    logs = query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()
    return logs
