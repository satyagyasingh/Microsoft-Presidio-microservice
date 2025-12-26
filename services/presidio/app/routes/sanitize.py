"""
Sanitize endpoint - anonymize PII in text.
"""

from fastapi import APIRouter, Request, HTTPException
import logging

from app.models.schemas import SanitizeRequest, SanitizeResponse, EntityResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sanitize", response_model=SanitizeResponse)
async def sanitize_text(request: Request, body: SanitizeRequest):
    """
    Sanitize text by replacing PII with placeholders.
    
    Detects and anonymizes:
    - Names (PERSON)
    - Email addresses (EMAIL_ADDRESS)
    - Phone numbers (PHONE_NUMBER)
    - Dates (DATE_TIME)
    - Locations (LOCATION)
    - SSN (US_SSN)
    - And more...
    
    Returns the sanitized text and list of detected entities.
    """
    try:
        # Get Presidio service from app state
        presidio = request.app.state.presidio
        
        # Sanitize text
        result = presidio.sanitize(
            text=body.text,
            language=body.language,
            entities=body.entities
        )
        
        # Convert to response model
        entities_found = [
            EntityResult(
                type=e["type"],
                text=e["text"],
                start=e["start"],
                end=e["end"],
                score=e["score"]
            )
            for e in result["entities_found"]
        ]
        
        return SanitizeResponse(
            original_text=result["original_text"],
            sanitized_text=result["sanitized_text"],
            entities_found=entities_found
        )
        
    except Exception as e:
        logger.error(f"Error in /sanitize: {e}")
        raise HTTPException(status_code=500, detail=str(e))
