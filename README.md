# AI Financial Copilot

A RAG (Retrieval-Augmented Generation) system for financial document analysis using Huggingface embeddings and Groq LLM API.

## Features

- **PDF Upload & Indexing**: Upload financial documents and automatically index them with 384-dimensional embeddings
- **Semantic Search**: Query documents using natural language with context-aware retrieval
- **AI-Powered Answers**: Get financial insights powered by Groq's fast LLM API
- **Fast & Scalable**: Built with FastAPI, FAISS vector database, optimized for production
- **Free Tier Compatible**: Huggingface embeddings + Groq LLM (both free tier)
- **Production Ready**: Deployed on Render with memory optimization

## Quick Start

### Prerequisites
- Python 3.11+
- Huggingface API token ([get one here](https://huggingface.co/settings/tokens)) - **required for embeddings**
- Groq API key ([get one here](https://console.groq.com/keys)) - **required for LLM generation**

### Local Development

1. **Clone & Install**
```bash
git clone https://github.com/robre8/ai-financial-copilot.git
cd ai-financial-copilot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. **Configure Environment**
```bash
# Create backend/.env file with your API tokens
echo "HF_TOKEN=your_huggingface_token_here" > backend/.env
echo "GROQ_API_KEY=your_groq_api_key_here" >> backend/.env
echo "FRONTEND_ORIGINS=http://localhost:5173" >> backend/.env
```

3. **Run Server**
```bash
cd backend
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

### Production Deployment (Render)

The application is already deployed on Render. Visit:
- **API**: https://ai-financial-copilot.onrender.com
- **API Docs**: https://ai-financial-copilot.onrender.com/docs

Environment variables are configured in Render dashboard.

## API Endpoints

### Health Check
```bash
GET /
```
Response: `{"message": "AI Financial Copilot - RAG System", "status": "online", ...}`

### Upload PDF
```bash
POST /upload-pdf
Content-Type: multipart/form-data

file: <your_pdf>
```
Response: `{"message": "PDF indexed successfully"}`

### Ask Question
```bash
POST /ask
Content-Type: application/json

{"question": "What are the company's quarterly earnings?"}
```
Response: `{"answer": "...", "model": "llama-3.1-8b-instant", "chunk_count": 3, "context": "..."}`

### Debug LLM (for testing)
```bash
POST /debug/llm-raw
Content-Type: application/json

{"prompt": "Summarize this document..."}
```
Response: `{"result": "...", "model": "llama-3.1-8b-instant", "status": 200}`

## Architecture

```
PDF Upload
    ↓
Text Extraction (PyPDF)
    ↓
Text Chunking (custom splitter)
    ↓
Embeddings Generation (Huggingface InferenceClient API)
    ↓
FAISS Vector Store (384-dim, max 5000 vectors)
    ↓
Semantic Search (similarity matching)
    ↓
Context Retrieval (top-3 chunks)
    ↓
LLM Generation (Groq API with 3-model fallback chain)
    ↓
Response to User
```

**LLM Models**: Uses Groq with automatic fallback chain: `llama-3.1-8b-instant` → `llama-3.1-70b-versatile` → `mixtral-8x7b-32768`

## Tech Stack

- **Framework**: FastAPI + Uvicorn (single worker, 10 concurrent requests)
- **Vector DB**: FAISS IndexFlatL2 (384-dim, max 5000 vectors)
- **Embeddings**: Huggingface InferenceClient API (sentence-transformers/all-MiniLM-L6-v2)
- **LLM API**: Groq API (llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768)
- **PDF Processing**: PyPDF
- **Text Chunking**: Custom text splitter (512 tokens/chunk, 100 token overlap)
- **Deployment**: Docker + Render (free tier, 512MB RAM)
- **Frontend**: React + Vite + Tailwind CSS
- **Optimization**: Memory limits, garbage collection, vector store pruning

## Environment Variables

```bash
HF_TOKEN=hf_your_token_here         # Required: Huggingface API token for embeddings
GROQ_API_KEY=gsk_your_key_here      # Required: Groq API key for LLM generation
FRONTEND_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

Get your tokens at:
- Huggingface: https://huggingface.co/settings/tokens
- Groq: https://console.groq.com/keys

## Example Usage

### Upload and Query

```bash
# 1. Upload a PDF
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@financial_report.pdf"

# 2. Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What was the net revenue?"}'

# Response:
# {
#   "answer": "Based on the indexed documents, the net revenue..."
# }
```

### Test LLM Endpoint

```bash
curl -X POST "http://localhost:8000/debug/llm-raw" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Summarize the following: ..."}'
```

## Deployment on Render

The application is currently deployed on Render with automatic deployments on git push.

**Configuration**:
- Service: https://ai-financial-copilot.onrender.com
- Environment: Free tier (512MB RAM)
- Auto-rebuild: On git push to main
- Memory-optimized: Single worker, 10 concurrent requests
 - Build: `pip install -r backend/requirements.txt`
 - Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --limit-concurrency 10`

To deploy:
1. Push to GitHub `main` branch
2. Render automatically rebuilds and deploys
3. Monitor at Render dashboard

## Troubleshooting

### Memory Issues
- Vector store limited to 5000 vectors (~75MB)
- Automatic garbage collection after each operation
- Single worker mode to prevent swapping

### LLM Generation Failures
- Groq API provides 3-model fallback chain for high availability
- If all models fail, check Groq API status at https://status.groq.com/
- Verify GROQ_API_KEY is set correctly in environment variables

### PDF Upload Issues
- Ensure PDF is valid and not corrupted
- Maximum tested with files up to 50MB
- System extracts text using PyPDF2

### CORS Issues
- Set `FRONTEND_ORIGINS` to your Vercel URL (and local dev URL)
- Example: `FRONTEND_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app`

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # FastAPI endpoints
│   │   ├── services/
│   │   │   ├── llm_service.py     # LLM inference
│   │   │   ├── embedding_service.py  # Embeddings generation
│   │   │   ├── vector_store_service.py  # FAISS vector DB
│   │   │   ├── pdf_service.py     # PDF extraction
│   │   │   └── rag_service.py     # RAG orchestration
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   └── logger.py          # Logging setup
│   │   ├── schemas/
│   │   │   └── rag_schema.py      # API schemas
│   │   ├── utils/
│   │   │   └── text_splitter.py   # Text chunking
│   │   ├── database.py            # DB setup
│   │   ├── models.py              # Data models
│   │   └── main.py                # FastAPI app
│   ├── requirements.txt           # Backend dependencies
│   └── Dockerfile                 # Backend container config
├── ai-copilot-frontend/           # React frontend (Vite + Tailwind)
├── render.yaml                    # Render deployment config
└── README.md
```

## License

MIT
