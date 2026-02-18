# AI Financial Copilot

A RAG (Retrieval-Augmented Generation) system for financial document analysis powered by Huggingface APIs.

## Features

- 📄 **PDF Upload & Indexing**: Upload financial documents and automatically index them with embeddings
- 🔍 **Semantic Search**: Query documents using natural language with context-aware retrieval
- 💡 **AI-Powered Answers**: Get accurate financial insights based on your documents
- 🚀 **Fast & Scalable**: Built with FastAPI and FAISS vector database

## Quick Start

### Prerequisites
- Python 3.11+
- Huggingface API key ([get one here](https://huggingface.co/settings/tokens))

### Local Development

1. **Clone & Install**
```bash
git clone https://github.com/your-username/ai-financial-copilot.git
cd ai-financial-copilot
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your HF_API_KEY
```

3. **Run Server**
```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

### Docker

```bash
docker build -t financial-copilot .
docker run -e HF_API_KEY=your_key_here -p 8000:8000 financial-copilot
```

## API Endpoints

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

{
  "question": "What are the company's quarterly earnings?"
}
```
Response: `{"answer": "...based on indexed documents"}`

## Architecture

```
PDF Input
   ↓
Text Extraction (PyPDF)
   ↓
Chunking (LangChain)
   ↓
Embeddings (all-MiniLM-L6-v2, 384-dim)
   ↓
FAISS Vector Store
   ↓
Context Retrieval (top-3 chunks)
   ↓
LLM Generation (Mistral-7B)
```

## Environment Variables

See `.env.example` for all required configuration.

## Testing

```bash
pytest test/
```

## Deployment

### Render
1. Push to GitHub
2. Create new Web Service on [Render](https://render.com)
3. Select "Deploy from GitHub" and choose this repository
4. Configure environment variable: `HF_API_KEY`
5. Deploy

The `render.yaml` will automatically handle build and deployment.

### Local Docker
```bash
docker run -e HF_API_KEY=your_key -p 8000:8000 financial-copilot:latest
```

## Project Structure

```
app/
├── api/           # FastAPI routes
├── services/      # Business logic (RAG, embeddings, PDF, LLM)
├── core/          # Configuration & logging
├── schemas/       # Pydantic models
└── utils/         # Text splitting utilities
test/
├── test_rag.py    # Integration tests
.github/
├── copilot-instructions.md  # AI Agent guidance
```

## Key Services

- **RAGService**: Orchestrates PDF indexing and question answering
- **EmbeddingService**: Generates embeddings via Huggingface
- **VectorStoreService**: FAISS index with JSON persistence
- **LLMService**: Text generation via Mistral-7B
- **PDFService**: Document text extraction

## Important Notes

⚠️ **Vector Store Persistence**: After indexing PDFs, vector store changes must be saved explicitly via `RAGService.vector_store.save()`. The system does NOT auto-save.

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
