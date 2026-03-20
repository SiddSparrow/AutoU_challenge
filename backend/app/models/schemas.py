from pydantic import BaseModel, Field


class ClassifyTextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Email text content to classify")


class ClassificationResponse(BaseModel):
    category: str = Field(..., description="Email category: Produtivo or Improdutivo")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score computed from text signals")
    confidence_flags: list[str] = Field(default_factory=list, description="Human-readable signals that reduced confidence")
    suggested_response: str = Field(..., description="AI-generated suggested response")
    summary: str = Field(..., description="Brief summary of the email")
    original_text: str = Field(..., description="Original extracted text")


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "email-classifier-api"
