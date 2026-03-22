import logging
import re

import httpx

from app.config import settings
from app.core.exceptions import ClassificationError
from app.core.interfaces import ClassificationResult, Classifier

logger = logging.getLogger(__name__)

_TAGS: list[str] = [
    "SPAM",
    "POSSÍVEL GOLPE",
    "URGENTE",
    "SOLICITAÇÃO",
    "RECLAMAÇÃO",
    "REUNIÃO",
    "INFORMATIVO",
    "NÃO IMPORTANTE",
]

_TAG_TO_CATEGORY: dict[str, str] = {
    "SPAM": "Improdutivo",
    "POSSÍVEL GOLPE": "Improdutivo",
    "URGENTE": "Produtivo",
    "SOLICITAÇÃO": "Produtivo",
    "RECLAMAÇÃO": "Produtivo",
    "REUNIÃO": "Produtivo",
    "INFORMATIVO": "Improdutivo",
    "NÃO IMPORTANTE": "Improdutivo",
}

_RESPONSE_TEMPLATES: dict[str, str] = {
    "SPAM":
        "Este email foi identificado como conteúdo não relevante e não requer ação.",
    "POSSÍVEL GOLPE":
        "Atenção: este email apresenta características suspeitas. "
        "Não clique em links nem forneça dados pessoais ou credenciais.",
    "URGENTE":
        "Prezado(a), sua mensagem urgente foi recebida. "
        "Nossa equipe foi notificada e retornará o contato com prioridade.",
    "SOLICITAÇÃO":
        "Prezado(a), agradecemos seu contato. "
        "Sua solicitação foi recebida e será analisada em breve.",
    "RECLAMAÇÃO":
        "Lamentamos o ocorrido. "
        "Estamos analisando a situação com prioridade e retornaremos o quanto antes.",
    "REUNIÃO":
        "Prezado(a), confirmamos o recebimento do seu convite. "
        "Retornaremos com nossa disponibilidade em breve.",
    "INFORMATIVO":
        "Agradecemos pelo comunicado. As informações foram registradas.",
    "NÃO IMPORTANTE":
        "Obrigado pela mensagem. Ficamos felizes com o contato.",
}

_CONFIDENCE_THRESHOLD = 0.4
_HF_API_BASE = "https://router.huggingface.co/models"


def _first_sentence(text: str, max_chars: int = 200) -> str:
    """Return the first sentence of text, capped at max_chars."""
    match = re.search(r"[^.!?\n]+[.!?\n]?", text.strip())
    sentence = match.group(0).strip() if match else text.strip()
    return sentence[:max_chars]


class HuggingFaceClassifier(Classifier):
    """Email classifier using HuggingFace zero-shot classification (Strategy Pattern).

    Sends the email text to the HuggingFace Inference API using
    joeddav/xlm-roberta-large-xnli (or a model configured via HF_MODEL).
    The 8 project tags are passed as candidate_labels; the top-scoring
    label becomes the tag, and category is derived from a fixed mapping.
    """

    def __init__(self) -> None:
        self._token = settings.hf_token
        self._model = settings.hf_model
        self._url = f"{_HF_API_BASE}/{self._model}"
        logger.info("HuggingFaceClassifier ready | model=%s", self._model)

    async def classify(self, text: str) -> ClassificationResult:
        logger.info("HuggingFaceClassifier.classify() | text_length=%d", len(text))

        if not self._token:
            raise ClassificationError(
                "HuggingFace service is not configured. Set the HF_TOKEN environment variable."
            )

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": _TAGS,
                "multi_label": False,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self._url, headers=headers, json=payload)
        except httpx.RequestError as e:
            logger.error("HuggingFace request error: %s", e)
            raise ClassificationError(f"Could not reach HuggingFace API: {e}")

        if response.status_code in (502, 503):
            estimated = 20
            try:
                body = response.json()
                estimated = int(float(body.get("estimated_time", 20)))
            except Exception:
                pass
            logger.warning("HuggingFace model unavailable | status=%d | estimated=%ss", response.status_code, estimated)
            raise ClassificationError(
                f"O modelo HuggingFace está carregando ou indisponível. Tente novamente em ~{estimated}s."
            )

        if response.status_code != 200:
            logger.error("HuggingFace API error | status=%d | body=%s", response.status_code, response.text[:300])
            raise ClassificationError(f"HuggingFace API returned status {response.status_code}.")

        try:
            data = response.json()
            # Response is either a dict or a list wrapping a dict
            result = data[0] if isinstance(data, list) else data
            labels: list[str] = result["labels"]
            scores: list[float] = result["scores"]
        except (KeyError, IndexError, TypeError) as e:
            logger.error("Unexpected HuggingFace response format: %s | body=%s", e, response.text[:300])
            raise ClassificationError("HuggingFace returned an unexpected response format.")

        top_tag = labels[0]
        top_score = scores[0]

        logger.info("HF result | top_tag=%s | score=%.3f", top_tag, top_score)

        if top_score < _CONFIDENCE_THRESHOLD:
            logger.info("Low confidence (%.3f) — fallback to NÃO IMPORTANTE", top_score)
            top_tag = "NÃO IMPORTANTE"

        category = _TAG_TO_CATEGORY.get(top_tag, "Improdutivo")
        summary = _first_sentence(text)
        suggested_response = _RESPONSE_TEMPLATES.get(top_tag, _RESPONSE_TEMPLATES["INFORMATIVO"])

        return ClassificationResult(
            category=category,
            tag=top_tag,
            summary=summary,
            suggested_response=suggested_response,
        )
