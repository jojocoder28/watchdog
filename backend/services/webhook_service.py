import os
import json
import random
import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from models.incident import Incident
from models.alert import Alert
from models.webhook_history import WebhookHistory, WebhookStatus
from schemas.webhook_history import WebhookHistoryCreate
from repositories.webhook_repository import WebhookRepository

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WebhookRepository(db)
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.emails_dir = os.path.join(project_root, "dataset", "simulated_emails")
        os.makedirs(self.emails_dir, exist_ok=True)

    def dispatch_all(self, alert: Alert, incident: Incident):
        """Dispatch to Slack, Discord, and Email simulated targets."""
        slack_payload = self._format_slack(alert, incident)
        self._simulate_dispatch(alert.id, "Slack", slack_payload, "https://hooks.slack.com/services/simulated")
        
        discord_payload = self._format_discord(alert, incident)
        self._simulate_dispatch(alert.id, "Discord", discord_payload, "https://discord.com/api/webhooks/simulated")
        
        email_payload = self._format_email(alert, incident)
        self._simulate_dispatch(alert.id, "Email", email_payload, "smtp://simulated")

    def _format_slack(self, alert: Alert, incident: Incident) -> dict:
        severity_emoji = "🔴" if incident.severity.value in ["HIGH", "CRITICAL"] else "🟡"
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emoji} {incident.title}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Service:*\n{incident.affected_service}"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{incident.severity.value}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{incident.start_time.isoformat() if incident.start_time else 'N/A'}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*AI Summary:*\n{incident.ai_analysis or 'No summary available.'}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"<{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/incidents/{incident.id}|View Incident Details>"
                    }
                }
            ]
        }

    def _format_discord(self, alert: Alert, incident: Incident) -> dict:
        colors = {
            "CRITICAL": 16711680,
            "HIGH": 16744192,
            "MEDIUM": 16776960,
            "LOW": 3447003
        }
        return {
            "embeds": [{
                "title": f"🚨 {incident.title}",
                "description": incident.ai_analysis or "No summary available.",
                "color": colors.get(incident.severity.value, 3447003),
                "fields": [
                    {"name": "Service", "value": incident.affected_service or "Unknown", "inline": True},
                    {"name": "Severity", "value": incident.severity.value, "inline": True}
                ],
                "timestamp": incident.start_time.isoformat() if incident.start_time else datetime.utcnow().isoformat()
            }]
        }

    def _format_email(self, alert: Alert, incident: Incident) -> dict:
        return {
            "subject": f"[{incident.severity.value}] Alert: {incident.title}",
            "body": f'''
            <html>
            <body>
                <h2>Incident: {incident.title}</h2>
                <p><strong>Service:</strong> {incident.affected_service}</p>
                <p><strong>Severity:</strong> {incident.severity.value}</p>
                <p><strong>Time:</strong> {incident.start_time}</p>
                <hr>
                <h3>AI Analysis</h3>
                <p>{incident.ai_analysis or 'N/A'}</p>
                <hr>
                <p><a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/incidents/{incident.id}">View in Dashboard</a></p>
            </body>
            </html>
            '''
        }

    def _simulate_dispatch(self, alert_id: str, target: str, payload: dict, endpoint: str):
        wh_create = WebhookHistoryCreate(
            alert_id=alert_id,
            target_type=target,
            endpoint_url=endpoint,
            payload_json=payload
        )
        wh = self.repo.create_webhook_history(wh_create)
        self.retry_dispatch(wh.id)

    def retry_dispatch(self, history_id: str):
        wh = self.db.query(WebhookHistory).filter(WebhookHistory.id == history_id).first()
        if not wh:
            return
            
        max_retries = 3
        backoff = 1.0
        
        if wh.target_type == "Email":
            file_path = os.path.join(self.emails_dir, f"email_{wh.id}.html")
        
        while wh.attempt_count <= max_retries:
            self.repo.update_webhook_status(wh.id, WebhookStatus.RETRYING if wh.attempt_count > 0 else WebhookStatus.PENDING, increment_attempt=True)
            
            time.sleep(0.5)
            
            if random.random() < 0.2:
                self.repo.update_webhook_status(wh.id, WebhookStatus.FAILED, response_code=500, response_body="Simulated network failure")
                logger.warning(f"Webhook {wh.id} to {wh.target_type} failed (Attempt {wh.attempt_count}).")
                
                if wh.attempt_count >= max_retries:
                    break
                    
                time.sleep(backoff)
                backoff *= 2
            else:
                self.repo.update_webhook_status(wh.id, WebhookStatus.SENT, response_code=200, response_body="Simulated success OK")
                logger.info(f"Webhook {wh.id} to {wh.target_type} sent successfully.")
                
                if wh.target_type == "Email":
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(wh.payload_json.get("body", "Empty body"))
                    except Exception as e:
                        logger.error(f"Failed to write simulated email: {e}")
                        
                break
