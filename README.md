# Email Classifier

Aplicação web para classificação inteligente de emails. Classifica emails como **Produtivo** ou **Improdutivo**, atribui uma tag, gera um resumo e sugere resposta automática.

## Stack

- **Backend:** Python 3.13 + FastAPI
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS v4
- **IA:** Claude API (Anthropic) — modelo `claude-sonnet-4-20250514`
- **NLP clássico:** TF-IDF + Logistic Regression (scikit-learn) + SnowballStemmer (NLTK) — sem dependência de API
- **Zero-shot:** HuggingFace Inference API — modelo `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (multilíngue)
- **PDF:** PyMuPDF (fitz)
- **Deploy:** Vercel (frontend) + Railway (backend)
- **Docker:** docker-compose com Nginx reverse proxy

## Funcionalidades

- Classificação via texto colado ou upload de arquivo `.txt` / `.pdf`
- Três providers de classificação alternáveis pela interface: **Claude**, **HuggingFace** e **ClassicNLP**
- 8 tags de categorização: `SPAM`, `POSSÍVEL GOLPE`, `URGENTE`, `SOLICITAÇÃO`, `RECLAMAÇÃO`, `REUNIÃO`, `INFORMATIVO`, `NÃO IMPORTANTE`
- Histórico de classificações com busca e filtros
- Estatísticas de uso (cards + barra de resumo)
- Exportação de resultados
- Dark mode

## Classificadores

### Pré-processamento comum (`TextPreprocessor`)

Aplicado a todos os providers antes da classificação:

| Etapa | O que remove |
|-------|-------------|
| Remoção de headers | `De:`, `Para:`, `Assunto:`, `From:`, `To:`, `Subject:`, etc. |
| Remoção de HTML | Tags `<...>` |
| Remoção de URLs | Links `http://` e `www.` |
| Remoção de assinatura | A partir de `Atenciosamente`, `Abraço`, `Regards`, `--`, etc. |
| Normalização de espaços | Linhas em branco excessivas e espaços duplicados |

### ClassicNLP — TF-IDF + Logistic Regression

Pipeline local, sem chamadas de API:

1. Detecção de idioma via stopwords (PT/EN) — ~0.1ms, sem dependência externa
2. Lowercasing → tokenização → remoção de stopwords (NLTK) → stemming (SnowballStemmer)
3. TF-IDF com unigramas e bigramas (1.500 features)
4. Features manuais: comprimento normalizado, presença de `?`, action words
5. Logistic Regression com thresholds separados (categoria ≥ 0.55 / tag ≥ 0.30)
6. Category derivada deterministicamente da tag quando confiante
7. Sumarização extrativa por score médio TF-IDF
8. **Cache do modelo em disco** — init de 3.7s na primeira execução, 14ms nas seguintes

Dataset de treino: 178 exemplos rotulados (~22/classe), PT + EN.

### HuggingFace — mDeBERTa-v3 zero-shot

Classificação via NLI (Natural Language Inference) sem fine-tuning:

- Labels descritivos enviados ao modelo em vez de tags curtas — evita falsos positivos por palavras isoladas (ex: "URGENTE" em spam)
- `hypothesis_template`: `"O propósito principal deste email corporativo é {}."`
- Threshold de confiança: 0.4 → fallback para `NÃO IMPORTANTE`

### Claude — claude-sonnet-4-20250514

- System prompt com definições, 5 exemplos few-shot e formato JSON obrigatório
- Validação de consistência tag↔categoria no post-processing com recovery automático
- Gera resumo e resposta sugerida contextualizados ao conteúdo real do email

## Benchmark (v3 — 12 casos de teste)

| Modelo | Acurácia (category) | Latência média |
|--------|:-------------------:|:--------------:|
| ClassicNLP | **100%** (12/12) | ~14ms |
| HuggingFace | **67%** (8/12) | ~1.6s |
| Claude | **100%** (12/12) | ~3.2s |

Resultados completos e histórico de versões em [`BENCHMARK.md`](BENCHMARK.md) e [`benchmarks/`](benchmarks/).

Para rodar um novo benchmark:

```bash
cd backend
python benchmark.py --note "descrição das mudanças"
```

## Pré-requisitos

- Python 3.13+
- Node.js 18+
- Chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com))
- Token da HuggingFace ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)) — necessário para o provider HuggingFace

## Executando Localmente

### Backend

```bash
cd backend
cp .env.example .env
# Edite o .env com sua ANTHROPIC_API_KEY e HF_TOKEN

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Disponível em `http://localhost:8000`. Documentação interativa em `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
cp .env.example .env
# VITE_API_URL=http://localhost:8000 (já configurado no .env.example)

npm install
npm run dev
```

Disponível em `http://localhost:5173`.

### Docker (alternativa)

```bash
docker compose up --build
```

## Variáveis de Ambiente

### Backend (`backend/.env`)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `ANTHROPIC_API_KEY` | Chave da API Anthropic | — |
| `ALLOWED_ORIGINS` | URLs permitidas no CORS | `http://localhost:5173,http://localhost:3000` |
| `AI_MODEL` | Modelo Claude a usar | `claude-sonnet-4-20250514` |
| `HF_TOKEN` | Token da HuggingFace (Inference API) | — |
| `HF_MODEL` | Modelo HuggingFace para zero-shot | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` |
| `API_KEY` | Chave secreta para autenticar o frontend | — (desativado se vazio) |

### Frontend (`frontend/.env`)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `VITE_API_URL` | URL base do backend | `""` (vazio = relativo) |
| `VITE_API_KEY` | Chave secreta enviada no header `X-API-Key` | — |

> **Importante:** `VITE_API_URL` é embutida no bundle em build time. Em produção, configure a variável no painel da Vercel **antes** do deploy.

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/classify/text` | Classifica email via texto (`{ text, provider }`) |
| `POST` | `/api/classify/file?provider=` | Classifica email via upload de arquivo |
| `GET` | `/api/health` | Health check |

**Providers disponíveis:** `claude` (padrão) \| `huggingface` \| `classic`

## Testes

```bash
cd backend
python -m pytest tests/ -v
```

18 testes cobrindo endpoints e lógica de classificação (pytest + httpx).

## Estrutura do Projeto

```
├── backend/
│   ├── app/
│   │   ├── main.py                        # FastAPI app + CORS
│   │   ├── config.py                      # pydantic-settings
│   │   ├── api/routes/email_routes.py     # Endpoints REST
│   │   ├── core/                          # interfaces.py, exceptions.py
│   │   ├── services/
│   │   │   ├── email_processor.py         # Facade: leitura → NLP → classificação → resposta
│   │   │   ├── text_preprocessor.py       # Limpeza de texto (headers, HTML, URLs, assinatura)
│   │   │   └── classifier/
│   │   │       ├── claude_classifier.py       # Provider IA (Claude)
│   │   │       ├── huggingface_classifier.py  # Provider HuggingFace (zero-shot NLI)
│   │   │       ├── classic_nlp_classifier.py  # Provider NLP (TF-IDF + LR)
│   │   │       └── factory.py                 # Factory Method
│   │   ├── readers/                       # txt_reader, pdf_reader, reader_factory
│   │   └── models/schemas.py              # DTOs Pydantic
│   ├── tests/
│   ├── benchmark.py                       # Script de benchmark versionado
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Header, EmailUploader, ResultCard, History, StatsCards, ...
│   │   ├── hooks/         # useEmailClassifier.ts
│   │   ├── services/      # api.ts (Axios)
│   │   └── types/         # index.ts
│   └── package.json
├── benchmarks/            # Histórico de benchmarks versionados (v1, v2, v3...)
├── BENCHMARK.md           # Benchmark mais recente
├── docker-compose.yml
└── README.md
```

## Deploy

### Vercel (Frontend)

1. Aponte o projeto para a pasta `frontend/`
2. Configure a variável de ambiente: `VITE_API_URL=https://<seu-backend>.up.railway.app`
3. Faça o deploy — o Vite embutte a URL no bundle

### Railway (Backend)

Configure as variáveis de ambiente no painel:

| Variável | Valor |
|----------|-------|
| `ANTHROPIC_API_KEY` | Sua chave da Anthropic |
| `ALLOWED_ORIGINS` | URL do frontend na Vercel (ex: `https://seu-app.vercel.app`) |
| `HF_TOKEN` | Seu token da HuggingFace |
| `HF_MODEL` | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` |
| `API_KEY` | Chave secreta compartilhada com o frontend |
