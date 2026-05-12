from fastapi import APIRouter
from app.api.routes import auth, logs, incidents, alerts, dashboard, settings, webhook, anomaly

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
api_router.include_router(anomaly.router, prefix="/anomaly", tags=["anomaly"])
