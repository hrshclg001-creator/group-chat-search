"""FastAPI application entry point: uvicorn app.main:app."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.config import LOCAL_FRONTEND_ORIGINS

app = FastAPI(title='Group Chat Search', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=['GET'],
    allow_headers=['Accept', 'Content-Type'],
)
app.include_router(health_router, prefix='/api')
