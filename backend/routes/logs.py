import os
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, SessionLocal
from models.user import User
from schemas.log import LogResponse, LogFilter, LogStats
from auth.jwt_handler import get_current_user
from repositories.log_repository import LogRepository
from services.file_processor import process_log_file_async

router = APIRouter(prefix="/logs", tags=["logs"])

@router.post("/upload")
async def upload_logs(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Accept multipart file (.log, .csv, .json), parse async, batch insert."""
    allowed_extensions = [".log", ".csv", ".json"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .log, .csv, .json allowed.")
    
    background_tasks.add_task(process_log_file_async, file, SessionLocal)
    
    return {"message": f"File {file.filename} is being processed in the background."}

@router.post("/generate")
def trigger_synthetic_logs(
    background_tasks: BackgroundTasks,
    count: int = Query(1000, description="Number of logs to generate"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Trigger synthetic generator and insert results."""
    background_tasks.add_task(_generate_and_insert, count)
    return {"message": f"Generating and inserting {count} synthetic logs in the background."}

def _generate_and_insert(count: int):
    """Background task to generate and insert logs."""
    from services.log_generator import generate_logs as gen_logs
    from schemas.log import LogCreate
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)
    
    db = SessionLocal()
    try:
        raw_logs = gen_logs(count)
        log_creates = []
        for rl in raw_logs:
            log_creates.append(LogCreate(
                timestamp=datetime.fromisoformat(rl["timestamp"]),
                service_name=rl["service_name"],
                level=rl["log_level"],
                message=rl["message"],
                metadata_json=rl["metadata"]
            ))
        repo = LogRepository(db)
        inserted = repo.batch_insert(log_creates)
        logger.info(f"Synthetic generation complete: inserted {inserted} logs.")
    except Exception as e:
        logger.error(f"Error generating logs: {e}")
    finally:
        db.close()

@router.get("/", response_model=List[LogResponse])
def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Paginated log listing with filters."""
    repo = LogRepository(db)
    filters = LogFilter(service=service, level=level, start_time=start_time, end_time=end_time)
    logs = repo.get_logs(skip=skip, limit=limit, filters=filters)
    return logs

@router.get("/stats", response_model=LogStats)
def get_log_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Counts by level, by service, error rate."""
    repo = LogRepository(db)
    
    total = repo.get_total_count()
    counts_by_level = repo.get_log_counts_by_level()
    counts_by_service = repo.get_log_counts_by_service()
    
    error_count = counts_by_level.get("ERROR", 0) + counts_by_level.get("FATAL", 0) + counts_by_level.get("CRITICAL", 0)
    error_rate = (error_count / total * 100) if total > 0 else 0.0
    
    return LogStats(
        total_logs=total,
        error_rate=round(error_rate, 2),
        counts_by_level=counts_by_level,
        counts_by_service=counts_by_service
    )
