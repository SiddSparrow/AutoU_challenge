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
2. Atribuir um nível de confiança (0.0 a 1.0)
3. Gerar um breve resumo do email
4. Sugerir uma resposta profissional adequada

## Definições:
- **Produtivo**: Emails que requerem uma ação ou resposta específica (solicitações de suporte, atualizações sobre casos, dúvidas técnicas, pedidos de informação, reclamações, solicitações de reunião).
- **Improdutivo**: Emails que não necessitam de ação imediata (felicitações, agradecimentos genéricos, mensagens de boas festas, correntes, spam, newsletters informativas sem ação requerida).

## Formato de resposta:
Responda APENAS com um JSON válido no seguinte formato, sem texto adicional:
{
  "category": "Produtivo" ou "Improdutivo",
  "confidence": 0.0 a 1.0,
  "summary": "Resumo breve do email em uma frase",
  "suggested_response": "Resposta profissional sugerida em português"
}

## Exemplos:

Email: "Prezado suporte, gostaria de saber o status do chamado #12345 aberto semana passada referente ao erro no sistema de pagamentos."
Resposta: {"category": "Produtivo", "confidence": 0.95, "summary": "Solicitação de status do chamado #12345 sobre erro no sistema de pagamentos", "suggested_response": "Prezado(a), agradecemos o contato. Informamos que o chamado #12345 está sendo analisado pela equipe técnica. Retornaremos com uma atualização em breve. Caso necessite de suporte urgente, entre em contato pelo nosso canal prioritário."}

Email: "Feliz Natal a todos da equipe! Que 2026 seja repleto de conquistas e realizações!"
Resposta: {"category": "Improdutivo", "confidence": 0.98, "summary": "Mensagem de felicitações de Natal e Ano Novo", "suggested_response": "Obrigado pela mensagem! Desejamos igualmente um excelente 2026 repleto de realizações. Boas festas!"}"""


class ClaudeClassifier(Classifier):
    """Classifies emails using the Claude API (Strategy Pattern)."""

    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.ai_model

    async def classify(self, text: str) -> ClassificationResult:
        try:
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

            response_text = message.content[0].text
            data = json.loads(response_text)

            return ClassificationResult(
                category=data["category"],
                confidence=data["confidence"],
                suggested_response=data["suggested_response"],
                summary=data["summary"],
            )
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude response as JSON: %s", e)
            raise ClassificationError("AI returned an invalid response format")
        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            raise ClassificationError(f"AI service error: {e.message}")
        except KeyError as e:
            logger.error("Missing key in Claude response: %s", e)
            raise ClassificationError("AI response missing required fields")
