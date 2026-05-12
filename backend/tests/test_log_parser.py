import pytest
from services.log_parser import parse_log_line, parse_csv_content, parse_json_content
from models.log import LogLevel


def test_parse_valid_log_file():
    # Matches the LOG_REGEX format: [timestamp] LEVEL Service host env - message
    log_content = '[2023-10-01T12:00:00Z] INFO AuthService localhost test - User logged in'
    log = parse_log_line(log_content)
    assert log is not None
    assert log.service_name == "AuthService"
    assert log.level == LogLevel.INFO
    assert log.message == "User logged in"


def test_parse_valid_csv():
    csv_content = (
        'timestamp,service_name,log_level,message\n'
        '2023-10-01T12:00:00Z,PaymentService,ERROR,Payment failed\n'
    )
    logs = parse_csv_content(csv_content)
    assert len(logs) == 1
    assert logs[0].service_name == "PaymentService"
    assert logs[0].level == LogLevel.ERROR


def test_parse_valid_json():
    json_content = (
        '[{"timestamp":"2023-10-01T12:00:00Z",'
        '"service_name":"DatabaseService","log_level":"WARN","message":"Slow query"}]'
    )
    logs = parse_json_content(json_content)
    assert len(logs) == 1
    assert logs[0].service_name == "DatabaseService"
    assert logs[0].level == LogLevel.WARN


def test_parse_malformed_line_skipped():
    log_content = 'Malformed junk line here without format'
    log = parse_log_line(log_content)
    assert log is None


def test_timestamp_normalization():
    log_content = '[2023-10-01T12:00:00Z] INFO AuthService localhost test - Timestamp test'
    log = parse_log_line(log_content)
    assert log is not None
    assert log.timestamp is not None


def test_severity_mapping():
    # ERR should map to ERROR
    csv_content = (
        'timestamp,service_name,log_level,message\n'
        '2023-10-01T12:00:00Z,PaymentService,ERR,Payment failed\n'
    )
    logs = parse_csv_content(csv_content)
    assert len(logs) == 1
    assert logs[0].level == LogLevel.ERROR


def test_deduplication(db_session):
    from repositories.log_repository import LogRepository
    from schemas.log import LogCreate
    from datetime import datetime

    ts = datetime(2023, 1, 1, 12, 0, 0)
    log = LogCreate(
        timestamp=ts,
        service_name="TestService",
        level=LogLevel.INFO,
        message="Dupe message",
        metadata_json={},
    )

    repo = LogRepository(db_session)
    # Insert same log twice
    repo.batch_insert([log, log])
    count = repo.get_total_count()
    assert count == 1
