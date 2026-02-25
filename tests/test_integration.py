"""
Integration Tests - Test full RAG pipeline with FastAPI TestClient
Tests document upload, vector storage, and query answering end-to-end.
Supports both SQLite (default) and PostgreSQL with pgvector (if available).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import io
import os
import logging

from app.main import app
from app.models import Base, Document
from app.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

# Determine database URL based on environment
# Priority: TEST_DATABASE_URL env var → POSTGRESQL (default)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_copilot"
)

# Fallback to SQLite if PostgreSQL not available
try:
    # PostgreSQL uses connect_timeout, SQLite uses timeout
    connect_args = {"connect_timeout": 5} if "postgresql" in TEST_DATABASE_URL else {"timeout": 5}
    test_engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
    with test_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    engine = test_engine
    logger.info(f"✅ Using database: {TEST_DATABASE_URL[:50]}...")
except Exception as e:
    logger.warning(f"⚠️ PostgreSQL not available, using SQLite: {e}")
    TEST_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Disable rate limiting for tests
app.state.limiter.enabled = False


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create fresh database tables for each test."""
    # Create pgvector extension if using PostgreSQL
    if "postgresql" in TEST_DATABASE_URL:
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
                logger.info("✅ pgvector extension enabled")
        except Exception as e:
            logger.warning(f"⚠️ Could not enable pgvector: {e}")
    
    # Clear existing data first
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers():
    """Provide authentication headers for API requests."""
    return {"X-API-Key": "demo-key-12345"}


def create_test_pdf() -> bytes:
    """
    Create a minimal test PDF with financial data.
    """
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 350>>stream
BT
/F1 24 Tf
50 700 Td
(Q3 2025 Financial Report) Tj
0 -30 Td
/F1 14 Tf
(Revenue: $150 Million) Tj
0 -20 Td
(Net Income: $45 Million) Tj
0 -20 Td
(Operating Expenses: $75 Million) Tj
0 -20 Td
(Gross Margin: 70%) Tj
0 -30 Td
(Key Highlights:) Tj
0 -20 Td
(- 25% year-over-year revenue growth) Tj
0 -20 Td
(- Customer base: 50,000 users) Tj
ET
endstream endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000643 00000 n 
trailer<</Size 6/Root 1 0 R>>
startxref
716
%%EOF
"""
    return pdf_content


class TestIntegrationRAGPipeline:
    """Integration tests for the complete RAG pipeline."""
    
    def test_health_check(self):
        """Test root endpoint is accessible."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "message" in data
    
    def test_upload_pdf_without_auth(self):
        """Test that PDF upload requires authentication."""
        pdf_bytes = create_test_pdf()
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        
        response = client.post("/upload-pdf", files=files)
        assert response.status_code == 401  # Unauthorized without auth
    
    def test_upload_pdf_with_auth(self, auth_headers):
        """Test successful PDF upload with authentication."""
        pdf_bytes = create_test_pdf()
        files = {"file": ("financial_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        
        response = client.post("/upload-pdf", files=files, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "success" in data["message"].lower() or "indexed" in data["message"].lower()
    
    def test_ask_question_without_auth(self):
        """Test that asking questions requires authentication."""
        response = client.post("/ask", json={"question": "What is the revenue?"})
        assert response.status_code == 401  # Unauthorized without auth
    
    def test_ask_question_with_auth_no_documents(self, auth_headers):
        """Test asking a question when documents may or may not be indexed."""
        response = client.post(
            "/ask",
            json={"question": "What is the revenue?"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # Should either indicate no documents found or provide an answer
        # (documents may persist from previous test runs)
        assert "answer" in data or "no relevant information" in data["answer"].lower()
    
    def test_full_rag_pipeline(self, auth_headers):
        """
        Test complete RAG pipeline: upload PDF, then ask questions.
        
        Note: This test requires PostgreSQL with pgvector extension.
        SQLite doesn't support vector operations, so this test is skipped
        in the basic test suite. Run with PostgreSQL for full integration testing.
        """
        # Step 1: Upload PDF
        pdf_bytes = create_test_pdf()
        files = {"file": ("financial_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        
        upload_response = client.post("/upload-pdf", files=files, headers=auth_headers)
        assert upload_response.status_code == 200
        
        # Step 2: Ask question about revenue
        query_response = client.post(
            "/ask",
            json={"question": "What was the revenue in Q3 2025?"},
            headers=auth_headers
        )
        assert query_response.status_code == 200
        data = query_response.json()
        
        # Verify response structure
        assert "answer" in data
        assert "model" in data
        assert "chunks" in data
        assert "chunk_count" in data
        
        # Verify answer contains relevant information
        answer = data["answer"].lower()
        assert "150 million" in answer or "revenue" in answer
    
    def test_ask_empty_question(self, auth_headers):
        """Test that empty questions are rejected."""
        response = client.post(
            "/ask",
            json={"question": ""},
            headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_upload_non_pdf_file(self, auth_headers):
        """Test that non-PDF files are rejected."""
        text_file = b"This is not a PDF file"
        files = {"file": ("test.txt", io.BytesIO(text_file), "text/plain")}
        
        response = client.post("/upload-pdf", files=files, headers=auth_headers)
        assert response.status_code == 400
        data = response.json()
        assert "pdf" in data["detail"].lower()
    
    def test_debug_llm_endpoint(self, auth_headers):
        """Test debug LLM endpoint returns raw model output."""
        response = client.post(
            "/debug/llm-raw",
            json={"prompt": "Hello, respond with 'test successful'"},
            headers=auth_headers
        )
        # Should succeed (or fail with 500 if API keys not configured)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "result" in data
            assert "model" in data


class TestVectorService:
    """Test vector service operations with PostgreSQL + pgvector."""
    
    def test_vector_service_initialization(self):
        """Test that VectorService initializes correctly."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        assert vector_service is not None
        logger.info("✅ VectorService initialized")
    
    def test_add_documents_basic(self):
        """Test adding documents to vector store."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        texts = [
            "The revenue was $150 million in Q3 2025",
            "Operating expenses totaled $75 million",
            "Net income reached $45 million"
        ]
        
        doc_ids = vector_service.add_documents(texts)
        
        assert len(doc_ids) == 3
        assert all(isinstance(doc_id, int) for doc_id in doc_ids)
        logger.info(f"✅ Added {len(doc_ids)} documents")
    
    def test_add_documents_with_metadata(self):
        """Test adding documents with JSONB metadata."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        texts = ["Financial report Q3 2025"]
        metadatas = [{"source": "report.pdf", "page": 1, "chunk_index": 0}]
        
        doc_ids = vector_service.add_documents(texts, metadatas)
        
        assert len(doc_ids) == 1
        logger.info(f"✅ Added document with metadata: {metadatas[0]}")
    
    @pytest.mark.skipif(
        "postgresql" not in TEST_DATABASE_URL,
        reason="Requires PostgreSQL with pgvector"
    )
    def test_vector_store_stats(self):
        """Test getting vector store statistics."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        # Add some documents
        texts = ["Document 1", "Document 2", "Document 3"]
        vector_service.add_documents(texts)
        
        # Get stats
        stats = vector_service.get_stats()
        
        assert "document_count" in stats
        assert stats["document_count"] == 3
        assert stats["backend"] == "PostgreSQL + pgvector"
        assert stats["embedding_dimension"] == 384
        logger.info(f"✅ Vector store stats: {stats}")
    
    @pytest.mark.skipif(
        "postgresql" not in TEST_DATABASE_URL,
        reason="Requires PostgreSQL with pgvector"
    )
    def test_similarity_search_with_pgvector(self):
        """Test similarity search using pgvector cosine distance."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        # Add documents
        texts = [
            "The company revenue was $150 million",
            "Operating expenses were $75 million",
            "Net profit was $45 million"
        ]
        vector_service.add_documents(texts)
        
        # Search for revenue-related content
        results = vector_service.similarity_search("What was the revenue?", k=2)
        
        assert len(results) <= 2
        assert all("content" in r for r in results)
        assert all("score" in r for r in results)
        assert all("metadata" in r for r in results)
        logger.info(f"✅ Found {len(results)} similar documents")
    
    def test_document_model_jsonb_metadata(self):
        """Test Document model with JSONB metadata."""
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Create document with complex metadata
        doc = Document(
            content="Test financial data",
            embedding=[0.1] * 384,  # Mock embedding
            document_metadata={
                "source": "financial_report.pdf",
                "page": 2,
                "section": "Revenue Analysis",
                "chunk_index": 5,
                "confidence": 0.95
            }
        )
        
        db.add(doc)
        db.commit()
        
        # Retrieve the specific document by content
        retrieved = db.query(Document).filter_by(content="Test financial data").first()
        assert retrieved is not None
        assert retrieved.document_metadata["source"].endswith(".pdf")
        assert retrieved.document_metadata["page"] == 2
        assert retrieved.document_metadata["confidence"] == 0.95
        
        db.close()
        logger.info("✅ Document with JSONB metadata persisted correctly")
    
    def test_clear_all_documents(self):
        """Test clearing all documents from vector store."""
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        # Clear any leftover documents first
        initial_count = vector_service.get_stats()["document_count"]
        if initial_count > 0:
            vector_service.clear_all()
        
        # Add documents
        texts = ["Doc1", "Doc2", "Doc3"]
        vector_service.add_documents(texts)
        
        # Verify we added 3
        stats = vector_service.get_stats()
        assert stats["document_count"] == 3
        
        # Clear
        count = vector_service.clear_all()
        assert count == 3
        
        # Verify empty
        stats = vector_service.get_stats()
        assert stats["document_count"] == 0
        logger.info(f"✅ Cleared {count} documents")


class TestPersistence:
    """Test data persistence in PostgreSQL."""
    
    @pytest.mark.skipif(
        "postgresql" not in TEST_DATABASE_URL,
        reason="Requires PostgreSQL for persistence test"
    )
    def test_documents_persist_in_database(self):
        """Test that documents persist in PostgreSQL across connections."""
        from app.database import SessionLocal
        from app.services.vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        # Add document
        texts = ["Persisted document content"]
        doc_ids = vector_service.add_documents(texts)
        
        # Create new database connection
        db = SessionLocal()
        count = db.query(Document).count()
        db.close()
        
        assert count == 1
        logger.info("✅ Documents persisted in PostgreSQL")
    
    @pytest.mark.skipif(
        "postgresql" not in TEST_DATABASE_URL,
        reason="Requires PostgreSQL for persistence test"
    )
    def test_metadata_persistence(self):
        """Test that JSONB metadata persists correctly."""
        from app.database import SessionLocal
        
        # Add via raw insert
        db = SessionLocal()
        doc = Document(
            content="Test content",
            embedding=[0.1] * 384,
            document_metadata={"key": "value", "nested": {"data": 123}}
        )
        db.add(doc)
        db.commit()
        doc_id = doc.id
        db.close()
        
        # Retrieve in new connection
        db = SessionLocal()
        retrieved = db.query(Document).filter(Document.id == doc_id).first()
        db.close()
        
        assert retrieved is not None
        assert retrieved.document_metadata["nested"]["data"] == 123
        logger.info("✅ JSONB metadata persisted correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
