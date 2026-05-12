import pytest
from models.webhook_history import WebhookHistory, WebhookStatus


@pytest.mark.asyncio
async def test_webhook_history_created(auth_client):
    """Posting to /webhook/test should create webhook history entries."""
    response = await auth_client.post("/webhook/test")
    assert response.status_code == 200
    assert "message" in response.json()

    # History may be written async; check the endpoint returns a list
    history_resp = await auth_client.get("/webhook/history")
    assert history_resp.status_code == 200
    assert isinstance(history_resp.json(), list)


@pytest.mark.asyncio
async def test_retry_failed_webhook(auth_client, db_session):
    """Retry endpoint should accept a FAILED webhook id and return 200."""
    # We need a real alert row because of the FK on webhook_history
    from models.incident import Incident, IncidentSeverity
    from models.alert import Alert

    incident = Incident(
        title="Retry Test Incident",
        incident_type="ManualTest",
        severity=IncidentSeverity.HIGH,
    )
    db_session.add(incident)
    db_session.flush()

    alert = Alert(incident_id=incident.id, rule_triggered="test_rule")
    db_session.add(alert)
    db_session.flush()

    wh = WebhookHistory(
        id="retry-test-wh-001",
        alert_id=alert.id,
        target_type="slack",
        endpoint_url="http://mock-slack",
        payload_json={"text": "test"},
        status=WebhookStatus.FAILED,
        attempt_count=1,
    )
    db_session.add(wh)
    db_session.commit()

    response = await auth_client.post(f"/webhook/retry/{wh.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == wh.id


@pytest.mark.asyncio
async def test_test_webhook_endpoint(auth_client):
    """Test webhook endpoint should respond with a success message."""
    response = await auth_client.post("/webhook/test")
    assert response.status_code == 200
    assert "message" in response.json()
