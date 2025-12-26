"""
Analyze endpoint - detect PII without anonymizing.
"""

from fastapi import APIRouter, Request, HTTPException
import logging

from app.models.schemas import AnalyzeRequest, AnalyzeResponse, EntityResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: Request, body: AnalyzeRequest):
    """
    Analyze text for PII without anonymizing.
    
    Useful for auditing or previewing what would be detected.
    Returns list of detected entities with positions and confidence scores.
    """
    try:
        # Get Presidio service from app state
        presidio = request.app.state.presidio
        
        # Analyze text
        entities = presidio.analyze(
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
            for e in entities
        ]
        
        return AnalyzeResponse(
            text=body.text,
            entities=entities_found
        )
        
    except Exception as e:
        logger.error(f"Error in /analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities")
async def get_supported_entities(request: Request):
    """
    Get list of supported entity types.
    """
    try:
        presidio = request.app.state.presidio
        entities = presidio.get_supported_entities()
        return {"entities": entities}
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
