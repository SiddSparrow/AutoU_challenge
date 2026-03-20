import re
from dataclasses import dataclass, field

# --- Spam signals ---

SPAM_KEYWORDS = [
    "promoção", "ganhe agora", "clique aqui", "acesse agora",
    "oferta especial", "você foi selecionado", "você ganhou",
    "100% gratuito", "free prize", "winner", "congratulations",
    "desconto exclusivo", "válido por tempo limitado", "não perca",
    "compre agora", "último dia", "grátis",
]

SPAM_PATTERNS = [
    re.compile(r"!{3,}"),                           # 3+ exclamation marks
    re.compile(r"\${2,}"),                          # 2+ dollar signs
    re.compile(r"[A-Z]{6,}"),                       # 6+ consecutive uppercase letters
    re.compile(r"(urgente|URGENTE).{0,30}(clique|acesse|baixe|download)", re.IGNORECASE),
]

# --- Suspicious URL signals ---

_SUSPICIOUS_URL = [
    re.compile(r"https?://(bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|rb\.gy)/"),
    re.compile(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),  # raw IP
    re.compile(r"\.(exe|bat|cmd|vbs|ps1|msi|dmg|apk)\b", re.IGNORECASE),
]

_URL = re.compile(r"https?://\S+")

# --- Mixed-signal markers ---

_PRODUCTIVE = [
    "preciso", "poderia", "você pode", "gostaria de", "solicito",
    "por favor", "prazo", "até quando", "status do chamado",
    "problema", "erro no sistema", "reunião", "contrato", "aguardo",
    "retorno", "solicitação", "dúvida",
]

_NON_PRODUCTIVE = [
    "feliz natal", "feliz ano novo", "boas festas", "boa semana",
    "bom fim de semana", "agradecemos sua parceria", "muito obrigado",
    "obrigada pela atenção", "parabéns pela conquista", "mensagem automática",
]


@dataclass
class ConfidenceScore:
    value: float
    flags: list[str] = field(default_factory=list)


def score(text: str) -> ConfidenceScore:
    """Compute a meaningful confidence score from deterministic text signals.

    Starts at 1.0 and applies penalties for each suspicious/ambiguous signal
    found in the email. Returns both the final score and human-readable flags.
    """
    lower = text.lower()
    penalties: list[tuple[float, str]] = []

    # 1. Spam keywords
    spam_hits = sum(1 for kw in SPAM_KEYWORDS if kw in lower)
    if spam_hits >= 2:
        penalties.append((0.30, "Múltiplos indicadores de spam detectados"))
    elif spam_hits == 1:
        penalties.append((0.15, "Indicador de spam detectado"))

    # 2. Spam patterns (caps, symbols, fake urgency)
    for pattern in SPAM_PATTERNS:
        if pattern.search(text):
            penalties.append((0.15, "Padrão suspeito no texto (maiúsculas, símbolos ou urgência falsa)"))
            break

    # 3. URL analysis
    urls = _URL.findall(text)
    suspicious = [u for u in urls if any(p.search(u) for p in _SUSPICIOUS_URL)]
    if suspicious:
        penalties.append((0.25, "Contém links suspeitos (encurtadores, IPs ou arquivos executáveis)"))
    elif urls:
        penalties.append((0.10, "Contém links externos"))

    # 4. Excessive uppercase ratio
    letters = [c for c in text if c.isalpha()]
    if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.40:
        penalties.append((0.15, "Uso excessivo de letras maiúsculas"))

    # 5. Very short text
    if len(text.strip()) < 50:
        penalties.append((0.15, "Texto muito curto para análise confiável"))

    # 6. Mixed signals: contains both action requests and courtesy-only phrases
    has_productive = any(m in lower for m in _PRODUCTIVE)
    has_non_productive = any(m in lower for m in _NON_PRODUCTIVE)
    if has_productive and has_non_productive:
        penalties.append((0.20, "Mensagem com sinais mistos (solicitação e cortesia simultâneas)"))

    total_penalty = min(sum(p for p, _ in penalties), 0.85)
    flags = [msg for _, msg in penalties]
    confidence = round(1.0 - total_penalty, 2)

    return ConfidenceScore(value=confidence, flags=flags)
