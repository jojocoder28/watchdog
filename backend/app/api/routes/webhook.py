from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.schemas import WebhookTestRequest
from app.api.deps import get_current_user
import httpx

router = APIRouter()

@router.post("/test")
async def test_webhook(req: WebhookTestRequest, current_user: User = Depends(get_current_user)) -> Any:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(req.url, json=req.payload, timeout=5.0)
            return {
                "status": "success",
                "status_code": response.status_code,
                "response": response.text[:200]
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
