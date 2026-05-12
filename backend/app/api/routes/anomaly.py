from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.api.deps import get_current_user
from app.services.anomaly import check_for_anomalies

router = APIRouter()

@router.post("/detect")
def trigger_detection(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    anomalies_found = check_for_anomalies(db)
    return {"anomalies_found": anomalies_found}
