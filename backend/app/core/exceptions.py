class EmailClassifierError(Exception):
    """Base exception for the email classifier application."""


class UnsupportedFileTypeError(EmailClassifierError):
    """Raised when an unsupported file type is uploaded."""

    def __init__(self, content_type: str):
        self.content_type = content_type
        super().__init__(f"Unsupported file type: {content_type}")


class TextExtractionError(EmailClassifierError):
    """Raised when text extraction from a file fails."""


class ClassificationError(EmailClassifierError):
    """Raised when the AI classification fails."""


class EmptyContentError(EmailClassifierError):
    """Raised when the email content is empty or too short."""
