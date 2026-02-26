# 📊 AI Financial Copilot

[![CI](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/robre8/ai-financial-copilot/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-grade Retrieval-Augmented Generation (RAG) microservice for intelligent financial document analysis.**

Upload PDFs → Ask questions → Get AI-powered insights powered by Groq LLMs, Huggingface embeddings, and PostgreSQL pgvector search.

**🚀 [Try Live Demo](https://ai-financial-copilot.vercel.app/)** | **📡 [API Docs](https://ai-financial-copilot-3.onrender.com/docs)** | **📖 [Enterprise Guide](./ENTERPRISE.md)**

---

## 🔀 Git Workflow & Branching Strategy

```
main (production)
  ├── Stable, production-ready code
  ├── Tagged releases
  ├── Frontend: https://ai-financial-copilot.vercel.app (Vercel production)
  └── Backend: https://ai-financial-copilot-3.onrender.com (Render production)
       ↑ (merges from feature branches)

feature/improvements (development)
  ├── Active development branch
  ├── Preview builds on every push
  ├── Frontend: https://ai-financial-copilot-preview.vercel.app (Vercel preview)
  └── Backend: Testing/staging endpoints
```

**Workflow**:
1. **Development**: All features on `feature/improvements` branch
2. **Preview**: Vercel automatically builds & deploys preview on every push
3. **Production**: Cherry-pick tested features to `main` when stable
4. **Releases**: Tag `main` with semantic versions (v1.0.0, v1.1.0, etc.)

**For Contributors**: Submit PRs against `feature/improvements` branch

## ✨ Key Features

| Feature | Details |
|---------|---------|
| **Intelligent RAG** | Semantic search + LLM generation with 3-model fallback |
| **PDF Processing** | Automatic extraction, chunking, and vector indexing |
| **Fast API** | FastAPI REST endpoints with CORS + error handling |
| **Modern UI** | React 18 + Tailwind CSS with dark mode & animations |
| **Production Ready** | Docker, tests, CI/CD, and monitoring included |
| **Secure** | Firebase Auth (OAuth2 + JWT) + rate limiting + retry logic |

## 🛠️ Tech Stack

**Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Firebase Auth  
**Backend**: FastAPI + Python 3.11 + Uvicorn + Firebase Admin SDK  
**AI/ML**: Groq API (LLMs) + Huggingface (embeddings)  
**Database**: PostgreSQL + pgvector (persistent vector storage)  
**Authentication**: Firebase Auth (Google OAuth2 + Email/Password) + JWT validation  
**Deployment**: Docker Compose + Render (backend) + Vercel (frontend)

## 🔄 CI/CD & Quality

- 50+ tests (backend + integration)
- GitHub Actions pipeline (test, lint, Docker build)
- Code coverage reporting
- Dockerized backend service
- Automated build validation on every push

## 📋 Prerequisites

- **Python 3.11+** (for local backend)
- **Node.js 18+** (for local frontend)
- **Huggingface API Token** ([get here](https://huggingface.co/settings/tokens))
- **Groq API Key** ([get here](https://console.groq.com/keys))
- **Firebase Project** ([create here](https://console.firebase.google.com/)) - for authentication

## 🚀 Quick Start

### Try Online (Easiest)
Visit https://ai-financial-copilot.vercel.app/, sign in with Google or create an account, upload a PDF, and start asking questions.

### Run Locally (5 minutes)

```bash
# Clone repo
git clone https://github.com/robre8/ai-financial-copilot.git
cd ai-financial-copilot

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Create backend/.env (Firebase service account JSON required)
cat > backend/.env << EOF
HF_TOKEN=your_token_here
GROQ_API_KEY=your_key_here
FRONTEND_ORIGINS=http://localhost:5173
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
EOF

# Run backend (in one terminal)
cd backend && uvicorn app.main:app --reload

# Frontend setup (in new terminal)
cd ai-copilot-frontend
npm install

# Create .env.local with Firebase config
cat > .env.local << EOF
VITE_API_BASE=http://localhost:8000
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
EOF

# Run frontend
npm run dev
```

Open http://localhost:5173, sign in, and start uploading PDFs!

**Note**: You'll need to create a Firebase project and configure authentication. See [Authentication Setup](#firebase-setup-required) section.

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

For production setup, use the Render blueprint in [render.yaml](render.yaml).

## 📡 API Endpoints

```bash
GET  /                    # Health check
POST /upload-pdf          # Upload & index PDF
POST /ask                 # Query the knowledge base
POST /debug/llm-raw       # Test LLM endpoint (dev only)
```

**Full API docs**: http://localhost:8000/docs (when running locally)

## 🔐 Authentication & Security

All endpoints (except `/`) are protected with **Firebase Authentication (OAuth2 + JWT)** and **rate limiting**.

### Firebase Authentication

The application uses Firebase Auth for secure user authentication with multiple sign-in methods:

**Supported Methods**:
- 🔐 **Google OAuth2**: One-click sign-in with Google account
- 📧 **Email/Password**: Traditional email registration and login
- 🔄 **JWT Tokens**: Automatic token refresh and validation

**How it works**:
1. User signs in via frontend (Google or Email/Password)
2. Firebase returns a JWT ID token
3. Frontend includes token in `Authorization: Bearer <token>` header
4. Backend validates token using Firebase Admin SDK
5. Request is authenticated ✅

### API Authentication

Include your Firebase JWT token in the `Authorization` header:

```bash
# First, sign in via the web UI and copy your token
# Then use it in API requests:

curl -X POST "https://ai-financial-copilot-3.onrender.com/upload-pdf" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6..." \
  -F "file=@document.pdf"
```

### User Management

Firebase Auth provides built-in features:
- Email verification
- Password reset
- Account security
- Multi-factor authentication (optional)
- User profile management

### Rate Limiting

- **Default limit**: 10 requests/minute per authenticated user
- **Debug endpoint**: 5 requests/minute
- Exceeding limits returns `429 Too Many Requests`

### Retry & Timeout Strategy

LLM requests automatically retry on failures:
- **Max retries**: 3 attempts
- **Backoff**: Exponential (1s → 2s → 4s)
- **Timeout**: 30 seconds (configurable via `LLM_TIMEOUT`)

### Firebase Setup (Required)

**Frontend - Firebase Web SDK**:
1. Create Firebase project at https://console.firebase.google.com/
2. Enable Authentication → Sign-in methods → Google and Email/Password
3. Get Firebase config from Project Settings
4. Add environment variables to Vercel (see Configuration section below)

**Backend - Firebase Admin SDK**:
1. Go to Project Settings → Service Accounts
2. Generate new private key (downloads JSON file)
3. Copy entire JSON content and set as `FIREBASE_SERVICE_ACCOUNT_JSON` environment variable in Render

For detailed setup instructions, see [SECURITY_AUTHENTICATION_GUIDE.md](./SECURITY_AUTHENTICATION_GUIDE.md).

## 📁 Project Structure

```
ai-financial-copilot/
├── main                               # Production branch (stable, released)
├── feature/improvements               # Development branch (preview on Vercel)
│
├── backend/                           # FastAPI microservice (Python 3.11)
│   ├── app/
│   │   ├── main.py                   # FastAPI app initialization
│   │   ├── models.py                 # SQLAlchemy ORM models
│   │   ├── database.py               # PostgreSQL connection & session factory
│   │   ├── api/
│   │   │   └── routes.py             # REST endpoints (/upload, /ask, /analyze, etc)
│   │   ├── services/
│   │   │   ├── vector_service.py     # pgvector operations (semantic search)
│   │   │   ├── llm_service.py        # Groq LLM with 3-model fallback & retry logic
│   │   │   ├── embedding_service.py  # Huggingface embeddings (all-MiniLM-L6-v2)
│   │   │   ├── pdf_service.py        # PDF extraction & text splitting
│   │   │   ├── rag_service.py        # RAG orchestration (upload → search → generate)
│   │   │   └── agent_service.py      # ReAct financial analysis agent
│   │   ├── core/
│   │   │   ├── config.py             # Settings & environment variables
│   │   │   ├── security.py           # Firebase JWT authentication & authorization
│   │   │   ├── logger.py             # Structured logging
│   │   │   └── rate_limit.py         # Per-user rate limiting (10 req/min default)
│   │   ├── schemas/
│   │   │   └── rag_schema.py         # Pydantic request/response models
│   │   └── utils/
│   │       └── text_splitter.py      # Document chunking (512 tokens per chunk)
│   ├── requirements.txt              # Python dependencies (FastAPI, SQLAlchemy, firebase-admin, etc)
│   ├── Dockerfile                    # Container image for backend
│   ├── vector.index                  # FAISS index (if used locally)
│   └── texts.json                    # Sample documents for testing
│
├── ai-copilot-frontend/              # React 18 + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.tsx     # Main chat & PDF upload UI
│   │   ├── App.tsx                   # Root React component
│   │   ├── main.tsx                  # Vite app entrypoint
│   │   ├── index.css                 # Tailwind CSS + globals
│   │   └── vite-env.d.ts             # TypeScript Vite env types
│   ├── package.json                  # Dependencies (React, Tailwind, Firebase SDK, etc)
│   ├── vite.config.ts                # Vite bundler configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   └── Dockerfile                    # Container image for frontend
│
├── tests/                            # Comprehensive test suite (50+ tests)
│   ├── conftest.py                   # Pytest fixtures (Firebase mock, DB session, etc)
│   ├── test_api.py                   # Endpoint unit tests
│   ├── test_agent.py                 # Financial agent tests (/analyze, /webhooks)
│   ├── test_integration.py           # Full RAG pipeline integration tests
│   ├── test_security.py              # Firebase auth & authorization tests
│   └── test_rag.py                   # RAG service unit tests
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions pipeline (test, build, deploy)
│
├── docker-compose.yml                # Local dev: PostgreSQL 15 + backend + pgvector
├── init-db.sql                       # Database initialization script
├── Dockerfile                        # (root) Main backend Dockerfile
│
├── README.md                         # ← You are here
├── ENTERPRISE.md                     # Production deployment & compliance guide
├── SECURITY_AUTHENTICATION_GUIDE.md  # Firebase setup & JWT validation
├── SECURITY_ACTIVATION_STEPS.md      # Step-by-step security configuration
├── SECURITY_VALIDATION_GUIDE.md      # Testing security features
├── SECURITY_FIX_CHECKLIST.md         # Security hardening checklist
│
└── README files
    ├── pytest.ini                    # Pytest configuration
    └── conftest.py                   # Root-level pytest setup
```

**Key Directories**:
- **backend/**: FastAPI REST API with PostgreSQL + pgvector
- **ai-copilot-frontend/**: React SPA with Tailwind CSS, Firebase Auth
- **tests/**: Unit & integration tests (auto-run on GitHub Actions)
- **.github/workflows/**: CI/CD pipeline definitions

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

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vercel)                  │
│          Dashboard | Chat | PDF Upload | Analytics         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Render/Docker)               │
├─────────────┬──────────────┬──────────────┬────────────────┤
│ REST API    │ Security     │ Rate Limit   │ Error Handling │
│ • /upload   │ • Firebase   │ • 10 req/min │ • Retries      │
│ • /ask      │ • JWT/OAuth2 │ • Per user   │ • Timeouts     │
│ • /analyze  │ • Scopes     │ • Backoff    │ • Graceful     │
│ • /webhooks │ • CORS       │ (enterprise) │ • Logging      │
└─────────────┴──────────────┴──────────────┴────────────────┘
     │                │                │
     ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   RAG        │  │   Agent      │  │   Webhooks   │
│   Service    │  │   Service    │  │   (Events)   │
│              │  │              │  │              │
│ • Orchestr.  │  │ • Tool setup │  │ • Notif.     │
│ • Chunking   │  │ • Reasoning  │  │ • External   │
│ • Query      │  │ • Memory     │  │   systems    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ├────────┬────────┴────────┬────────┤
       ▼        ▼                 ▼        ▼
   ┌─────────────────────────────────────────┐
   │     Microservices (Python Services)     │
   ├─────────────────────────────────────────┤
   │ • Embedding Service (HF: all-MiniLM)   │
   │ • LLM Service (Groq: 3-model fallback) │
   │ • Vector Service (pgvector ops)        │
   │ • PDF Processing (pypdf)               │
   └────────┬────────────────────────────────┘
            │
            ▼
   ┌─────────────────────────────────────────┐
   │      Data Layer (PostgreSQL 15)         │
   ├─────────────────────────────────────────┤
   │ • pgvector extension (384-dim)          │
   │ • Persistent embeddings cache           │
   │ • Metadata (JSONB)                      │
   │ • Analysis history                      │
   └─────────────────────────────────────────┘
```

## 🤖 Financial Analysis Agent

The **agent** uses a ReAct (Reasoning + Acting) pattern with specialized tools:

### Agent Workflow

```
Input Document
    ↓
┌─────────────────────────────────────────┐
│   Agent Decision Making                 │
│   "What tools do I need?"               │
└─────────────────────────────────────────┘
    ↓
    ├─→ Tool 1: Extract Financial Metrics
    │        Extract: Revenue, Assets, Ratios
    │        Calculate: Liquidity, Leverage, Profitability
    │
    ├─→ Tool 2: Detect Risk Patterns  
    │        Analyze: Debt levels, Margins, Keywords
    │        Score: Risk assessment (low/medium/high)
    │
    └─→ Tool 3: Generate Structured Report
             Synthesize: Metrics + Risks
             Output: JSON with recommendations
    ↓
Structured Financial Analysis
{
  "financial_metrics": {
    "revenue": 150000000,
    "net_income": 45000000,
    "liquidity_ratio": 1.3,
    "debt_ratio": 0.62,
    "profit_margin": 0.30
  },
  "risk_assessment": {
    "risk_level": "medium",
    "risk_score": 45,
    "identified_risks": [...]
  },
  "recommendations": [...]
}
```

### Integration Points

```bash
# 1. Sign in and get Firebase JWT token via web UI first
# 2. Use token to analyze via endpoint
curl -X POST "https://ai-financial-copilot-3.onrender.com/analyze" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6..." \
  -H "Content-Type: application/json" \
  -d '{"question": "Q3 2025 Financial Report..."}'

# 3. Webhook notification on completion
# Triggers: POST /webhooks/analysis-complete
# External systems notified of results
```

## 🚀 Enterprise Features

| Feature | Status | Details |
|---------|--------|---------|
| **Firebase Auth (OAuth2 + JWT)** | ✅ | Google login + Email/Password with JWT validation |
| **Rate Limiting** | ✅ | Per-user limits with backoff |
| **Webhook Support** | ✅ | Event-driven integration |
| **Financial Analysis Agent** | ✅ | ReAct with 3 specialized tools |
| **Persistent Storage** | ✅ | PostgreSQL with pgvector |
| **Error Handling** | ✅ | Graceful degradation + retries |
| **Monitoring/Logging** | ✅ | Structured logs, debug endpoints |
| **Docker Ready** | ✅ | Production-grade container setup |
| **Multi-tenancy** | 🔄 | Custom scoping layer |
| **Analytics** | ⏳ | Query metrics dashboard |
| **Caching Layer** | ⏳ | Redis integration |

**Legend**: ✅ Implemented | 🔄 In Progress | ⏳ Planned

### Webhook Events

```json
{
  "event_type": "analysis.completed",
  "event_id": "evt_abc123",
  "timestamp": "2026-02-24T20:30:00Z",
  "status": "success",
  "payload": {
    "analysis_id": "analysis_123",
    "risk_level": "medium",
    "recommendations_count": 3
  },
  "delivery_attempts": 1
}
```

## 📋 Roadmap

### Q2 2026
- [ ] Multi-tenancy with organization scoping
- [ ] Redis caching layer for embeddings
- [ ] Advanced analytics dashboard
- [ ] PDF OCR support (Tesseract integration)
- [ ] Streaming LLM responses

### Q3 2026  
- [ ] OAuth2/SAML enterprise auth
- [ ] Scheduled analysis reports
- [ ] Custom model fine-tuning
- [ ] Graph database for entity relationships
- [ ] Multi-model ensemble predictions

### Q4 2026
- [ ] Real-time document collaboration
- [ ] Advanced anomaly detection
- [ ] Compliance audit trails
- [ ] Custom LLM deployment (Ollama)
- [ ] CLI tool and SDK

---

## 🧠 Design Decisions

- **Firebase Auth** over custom JWT: Industry-standard OAuth2, built-in security, easy integration
- **PostgreSQL + pgvector** over FAISS: Persistent storage, production-ready, survives restarts
- **Groq** over OpenAI: 10x faster inference, generous free tier
- **Custom RAG** over LangChain: Lower memory footprint, full control
- **Clean Architecture**: Separated services (vector, llm, embeddings, agent)
- **Docker Compose**: Local dev environment with PostgreSQL
- **GitHub Actions**: Automated testing and CI/CD

## ⚠️ Limitations

- **Requires PostgreSQL**: Need Docker or local PostgreSQL with pgvector extension
- **Authentication required**: Must sign in with Google or Email to use the API
- **Scanned PDFs** not supported (no OCR)
- **No streaming** responses (full generation then return)

## 🔄 Migration Notes

**v2.0 (February 2026)**: Migrated from simple API key authentication to Firebase Auth (OAuth2 + JWT) for production-ready user management. This provides:
- Individual user accounts and sessions
- Industry-standard OAuth2 security
- Built-in password reset and email verification
- Better audit trails and user management

Legacy API key authentication was removed in favor of Firebase tokens for all protected endpoints.

## ⚙️ Configuration

### Environment Variables

**Backend** (`backend/.env`):
```bash
# Required API Tokens
HF_TOKEN=hf_xxxxx              # Huggingface token for embeddings
GROQ_API_KEY=gsk_xxxxx         # Groq API key for LLM

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_copilot

# Firebase Authentication (Required for protected endpoints)
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}  # Full JSON from Firebase

# CORS Configuration
FRONTEND_ORIGINS=http://localhost:5173,https://ai-financial-copilot.vercel.app,https://ai-financial-copilot-preview.vercel.app

# Performance Tuning
LLM_TIMEOUT=30                 # LLM timeout in seconds
MAX_RETRIES=3                  # Retry attempts for LLM
EMBEDDING_TIMEOUT=20           # Embedding timeout in seconds
RETRY_MULTIPLIER=2             # Exponential backoff multiplier
```

**Frontend** (`ai-copilot-frontend/.env.local`):
```bash
# API Backend URL
VITE_API_BASE=http://localhost:8000

# Firebase Web SDK Configuration (from Firebase Console)
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=1234567890
VITE_FIREBASE_APP_ID=1:1234567890:web:abcdef
VITE_FIREBASE_MEASUREMENT_ID=G-XXXXXXXXXX
```

**Production** (`.env.production`):
```bash
VITE_API_BASE=https://ai-financial-copilot-3.onrender.com
# + all VITE_FIREBASE_* variables (same as above)
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
- **Authentication Guide**: See [SECURITY_AUTHENTICATION_GUIDE.md](./SECURITY_AUTHENTICATION_GUIDE.md) for Firebase setup
- **API docs**: https://ai-financial-copilot-3.onrender.com/docs
- **Live Demo**: https://ai-financial-copilot.vercel.app/
- **Issues**: GitHub Issues

## 📝 License

MIT License - see LICENSE file

---

**Made with ❤️ using Groq, Huggingface, PostgreSQL + pgvector**
