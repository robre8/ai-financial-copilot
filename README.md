# AI Financial Copilot

A RAG (Retrieval-Augmented Generation) system for financial document analysis using Huggingface embeddings and LLM inference API.

## Features

- **PDF Upload & Indexing**: Upload financial documents and automatically index them with 384-dimensional embeddings
- **Semantic Search**: Query documents using natural language with context-aware retrieval
- **AI-Powered Answers**: Get financial insights using Huggingface inference API with graceful fallback
- **Fast & Scalable**: Built with FastAPI, FAISS vector database, and optimized for production
- **Zero Costs**: Free tier compatible (Huggingface, Render free tier)
- **Production Ready**: Deployed on Render with memory optimization

## Quick Start

### Prerequisites
- Python 3.11+
- Huggingface API token ([get one here](https://huggingface.co/settings/tokens)) - **required for embeddings**

### Local Development

1. **Clone & Install**
```bash
git clone https://github.com/robre8/ai-financial-copilot.git
cd ai-financial-copilot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy .env template and add your HF_TOKEN
echo "HF_TOKEN=your_huggingface_token_here" > .env
```

3. **Run Server**
```bash
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
Response: `{"answer": "Based on the indexed documents, ..."}`

### Debug LLM (for testing)
```bash
POST /debug/llm-raw
Content-Type: application/json

{"prompt": "Summarize this document..."}
```
Response: `{"result": "...", "status": 200}`

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
LLM Generation (Huggingface Inference API with fallback)
    ↓
Response to User
```

**Fallback Behavior**: If LLM models are unavailable, system returns processed context directly (still useful for document analysis)

## Tech Stack

- **Framework**: FastAPI + Uvicorn (single worker, 10 concurrent requests)
- **Vector DB**: FAISS IndexFlatL2 (384-dim, max 5000 vectors)
- **Embeddings**: Huggingface InferenceClient API (sentence-transformers/all-MiniLM-L6-v2)
- **LLM API**: Huggingface Inference API with automatic fallback
- **PDF Processing**: PyPDF
- **Text Chunking**: Custom text splitter (512 tokens/chunk, 100 token overlap)
- **Deployment**: Docker + Render (free tier, 512MB RAM)
- **Optimization**: Memory limits, garbage collection, vector store pruning

## Environment Variables

```bash
HF_TOKEN=hf_your_token_here  # Required: Huggingface API token for embeddings
```

Get your token at: https://huggingface.co/settings/tokens

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
- System gracefully falls back to returning context chunks
- LLM models may be unavailable on free tier
- Check Huggingface API status or add GROQ_API_KEY for alternative LLM

### PDF Upload Issues
- Ensure PDF is valid and not corrupted
- Maximum tested with files up to 50MB
- System extracts text using PyPDF2

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI endpoints
│   ├── services/
│   │   ├── llm_service.py     # LLM inference
│   │   ├── embedding_service.py  # Embeddings generation
│   │   ├── vector_store_service.py  # FAISS vector DB
│   │   ├── pdf_service.py     # PDF extraction
│   │   └── rag_service.py     # RAG orchestration
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── logger.py          # Logging setup
│   ├── schemas/
│   │   └── rag_schema.py      # API schemas
│   ├── utils/
│   │   └── text_splitter.py   # Text chunking
│   ├── database.py            # DB setup
│   ├── models.py              # Data models
│   └── main.py                # FastAPI app
├── test/
│   └── test_rag.py            # Integration tests
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container config
├── render.yaml               # Render deployment config
└── README.md
```

## License

MIT
