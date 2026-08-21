"""
FastAPI application entrypoint.

Keep this file thin — it wires together routers and startup config.
Route logic lives in app/api/routes/, business logic in app/services/.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import applications, health, jobs, matches, resumes
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="AI Job Intelligence & Application Tracker",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["health"])
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(matches.router)
app.include_router(applications.router)
