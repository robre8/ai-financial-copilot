# AI Financial Copilot

A RAG (Retrieval-Augmented Generation) system for financial document analysis using local embeddings and Groq''s Llama 3.1 LLM.

## Features

-  **PDF Upload & Indexing**: Upload financial documents and automatically index them with embeddings
-  **Semantic Search**: Query documents using natural language with context-aware retrieval
-  **AI-Powered Answers**: Get accurate financial insights using Groq''s Llama 3.1 (free & fast)
-  **Fast & Scalable**: Built with FastAPI and FAISS vector database
-  **No Hidden Costs**: Local embeddings + free Groq tier

## Quick Start

### Prerequisites
- Python 3.11+
- Groq API key ([get one here](https://console.groq.com)) - **required for LLM**

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
# Edit .env and add your GROQ_API_KEY
```

3. **Run Server**
```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for API documentation.

### Docker

```bash
docker build -t financial-copilot .
docker run -e GROQ_API_KEY=your_key_here -p 8000:8000 financial-copilot
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
  "question": "What are the company''s quarterly earnings?"
}
```
Response: `{"answer": "...based on indexed documents"}`

## Architecture

```
PDF Input
   
Text Extraction (PyPDF)
   
Chunking (LangChain)
   
Embeddings (Local: all-MiniLM-L6-v2, 384-dim)
   
FAISS Vector Store
   
Context Retrieval (top-3 chunks)
   
LLM Generation (Groq - Llama 3.1)
```

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Vector DB**: FAISS with IndexFlatL2
- **Embeddings**: Local sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **LLM**: Groq''s Llama 3.1 (free tier)
- **PDF Processing**: PyPDF
- **Text Chunking**: LangChain text-splitters
- **Database**: SQLite

## Environment Variables

See `.env.example` for all required configuration.

## Testing

```bash
pytest test/
```

## Deployment

### Render
1. Push to GitHub
2. Connect repository to Render
3. Set environment variable: `GROQ_API_KEY`
4. Deploy - automatic on git push

## License

MIT
