"""
Microsoft Presidio PII Sanitization Microservice
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.config import get_settings, Settings
from app.routes import sanitize, analyze, health
from app.services.presidio_service import PresidioService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize and cleanup."""
    # Startup
    logger.info("Starting Presidio Microservice...")
    
    # Initialize Presidio service (downloads spaCy model if needed)
    presidio = PresidioService()
    app.state.presidio = presidio
    
    logger.info("Presidio Microservice started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Presidio Microservice...")


# Create FastAPI app
app = FastAPI(
    title="Presidio PII Sanitization Service",
    description="Microservice for detecting and anonymizing PII using Microsoft Presidio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware (for internal Render network)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Token authentication dependency
async def verify_token(request: Request, settings: Settings = Depends(get_settings)):
    """Verify API token from header."""
    # Skip auth for health check
    if request.url.path == "/health":
        return True
    
    # Get token from header
    token = request.headers.get("X-API-Token")
    
    if not settings.api_token:
        # No token configured - allow all (for development)
        logger.warning("No API_TOKEN configured - authentication disabled")
        return True
    
    if not token or token != settings.api_token:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
    
    return True


# Apply token verification to all routes
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Authentication middleware."""
    # Skip auth for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    settings = get_settings()
    
    if settings.api_token:
        token = request.headers.get("X-API-Token")
        if not token or token != settings.api_token:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API token"}
            )
    
    return await call_next(request)


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(sanitize.router, tags=["Sanitization"])
app.include_router(analyze.router, tags=["Analysis"])


@app.get("/")
async def root():
    """Root endpoint - service info."""
    return {
        "service": "Presidio PII Sanitization Service",
        "version": "1.0.0",
        "status": "running"
    }
