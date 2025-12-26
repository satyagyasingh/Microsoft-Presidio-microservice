# Presidio PII Sanitization Service

Microservice for detecting and anonymizing PII using Microsoft Presidio.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/sanitize` | Anonymize PII in text |
| POST | `/analyze` | Detect PII without anonymizing |
| GET | `/entities` | List supported entity types |

## Local Development

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
uvicorn app.main:app --reload --port 8001
```

## API Examples

### Sanitize
```bash
curl -X POST http://localhost:8001/sanitize \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient John Doe, email john@example.com"}'
```

### Response
```json
{
  "original_text": "Patient John Doe, email john@example.com",
  "sanitized_text": "Patient <PERSON>, email <EMAIL>",
  "entities_found": [...]
}
```
