import json
import logging
import re

import anthropic

from app.config import settings
from app.core.exceptions import ClassificationError
from app.core.interfaces import ClassificationResult, Classifier

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um especialista em classificação de emails corporativos do setor financeiro.

Sua tarefa é:
1. Classificar o email como "Produtivo" ou "Improdutivo"
2. Atribuir exatamente UMA tag que descreve a natureza do email
3. Gerar um breve resumo do email
4. Sugerir uma resposta profissional adequada

## Definições de categoria:
- **Produtivo**: Emails que requerem uma ação ou resposta específica (suporte, dúvidas, reclamações, reuniões, pedidos de informação).
- **Improdutivo**: Emails que não necessitam de ação imediata (felicitações, agradecimentos, spam, newsletters sem ação).

## Tags disponíveis (escolha exatamente UMA):
- "SPAM" — email promocional, newsletter, publicidade não solicitada, correntes
- "POSSÍVEL GOLPE" — phishing, fraude, pedido de dados pessoais, links suspeitos, urgência falsa para clicar em links ou fornecer credenciais
- "URGENTE" — requer ação imediata com prazo explícito crítico ou emergência real de negócio
- "SOLICITAÇÃO" — pedido de suporte, informação, serviço ou esclarecimento sem urgência extrema
- "RECLAMAÇÃO" — manifestação de insatisfação, problema reportado, crítica formal
- "REUNIÃO" — convite, agendamento ou confirmação de reunião, call ou evento
- "INFORMATIVO" — comunicado corporativo, atualização de status, aviso sem necessidade de resposta
- "NÃO IMPORTANTE" — agradecimento genérico, felicitação, cortesia, boas festas, mensagem de relacionamento sem ação

## Formato de resposta:
Responda APENAS com um JSON válido no seguinte formato, sem texto adicional:
{
  "category": "Produtivo" ou "Improdutivo",
  "tag": "uma das 8 tags listadas acima",
  "summary": "Resumo breve do email em uma frase",
  "suggested_response": "Resposta profissional sugerida em português"
}

ATENÇÃO: O campo "category" deve ser EXATAMENTE a string "Produtivo" ou "Improdutivo". Nunca use o nome de uma tag (ex: "INFORMATIVO", "SPAM") como valor de "category".

## Exemplos:

Email: "Prezado suporte, gostaria de saber o status do chamado #12345 aberto semana passada referente ao erro no sistema de pagamentos."
Resposta: {"category": "Produtivo", "tag": "SOLICITAÇÃO", "summary": "Solicitação de status do chamado #12345 sobre erro no sistema de pagamentos", "suggested_response": "Prezado(a), agradecemos o contato. Informamos que o chamado #12345 está sendo analisado pela equipe técnica. Retornaremos com uma atualização em breve. Caso necessite de suporte urgente, entre em contato pelo nosso canal prioritário."}

Email: "Feliz Natal a todos da equipe! Que 2026 seja repleto de conquistas e realizações!"
Resposta: {"category": "Improdutivo", "tag": "NÃO IMPORTANTE", "summary": "Mensagem de felicitações de Natal e Ano Novo", "suggested_response": "Obrigado pela mensagem! Desejamos igualmente um excelente 2026 repleto de realizações. Boas festas!"}

Email: "PARABÉNS!!! Você foi selecionado para receber R$5.000. Clique AGORA em http://bit.ly/premio para resgatar."
Resposta: {"category": "Improdutivo", "tag": "POSSÍVEL GOLPE", "summary": "Mensagem fraudulenta prometendo prêmio mediante clique em link suspeito", "suggested_response": "Este email apresenta características de golpe (phishing). Recomendamos não clicar em nenhum link e deletar a mensagem imediatamente."}

Email: "Obrigado pelo atendimento de ontem, aliás, você pode reenviar o contrato?"
Resposta: {"category": "Produtivo", "tag": "SOLICITAÇÃO", "summary": "Solicitação de reenvio de contrato com agradecimento pelo atendimento", "suggested_response": "Prezado(a), obrigado pelo retorno! Segue o contrato em anexo conforme solicitado. Qualquer dúvida, estou à disposição."}"""


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

            # Extract JSON object from response, tolerating surrounding text or markdown fences
            cleaned = response_text.strip()
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                raise json.JSONDecodeError("No JSON object found", cleaned, 0)
            cleaned = match.group(0)
            logger.debug("Extracted JSON: %s", cleaned[:200])

            data = json.loads(cleaned)
            logger.info("JSON parsed successfully | category=%s", data.get("category"))

            valid_categories = {"Produtivo", "Improdutivo"}
            if data.get("category") not in valid_categories:
                logger.error("Invalid category returned by Claude: %s", data.get("category"))
                raise ClassificationError(
                    f"AI returned an invalid category: '{data.get('category')}'. Expected 'Produtivo' or 'Improdutivo'."
                )

            return ClassificationResult(
                category=data["category"],
                tag=data["tag"],
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
