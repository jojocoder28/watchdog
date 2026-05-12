from typing import List, Optional
from sqlalchemy.orm import Session
from models.incident import Incident, IncidentStatus
from schemas.incident import IncidentCreate, IncidentUpdate

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_incident(self, incident_in: IncidentCreate) -> Incident:
        db_incident = Incident(**incident_in.model_dump())
        self.db.add(db_incident)
        self.db.commit()
        self.db.refresh(db_incident)
        return db_incident

    def get_incidents(self, skip: int = 0, limit: int = 100, service: Optional[str] = None, status: Optional[str] = None) -> List[Incident]:
        query = self.db.query(Incident)
        if service:
            query = query.filter(Incident.affected_service == service)
        if status:
            query = query.filter(Incident.status == status)
        return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    def update_incident_status(self, id: str, status: str) -> Optional[Incident]:
        incident = self.db.query(Incident).filter(Incident.id == id).first()
        if not incident:
            return None
        incident.status = status
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_open_incidents(self) -> List[Incident]:
        return self.db.query(Incident).filter(Incident.status != IncidentStatus.RESOLVED).all()
        
    def get_incident(self, id: str) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == id).first()
