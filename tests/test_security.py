"""
Simple Security Tests - Firebase Auth validation
Tests basic authentication with mocked Firebase tokens
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import verify_firebase_token
from fastapi import HTTPException


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_dependencies():
    """Reset dependency overrides between tests"""
    yield
    # Clear all overrides after test
    app.dependency_overrides.clear()


class TestFirebaseAuthentication:
    """Test Firebase authentication is required for protected endpoints"""

    def test_ask_requires_auth(self, client):
        """Test /ask requires Firebase token"""
        payload = {"question": "What are the earnings?"}
        response = client.post("/ask", json=payload)
        # Should return 401 Unauthorized when no Bearer token provided
        assert response.status_code == 401
    
    def test_upload_requires_auth(self, client):
        """Test /upload-pdf requires Firebase token"""
        response = client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", b"fake pdf")}
        )
        assert response.status_code == 401
    
    def test_analyze_requires_auth(self, client):
        """Test /analyze requires Firebase token"""
        payload = {"question": "Analyze this"}
        response = client.post("/analyze", json=payload)
        assert response.status_code == 401
    
    def test_valid_token_passes_auth(self, client):
        """Test valid Firebase token allows access"""
        def mock_verify():
            return {
                'uid': 'test-user',
                'email': 'test@example.com',
                'email_verified': True
            }
        
        app.dependency_overrides[verify_firebase_token] = mock_verify
        
        with patch('app.services.rag_service.RAGService.ask') as mock_ask:
            mock_ask.return_value = {
                "answer": "test answer",
                "model": "test",
                "chunks": [],
                "context": ""
            }
            
            # Should not fail with 401/403
            payload = {"question": "Test"}
            headers = {"Authorization": "Bearer valid-token"}
            response = client.post("/ask", json=payload, headers=headers)
            
            # As long as it's not auth error, we're good
            assert response.status_code != 403
            assert response.status_code != 401
    
    def test_invalid_token_rejected(self, client):
        """Test invalid/missing Firebase token is rejected"""
        def mock_verify_fail():
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
        
        app.dependency_overrides[verify_firebase_token] = mock_verify_fail
        
        payload = {"question": "Test"}
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/ask", json=payload, headers=headers)
        
        # Should return 401 when token is invalid
        assert response.status_code == 401


class TestRootEndpoint:
    """Test that root endpoint is publicly accessible"""
    
    def test_root_no_auth_required(self, client):
        """Test root endpoint doesn't require authentication"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"
