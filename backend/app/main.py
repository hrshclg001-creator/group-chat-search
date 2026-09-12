"""FastAPI application entry point: uvicorn app.main:app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.search import router as search_router
from app.config import LOCAL_FRONTEND_ORIGINS
from app.services.search import SearchService

def create_app(service_factory=None):
    factory = SearchService.from_disk if service_factory is None else service_factory

    @asynccontextmanager
    async def lifespan(application):
        application.state.search_service = factory()
        try:
            yield
        finally:
            del application.state.search_service

    application = FastAPI(title='Group Chat Search', version='0.2.0', lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_FRONTEND_ORIGINS,
        allow_credentials=False,
        allow_methods=['GET', 'POST'],
        allow_headers=['Accept', 'Content-Type'],
    )
    application.include_router(health_router, prefix='/api')
    application.include_router(search_router, prefix='/api')
    return application


app = create_app()
