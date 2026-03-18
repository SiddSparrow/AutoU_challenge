from fastapi import UploadFile

from app.core.exceptions import EmptyContentError
from app.core.interfaces import Classifier
from app.models.schemas import ClassificationResponse
from app.readers.reader_factory import ReaderFactory
from app.services.text_preprocessor import TextPreprocessor

MIN_TEXT_LENGTH = 10


class EmailProcessorService:
    """Facade that orchestrates the full email processing pipeline."""

    def __init__(self, classifier: Classifier, preprocessor: TextPreprocessor):
        self._classifier = classifier
        self._preprocessor = preprocessor

    async def process_file(self, file: UploadFile) -> ClassificationResponse:
        """Process an uploaded email file (txt or pdf)."""
        reader = ReaderFactory.create(file.content_type)
        raw_text = await reader.extract_text(file)
        return await self._process(raw_text)

    async def process_text(self, text: str) -> ClassificationResponse:
        """Process raw email text."""
        return await self._process(text)

    async def _process(self, raw_text: str) -> ClassificationResponse:
        processed_text = self._preprocessor.process(raw_text)

        if len(processed_text) < MIN_TEXT_LENGTH:
            raise EmptyContentError(
                "Email content is too short to classify (minimum 10 characters)"
            )

        result = await self._classifier.classify(processed_text)

        return ClassificationResponse(
            category=result.category,
            confidence=result.confidence,
            suggested_response=result.suggested_response,
            summary=result.summary,
            original_text=raw_text,
        )
