# 📊 AI Financial Copilot

[![CI](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-grade Retrieval-Augmented Generation (RAG) microservice for intelligent financial document analysis.**

Upload PDFs → Ask questions → Get AI-powered insights powered by Groq LLMs, Huggingface embeddings, and FAISS vector search.

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
**AI/ML**: Groq API (LLMs) + Huggingface (embeddings) + FAISS (vector store)  
**Database**: FAISS in-memory (PostgreSQL pgvector recommended for production)  
**Deployment**: Docker + Render (backend) + Vercel (frontend)

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
│   │   ├── api/routes.py             # Endpoints
│   │   ├── services/                 # Business logic (RAG, LLM, embeddings)
│   │   ├── core/config.py            # Configuration
│   │   └── utils/text_splitter.py    # Chunking
│   ├── requirements.txt
│   └── Dockerfile
├── ai-copilot-frontend/              # React app
│   ├── src/components/ChatInterface.tsx
│   ├── package.json
│   └── vite.config.ts
├── tests/                            # 20+ unit tests
├── .github/workflows/ci.yml          # GitHub Actions
└── ENTERPRISE.md                     # Enterprise setup guide
```

## 🏗️ How It Works

```
User uploads PDF
    ↓
Text extraction + Chunking (512 tokens)
    ↓
Huggingface: Generate 384-dim embeddings per chunk
    ↓
FAISS: Store vectors in in-memory index
    ↓
User asks question
    ↓
Semantic search: Retrieve top-3 similar chunks
    ↓
Groq LLM: Generate answer from context
    ↓
Return answer + model info + source chunks
```

## 🧠 Design Decisions

- **FAISS** over Pinecone: Zero-cost, in-memory, perfect for prototypes
- **Groq** over OpenAI: 10x faster inference, generous free tier
- **Custom RAG** over LangChain: Lower memory footprint, full control
- **Docker + GitHub Actions**: Automated testing and CI/CD out-of-the-box

## ⚠️ Limitations

- Vector store is **in-memory** (resets on restart) → use `ENTERPRISE.md` for PostgreSQL setup
- **No authentication** (demo purposes) → see `ENTERPRISE.md` for auth patterns
- **Single document** session model → extend for multi-doc support
- **Scanned PDFs** not supported (no OCR)
- **No streaming** responses (full generation then return)

## ⚙️ Configuration

### Environment Variables

**Backend** (`backend/.env`):
```
HF_TOKEN=hf_xxxxx              # Huggingface token for embeddings
GROQ_API_KEY=gsk_xxxxx         # Groq API key for LLM
FRONTEND_ORIGINS=http://localhost:5173   # CORS origins
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

- **Enterprise setup**: See [ENTERPRISE.md](./ENTERPRISE.md)
- **API docs**: https://ai-financial-copilot-2.onRenderer.com/docs
- **Issues**: GitHub Issues

## 📝 License

MIT License - see LICENSE file

---

**Made with ❤️ using Groq, Huggingface, and FAISS**
