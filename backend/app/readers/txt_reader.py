from fastapi import UploadFile

from app.core.exceptions import TextExtractionError
from app.core.interfaces import EmailReader


class TxtReader(EmailReader):
    """Reads text content from .txt files."""

    async def extract_text(self, file: UploadFile) -> str:
        try:
            content = await file.read()
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except Exception as e:
                raise TextExtractionError(f"Failed to decode text file: {e}")
        except Exception as e:
            raise TextExtractionError(f"Failed to read text file: {e}")
