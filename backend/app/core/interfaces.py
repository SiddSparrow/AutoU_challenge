from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import UploadFile


@dataclass
class ClassificationResult:
    """Result of an email classification."""

    category: str
    confidence: float
    suggested_response: str
    summary: str


class EmailReader(ABC):
    """Interface for reading email content from different file formats."""

    @abstractmethod
    async def extract_text(self, file: UploadFile) -> str:
        """Extract text content from an uploaded file."""
        ...


class Classifier(ABC):
    """Interface for classifying email content."""

    @abstractmethod
    async def classify(self, text: str) -> ClassificationResult:
        """Classify email text and return structured result."""
        ...
