from pydantic import BaseModel, Field


class ClassifyTextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Email text content to classify")


class ClassificationResponse(BaseModel):
    category: str = Field(..., description="Email category: Produtivo or Improdutivo")
    tag: str = Field(..., description="Email tag: SPAM | POSSÍVEL GOLPE | URGENTE | SOLICITAÇÃO | RECLAMAÇÃO | REUNIÃO | INFORMATIVO | NÃO IMPORTANTE")
    suggested_response: str = Field(..., description="AI-generated suggested response")
    summary: str = Field(..., description="Brief summary of the email")
    original_text: str = Field(..., description="Original extracted text")


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "email-classifier-api"
