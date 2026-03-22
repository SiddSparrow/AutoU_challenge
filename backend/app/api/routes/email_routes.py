from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from app.core.exceptions import (
    ClassificationError,
    EmptyContentError,
    TextExtractionError,
    UnsupportedFileTypeError,
)
from app.models.schemas import ClassificationResponse, ClassifyTextRequest, HealthResponse
from app.services.classifier.factory import ClassifierFactory
from app.services.email_processor import EmailProcessorService
from app.services.text_preprocessor import TextPreprocessor

router = APIRouter(prefix="/api", tags=["email"])

ALLOWED_CONTENT_TYPES = {"text/plain", "application/pdf"}


def _get_processor(provider: str = "claude") -> EmailProcessorService:
    classifier = ClassifierFactory.create(provider)
    preprocessor = TextPreprocessor()
    return EmailProcessorService(classifier, preprocessor)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


@router.post("/classify/text", response_model=ClassificationResponse)
async def classify_text(request: ClassifyTextRequest):
    """Classify email from raw text input."""
    processor = _get_processor(request.provider)
    try:
        return await processor.process_text(request.text)
    except EmptyContentError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ClassificationError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/classify/file", response_model=ClassificationResponse)
async def classify_file(
    file: UploadFile = File(...),
    provider: str = Query("claude", description="Classifier provider: claude or classic"),
):
    """Classify email from an uploaded .txt or .pdf file."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: .txt, .pdf",
        )

    processor = _get_processor(provider)
    try:
        return await processor.process_file(file)
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except TextExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except EmptyContentError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ClassificationError as e:
        raise HTTPException(status_code=502, detail=str(e))
