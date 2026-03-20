import json
import logging

import anthropic

from app.config import settings
from app.core.exceptions import ClassificationError
from app.core.interfaces import ClassificationResult, Classifier

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista em classificação de emails corporativos do setor financeiro.

Sua tarefa é:
1. Classificar o email como "Produtivo" ou "Improdutivo"
2. Gerar um breve resumo do email
3. Sugerir uma resposta profissional adequada

## Definições:
- **Produtivo**: Emails que requerem uma ação ou resposta específica (solicitações de suporte, atualizações sobre casos, dúvidas técnicas, pedidos de informação, reclamações, solicitações de reunião).
- **Improdutivo**: Emails que não necessitam de ação imediata (felicitações, agradecimentos genéricos, mensagens de boas festas, correntes, spam, newsletters informativas sem ação requerida).

## Formato de resposta:
Responda APENAS com um JSON válido no seguinte formato, sem texto adicional:
{
  "category": "Produtivo" ou "Improdutivo",
  "summary": "Resumo breve do email em uma frase",
  "suggested_response": "Resposta profissional sugerida em português"
}

## Exemplos:

Email: "Prezado suporte, gostaria de saber o status do chamado #12345 aberto semana passada referente ao erro no sistema de pagamentos."
Resposta: {"category": "Produtivo", "summary": "Solicitação de status do chamado #12345 sobre erro no sistema de pagamentos", "suggested_response": "Prezado(a), agradecemos o contato. Informamos que o chamado #12345 está sendo analisado pela equipe técnica. Retornaremos com uma atualização em breve. Caso necessite de suporte urgente, entre em contato pelo nosso canal prioritário."}

Email: "Feliz Natal a todos da equipe! Que 2026 seja repleto de conquistas e realizações!"
Resposta: {"category": "Improdutivo", "summary": "Mensagem de felicitações de Natal e Ano Novo", "suggested_response": "Obrigado pela mensagem! Desejamos igualmente um excelente 2026 repleto de realizações. Boas festas!"}"""


class ClaudeClassifier(Classifier):
    """Classifies emails using the Claude API (Strategy Pattern)."""

    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.ai_model

    async def classify(self, text: str) -> ClassificationResult:
        logger.info("classify() called | model=%s | text_length=%d", self._model, len(text))
        logger.info("API key configured: %s", bool(settings.anthropic_api_key))

        if not settings.anthropic_api_key:
            raise ClassificationError(
                "AI service is not configured. Set the ANTHROPIC_API_KEY environment variable."
            )

        try:
            logger.info("Sending request to Claude API...")
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Classifique o seguinte email:\n\n{text}",
                    }
                ],
            )

            logger.info("Claude API response received | stop_reason=%s", message.stop_reason)
            response_text = message.content[0].text
            logger.info("Raw response length: %d chars", len(response_text))
            logger.debug("Raw response: %s", response_text[:500])

            # Strip markdown code fences if Claude wraps JSON in ```
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                logger.info("Stripped markdown fences from response")

            data = json.loads(cleaned)
            logger.info("JSON parsed successfully | category=%s", data.get("category"))

            return ClassificationResult(
                category=data["category"],
                suggested_response=data["suggested_response"],
                summary=data["summary"],
            )
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude response as JSON: %s", e)
            logger.error("Raw response was: %s", response_text)
            raise ClassificationError("AI returned an invalid response format")
        except anthropic.APIError as e:
            logger.error("Claude API error [%s]: %s", type(e).__name__, e)
            raise ClassificationError(f"AI service error: {e.message}")
        except KeyError as e:
            logger.error("Missing key in Claude response: %s", e)
            raise ClassificationError("AI response missing required fields")
        except Exception as e:
            logger.error("Unexpected error during classification: [%s] %s", type(e).__name__, e)
            raise ClassificationError(f"Unexpected error: {str(e)}")
