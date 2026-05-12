import hashlib
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from models.log import LogEntry, LogLevel
from schemas.log import LogCreate, LogFilter

def _generate_log_hash(log: LogCreate) -> str:
    """Generate a unique hash for deduplication based on timestamp, service, and message."""
    ts_str = log.timestamp.isoformat() if log.timestamp else ""
    hash_str = f"{ts_str}_{log.service_name}_{log.message}"
    return hashlib.md5(hash_str.encode('utf-8')).hexdigest()

class LogRepository:
    def __init__(self, db: Session):
        self.db = db

    def batch_insert(self, logs: List[LogCreate]) -> int:
        """Bulk insert logs with deduplication."""
        inserted_count = 0
        seen_hashes = set()
        db_logs = []
        
        for log in logs:
            log_hash = _generate_log_hash(log)
            if log_hash in seen_hashes:
                continue
            seen_hashes.add(log_hash)
            
            db_log = LogEntry(
                timestamp=log.timestamp or datetime.utcnow(),
                service_name=log.service_name,
                level=log.level,
                message=log.message,
                metadata_json=log.metadata_json
            )
            db_logs.append(db_log)
            inserted_count += 1
            
        if db_logs:
            self.db.bulk_save_objects(db_logs)
            self.db.commit()
            
        return inserted_count

    def get_logs(self, skip: int = 0, limit: int = 100, filters: LogFilter = None) -> List[LogEntry]:
        """Paginated query with filters."""
        query = self.db.query(LogEntry)
        
        if filters:
            if filters.service:
                query = query.filter(LogEntry.service_name == filters.service)
            if filters.level:
                query = query.filter(LogEntry.level == filters.level)
            if filters.start_time:
                query = query.filter(LogEntry.timestamp >= filters.start_time)
            if filters.end_time:
                query = query.filter(LogEntry.timestamp <= filters.end_time)
                
        return query.order_by(LogEntry.timestamp.desc()).offset(skip).limit(limit).all()

    def get_log_counts_by_level(self) -> Dict[str, int]:
        """Aggregated counts by level."""
        results = self.db.query(LogEntry.level, func.count(LogEntry.id)).group_by(LogEntry.level).all()
        return {str(level.value): count for level, count in results}
        
    def get_log_counts_by_service(self) -> Dict[str, int]:
        """Aggregated counts by service."""
        results = self.db.query(LogEntry.service_name, func.count(LogEntry.id)).group_by(LogEntry.service_name).all()
        return {service: count for service, count in results}

    def get_recent_logs(self, limit: int = 10) -> List[LogEntry]:
        """Get the most recent logs."""
        return self.db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()
        
    def get_total_count(self) -> int:
        return self.db.query(LogEntry).count()
