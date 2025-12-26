"""
Pydantic models for request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class EntityResult(BaseModel):
    """A single detected PII entity."""
    type: str = Field(..., description="Entity type (e.g., PERSON, EMAIL_ADDRESS)")
    text: str = Field(..., description="The detected text")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    score: float = Field(..., description="Confidence score (0-1)")


class SanitizeRequest(BaseModel):
    """Request body for /sanitize endpoint."""
    text: str = Field(..., description="Text to sanitize", min_length=1)
    language: str = Field(default="en", description="Language code")
    entities: Optional[List[str]] = Field(
        default=None, 
        description="Specific entity types to detect (e.g., ['PERSON', 'EMAIL_ADDRESS'])"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "John Doe, email john@example.com, SSN 123-45-6789",
                "language": "en",
                "entities": ["PERSON", "EMAIL_ADDRESS", "US_SSN"]
            }
        }


class SanitizeResponse(BaseModel):
    """Response body for /sanitize endpoint."""
    original_text: str = Field(..., description="Original input text")
    sanitized_text: str = Field(..., description="Text with PII replaced by placeholders")
    entities_found: List[EntityResult] = Field(
        default=[], 
        description="List of detected PII entities"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "John Doe, email john@example.com",
                "sanitized_text": "<PERSON>, email <EMAIL_ADDRESS>",
                "entities_found": [
                    {"type": "PERSON", "text": "John Doe", "start": 0, "end": 8, "score": 0.85},
                    {"type": "EMAIL_ADDRESS", "text": "john@example.com", "start": 16, "end": 32, "score": 0.95}
                ]
            }
        }


class AnalyzeRequest(BaseModel):
    """Request body for /analyze endpoint."""
    text: str = Field(..., description="Text to analyze", min_length=1)
    language: str = Field(default="en", description="Language code")
    entities: Optional[List[str]] = Field(
        default=None,
        description="Specific entity types to detect"
    )


class AnalyzeResponse(BaseModel):
    """Response body for /analyze endpoint."""
    text: str = Field(..., description="Original input text")
    entities: List[EntityResult] = Field(
        default=[],
        description="List of detected PII entities"
    )


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
