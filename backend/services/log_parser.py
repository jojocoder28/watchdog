import re
import csv
import json
import logging
from io import StringIO
from typing import List, Optional, Dict, Any
from datetime import datetime
from schemas.log import LogCreate
from models.log import LogLevel

logger = logging.getLogger(__name__)

# Basic regex for standard log format: [2023-01-01T12:00:00Z] INFO ServiceName host env - Message | Metadata: {}
LOG_REGEX = re.compile(
    r"^\[(?P<timestamp>.*?)\]\s+(?P<level>\w+)\s+(?P<service>\S+)\s+(?P<host>\S+)\s+(?P<env>\S+)\s+-\s+(?P<message>.*?)(?:\s+\|\s+Metadata:\s+(?P<metadata>.*))?$"
)

def normalize_level(level_str: str) -> LogLevel:
    """Normalize various severity strings to standard LogLevel."""
    level_str = level_str.upper().strip()
    mapping = {
        "ERR": LogLevel.ERROR,
        "ERROR": LogLevel.ERROR,
        "WARNING": LogLevel.WARN,
        "WARN": LogLevel.WARN,
        "INF": LogLevel.INFO,
        "INFO": LogLevel.INFO,
        "DBG": LogLevel.DEBUG,
        "DEBUG": LogLevel.DEBUG,
        "CRITICAL": LogLevel.FATAL,
        "FATAL": LogLevel.FATAL
    }
    return mapping.get(level_str, LogLevel.INFO)

def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse and normalize timestamp to UTC datetime ISO 8601."""
    try:
        ts_str = ts_str.replace('Z', '+00:00')
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None

def parse_log_line(line: str) -> Optional[LogCreate]:
    """Parse a single text log line using regex."""
    match = LOG_REGEX.match(line)
    if not match:
        logger.warning(f"Malformed log line skipped: {line[:50]}...")
        return None
    
    d = match.groupdict()
    ts = parse_timestamp(d["timestamp"])
    if not ts:
        ts = datetime.utcnow()
        
    meta = {}
    if d.get("metadata"):
        try:
            meta = json.loads(d["metadata"])
        except Exception:
            pass
            
    return LogCreate(
        timestamp=ts,
        level=normalize_level(d["level"]),
        service_name=d["service"],
        message=d["message"],
        metadata_json=meta
    )

def parse_csv_content(content: str) -> List[LogCreate]:
    """Parse logs from CSV format."""
    logs = []
    reader = csv.DictReader(StringIO(content))
    for row in reader:
        try:
            ts = parse_timestamp(row.get("timestamp", "")) or datetime.utcnow()
            meta = {}
            if row.get("metadata"):
                try:
                    meta = json.loads(row["metadata"])
                except Exception:
                    pass
                    
            logs.append(LogCreate(
                timestamp=ts,
                service_name=row.get("service_name", "Unknown"),
                level=normalize_level(row.get("log_level", "INFO")),
                message=row.get("message", ""),
                metadata_json=meta
            ))
        except Exception as e:
            logger.warning(f"Skipping malformed CSV row: {e}")
    return logs

def parse_json_content(content: str) -> List[LogCreate]:
    """Parse logs from JSON format."""
    logs = []
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]
            
        for item in data:
            ts = parse_timestamp(item.get("timestamp", "")) or datetime.utcnow()
            logs.append(LogCreate(
                timestamp=ts,
                service_name=item.get("service_name", "Unknown"),
                level=normalize_level(item.get("log_level", "INFO")),
                message=item.get("message", ""),
                metadata_json=item.get("metadata", {})
            ))
    except Exception as e:
        logger.warning(f"JSON parsing error: {e}")
    return logs
