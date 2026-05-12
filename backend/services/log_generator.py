"""
Synthetic Log Generator Module

Simulates logs from 5 microservices with realistic patterns such as:
- Normal INFO/WARN logs
- ERROR spikes
- CPU/Memory pressure events
- Timeout storms
- Brute force login patterns
- Payment failure cascades

Outputs to .log, .csv, and .json formats.
"""

import argparse
import csv
import json
import random
import uuid
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from faker import Faker

fake = Faker()

SERVICES = [
    "AuthService",
    "PaymentService",
    "DatabaseService",
    "APIGateway",
    "NotificationService"
]

LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
ENVIRONMENTS = ["production", "production", "production", "staging"] # Weight towards prod

def generate_timestamp(start_time: datetime, end_time: datetime) -> datetime:
    """Generate a random timestamp between start_time and end_time."""
    time_between = end_time - start_time
    random_seconds = random.randrange(int(time_between.total_seconds()))
    return start_time + timedelta(seconds=random_seconds)

def generate_base_log(timestamp: datetime, service: str, level: str, message: str) -> Dict[str, Any]:
    """Create the base dictionary for a log entry."""
    return {
        "timestamp": timestamp.isoformat(),
        "service_name": service,
        "log_level": level,
        "message": message,
        "metadata": {
            "request_id": str(uuid.uuid4()),
            "user_id": fake.random_int(min=1, max=10000) if random.random() > 0.3 else None,
            "latency_ms": random.randint(10, 500),
            "status_code": 200 if level in ["INFO", "DEBUG"] else (400 if level == "WARN" else 500)
        },
        "host": f"{service.lower()}-{fake.hexify(text='^^^')}.internal",
        "environment": random.choice(ENVIRONMENTS)
    }

def inject_brute_force_pattern(logs: List[Dict[str, Any]], start_time: datetime, count: int = 50):
    """Simulate a brute force login attempt pattern on AuthService."""
    user_id = fake.random_int(min=1, max=10000)
    for i in range(count):
        ts = start_time + timedelta(seconds=i * random.uniform(0.1, 0.5))
        log = generate_base_log(ts, "AuthService", "WARN", "Failed login attempt")
        log["metadata"]["user_id"] = user_id
        log["metadata"]["status_code"] = 401
        log["metadata"]["reason"] = "Invalid credentials"
        logs.append(log)

def inject_payment_cascade(logs: List[Dict[str, Any]], start_time: datetime, count: int = 30):
    """Simulate a database failure causing payment cascades."""
    for i in range(count):
        ts = start_time + timedelta(seconds=i * random.uniform(0.2, 1.0))
        # DB fails first
        db_log = generate_base_log(ts, "DatabaseService", "CRITICAL", "Connection pool exhausted")
        db_log["metadata"]["latency_ms"] = random.randint(5000, 10000)
        logs.append(db_log)
        
        # Payment service fails right after
        pay_ts = ts + timedelta(milliseconds=random.randint(10, 50))
        pay_log = generate_base_log(pay_ts, "PaymentService", "ERROR", "Transaction failed due to database timeout")
        pay_log["metadata"]["status_code"] = 503
        logs.append(pay_log)

def inject_timeout_storm(logs: List[Dict[str, Any]], start_time: datetime, count: int = 100):
    """Simulate APIGateway timeout storms."""
    for i in range(count):
        ts = start_time + timedelta(seconds=i * random.uniform(0.01, 0.1))
        log = generate_base_log(ts, "APIGateway", "ERROR", "Upstream service timeout")
        log["metadata"]["latency_ms"] = random.randint(30000, 60000)
        log["metadata"]["status_code"] = 504
        logs.append(log)

def inject_resource_pressure(logs: List[Dict[str, Any]], start_time: datetime, service: str, pressure_type: str):
    """Simulate CPU or Memory pressure events."""
    for i in range(20):
        ts = start_time + timedelta(seconds=i * 5)
        level = "WARN" if i < 15 else "CRITICAL"
        message = f"High {pressure_type} utilization detected: {random.randint(85, 99)}%"
        log = generate_base_log(ts, service, level, message)
        log["metadata"][f"{pressure_type.lower()}_usage"] = random.randint(85, 99)
        logs.append(log)

def generate_logs(total_count: int) -> List[Dict[str, Any]]:
    """Generate synthetic logs with normal traffic and injected anomalous patterns."""
    logs = []
    now = datetime.utcnow()
    start_time = now - timedelta(days=1)  # Spread over the last 24 hours
    
    # 1. Generate Normal Traffic (90% of total_count)
    normal_count = int(total_count * 0.9)
    for _ in range(normal_count):
        ts = generate_timestamp(start_time, now)
        service = random.choice(SERVICES)
        # Weight levels heavily towards INFO/DEBUG
        level = random.choices(LOG_LEVELS, weights=[20, 70, 5, 4, 1])[0]
        message = fake.sentence(nb_words=6)
        logs.append(generate_base_log(ts, service, level, message))
        
    # 2. Inject Anomalous Patterns
    remaining_count = total_count - normal_count
    
    # Spread anomalies throughout the timeline
    num_patterns = 10
    for _ in range(num_patterns):
        pattern_ts = generate_timestamp(start_time, now)
        pattern_type = random.choice(["brute_force", "payment_cascade", "timeout_storm", "cpu_pressure", "mem_pressure"])
        
        if pattern_type == "brute_force":
            inject_brute_force_pattern(logs, pattern_ts, count=random.randint(50, 200))
        elif pattern_type == "payment_cascade":
            inject_payment_cascade(logs, pattern_ts, count=random.randint(20, 100))
        elif pattern_type == "timeout_storm":
            inject_timeout_storm(logs, pattern_ts, count=random.randint(100, 500))
        elif pattern_type == "cpu_pressure":
            inject_resource_pressure(logs, pattern_ts, random.choice(SERVICES), "CPU")
        elif pattern_type == "mem_pressure":
            inject_resource_pressure(logs, pattern_ts, random.choice(SERVICES), "Memory")
            
    # Sort logs chronologically
    logs.sort(key=lambda x: x["timestamp"])
    
    # Trim to exact count if we overshot due to pattern injection
    return logs[:total_count]

def save_to_json(logs: List[Dict[str, Any]], filepath: str):
    """Save logs to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(logs, f, indent=2)

def save_to_csv(logs: List[Dict[str, Any]], filepath: str):
    """Save logs to a CSV file."""
    if not logs:
        return
    keys = ["timestamp", "service_name", "log_level", "message", "metadata", "host", "environment"]
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for log in logs:
            row = log.copy()
            row["metadata"] = json.dumps(row["metadata"])
            writer.writerow(row)

def save_to_log(logs: List[Dict[str, Any]], filepath: str):
    """Save logs to a standard .log file format."""
    with open(filepath, 'w') as f:
        for log in logs:
            meta_str = json.dumps(log["metadata"])
            line = f"[{log['timestamp']}] {log['log_level']} {log['service_name']} {log['host']} {log['environment']} - {log['message']} | Metadata: {meta_str}\n"
            f.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Log Generator")
    parser.add_argument("--count", type=int, default=50000, help="Number of log entries to generate")
    args = parser.parse_args()
    
    print(f"Generating {args.count} synthetic logs with patterns...")
    logs = generate_logs(args.count)
    
    # Resolve dataset directory relative to this script
    # backend/services/log_generator.py -> backend/services -> backend -> project_root -> project_root/dataset
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_dir = os.path.join(project_root, "dataset")
    
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir, exist_ok=True)
        
    print(f"Saving to {dataset_dir}...")
    
    json_path = os.path.join(dataset_dir, "synthetic_logs.json")
    csv_path = os.path.join(dataset_dir, "synthetic_logs.csv")
    log_path = os.path.join(dataset_dir, "synthetic_logs.log")
    
    save_to_json(logs, json_path)
    print(f"Saved {json_path}")
    
    save_to_csv(logs, csv_path)
    print(f"Saved {csv_path}")
    
    save_to_log(logs, log_path)
    print(f"Saved {log_path}")
    
    print("Done!")
