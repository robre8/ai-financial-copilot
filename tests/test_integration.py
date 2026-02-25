"""
Integration Tests - Test full RAG pipeline with FastAPI TestClient
Tests document upload, vector storage, and query answering end-to-end.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io

from app.main import app
from app.models import Base, Document
from app.database import get_db
from app.core.config import settings

# Test database URL (use in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine and session
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
        assert response.status_code == 403  # Forbidden without auth
    
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
        assert response.status_code == 403  # Forbidden without auth
    
    def test_ask_question_with_auth_no_documents(self, auth_headers):
        """Test asking a question when no documents are indexed."""
        response = client.post(
            "/ask",
            json={"question": "What is the revenue?"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # Should indicate no documents found
        assert "no relevant information" in data["answer"].lower() or "not found" in data["answer"].lower()
    
    @pytest.mark.skip(reason="Requires actual database with pgvector - SQLite doesn't support vector operations")
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
    """Test vector service operations (unit tests)."""
    
    @pytest.mark.skip(reason="Requires PostgreSQL with pgvector")
    def test_add_and_search_documents(self):
        """Test adding documents and searching for similar ones."""
        from app.services.vector_service import VectorService
        
        vector_service = VectorService()
        
        # Add test documents
        texts = [
            "The company revenue was $150 million in Q3 2025.",
            "Net income reached $45 million this quarter.",
            "Operating expenses totaled $75 million."
        ]
        doc_ids = vector_service.add_documents(texts)
        
        assert len(doc_ids) == 3
        
        # Search for similar documents
        results = vector_service.similarity_search("What was the revenue?", k=2)
        
        assert len(results) <= 2
        assert results[0]["content"] in texts
        assert "score" in results[0]
    
    @pytest.mark.skip(reason="Requires PostgreSQL with pgvector")
    def test_vector_service_stats(self):
        """Test getting vector store statistics."""
        from app.services.vector_service import VectorService
        
        vector_service = VectorService()
        stats = vector_service.get_stats()
        
        assert "document_count" in stats
        assert "backend" in stats
        assert stats["backend"] == "PostgreSQL + pgvector"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
