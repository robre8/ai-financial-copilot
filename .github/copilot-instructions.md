# AI Financial Copilot - Copilot Instructions

## Architecture Overview

This is a **RAG (Retrieval-Augmented Generation) system** for financial document analysis using Huggingface APIs.

**Data Flow**: PDF Upload → Text Extraction → Chunking → Embeddings → FAISS Vector Store → Prompt Generation → LLM Response

### Core Components

- **[app/api/routes.py](app/api/routes.py)**: Two endpoints: `/upload-pdf` (index documents) and `/ask` (query with context)
- **[app/services/rag_service.py](app/services/rag_service.py)**: Orchestrates the RAG pipeline - no imports needed, it coordinates all steps
- **[app/services/vector_store_service.py](app/services/vector_store_service.py)**: FAISS index with persistent JSON storage (manual `save()` required)
- **[app/services/embedding_service.py](app/services/embedding_service.py)**: Huggingface sentence-transformers (all-MiniLM-L6-v2, 384 dimensions)
- **[app/services/llm_service.py](app/services/llm_service.py)**: GPT-2 via Huggingface Inference API
- **[app/services/pdf_service.py](app/services/pdf_service.py)**: PyPDF text extraction per page
- **[app/utils/text_splitter.py](app/utils/text_splitter.py)**: LangChain text chunking

## Critical Knowledge for AI Agents

### Vector Store Persistence Pattern
The `VectorStoreService.save()` must be **explicitly called** - it does NOT auto-save. After indexing PDFs or adding embeddings, agents must call `RAGService.vector_store.save()` to persist FAISS index + JSON metadata. **Forgetting this loses indexed data**. See [vector_store_service.py lines 22-28](app/services/vector_store_service.py#L22-L28).

### RAG Prompt Engineering
The system uses **in-context prompting** in [rag_service.py](app/services/rag_service.py#L30-L44) with explicit fallback behavior: if no chunks found, return "No relevant information". The prompt instructs the LLM to stay grounded and avoid hallucination. Modify this template carefully—changes impact all AI responses.

### Embedding Dimension Alignment
All vector operations use **384-dimensional embeddings** (all-MiniLM-L6-v2 model). If changing embedding models, update `EmbeddingService.dimension` in both [embedding_service.py](app/services/embedding_service.py#L13) and the FAISS index initialization in [vector_store_service.py](app/services/vector_store_service.py#L11).

### Huggingface API Configuration
Both embedding and LLM services use the same `HF_API_KEY` from `.env` (via [config.py](app/core/config.py)). Endpoints are hardcoded—adding new models requires updating service classes directly. Temperature set to 0.3 for deterministic financial responses.

### Stateless vs Stateful Services
- **RAGService.vector_store** is a **class variable singleton** (shared across requests)
- Question history stored in SQLDatabase (currently not connected in routes)
- Temporary files cleaned up immediately after PDF processing (see [routes.py lines 13-14](app/api/routes.py#L13-L14))

## Development Workflow

### Running the Application
```bash
# Docker build/run
docker build -t financial-copilot .
docker run -e HF_API_KEY=<key> -p 8000:8000 financial-copilot

# Local development (Python 3.11+)
pip install -r requirements.txt
export HF_API_KEY=<key>  # or set in .env file
uvicorn app.main:app --reload
```

### Testing
Check [test/test_rag.py](test/test_rag.py) for test patterns. Key distinction: embeddings are real API calls (not mocked), so tests are integration tests, not unit tests.

## Project-Specific Conventions

1. **Service Orchestration**: All business logic flows through service classes with static methods—never import routes into services
2. **Error Handling**: Services raise exceptions; routes handle HTTP responses. The PDF upload route catches and cleans up files in `finally` block
3. **Configuration**: Use `settings` singleton from `app.core.config` for all external APIs
4. **Spanish Comments**: Codebase uses Spanish comments (`🔹` markers)—preserve these when modifying

## When Adding Features

- **New API endpoint?** Add to [app/api/routes.py](app/api/routes.py), delegate business logic to service layer
- **Modify RAG behavior?** Update `RAGService` in [app/services/rag_service.py](app/services/rag_service.py)
- **New embedding source?** Extend [app/services/embedding_service.py](app/services/embedding_service.py) with new model class
- **Vector store changes?** Call `VectorStoreService.save()` explicitly; update FAISS dimension if model changes
- **New document type (not PDF)?** Create service in `app/services/` following `PDFService` pattern

## Environment Setup

- **Required**: `.env` file with `HF_API_KEY` (Huggingface API key)
- **Database**: SQLite ([app/models.py](app/models.py) defines schema, not currently used in routes)
- **Embeddings**: 384-dim vectors stored in `vector.index` + `texts.json` in working directory
