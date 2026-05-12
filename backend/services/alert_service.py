import logging
from sqlalchemy.orm import Session
from models.incident import Incident, IncidentSeverity
from models.alert import Alert
from schemas.alert import AlertCreate
from services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.webhook_service = WebhookService(db)

    def create_alert_from_incident(self, incident: Incident) -> Alert:
        """Auto-create alert when incident severity >= HIGH."""
        if incident.severity not in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            logger.info(f"Incident {incident.id} severity is {incident.severity}. No alert created.")
            return None
            
        alert = Alert(
            incident_id=incident.id,
            rule_triggered=f"Severity threshold breached: {incident.severity.value}"
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Created alert {alert.id} for incident {incident.id}.")
        return alert

    def dispatch_alert(self, alert: Alert):
        """Call all webhook dispatchers for an alert."""
        incident = self.db.query(Incident).filter(Incident.id == alert.incident_id).first()
        if not incident:
            logger.error(f"Cannot dispatch alert {alert.id}: Incident {alert.incident_id} not found.")
            return
            
        self.webhook_service.dispatch_all(alert, incident)

    def get_active_alerts(self):
        """Get recent or active alerts."""
        return self.db.query(Alert).order_by(Alert.created_at.desc()).limit(100).all()
