from app.services.text_preprocessor import TextPreprocessor


class TestTextPreprocessor:
    def setup_method(self):
        self.preprocessor = TextPreprocessor()

    def test_remove_email_headers(self):
        text = "From: user@example.com\nTo: support@company.com\nSubject: Help\n\nI need help with my account."
        result = self.preprocessor.process(text)
        assert "From:" not in result
        assert "To:" not in result
        assert "Subject:" not in result
        assert "I need help with my account." in result

    def test_remove_html_tags(self):
        text = "<p>Hello <b>world</b></p>"
        result = self.preprocessor.process(text)
        assert "<p>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "world" in result

    def test_remove_urls(self):
        text = "Visit https://example.com for more info."
        result = self.preprocessor.process(text)
        assert "https://example.com" not in result
        assert "Visit" in result

    def test_remove_signature(self):
        text = "Please review the document.\n\nAtenciosamente,\nJoão Silva\nDiretor"
        result = self.preprocessor.process(text)
        assert "Please review the document." in result
        assert "João Silva" not in result

    def test_normalize_whitespace(self):
        text = "Hello\n\n\n\n\nWorld"
        result = self.preprocessor.process(text)
        assert "\n\n\n" not in result

    def test_preserves_meaningful_content(self):
        text = "Gostaria de saber o status do chamado #12345 aberto semana passada."
        result = self.preprocessor.process(text)
        assert "status do chamado #12345" in result

    def test_empty_text(self):
        result = self.preprocessor.process("")
        assert result == ""
