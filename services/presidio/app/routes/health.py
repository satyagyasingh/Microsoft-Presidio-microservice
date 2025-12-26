"""
Health check endpoint.
"""

from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for Render monitoring.
    Returns service status and version.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
