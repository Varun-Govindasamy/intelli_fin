# IntelliFinance — AI-Powered Financial Insights & Decision Support

A full-stack AI financial assistant that combines RAG-based document analysis, multi-agent trade analysis, real-time news, financial planning flowcharts, and a general finance chat interface — all protected by **NVIDIA NeMo Guardrails**.

---

## Features

### 1. General Financial Chat
- Conversational AI powered exclusively by **OpenAI GPT-4o-mini**
- Full NeMo Guardrails pipeline: input rails → LLM → output rails
- Plain-text formatted responses — no markdown bleed-through

### 2. Trade Decision Assistant
- Multi-agent workflow via **CrewAI**: Research Agent → Analysis Agent → Decision Agent
- Live stock data, sentiment scoring, and position-sizing recommendations
- Historical decision memory persisted to `data/trade_decisions.json`
- All inputs and outputs validated through NeMo Guardrails

### 3. RAG-Based Document Analysis
- Upload and query multiple PDF financial reports
- Retrieval pipeline: **FAISS** vector search → **CrossEncoder** re-ranking → **GPT-4o-mini** generation
- Persistent vector store across sessions
- Confidence scoring rescaled from raw re-ranker logits (human-readable 0–100%)
- NeMo Guardrails applied on both input query and generated response

### 4. Financial Planning Flowcharts
- AI-generated financial planning workflows
- Interactive visualization using **React Flow**
- Customisable goals, time horizons, and risk tolerance

### 5. Financial News Feed
- Real-time financial news via **Serper API**
- Company-specific news watchlists
- General market news aggregation

---

## Safety — NVIDIA NeMo Guardrails

All AI services are protected by **NeMo Guardrails** (`nemoguardrails >= 0.10.0`) with 11 rails implemented via Colang flows, LLM-based prompts, and custom Python actions.

### Input Guardrails (before the LLM sees the query)

| # | Rail | Method |
|---|------|--------|
| 1 | **Topic / Domain Control** — blocks non-finance queries (medical, coding, politics) | LLM prompt (`self_check_input`) |
| 2 | **Jailbreak & Prompt Injection Detection** — blocks instruction-override attempts | LLM prompt (`self_check_input`) |
| 3 | **PII Detection & Masking** — detects and masks Aadhaar, PAN, SSN, credit cards, IBANs, email | Python action (`check_pii_input`) |
| 4 | **Regulatory Compliance Filter** — blocks requests for specific personalised investment advice | LLM prompt (`self_check_input`) |
| 5 | **Sensitive Query Flagging** — blocks queries about insider trading, tax evasion, fraud, money laundering | LLM prompt (`self_check_input`) |

### Output Guardrails (before the response reaches the user)

| # | Rail | Method |
|---|------|--------|
| 1 | **Hallucination / Grounding Check** — verifies figures in response appear in retrieved RAG context | Python action (`process_output_quality`) |
| 2 | **Disclaimer Injection** — auto-appends SEBI / financial advisor disclaimer on investment-related responses | Python action (`process_output_quality`) |
| 3 | **PII Leakage Detection** — masks PII that may have leaked into the generated response | Python action (`process_output_quality`) |
| 4 | **Numerical Sanity Checks** — flags returns > 500% or suspiciously low/high prices | Python action (`process_output_quality`) |
| 5 | **Sentiment & Toxicity Filter** — blocks manipulative pump-and-dump language, guaranteed-return claims | LLM prompt (`self_check_output`) |
| 6 | **Source Citation Enforcement** (RAG only) — appends source attribution if not already present | Python action (`process_output_quality`) |

---

## Technology Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Uvicorn |
| LLM | OpenAI GPT-4o-mini (all services) |
| Guardrails | NVIDIA NeMo Guardrails 0.21+ |
| AI Orchestration | CrewAI |
| Vector Store | FAISS (persistent on disk) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local) |
| Re-ranker | CrossEncoder `ms-marco-MiniLM-L-6-v2` (local) |
| Document Processing | LangChain + LangChain Text Splitters |
| News & Research | Serper API |
| PDF Parsing | PyPDF |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | React.js |
| Styling | Tailwind CSS |
| Visualization | React Flow |
| HTTP Client | Axios |
| File Upload | React Dropzone |
| Notifications | React Hot Toast |
| Icons | Heroicons |

---

## Installation & Setup

### Prerequisites
- Python 3.10 – 3.12
- Node.js 16+
- An **OpenAI API key** (the only external LLM dependency)

> Ollama, Gemini, and Groq are **not required**.

---

### Backend Setup

```bash
# 1. Enter the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-...          # Required — used for all LLM calls
SERPER_API_KEY=...             # Required — for news & trade research
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
```

```bash
# 5. Start the backend
python main.py
```

---

### Frontend Setup

```bash
# 1. Enter the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API / Docs**: http://localhost:8000/docs

---

## API Keys

| Key | Purpose | Required |
|-----|---------|----------|
| `OPENAI_API_KEY` | All LLM inference (chat, RAG, guardrails, trade summaries) | Yes |
| `SERPER_API_KEY` | News aggregation and trade research | Yes |

---

## Project Structure

```
finance-bot/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── chat_service.py          # General chat (NeMo full pipeline)
│   │   │   ├── rag_service.py           # RAG: FAISS + CrossEncoder + GPT-4o-mini
│   │   │   ├── guardrails_service.py    # NeMo Guardrails wrapper (11 rails)
│   │   │   ├── trade_agent_service.py   # CrewAI multi-agent trade analysis
│   │   │   ├── flowchart_service.py     # Financial planning flowcharts
│   │   │   └── news_service.py          # Serper-based news aggregation
│   │   └── utils/
│   │       ├── response_cleaner.py      # Strips markdown from LLM output
│   │       └── file_manager.py          # PDF upload management
│   ├── nemo_config/                     # NVIDIA NeMo Guardrails config
│   │   ├── config.yml                   # Model config + rail activation
│   │   ├── rails.co                     # Colang flow definitions
│   │   ├── prompts.yml                  # Finance-specific LLM check prompts
│   │   └── actions.py                   # Custom Python guardrail actions
│   ├── data/
│   │   ├── uploads/                     # Uploaded PDF files
│   │   ├── vector_store/                # Persistent FAISS index
│   │   └── trade_decisions.json         # Agent decision memory
│   ├── requirements.txt
│   └── main.py                          # FastAPI app entry point
│
└── frontend/
    └── src/
        ├── components/
        │   ├── MainChat.js              # General chat interface
        │   ├── RAGChat.js               # Document analysis interface
        │   ├── TradeDecisionChat.js     # Trade analysis interface
        │   ├── FlowchartGenerator.js    # Planning flowchart UI
        │   ├── NewsPanel.js             # News feed
        │   └── Sidebar.js              # Navigation
        ├── services/
        │   └── api.js                  # Axios API layer
        └── App.js
```

---

## Guardrails API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/guardrails/status` | GET | Current guardrails configuration |
| `/api/guardrails/validate-input` | POST | Manually test input guardrails |
| `/api/guardrails/validate-output` | POST | Manually test output guardrails |
| `/api/guardrails/configure` | POST | Enable/disable guardrails or strict mode |

---

## Security & Privacy

- API keys stored exclusively in `.env` (never committed — `.gitignore` enforced)
- PII masked before reaching any LLM or being logged
- CORS restricted to `http://localhost:3000` in development
- All file uploads validated for PDF format and size limits
- GitHub Push Protection enforced — secrets blocked from commits

---

## Deployment

### Backend
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend
```bash
npm run build
# Serve the build/ folder via Nginx, Vercel, or similar
```

---

## Acknowledgements

- [OpenAI](https://openai.com) — GPT-4o-mini for all LLM inference
- [NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) — Safety and compliance rails
- [CrewAI](https://crewai.com) — Multi-agent trade analysis orchestration
- [LangChain](https://langchain.com) — Document processing and text splitting
- [Hugging Face](https://huggingface.co) — Local embeddings and cross-encoder re-ranking
- [React Flow](https://reactflow.dev) — Interactive flowchart visualization
- [Serper](https://serper.dev) — Financial news and research API
