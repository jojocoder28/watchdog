from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import logging

from config import settings
from database import engine, Base
import models # ensure models are registered
from auth.router import router as auth_router
from routes.logs import router as logs_router
from routes.anomaly import router as anomaly_router
from routes.webhook import router as webhook_router
from routes.health import router as health_router
from routes.settings import router as settings_router
from middleware.error_handler import (
    custom_http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from middleware.logging_middleware import LoggingMiddleware

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to initialize the database."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title="Intelligent Observability & Event Watchdog",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

if settings.ENVIRONMENT != "development":
    origins = ["https://yourproductiondomain.com"] # Replace with real domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom logging middleware
app.add_middleware(LoggingMiddleware)

# Register custom exception handlers
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth_router)
app.include_router(logs_router)
app.include_router(anomaly_router)
app.include_router(webhook_router)
app.include_router(health_router)
app.include_router(settings_router)

@app.get("/")
def read_root():
    return {"message": "Intelligent Observability API is running."}
