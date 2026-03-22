# Email Classifier

Aplicação web para classificação inteligente de emails do setor financeiro. Classifica emails como **Produtivo** ou **Improdutivo**, atribui uma tag, gera um resumo e sugere resposta automática.

## Stack

- **Backend:** Python 3.13 + FastAPI
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS v4
- **IA:** Claude API (Anthropic) — modelo `claude-sonnet-4-20250514`
- **NLP:** HuggingFace Inference API — modelo `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (zero-shot, multilíngue) e classificador clássico baseado em regex (sem dependência de API)
- **PDF:** PyMuPDF (fitz)
- **Deploy:** Vercel (frontend) + Railway (backend)
- **Docker:** docker-compose com Nginx reverse proxy

## Funcionalidades

- Classificação via texto colado ou upload de arquivo `.txt` / `.pdf`
- Três providers de classificação: **Claude (IA)**, **HuggingFace (zero-shot)** e **Clássico (NLP)** — alternável pela interface
- 8 tags de categorização: `SPAM`, `POSSÍVEL GOLPE`, `URGENTE`, `SOLICITAÇÃO`, `RECLAMAÇÃO`, `REUNIÃO`, `INFORMATIVO`, `NÃO IMPORTANTE`
- Histórico de classificações com busca e filtros
- Estatísticas de uso (cards + barra de resumo)
- Exportação de resultados
- Dark mode

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
│   │   │   ├── text_preprocessor.py       # Limpeza de texto
│   │   │   ├── confidence_scorer.py       # Score de confiança
│   │   │   └── classifier/
│   │   │       ├── claude_classifier.py       # Provider IA (Claude)
│   │   │       ├── huggingface_classifier.py  # Provider HuggingFace (zero-shot)
│   │   │       ├── classic_nlp_classifier.py  # Provider NLP (regex)
│   │   │       └── factory.py                 # Factory Method
│   │   ├── readers/                       # txt_reader, pdf_reader, reader_factory
│   │   └── models/schemas.py              # DTOs Pydantic
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Header, EmailUploader, ResultCard, History, StatsCards, ...
│   │   ├── hooks/         # useEmailClassifier.ts
│   │   ├── services/      # api.ts (Axios)
│   │   └── types/         # index.ts
│   └── package.json
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
