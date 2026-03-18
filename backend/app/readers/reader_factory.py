from app.core.exceptions import UnsupportedFileTypeError
from app.core.interfaces import EmailReader
from app.readers.pdf_reader import PdfReader
from app.readers.txt_reader import TxtReader

_READER_MAP: dict[str, type[EmailReader]] = {
    "text/plain": TxtReader,
    "application/pdf": PdfReader,
}


class ReaderFactory:
    """Factory that creates the appropriate EmailReader based on file content type."""

    @staticmethod
    def create(content_type: str) -> EmailReader:
        reader_class = _READER_MAP.get(content_type)
        if reader_class is None:
            raise UnsupportedFileTypeError(content_type)
        return reader_class()

    @staticmethod
    def supported_types() -> list[str]:
        return list(_READER_MAP.keys())
