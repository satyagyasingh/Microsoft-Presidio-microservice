"""
Presidio Service - Wrapper for Microsoft Presidio analyzer and anonymizer.
"""

import logging
from typing import List, Optional
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)


class PresidioService:
    """Service for PII detection and anonymization using Microsoft Presidio."""
    
    def __init__(self):
        """Initialize Presidio analyzer and anonymizer engines."""
        logger.info("Initializing Presidio engines...")
        
        # Initialize analyzer with default recognizers
        self.analyzer = AnalyzerEngine()
        
        # Initialize anonymizer
        self.anonymizer = AnonymizerEngine()
        
        # Healthcare-relevant entity types
        self.healthcare_entities = [
            "PERSON",
            "EMAIL_ADDRESS", 
            "PHONE_NUMBER",
            "DATE_TIME",
            "LOCATION",
            "US_SSN",
            "CREDIT_CARD",
            "IP_ADDRESS",
            "URL",
            "US_DRIVER_LICENSE",
            "MEDICAL_LICENSE"
        ]
        
        logger.info("Presidio engines initialized successfully")
    
    def analyze(
        self, 
        text: str, 
        language: str = "en",
        entities: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Analyze text for PII entities.
        
        Args:
            text: Text to analyze
            language: Language code (default: en)
            entities: Specific entity types to detect, or None for all
            
        Returns:
            List of detected entities with type, text, position, and score
        """
        try:
            # Use specified entities or healthcare defaults
            target_entities = entities if entities else self.healthcare_entities
            
            # Analyze text
            results: List[RecognizerResult] = self.analyzer.analyze(
                text=text,
                language=language,
                entities=target_entities
            )
            
            # Convert to dict format
            entities_found = []
            for result in results:
                entities_found.append({
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "start": result.start,
                    "end": result.end,
                    "score": round(result.score, 2)
                })
            
            logger.info(f"Analyzed text: found {len(entities_found)} entities")
            return entities_found
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise
    
    def sanitize(
        self,
        text: str,
        language: str = "en",
        entities: Optional[List[str]] = None
    ) -> dict:
        """
        Sanitize text by replacing PII with placeholders.
        
        Args:
            text: Text to sanitize
            language: Language code (default: en)
            entities: Specific entity types to detect, or None for all
            
        Returns:
            Dict with original_text, sanitized_text, and entities_found
        """
        try:
            # Use specified entities or healthcare defaults
            target_entities = entities if entities else self.healthcare_entities
            
            # Analyze text first
            analyzer_results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=target_entities
            )
            
            if not analyzer_results:
                # No PII found
                logger.info("No PII found in text")
                return {
                    "original_text": text,
                    "sanitized_text": text,
                    "entities_found": []
                }
            
            # Anonymize - replace with entity type placeholders
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators={
                    "DEFAULT": OperatorConfig("replace", {"new_value": "<REDACTED>"}),
                    "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
                    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
                    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
                    "DATE_TIME": OperatorConfig("replace", {"new_value": "<DATE>"}),
                    "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
                    "US_SSN": OperatorConfig("replace", {"new_value": "<SSN>"}),
                    "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<CREDIT_CARD>"}),
                    "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP_ADDRESS>"}),
                    "URL": OperatorConfig("replace", {"new_value": "<URL>"}),
                    "US_DRIVER_LICENSE": OperatorConfig("replace", {"new_value": "<DRIVER_LICENSE>"}),
                    "MEDICAL_LICENSE": OperatorConfig("replace", {"new_value": "<MEDICAL_LICENSE>"})
                }
            )
            
            # Build entities list
            entities_found = []
            for result in analyzer_results:
                entities_found.append({
                    "type": result.entity_type,
                    "text": text[result.start:result.end],
                    "start": result.start,
                    "end": result.end,
                    "score": round(result.score, 2)
                })
            
            logger.info(f"Sanitized text: replaced {len(entities_found)} entities")
            
            return {
                "original_text": text,
                "sanitized_text": anonymized.text,
                "entities_found": entities_found
            }
            
        except Exception as e:
            logger.error(f"Error sanitizing text: {e}")
            raise
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types."""
        return self.analyzer.get_supported_entities()
