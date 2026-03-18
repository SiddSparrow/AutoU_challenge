import io

import pytest

from app.core.exceptions import UnsupportedFileTypeError
from app.readers.reader_factory import ReaderFactory
from app.readers.txt_reader import TxtReader


class FakeUploadFile:
    """Minimal UploadFile mock for testing."""

    def __init__(self, content: bytes, content_type: str = "text/plain"):
        self.content_type = content_type
        self._content = content

    async def read(self) -> bytes:
        return self._content


class TestReaderFactory:
    def test_create_txt_reader(self):
        reader = ReaderFactory.create("text/plain")
        assert isinstance(reader, TxtReader)

    def test_create_pdf_reader(self):
        reader = ReaderFactory.create("application/pdf")
        assert reader is not None

    def test_unsupported_type_raises(self):
        with pytest.raises(UnsupportedFileTypeError):
            ReaderFactory.create("image/png")

    def test_supported_types(self):
        types = ReaderFactory.supported_types()
        assert "text/plain" in types
        assert "application/pdf" in types


class TestTxtReader:
    @pytest.mark.asyncio
    async def test_extract_utf8_text(self):
        reader = TxtReader()
        content = "Olá, como vai você?".encode("utf-8")
        file = FakeUploadFile(content)
        result = await reader.extract_text(file)
        assert "Olá, como vai você?" == result

    @pytest.mark.asyncio
    async def test_extract_latin1_fallback(self):
        reader = TxtReader()
        content = "Olá mundo".encode("latin-1")
        # Create bytes that are invalid UTF-8 but valid Latin-1
        bad_utf8 = b"\xc0\xe9\xf1"
        file = FakeUploadFile(bad_utf8)
        result = await reader.extract_text(file)
        assert len(result) > 0
