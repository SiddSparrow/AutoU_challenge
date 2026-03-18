# Email Classifier

Aplicação web para classificação inteligente de emails usando IA. Classifica emails como **Produtivo** ou **Improdutivo** e sugere respostas automáticas.

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **IA:** Claude API (Anthropic)
- **PDF:** PyMuPDF

## Pré-requisitos

- Python 3.13+
- Node.js 18+
- Chave de API da Anthropic ([console.anthropic.com](https://console.anthropic.com))

## Executando Localmente

### Backend

```bash
cd backend
cp .env.example .env
# Edite o .env com sua ANTHROPIC_API_KEY

pip install -r requirements.txt
uvicorn app.main:app --reload
```

O backend estará disponível em `http://localhost:8000`. Documentação da API em `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend estará disponível em `http://localhost:5173`.

## Uso

1. Acesse `http://localhost:5173`
2. Cole o texto de um email ou faça upload de um arquivo `.txt` / `.pdf`
3. Clique em "Classificar Email"
4. Veja a classificação (Produtivo/Improdutivo), o resumo e a resposta sugerida

## Estrutura do Projeto

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configurações
│   │   ├── api/routes/          # Endpoints da API
│   │   ├── core/                # Interfaces e exceções
│   │   ├── services/            # Lógica de negócio e IA
│   │   ├── readers/             # Leitores de arquivos (txt, pdf)
│   │   └── models/              # Schemas Pydantic
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # Chamadas à API
│   │   └── types/               # TypeScript interfaces
│   └── package.json
└── README.md
```

## Deploy

- **Frontend:** Vercel (apontar para pasta `frontend/`)
- **Backend:** Railway (apontar para pasta `backend/`, variáveis: `ANTHROPIC_API_KEY`, `ALLOWED_ORIGINS`)
