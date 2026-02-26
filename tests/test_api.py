import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.schemas.rag_schema import QuestionRequest


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Return authentication headers with mocked Firebase token"""
    return {"Authorization": "Bearer mock-firebase-token"}


@pytest.fixture(autouse=True)
def mock_firebase_auth():
    """Mock Firebase authentication for all tests"""
    with patch('app.core.security.verify_firebase_token') as mock_verify:
        # Return a mock user data dict that Firebase would return
        mock_verify.return_value = {
            'uid': 'test-user-123',
            'email': 'test@example.com',
            'email_verified': True
        }
        yield mock_verify


class TestAPIEndpoints:
    """Test suite for API endpoints"""

    def test_root_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "message" in data
        assert "endpoints" in data

    def test_root_endpoint_includes_docs(self, client):
        """Test that root endpoint provides docs URL"""
        response = client.get("/")
        data = response.json()
        
        assert "docs" in data
        assert data["docs"] == "/docs"
        assert "upload_pdf" in data["endpoints"]
        assert "ask_question" in data["endpoints"]

    @patch('app.api.routes.RAGService')
    @patch('app.api.routes.settings')
    def test_ask_question_success(self, mock_settings, mock_rag_service, client, auth_headers):
        """Test asking a question successfully"""
        # Arrange
        mock_settings.validate.return_value = None
        mock_rag_service.ask.return_value = {
            "answer": "The quarterly earnings were $100M",
            "model": "llama-3.1-8b-instant",
            "chunks": ["Q3 earnings: $100M"],
            "context": "Q3 earnings: $100M"
        }

        payload = {
            "question": "What are the quarterly earnings?"
        }

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "The quarterly earnings were $100M"
        assert data["model"] == "llama-3.1-8b-instant"
        assert len(data["chunks"]) == 1

    @patch('app.api.routes.settings')
    def test_ask_question_empty_question(self, mock_settings, client, auth_headers):
        """Test that empty questions are rejected"""
        # Arrange
        mock_settings.validate.return_value = None

        payload = {
            "question": "   "
        }

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400

    @patch('app.api.routes.RAGService')
    @patch('app.api.routes.settings')
    def test_ask_question_response_format(self, mock_settings, mock_rag_service, client, auth_headers):
        """Test that response follows QuestionResponse schema"""
        # Arrange
        mock_settings.validate.return_value = None
        mock_rag_service.ask.return_value = {
            "answer": "Test answer",
            "model": "test-model",
            "chunks": ["chunk1", "chunk2"],
            "context": "combined context"
        }

        payload = {"question": "test question"}

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "model" in data
        assert "chunks" in data
        assert "context" in data
        assert "chunk_count" in data

    @patch('app.api.routes.settings')
    def test_ask_question_missing_api_key(self, mock_settings, client, auth_headers):
        """Test that requests fail gracefully when API key is missing"""
        # Arrange
        mock_settings.validate.side_effect = ValueError("API key not configured")

        payload = {"question": "What are earnings?"}

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 500

    @patch('app.api.routes.RAGService')
    @patch('app.api.routes.settings')
    def test_upload_pdf_success(self, mock_settings, mock_rag_service, client, auth_headers):
        """Test successful PDF upload"""
        # Arrange
        mock_settings.validate.return_value = None
        mock_rag_service.process_document.return_value = None
        mock_rag_service.vector_store = MagicMock()
        mock_rag_service.vector_store.save.return_value = None

        pdf_content = b"%PDF-1.4\n test pdf content"
        
        # Act
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "indexed" in data.get("message", "").lower()

    @patch('app.api.routes.settings')
    def test_upload_non_pdf_file(self, mock_settings, client, auth_headers):
        """Test that non-PDF files are rejected"""
        # Arrange
        mock_settings.validate.return_value = None

        file_content = b"This is not a PDF"
        
        # Act
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.txt", file_content, "text/plain")},
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400

    @patch('app.api.routes.settings')
    @patch('app.api.routes.RAGService')
    def test_upload_empty_pdf(self, mock_rag_service, mock_settings, client, auth_headers):
        """Test that empty PDF files are rejected"""
        # Arrange
        mock_settings.validate.return_value = None

        # Act
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", b"", "application/pdf")},
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400

    @patch('app.api.routes.settings')
    @patch('app.api.routes.RAGService')
    def test_upload_pdf_processing_error(self, mock_rag_service, mock_settings, client, auth_headers):
        """Test error handling when PDF processing fails"""
        # Arrange
        mock_settings.validate.return_value = None
        mock_rag_service.process_document.side_effect = Exception("PDF processing failed")

        pdf_content = b"%PDF-1.4\n test pdf content"
        
        # Act
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 500

    @patch('app.api.routes.RAGService')
    @patch('app.api.routes.settings')
    def test_ask_question_with_multiple_chunks(self, mock_settings, mock_rag_service, client, auth_headers):
        """Test that chunk_count matches chunks array length"""
        # Arrange
        mock_settings.validate.return_value = None
        chunks = ["chunk1", "chunk2", "chunk3"]
        mock_rag_service.ask.return_value = {
            "answer": "Test answer",
            "model": "test-model",
            "chunks": chunks,
            "context": "combined context"
        }

        payload = {"question": "test question"}

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["chunk_count"] == 3
        assert len(data["chunks"]) == 3

    @patch('app.api.routes.settings')
    def test_check_api_key_validation(self, mock_settings, client, auth_headers):
        """Test that check_api_key is called on requests"""
        # Arrange
        mock_settings.validate.side_effect = ValueError("HF_TOKEN not found")

        payload = {"question": "test"}

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 500
        mock_settings.validate.assert_called()

    @patch('app.api.routes.RAGService')
    @patch('app.api.routes.settings')
    def test_model_indicator_in_response(self, mock_settings, mock_rag_service, client, auth_headers):
        """Test that model indicator is included in response"""
        # Arrange
        mock_settings.validate.return_value = None
        test_model = "llama-3.1-70b-versatile"
        mock_rag_service.ask.return_value = {
            "answer": "Test answer",
            "model": test_model,
            "chunks": [],
            "context": ""
        }

        payload = {"question": "test question"}

        # Act
        response = client.post("/ask", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == test_model
