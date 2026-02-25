# 📊 AI Financial Copilot

[![CI](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-grade Retrieval-Augmented Generation (RAG) microservice for intelligent financial document analysis.**

Upload PDFs → Ask questions → Get AI-powered insights powered by Groq LLMs, Huggingface embeddings, and PostgreSQL pgvector search.

**🚀 [Try Live Demo](https://ai-financial-copilot-bdtd.vercel.app/)** | **📡 [API Docs](https://ai-financial-copilot-2.onrender.com/docs)** | **📖 [Enterprise Guide](./ENTERPRISE.md)**

## ✨ Key Features

| Feature | Details |
|---------|---------|
| **Intelligent RAG** | Semantic search + LLM generation with 3-model fallback |
| **PDF Processing** | Automatic extraction, chunking, and vector indexing |
| **Fast API** | FastAPI REST endpoints with CORS + error handling |
| **Modern UI** | React 18 + Tailwind CSS with dark mode & animations |
| **Production Ready** | Docker, tests, CI/CD, and monitoring included |
| **Secure** | API key auth + rate limiting + retry logic |

## 🛠️ Tech Stack

**Frontend**: React 18 + TypeScript + Vite + Tailwind CSS  
**Backend**: FastAPI + Python 3.11 + Uvicorn  
**AI/ML**: Groq API (LLMs) + Huggingface (embeddings)  
**Database**: PostgreSQL + pgvector (persistent vector storage)  
**Deployment**: Docker Compose + Render (backend) + Vercel (frontend)

## 🔄 CI/CD & Quality

- 20+ unit tests (backend + frontend)
- GitHub Actions pipeline (test, lint, Docker build)
- Code coverage reporting
- Dockerized backend service
- Automated build validation on every push

## 📋 Prerequisites

- **Python 3.11+** (for local backend)
- **Node.js 18+** (for local frontend)
- **Huggingface API Token** ([get here](https://huggingface.co/settings/tokens))
- **Groq API Key** ([get here](https://console.groq.com/keys))

## 🚀 Quick Start

### Try Online (Easiest)
Visit https://ai-financial-copilot-bdtd.vercel.app/, upload a PDF, and start asking questions.

### Run Locally (5 minutes)

```bash
# Clone repo
git clone https://github.com/robre8/ai-financial-copilot.git
cd ai-financial-copilot

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Create backend/.env
cat > backend/.env << EOF
HF_TOKEN=your_token_here
GROQ_API_KEY=your_key_here
FRONTEND_ORIGINS=http://localhost:5173
API_KEYS=demo-key-12345:admin:DemoKey
EOF

# Run backend (in one terminal)
cd backend && uvicorn app.main:app --reload

# Frontend setup (in new terminal)
cd ai-copilot-frontend
npm install
cat > .env.local << EOF
VITE_API_BASE=http://localhost:8000
EOF

# Run frontend
npm run dev
```

Open http://localhost:5173 and start uploading PDFs!

### Run with Docker Compose (Recommended)

```bash
# Start PostgreSQL + Backend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

**Includes**:
- PostgreSQL 15 with pgvector extension
- Persistent volume for data
- Auto-created database and tables
- Hot-reload for development

See [POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md) for production setup with Render.

## 📡 API Endpoints

```bash
GET  /                    # Health check
POST /upload-pdf          # Upload & index PDF
POST /ask                 # Query the knowledge base
POST /debug/llm-raw       # Test LLM endpoint (dev only)
```

**Full API docs**: http://localhost:8000/docs (when running locally)

## 🔐 Security

All endpoints (except `/`) are protected with **API key authentication** and **rate limiting**.

### API Key Authentication

Include your API key in the `X-API-Key` header:

```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -H "X-API-Key: demo-key-12345" \
  -F "file=@document.pdf"
```

### API Key Scopes

| Scope | Permissions | Use Case |
|-------|-------------|----------|
| `read` | Query documents (`/ask`) | Read-only access |
| `write` | Upload + query (`/upload-pdf`, `/ask`) | Content contributors |
| `admin` | All endpoints + debug | Full system access |

### Rate Limiting

- **Default limit**: 10 requests/minute per API key
- **Debug endpoint**: 5 requests/minute
- Exceeding limits returns `429 Too Many Requests`

### Configuration

Set API keys in `backend/.env`:

```bash
# Format: key:scope:name (comma-separated)
API_KEYS=demo-key-12345:admin:DemoKey,prod-key-xyz:read:ReadOnlyKey
```

### Retry & Timeout Strategy

LLM requests automatically retry on failures:
- **Max retries**: 3 attempts
- **Backoff**: Exponential (1s → 2s → 4s)
- **Timeout**: 30 seconds (configurable via `LLM_TIMEOUT`)

For enterprise JWT/OAuth2 integration, see [ENTERPRISE.md](./ENTERPRISE.md).

## 📁 Project Structure

```
ai-financial-copilot/
├── backend/                          # FastAPI server
│   ├── app/
│   │   ├── api/routes.py             # REST endpoints
│   │   ├── services/
│   │   │   ├── vector_service.py     # PostgreSQL + pgvector
│   │   │   ├── llm_service.py        # Groq LLM with retry logic
│   │   │   ├── embedding_service.py  # Huggingface embeddings
│   │   │   ├── rag_service.py        # RAG orchestration
│   │   │   └── agent_service.py      # Future: AI agents
│   │   ├── core/
│   │   │   ├── config.py             # Settings
│   │   │   ├── security.py           # API key auth
│   │   │   └── rate_limit.py         # Rate limiting
│   │   ├── models.py                 # SQLAlchemy models
│   │   ├── database.py               # DB connection
│   │   └── utils/text_splitter.py    # Chunking
│   ├── requirements.txt
│   └── Dockerfile
├── ai-copilot-frontend/              # React app
│   ├── src/components/ChatInterface.tsx
│   └── vite.config.ts
├── tests/
│   ├── test_api.py                   # Unit tests
│   └── test_integration.py           # Integration tests
├── docker-compose.yml                # PostgreSQL + Backend
├── init-db.sql                       # Database initialization
├── POSTGRESQL_SETUP.md               # Database setup guide
└── ENTERPRISE.md                     # Enterprise guide
```

## 🏗️ How It Works

```
User uploads PDF
    ↓
Text extraction + Chunking (512 tokens)
    ↓
Huggingface: Generate 384-dim embeddings per chunk
    ↓
PostgreSQL + pgvector: Store vectors persistently
    ↓
User asks question
    ↓
Cosine similarity search: Retrieve top-3 similar chunks
    ↓
Groq LLM: Generate answer from context (with retry logic)
    ↓
Return answer + model info + source chunks
```

## 🧠 Design Decisions

- **PostgreSQL + pgvector** over FAISS: Persistent storage, production-ready, survives restarts
- **Groq** over OpenAI: 10x faster inference, generous free tier
- **Custom RAG** over LangChain: Lower memory footprint, full control
- **Clean Architecture**: Separated services (vector, llm, embeddings, agent)
- **Docker Compose**: Local dev environment with PostgreSQL
- **GitHub Actions**: Automated testing and CI/CD

## ⚠️ Limitations

- **Requires PostgreSQL**: Need Docker or local PostgreSQL with pgvector extension
- **Single tenant**: No multi-user isolation (extend with tenant_id in metadata)
- **Scanned PDFs** not supported (no OCR)
- **No streaming** responses (full generation then return)
- **Agent service**: Placeholder only (future: multi-step reasoning)

## ⚙️ Configuration

### Environment Variables

**Backend** (`backend/.env`):
```
HF_TOKEN=hf_xxxxx              # Huggingface token for embeddings
GROQ_API_KEY=gsk_xxxxx         # Groq API key for LLM
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_copilot  # PostgreSQL
FRONTEND_ORIGINS=http://localhost:5173   # CORS origins
API_KEYS=demo-key-12345:admin:DemoKey    # API authentication
LLM_TIMEOUT=30                 # LLM timeout in seconds
MAX_RETRIES=3                  # Retry attempts for LLM
```

**Frontend** (`.env.production`):
```
VITE_API_BASE=https://your-api-url.com
```

### LLM Models

Automatic fallback chain (tries in order):
1. `llama-3.1-8b-instant` (fast)
2. `llama-3.1-70b-versatile` (balanced)
3. `mixtral-8x7b-32768` (powerful)

### Performance

| Metric | Value |
|--------|-------|
| PDF upload | 2-5 sec |
| Embedding | ~100ms/chunk |
| Vector search | <10ms |
| LLM generation | 1-3 sec |
| **Total query** | **3-8 sec** |

## 📚 More Information

- **PostgreSQL setup**: See [POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md) for local and Render deployment
- **Enterprise setup**: See [ENTERPRISE.md](./ENTERPRISE.md) for scaling and multi-tenancy
- **API docs**: https://ai-financial-copilot-2.onRenderer.com/docs
- **Issues**: GitHub Issues

## 📝 License

MIT License - see LICENSE file

---

**Made with ❤️ using Groq, Huggingface, PostgreSQL + pgvector**
