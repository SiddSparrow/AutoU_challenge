import io

import fitz  # PyMuPDF
from fastapi import UploadFile

from app.core.exceptions import TextExtractionError
from app.core.interfaces import EmailReader


class PdfReader(EmailReader):
    """Reads text content from .pdf files using PyMuPDF."""

    async def extract_text(self, file: UploadFile) -> str:
        try:
            content = await file.read()
            pdf_stream = io.BytesIO(content)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")

            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())

            doc.close()
            text = "\n".join(text_parts).strip()

            if not text:
                raise TextExtractionError("PDF file contains no extractable text")

            return text
        except TextExtractionError:
            raise
        except Exception as e:
            raise TextExtractionError(f"Failed to extract text from PDF: {e}")
