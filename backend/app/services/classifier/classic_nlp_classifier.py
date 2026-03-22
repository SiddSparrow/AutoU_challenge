import re
import logging

import nltk
import numpy as np
import scipy.sparse as sp
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

try:
    from langdetect import detect, LangDetectException
except ImportError:
    detect = None
    LangDetectException = Exception

from app.core.interfaces import ClassificationResult, Classifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language maps
# ---------------------------------------------------------------------------

# ISO 639-1 → NLTK language name
_LANG_TO_NLTK: dict[str, str] = {
    "pt": "portuguese", "en": "english",  "de": "german",
    "fr": "french",     "es": "spanish",  "it": "italian",
    "nl": "dutch",      "ru": "russian",  "ar": "arabic",
    "da": "danish",     "fi": "finnish",  "hu": "hungarian",
    "no": "norwegian",  "ro": "romanian", "sv": "swedish",
}

# ISO 639-1 → SnowballStemmer language name
_LANG_TO_SNOWBALL: dict[str, str] = _LANG_TO_NLTK.copy()

_DEFAULT_LANG_CODE = "pt"
_DEFAULT_LANG = "portuguese"

# ---------------------------------------------------------------------------
# Low-information detection
# ---------------------------------------------------------------------------

_LOW_INFO_EXACT: frozenset[str] = frozenset({
    "ok", "teste", "test", "hello", "hi", "oi", "olá", "ola",
    "bom dia", "boa tarde", "boa noite", "boas",
    "obrigado", "obrigada", "thanks", "thx", "ty",
    "yes", "no", "sim", "não", "nao",
    "texto qualquer", "qualquer texto", "exemplo", "example",
    "ping", "apenas um teste", "só um teste",
})

# Action words that rescue a short text from low-info classification
_ACTION_WORDS: frozenset[str] = frozenset({
    "preciso", "gostaria", "poderia", "solicito", "ajuda",
    "solicitar", "necessito", "quero", "peço", "pedir",
    "favor", "requer", "necessário", "urgente", "aguardo",
    "consegue", "conseguir", "resolver", "enviar", "envie",
    "atualizar", "verificar", "confirmar", "agendar",
})

_LOW_INFO_MIN_WORDS = 4
_CONFIDENCE_THRESHOLD = 0.6

# ---------------------------------------------------------------------------
# Feature engineering constants
# ---------------------------------------------------------------------------

_TOKEN_COUNT_NORM = 50.0  # normalisation factor for text_length feature

# ---------------------------------------------------------------------------
# Response templates (deterministic by tag)
# ---------------------------------------------------------------------------

RESPONSE_TEMPLATES: dict[str, str] = {
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

# ---------------------------------------------------------------------------
# Training dataset (~56 labelled examples — 6-7 per tag + negatives)
# ---------------------------------------------------------------------------

_TRAINING_DATA: list[tuple[str, str, str]] = [
    # --- SPAM ---
    ("Promoção imperdível! Ganhe 50% de desconto em todos os produtos. Oferta válida por tempo limitado. Clique aqui e compre agora!", "Improdutivo", "SPAM"),
    ("Newsletter semanal: confira as novidades do mercado financeiro e as melhores ofertas da semana para você.", "Improdutivo", "SPAM"),
    ("Você foi selecionado para receber um brinde exclusivo. Acesse agora e resgate seu presente gratuito.", "Improdutivo", "SPAM"),
    ("Desconto especial de 70% apenas hoje! Não perca esta oportunidade única de economizar muito.", "Improdutivo", "SPAM"),
    ("Corrente da sorte: encaminhe para 10 amigos e receberá boa sorte. Não quebre a corrente!", "Improdutivo", "SPAM"),
    ("Assine nossa newsletter e receba dicas exclusivas de finanças pessoais toda semana no seu email.", "Improdutivo", "SPAM"),

    # --- POSSÍVEL GOLPE ---
    ("URGENTE: sua conta bancária foi suspensa. Clique no link abaixo e atualize seus dados imediatamente para evitar bloqueio.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Parabéns! Você ganhou R$10.000. Para receber, informe seu CPF e dados bancários no formulário.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Verificação de segurança necessária. Acesse http://bit.ly/banco-seguro e confirme sua senha agora.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Seu PIX foi bloqueado por atividade suspeita. Clique aqui para desbloquear informando sua senha.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Oportunidade de investimento: retorno garantido de 300% em 30 dias. Envie seus dados para participar.", "Improdutivo", "POSSÍVEL GOLPE"),
    ("Atualização obrigatória do aplicativo do banco. Baixe agora pelo link ou sua conta será encerrada.", "Improdutivo", "POSSÍVEL GOLPE"),

    # --- URGENTE ---
    ("URGENTE: sistema de pagamentos fora do ar desde as 14h. Clientes não conseguem finalizar transações. Precisamos de resolução imediata.", "Produtivo", "URGENTE"),
    ("Atenção: prazo para entrega do relatório regulatório vence hoje às 17h. Necessito da sua assinatura com urgência.", "Produtivo", "URGENTE"),
    ("Servidor de produção caiu. Todos os serviços estão indisponíveis. Equipe de TI precisa agir imediatamente.", "Produtivo", "URGENTE"),
    ("Reunião de crise convocada para daqui a 30 minutos. Presença obrigatória da diretoria. Assunto: vazamento de dados.", "Produtivo", "URGENTE"),
    ("Prazo regulatório expira amanhã às 09h. Precisamos protocolar os documentos hoje sem falta.", "Produtivo", "URGENTE"),
    ("Cliente VIP ameaça cancelar contrato de R$2M até o fim do dia. Necessária resposta imediata da gerência.", "Produtivo", "URGENTE"),

    # --- SOLICITAÇÃO ---
    ("Gostaria de saber o status do chamado #12345 aberto semana passada referente ao erro no sistema de pagamentos.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia me enviar o relatório de conciliação bancária do mês de outubro? Preciso para auditoria.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito acesso ao módulo de relatórios do sistema financeiro para o novo analista João Silva.", "Produtivo", "SOLICITAÇÃO"),
    ("Por favor, preciso de esclarecimentos sobre a política de reembolso de despesas de viagem.", "Produtivo", "SOLICITAÇÃO"),
    ("Você pode reenviar o contrato assinado? Não encontrei o arquivo no email anterior.", "Produtivo", "SOLICITAÇÃO"),
    ("Solicito cotação para renovação do seguro empresarial com vigência a partir de janeiro.", "Produtivo", "SOLICITAÇÃO"),
    ("Poderia verificar o status da transferência realizada ontem? Ainda não foi creditada na conta.", "Produtivo", "SOLICITAÇÃO"),

    # --- RECLAMAÇÃO ---
    ("Estou muito insatisfeito com o serviço prestado. O prazo foi descumprido pela terceira vez consecutiva.", "Produtivo", "RECLAMAÇÃO"),
    ("O sistema continua apresentando erros mesmo após a manutenção prometida. Isto é inaceitável.", "Produtivo", "RECLAMAÇÃO"),
    ("Minha fatura apresentou cobranças indevidas no valor de R$500. Exijo estorno imediato e explicação.", "Produtivo", "RECLAMAÇÃO"),
    ("O atendimento da equipe de suporte foi extremamente insatisfatório. Abro reclamação formal.", "Produtivo", "RECLAMAÇÃO"),
    ("Já solicitei 3 vezes o cancelamento e o serviço continua sendo cobrado. Situação inadmissível.", "Produtivo", "RECLAMAÇÃO"),
    ("Produto entregue com defeito e a equipe de suporte se recusa a providenciar a troca. Registro reclamação.", "Produtivo", "RECLAMAÇÃO"),

    # --- REUNIÃO ---
    ("Convido para reunião de alinhamento sobre o projeto de transformação digital na próxima terça-feira às 10h.", "Produtivo", "REUNIÃO"),
    ("Confirmo presença na reunião de diretoria marcada para sexta-feira às 14h na sala de conferências.", "Produtivo", "REUNIÃO"),
    ("Podemos agendar uma call para discutir os resultados do terceiro trimestre? Sugiro quinta às 15h.", "Produtivo", "REUNIÃO"),
    ("Convocação para reunião extraordinária do conselho administrativo em 20/03 às 09h.", "Produtivo", "REUNIÃO"),
    ("Você tem disponibilidade para um café na próxima semana para discutirmos a parceria?", "Produtivo", "REUNIÃO"),
    ("Segue o convite para o webinar sobre compliance regulatório. Confirme sua participação.", "Produtivo", "REUNIÃO"),

    # --- INFORMATIVO ---
    ("Informamos que o sistema estará em manutenção programada no sábado das 02h às 06h.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado: a partir de 01/04, o horário de atendimento será das 08h às 18h de segunda a sexta.", "Improdutivo", "INFORMATIVO"),
    ("Aviso: nova política de senhas entra em vigor na próxima semana. Todos devem atualizar seus acessos.", "Improdutivo", "INFORMATIVO"),
    ("Nota informativa: o escritório estará fechado nos dias 20 e 21 de março em razão do feriado municipal.", "Improdutivo", "INFORMATIVO"),
    ("Atualização do sistema ERP prevista para o próximo final de semana. Backup realizado automaticamente.", "Improdutivo", "INFORMATIVO"),
    ("Comunicado interno: mudança de endereço da matriz a partir de 01/05. Novo endereço em anexo.", "Improdutivo", "INFORMATIVO"),

    # --- NÃO IMPORTANTE (substantive) ---
    ("Feliz Natal a todos da equipe! Que 2026 seja repleto de conquistas e realizações para todos.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Obrigado pelo excelente atendimento de ontem! Fico muito satisfeito com a qualidade do serviço.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Bom fim de semana a todos! Aproveitem o descanso merecido após uma semana produtiva.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Parabéns pela promoção! Você merece muito este reconhecimento pelo seu trabalho dedicado.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Agradecemos a parceria ao longo desses anos. Esperamos continuar crescendo juntos.", "Improdutivo", "NÃO IMPORTANTE"),
    ("Boa semana para todos! Que seja cheia de produtividade e boas notícias para a equipe.", "Improdutivo", "NÃO IMPORTANTE"),

    # --- NÃO IMPORTANTE (negative/low-info examples) ---
    ("ok tudo certo pode fechar", "Improdutivo", "NÃO IMPORTANTE"),
    ("teste de envio do sistema de emails corporativos", "Improdutivo", "NÃO IMPORTANTE"),
    ("olá tudo bem com você hoje", "Improdutivo", "NÃO IMPORTANTE"),
    ("bom dia para toda a equipe presente", "Improdutivo", "NÃO IMPORTANTE"),
    ("obrigado pela sua atenção e apoio", "Improdutivo", "NÃO IMPORTANTE"),
    ("texto qualquer sem nenhum sentido específico aqui", "Improdutivo", "NÃO IMPORTANTE"),
    ("hello how are you doing today friend", "Improdutivo", "NÃO IMPORTANTE"),
    ("apenas verificando se o email está funcionando corretamente", "Improdutivo", "NÃO IMPORTANTE"),
]


# ---------------------------------------------------------------------------
# Standalone heuristic (importable / testable independently)
# ---------------------------------------------------------------------------

def is_low_information(text: str) -> bool:
    """Return True when the text carries no classifiable intent.

    Rules (applied in order):
    1. Empty / whitespace-only.
    2. Exact match against known low-info phrases.
    3. Fewer than _LOW_INFO_MIN_WORDS tokens AND no action words detected.
    """
    stripped = text.strip().lower()
    if not stripped:
        return True

    if stripped in _LOW_INFO_EXACT:
        return True

    tokens = re.findall(r"\b\w+\b", stripped)
    if len(tokens) < _LOW_INFO_MIN_WORDS:
        if any(t in _ACTION_WORDS for t in tokens):
            return False  # short but has clear intent — not low-info
        return True

    return False


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class ClassicNLPClassifier(Classifier):
    """Email classifier using a classic NLP pipeline (Strategy Pattern).

    Pipeline:
      0. Low-information heuristic (fast path — no ML needed)
      1. Language detection (langdetect)
      2. Stopword removal + SnowballStemmer (NLTK)
      3. TF-IDF (1-2 ngrams) + engineered features → combined sparse matrix
      4. Logistic Regression for category + tag (scikit-learn, predict_proba)
      5. Confidence threshold: if max(proba) < 0.6 → force Improdutivo/NÃO IMPORTANTE
      6. Extractive summarisation via TF-IDF sentence scoring
      7. Deterministic template-based response generation
    """

    def __init__(self) -> None:
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt_tab", quiet=True)

        texts, categories, tags = zip(*_TRAINING_DATA)

        processed = [self._nlp_preprocess(t) for t in texts]

        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
        X_tfidf = self._vectorizer.fit_transform(processed)
        X_extra = sp.csr_matrix(self._extra_features(list(texts)))
        X = sp.hstack([X_tfidf, X_extra])

        self._cat_clf = LogisticRegression(max_iter=1000, random_state=42)
        self._cat_clf.fit(X, categories)

        self._tag_clf = LogisticRegression(max_iter=1000, random_state=42)
        self._tag_clf.fit(X, tags)

        logger.info(
            "ClassicNLPClassifier ready | training_samples=%d | vocab_size=%d",
            len(texts),
            len(self._vectorizer.vocabulary_),
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def classify(self, text: str) -> ClassificationResult:
        logger.info("ClassicNLPClassifier.classify() | text_length=%d", len(text))

        # --- Step 0: low-information fast path ---
        if is_low_information(text):
            logger.info("Low-information input detected — returning NÃO IMPORTANTE")
            return ClassificationResult(
                category="Improdutivo",
                tag="NÃO IMPORTANTE",
                summary=text.strip()[:150] or "Mensagem sem conteúdo relevante.",
                suggested_response=RESPONSE_TEMPLATES["NÃO IMPORTANTE"],
            )

        # --- Steps 1-3: preprocess + build feature matrix ---
        processed = self._nlp_preprocess(text)
        X_tfidf = self._vectorizer.transform([processed])
        X_extra = sp.csr_matrix(self._extra_features([text]))
        X = sp.hstack([X_tfidf, X_extra])

        # --- Step 4: predict with probabilities ---
        cat_proba = self._cat_clf.predict_proba(X)[0]
        tag_proba = self._tag_clf.predict_proba(X)[0]

        cat_confidence = float(cat_proba.max())
        tag_confidence = float(tag_proba.max())
        min_confidence = min(cat_confidence, tag_confidence)

        # --- Step 5: confidence threshold fallback ---
        if min_confidence < _CONFIDENCE_THRESHOLD:
            logger.info(
                "Low confidence (cat=%.2f, tag=%.2f) — forcing Improdutivo/NÃO IMPORTANTE",
                cat_confidence, tag_confidence,
            )
            category = "Improdutivo"
            tag = "NÃO IMPORTANTE"
        else:
            category = str(self._cat_clf.classes_[cat_proba.argmax()])
            tag = str(self._tag_clf.classes_[tag_proba.argmax()])

        summary = self._summarize(text)
        suggested_response = RESPONSE_TEMPLATES.get(tag, RESPONSE_TEMPLATES["INFORMATIVO"])

        logger.info(
            "Classic result: category=%s, tag=%s, confidence=%.2f",
            category, tag, min_confidence,
        )
        return ClassificationResult(
            category=category,
            tag=tag,
            summary=summary,
            suggested_response=suggested_response,
        )

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------

    def _extra_features(self, texts: list[str]) -> np.ndarray:
        """Compute lightweight handcrafted features alongside TF-IDF.

        Features (per text):
          - text_length:       normalised token count (capped at 1.0)
          - has_question_mark: 1 if '?' present, else 0
          - has_action_words:  1 if any action word found, else 0
        """
        rows: list[list[float]] = []
        for t in texts:
            tokens = re.findall(r"\b\w+\b", t.lower())
            rows.append([
                min(len(tokens) / _TOKEN_COUNT_NORM, 1.0),
                float("?" in t),
                float(any(tok in _ACTION_WORDS for tok in tokens)),
            ])
        return np.array(rows, dtype=float)

    # ------------------------------------------------------------------
    # NLP preprocessing
    # ------------------------------------------------------------------

    def _detect_lang_code(self, text: str) -> str:
        """Return ISO 639-1 language code; default 'pt'."""
        if detect is None:
            return _DEFAULT_LANG_CODE
        try:
            return detect(text)
        except LangDetectException:
            return _DEFAULT_LANG_CODE

    def _nlp_preprocess(self, text: str) -> str:
        """Lowercase → remove punctuation → remove stopwords → stem."""
        lang_code = self._detect_lang_code(text)
        nltk_lang = _LANG_TO_NLTK.get(lang_code, _DEFAULT_LANG)
        snowball_lang = _LANG_TO_SNOWBALL.get(lang_code, _DEFAULT_LANG)

        try:
            sw = set(stopwords.words(nltk_lang))
        except OSError:
            sw = set(stopwords.words(_DEFAULT_LANG))

        try:
            stemmer = SnowballStemmer(snowball_lang)
        except Exception:
            stemmer = SnowballStemmer(_DEFAULT_LANG)

        tokens = re.findall(r"\b\w+\b", text.lower())
        stemmed = [stemmer.stem(t) for t in tokens if t not in sw and len(t) > 1]
        return " ".join(stemmed)

    # ------------------------------------------------------------------
    # Extractive summarisation
    # ------------------------------------------------------------------

    def _summarize(self, text: str) -> str:
        """Pick the sentence with highest mean TF-IDF score."""
        sentences = [s.strip() for s in sent_tokenize(text) if len(s.strip()) > 10]
        if not sentences:
            return text.strip()[:150]
        if len(sentences) == 1:
            return sentences[0][:200]

        X = self._vectorizer.transform(sentences)
        scores = X.toarray().mean(axis=1)
        return sentences[int(scores.argmax())][:250]
