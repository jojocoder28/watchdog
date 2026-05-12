import google.generativeai as genai
from app.core.config import settings
from app.db.models import LogEntry
from typing import List

def analyze_incident_logs(logs: List[LogEntry]) -> str:
    if not settings.GEMINI_API_KEY:
        return "Gemini API key is not configured. AI analysis skipped."
    
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    log_text = "\n".join([f"[{l.timestamp}] {l.level} ({l.service_name}): {l.message}" for l in logs])
    
    prompt = f"""
    You are a Senior Site Reliability Engineer analyzing system logs.
    An incident has occurred. Review the following logs and provide:
    1. A probable root cause.
    2. Recommended remediation steps.
    
    Logs:
    {log_text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to generate AI analysis: {str(e)}"
