from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import LogEntry, Incident, Alert, IncidentStatus, SystemSettings, WebhookHistory
from app.services.ai_service import analyze_incident_logs
from app.core.config import settings
import httpx
import asyncio

def check_for_anomalies(db: Session):
    settings_db = db.query(SystemSettings).first()
    error_threshold = settings_db.anomaly_threshold_error_rate if settings_db else 5.0
    
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_logs = db.query(LogEntry).filter(LogEntry.timestamp >= five_mins_ago).all()
    
    if not recent_logs:
        return 0
        
    error_logs = [l for l in recent_logs if l.level == "ERROR" or l.level == "FATAL"]
    error_rate = (len(error_logs) / len(recent_logs)) * 100
    
    if error_rate >= error_threshold and len(error_logs) > 3:
        active_incident = db.query(Incident).filter(Incident.status == IncidentStatus.OPEN).first()
        
        if not active_incident:
            active_incident = Incident(
                title=f"High Error Rate Detected: {error_rate:.2f}%",
            )
            db.add(active_incident)
            db.commit()
            db.refresh(active_incident)
            
            analysis = analyze_incident_logs(error_logs)
            active_incident.ai_analysis = analysis
            db.commit()
        
        newest_error = sorted(error_logs, key=lambda x: x.timestamp, reverse=True)[0]
        alert = Alert(
            incident_id=active_incident.id,
            log_id=newest_error.id,
            rule_triggered=f"Error rate > {error_threshold}%"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        webhook_url = settings_db.default_webhook_url if settings_db else None
        if webhook_url:
            asyncio.run(trigger_webhook(db, alert, active_incident, webhook_url))
            
        return 1
    return 0

async def trigger_webhook(db: Session, alert: Alert, incident: Incident, url: str):
    payload = {
        "text": f"🚨 *ALERT TRIGGERED* 🚨\nIncident: {incident.title}\nRule: {alert.rule_triggered}\nAI Analysis: {incident.ai_analysis[:100] if incident.ai_analysis else 'N/A'}..."
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5.0)
            history = WebhookHistory(
                alert_id=alert.id,
                endpoint_url=url,
                payload=payload,
                status_code=response.status_code,
                response_body=response.text[:500]
            )
            db.add(history)
            db.commit()
    except Exception as e:
        history = WebhookHistory(
            alert_id=alert.id,
            endpoint_url=url,
            payload=payload,
            status_code=500,
            response_body=str(e)
        )
        db.add(history)
        db.commit()
