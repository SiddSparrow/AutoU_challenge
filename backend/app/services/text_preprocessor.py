import re


class TextPreprocessor:
    """Preprocesses email text for classification using NLP techniques."""

    # Common email header patterns (English and Portuguese)
    _HEADER_PATTERNS = [
        r"^(From|To|Cc|Bcc|Subject|Date|Sent|Received):\s*.*$",
        r"^(De|Para|Assunto|Data|Cc|Cco|Enviado em):\s*.*$",
        r"^-{2,}\s*(Original Message|Forwarded message|Mensagem original)\s*-{2,}$",
    ]

    # Email signature indicators
    _SIGNATURE_INDICATORS = [
        r"^--\s*$",
        r"^(Atenciosamente|Att\.|Cordialmente|Abraço|Abraços|Best regards|Regards|Sincerely)",
        r"^(Enviado do meu|Sent from my)",
    ]

    def process(self, text: str) -> str:
        """Clean and normalize email text for classification."""
        text = self._remove_headers(text)
        text = self._remove_html_tags(text)
        text = self._remove_urls(text)
        text = self._remove_signature(text)
        text = self._normalize_whitespace(text)
        return text.strip()

    def _remove_headers(self, text: str) -> str:
        lines = text.split("\n")
        cleaned = []
        for line in lines:
            is_header = any(
                re.match(pattern, line.strip(), re.IGNORECASE)
                for pattern in self._HEADER_PATTERNS
            )
            if not is_header:
                cleaned.append(line)
        return "\n".join(cleaned)

    def _remove_html_tags(self, text: str) -> str:
        return re.sub(r"<[^>]+>", "", text)

    def _remove_urls(self, text: str) -> str:
        return re.sub(r"https?://\S+|www\.\S+", "", text)

    def _remove_signature(self, text: str) -> str:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            for pattern in self._SIGNATURE_INDICATORS:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    return "\n".join(lines[:i])
        return text

    def _normalize_whitespace(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text
