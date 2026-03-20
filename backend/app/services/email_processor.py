import logging

from fastapi import UploadFile

from app.core.exceptions import EmptyContentError
from app.core.interfaces import Classifier
from app.models.schemas import ClassificationResponse
from app.readers.reader_factory import ReaderFactory
from app.services.text_preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 10


class EmailProcessorService:
    """Facade that orchestrates the full email processing pipeline."""

    def __init__(self, classifier: Classifier, preprocessor: TextPreprocessor):
        self._classifier = classifier
        self._preprocessor = preprocessor

    async def process_file(self, file: UploadFile) -> ClassificationResponse:
        """Process an uploaded email file (txt or pdf)."""
        logger.info("Processing file: %s (type: %s)", file.filename, file.content_type)
        reader = ReaderFactory.create(file.content_type)
        raw_text = await reader.extract_text(file)
        logger.info("Extracted text length: %d chars", len(raw_text))
        return await self._process(raw_text)

    async def process_text(self, text: str) -> ClassificationResponse:
        """Process raw email text."""
        logger.info("Processing raw text input, length: %d chars", len(text))
        return await self._process(text)

    async def _process(self, raw_text: str) -> ClassificationResponse:
        processed_text = self._preprocessor.process(raw_text)
        logger.info("Preprocessed text length: %d chars", len(processed_text))
        logger.debug("Preprocessed text: %s", processed_text[:200])

        if len(processed_text) < MIN_TEXT_LENGTH:
            logger.warning("Text too short after preprocessing: '%s'", processed_text)
            raise EmptyContentError(
                "Email content is too short to classify (minimum 10 characters)"
            )

        logger.info("Sending to classifier: %s", type(self._classifier).__name__)
        result = await self._classifier.classify(processed_text)
        logger.info("Classification result: category=%s, tag=%s", result.category, result.tag)

        return ClassificationResponse(
            category=result.category,
            tag=result.tag,
            suggested_response=result.suggested_response,
            summary=result.summary,
            original_text=raw_text,
        )
