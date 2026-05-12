from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
import app.db.models  # to ensure models are registered

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Observability & Event Watchdog", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Intelligent Observability API is running."}
