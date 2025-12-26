"""
Shared authentication utilities for Python microservices.
"""

from functools import wraps
from fastapi import Request, HTTPException
import os


def get_api_token() -> str:
    """Get API token from environment."""
    return os.getenv("API_TOKEN", "")


def verify_token(token: str) -> bool:
    """Verify if provided token matches expected token."""
    expected = get_api_token()
    if not expected:
        return True  # No token configured, allow all
    return token == expected


def require_auth(func):
    """Decorator to require authentication on endpoints."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.headers.get("X-API-Token")
        if not verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid or missing API token")
        return await func(request, *args, **kwargs)
    return wrapper
