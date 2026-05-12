import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import LogEntry, LogLevel

SERVICES = ["payment-api", "user-service", "auth-gateway", "frontend-app"]
ERROR_MESSAGES = ["Connection timed out", "Database lock acquired", "Invalid credentials", "Null pointer exception", "Rate limit exceeded"]
INFO_MESSAGES = ["User logged in", "Payment processed", "Data synced", "Cache refreshed", "Request successful"]

def generate_synthetic_logs(db: Session, count: int, error_ratio: float) -> int:
    now = datetime.utcnow()
    for i in range(count):
        is_error = random.random() < error_ratio
        level = LogLevel.ERROR if is_error else LogLevel.INFO
        message = random.choice(ERROR_MESSAGES) if is_error else random.choice(INFO_MESSAGES)
        
        timestamp = now - timedelta(seconds=random.randint(0, 3600))
        
        log = LogEntry(
            service_name=random.choice(SERVICES),
            level=level,
            message=message,
            timestamp=timestamp
        )
        db.add(log)
    
    db.commit()
    return count
