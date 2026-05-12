import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.log import LogEntry, LogLevel
from models.incident import IncidentSeverity
from schemas.incident import IncidentCreate

logger = logging.getLogger(__name__)

class AnomalyEngine:
    def __init__(self, db: Session):
        self.db = db

    def run_all_detectors(self) -> List[IncidentCreate]:
        """Run all anomaly detection methods and return created incidents."""
        now = datetime.utcnow()
        incidents = []
        
        window_start = now - timedelta(minutes=5)
        recent_logs = self.db.query(LogEntry).filter(LogEntry.timestamp >= window_start).all()
        
        if not recent_logs:
            return incidents
            
        incidents.extend(self._detect_thresholds(recent_logs))
        incidents.extend(self._detect_spikes(now))
        incidents.extend(self._detect_zscore(now))
        incidents.extend(self._detect_isolation_forest(now))
        incidents.extend(self._detect_specific_patterns(recent_logs))
        
        return incidents

    def _detect_thresholds(self, logs: List[LogEntry]) -> List[IncidentCreate]:
        incidents = []
        error_count = sum(1 for log in logs if log.level == LogLevel.ERROR)
        critical_count = sum(1 for log in logs if log.level == LogLevel.FATAL)
        
        if critical_count > 10:
            log_ids = [log.id for log in logs if log.level == LogLevel.FATAL][:10]
            incidents.append(IncidentCreate(
                title="Critical Failure Threshold Exceeded",
                incident_type="ThresholdViolation",
                severity=IncidentSeverity.CRITICAL,
                confidence_score=1.0,
                start_time=datetime.utcnow(),
                log_sample=log_ids
            ))
            
        if error_count > 50:
            log_ids = [log.id for log in logs if log.level == LogLevel.ERROR][:10]
            incidents.append(IncidentCreate(
                title="High Error Volume Detected",
                incident_type="ThresholdViolation",
                severity=IncidentSeverity.HIGH,
                confidence_score=1.0,
                start_time=datetime.utcnow(),
                log_sample=log_ids
            ))
            
        service_counts = {}
        for log in logs:
            if log.service_name not in service_counts:
                service_counts[log.service_name] = {"total": 0, "errors": 0}
            service_counts[log.service_name]["total"] += 1
            if log.level in [LogLevel.ERROR, LogLevel.FATAL]:
                service_counts[log.service_name]["errors"] += 1
                
        for service, counts in service_counts.items():
            if counts["total"] > 10:
                rate = counts["errors"] / counts["total"]
                if rate > 0.3:
                    incidents.append(IncidentCreate(
                        title=f"{service} Degradation: Error Rate > 30%",
                        incident_type="ServiceDegradation",
                        severity=IncidentSeverity.HIGH,
                        confidence_score=round(rate, 2),
                        affected_service=service,
                        start_time=datetime.utcnow()
                    ))
                    
        for log in logs:
            if log.metadata_json and log.metadata_json.get("latency_ms", 0) > 5000:
                incidents.append(IncidentCreate(
                    title="Severe Latency Spike",
                    incident_type="LatencySpike",
                    severity=IncidentSeverity.HIGH,
                    confidence_score=1.0,
                    affected_service=log.service_name,
                    start_time=datetime.utcnow(),
                    log_sample=[log.id]
                ))
                break
                
        return incidents

    def _detect_spikes(self, now: datetime) -> List[IncidentCreate]:
        incidents = []
        current_start = now - timedelta(minutes=5)
        prev_start = now - timedelta(minutes=10)
        
        current_errors = self.db.query(func.count(LogEntry.id)).filter(
            LogEntry.timestamp >= current_start,
            LogEntry.level.in_([LogLevel.ERROR, LogLevel.FATAL])
        ).scalar() or 0
        
        prev_errors = self.db.query(func.count(LogEntry.id)).filter(
            LogEntry.timestamp >= prev_start,
            LogEntry.timestamp < current_start,
            LogEntry.level.in_([LogLevel.ERROR, LogLevel.FATAL])
        ).scalar() or 0
        
        if prev_errors > 5 and current_errors > (prev_errors * 3):
            incidents.append(IncidentCreate(
                title="Error Spike Detected (>200% increase)",
                incident_type="ErrorSpike",
                severity=IncidentSeverity.HIGH,
                confidence_score=0.9,
                start_time=now
            ))
            
        return incidents

    def _detect_zscore(self, now: datetime) -> List[IncidentCreate]:
        incidents = []
        current_start = now - timedelta(minutes=5)
        start_24h = now - timedelta(hours=24)
        
        errors_24h = self.db.query(func.count(LogEntry.id)).filter(
            LogEntry.timestamp >= start_24h,
            LogEntry.level.in_([LogLevel.ERROR, LogLevel.FATAL])
        ).scalar() or 0
        
        current_errors = self.db.query(func.count(LogEntry.id)).filter(
            LogEntry.timestamp >= current_start,
            LogEntry.level.in_([LogLevel.ERROR, LogLevel.FATAL])
        ).scalar() or 0
        
        mean = errors_24h / 288.0
        std_dev = np.sqrt(mean) if mean > 0 else 1.0
        
        if std_dev > 0:
            z_score = (current_errors - mean) / std_dev
            if z_score > 2.5:
                conf = min(z_score / 10.0, 1.0)
                incidents.append(IncidentCreate(
                    title=f"Z-Score Anomaly Detected (Z={z_score:.2f})",
                    incident_type="ZScoreAnomaly",
                    severity=IncidentSeverity.MEDIUM if z_score < 4.0 else IncidentSeverity.HIGH,
                    confidence_score=round(conf, 2),
                    start_time=now
                ))
                
        return incidents

    def _detect_isolation_forest(self, now: datetime) -> List[IncidentCreate]:
        incidents = []
        try:
            start_time = now - timedelta(hours=4)
            logs = self.db.query(LogEntry).filter(LogEntry.timestamp >= start_time).all()
            
            if len(logs) < 100:
                return incidents
                
            buckets = {}
            for log in logs:
                bucket_min = log.timestamp.minute - (log.timestamp.minute % 5)
                bucket_key = log.timestamp.replace(minute=bucket_min, second=0, microsecond=0)
                
                if bucket_key not in buckets:
                    buckets[bucket_key] = {"error": 0, "warn": 0, "latency_sum": 0, "req": 0}
                    
                buckets[bucket_key]["req"] += 1
                if log.level in [LogLevel.ERROR, LogLevel.FATAL]:
                    buckets[bucket_key]["error"] += 1
                elif log.level == LogLevel.WARN:
                    buckets[bucket_key]["warn"] += 1
                    
                if log.metadata_json:
                    buckets[bucket_key]["latency_sum"] += log.metadata_json.get("latency_ms", 0)
                    
            X = []
            keys = sorted(list(buckets.keys()))
            for k in keys:
                b = buckets[k]
                avg_lat = b["latency_sum"] / b["req"] if b["req"] > 0 else 0
                X.append([b["error"], b["warn"], avg_lat, b["req"]])
                
            if len(X) < 10:
                return incidents
                
            clf = IsolationForest(contamination=0.05, random_state=42)
            clf.fit(X[:-1])
            
            latest_vector = [X[-1]]
            pred = clf.predict(latest_vector)[0]
            score = clf.decision_function(latest_vector)[0]
            
            if pred == -1:
                conf = min(abs(score), 1.0)
                incidents.append(IncidentCreate(
                    title="Isolation Forest ML Anomaly Detected",
                    incident_type="MLAnomaly",
                    severity=IncidentSeverity.HIGH,
                    confidence_score=round(conf, 2),
                    start_time=keys[-1]
                ))
                
        except Exception as e:
            logger.error(f"Isolation Forest error: {e}")
            
        return incidents

    def _detect_specific_patterns(self, logs: List[LogEntry]) -> List[IncidentCreate]:
        incidents = []
        
        auth_failures = {}
        for log in logs:
            if log.service_name == "AuthService" and log.metadata_json and log.metadata_json.get("status_code") == 401:
                uid = log.metadata_json.get("user_id")
                if uid:
                    auth_failures[uid] = auth_failures.get(uid, 0) + 1
                    
        for uid, count in auth_failures.items():
            if count > 20:
                incidents.append(IncidentCreate(
                    title=f"Brute Force Login Attempt (User {uid})",
                    incident_type="Security",
                    severity=IncidentSeverity.HIGH,
                    confidence_score=1.0,
                    affected_service="AuthService",
                    start_time=datetime.utcnow()
                ))
                
        db_timeouts = sum(1 for log in logs if log.service_name == "DatabaseService" and "pool exhausted" in log.message.lower())
        payment_fails = sum(1 for log in logs if log.service_name == "PaymentService" and log.level == LogLevel.ERROR)
        
        if db_timeouts > 0 and payment_fails > 10:
            incidents.append(IncidentCreate(
                title="Payment Cascade Failure due to DB",
                incident_type="CascadeFailure",
                severity=IncidentSeverity.CRITICAL,
                confidence_score=0.95,
                affected_service="PaymentService",
                start_time=datetime.utcnow()
            ))
            
        for log in logs:
            if log.metadata_json:
                cpu = log.metadata_json.get("cpu_usage", 0)
                mem = log.metadata_json.get("memory_usage", 0)
                if cpu > 90 or mem > 90:
                    incidents.append(IncidentCreate(
                        title=f"Resource Exhaustion in {log.service_name}",
                        incident_type="ResourcePressure",
                        severity=IncidentSeverity.HIGH,
                        confidence_score=0.85,
                        affected_service=log.service_name,
                        start_time=datetime.utcnow(),
                        log_sample=[log.id]
                    ))
                    break
                    
        return incidents
