import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from functools import wraps
from threading import Lock
from datetime import datetime, timedelta

from google import genai

from config import settings
from models.incident import Incident
from models.log import LogEntry
from models.alert import Alert

logger = logging.getLogger(__name__)

# Very simple dictionary cache
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = Lock()

# Token bucket for rate limiting (10 req / min)
_rate_limit_lock = Lock()
_tokens = 10
_last_refill = time.time()
REFILL_RATE_SECONDS = 60.0 / 10.0 # 1 token per 6 seconds

def _get_token():
    global _tokens, _last_refill
    with _rate_limit_lock:
        now = time.time()
        elapsed = now - _last_refill
        # Refill
        if elapsed > REFILL_RATE_SECONDS:
            tokens_to_add = int(elapsed / REFILL_RATE_SECONDS)
            _tokens = min(10, _tokens + tokens_to_add)
            _last_refill = now - (elapsed % REFILL_RATE_SECONDS)
        
        if _tokens >= 1:
            _tokens -= 1
            return True
        return False

def rate_limited_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            backoff_delay = 1.0
            
            while retries <= max_retries:
                # Check rate limit
                while not _get_token():
                    time.sleep(1.0) # wait for token
                    
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Gemini API error (Attempt {retries+1}/{max_retries+1}): {str(e)}")
                    retries += 1
                    if retries > max_retries:
                        break
                    time.sleep(backoff_delay)
                    backoff_delay *= 2
            
            # Fallback
            logger.error("Gemini API failed after all retries. Returning fallback.")
            return "AI service is currently unavailable. Please review the raw logs."
        return wrapper
    return decorator

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not set. AI functions will use fallback.")
            
        self.model_name = "gemini-2.5-flash"
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

    def _read_prompt(self, filename: str) -> str:
        path = os.path.join(self.prompts_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file {filename} not found at {path}.")
            return ""

    @rate_limited_with_backoff(max_retries=3)
    def _generate_content(self, prompt_text: str) -> str:
        if not self.client:
            raise ValueError("Gemini API Client not initialized. Key is missing.")
            
        logger.info(f"Sending prompt to Gemini ({len(prompt_text)} chars)")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_text
        )
        logger.info("Received response from Gemini.")
        return response.text.strip()

    def _check_cache(self, key: str) -> Optional[str]:
        with _cache_lock:
            cached = _cache.get(key)
            if cached and datetime.utcnow() < cached["expires"]:
                return cached["value"]
        return None

    def _set_cache(self, key: str, value: str):
        with _cache_lock:
            _cache[key] = {
                "value": value,
                "expires": datetime.utcnow() + timedelta(minutes=5)
            }

    def summarize_incident(self, incident: Incident, logs: List[LogEntry]) -> str:
        cache_key = f"summary_{incident.id}"
        cached = self._check_cache(cache_key)
        if cached: return cached

        template = self._read_prompt("incident_summary.txt")
        if not template:
            return "Could not load summary prompt template."

        log_text = "\n".join([f"[{l.timestamp}] {l.level} {l.service_name}: {l.message}" for l in logs])
        
        prompt = template.format(
            title=incident.title,
            severity=incident.severity.value,
            service=incident.affected_service or "Unknown",
            start_time=incident.start_time.isoformat() if incident.start_time else "Unknown",
            logs=log_text[:2000] # truncate to avoid huge prompts
        )
        
        result = self._generate_content(prompt)
        self._set_cache(cache_key, result)
        return result

    def generate_root_cause_hypothesis(self, incident: Incident, logs: List[LogEntry]) -> str:
        cache_key = f"rootcause_{incident.id}"
        cached = self._check_cache(cache_key)
        if cached: return cached

        template = self._read_prompt("root_cause.txt")
        if not template:
            return "Could not load root cause prompt template."

        log_text = "\n".join([f"[{l.timestamp}] {l.level} {l.service_name}: {l.message}" for l in logs])
        
        prompt = template.format(
            title=incident.title,
            severity=incident.severity.value,
            service=incident.affected_service or "Unknown",
            logs=log_text[:2000]
        )
        
        result = self._generate_content(prompt)
        self._set_cache(cache_key, result)
        return result

    def generate_human_readable_alert(self, alert: Alert) -> str:
        template = self._read_prompt("alert_explanation.txt")
        if not template:
            return "Could not load alert explanation template."

        prompt = template.format(
            incident_id=alert.incident_id,
            rule_triggered=alert.rule_triggered,
            created_at=alert.created_at.isoformat() if alert.created_at else "Unknown"
        )
        
        return self._generate_content(prompt)

    def explain_anomaly(self, anomaly_data: dict) -> str:
        template = self._read_prompt("anomaly_explain.txt")
        if not template:
            return "Could not load anomaly explain template."

        data_str = json.dumps(anomaly_data, indent=2)
        prompt = template.format(anomaly_data=data_str)
        
        return self._generate_content(prompt)
