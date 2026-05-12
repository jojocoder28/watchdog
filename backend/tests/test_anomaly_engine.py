import pytest
from datetime import datetime, timedelta
from services.anomaly_engine import AnomalyEngine
from schemas.log import LogCreate
from models.incident import Incident
from models.log import LogLevel
from repositories.log_repository import LogRepository
from repositories.incident_repository import IncidentRepository


@pytest.fixture
def log_factory(db_session):
    """Factory fixture to generate and persist logs into the test DB."""
    def _generate(service, level_str, count, time_offset_min=0):
        level = LogLevel(level_str)
        base_time = datetime.utcnow() - timedelta(minutes=time_offset_min)
        logs = [
            LogCreate(
                timestamp=base_time,
                service_name=service,
                level=level,
                message=f"Test msg {i}",
                metadata_json={"latency_ms": 100},
            )
            for i in range(count)
        ]
        repo = LogRepository(db_session)
        repo.batch_insert(logs)
    return _generate


def test_threshold_breach_detected(db_session, log_factory):
    log_factory("AuthService", "ERROR", 55)
    engine = AnomalyEngine(db_session)
    incidents = engine.run_all_detectors()
    assert any(i.incident_type == "ThresholdViolation" for i in incidents)


def test_no_anomaly_normal_logs(db_session, log_factory):
    log_factory("InfoService", "INFO", 100)
    log_factory("InfoService", "ERROR", 5)
    engine = AnomalyEngine(db_session)
    incidents = engine.run_all_detectors()
    # No threshold should fire: <50 errors, <10 criticals
    threshold_incidents = [i for i in incidents if i.incident_type == "ThresholdViolation"]
    assert len(threshold_incidents) == 0


def test_zscore_spike_detected(db_session, log_factory):
    # Build 24h baseline with low errors, then spike now
    log_factory("PaymentService", "ERROR", 2, time_offset_min=120)
    log_factory("PaymentService", "ERROR", 2, time_offset_min=60)
    log_factory("PaymentService", "ERROR", 80)   # current 5-min window spike
    engine = AnomalyEngine(db_session)
    incidents = engine.run_all_detectors()
    assert any(i.incident_type == "ZScoreAnomaly" for i in incidents)


def test_rolling_window_spike(db_session, log_factory):
    # Previous window: 10 errors; current window: 40 errors → >200% increase
    log_factory("DatabaseService", "ERROR", 10, time_offset_min=6)
    log_factory("DatabaseService", "ERROR", 40, time_offset_min=0)
    engine = AnomalyEngine(db_session)
    incidents = engine.run_all_detectors()
    assert any(i.incident_type == "ErrorSpike" for i in incidents)


def test_isolation_forest_anomaly(db_session, log_factory):
    """IsolationForest path: mock sklearn to return anomaly so the test is deterministic."""
    from unittest.mock import patch, MagicMock
    import numpy as np

    # Build enough history (>100 logs, >10 buckets) for the code to reach the model
    for i in range(15):
        log_factory("APIGateway", "INFO", 8, time_offset_min=i * 10 + 5)
    repo = LogRepository(db_session)
    anomalous = [
        LogCreate(
            timestamp=datetime.utcnow(),
            service_name="APIGateway",
            level=LogLevel.ERROR,
            message=f"Anomalous event {j}",
            metadata_json={"latency_ms": 30000},
        )
        for j in range(10)
    ]
    repo.batch_insert(anomalous)

    # Mock the IsolationForest so it deterministically returns -1 (anomaly)
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([-1])
    mock_clf.decision_function.return_value = np.array([-0.3])

    with patch('services.anomaly_engine.IsolationForest', return_value=mock_clf):
        engine = AnomalyEngine(db_session)
        incidents = engine.run_all_detectors()

    assert any(i.incident_type == "MLAnomaly" for i in incidents)


def test_incident_created_on_detection(db_session, log_factory):
    log_factory("NotificationService", "ERROR", 60)
    engine = AnomalyEngine(db_session)
    detected = engine.run_all_detectors()
    # Simulate what the route does: persist each detected incident
    inc_repo = IncidentRepository(db_session)
    for inc_data in detected:
        inc_repo.create_incident(inc_data)
    count = db_session.query(Incident).count()
    assert count > 0
