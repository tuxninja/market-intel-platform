"""
Main FastAPI application entry point.

Configures CORS, routes, middleware, and lifecycle events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import init_db, close_db
from app.api import auth, digest, debug

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Market Intelligence Platform API")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Market Intelligence Platform API")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information about the API.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(digest.router, prefix=f"{settings.API_V1_PREFIX}/digest", tags=["Digest"])
app.include_router(debug.router, prefix=f"{settings.API_V1_PREFIX}/debug", tags=["Debug"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
