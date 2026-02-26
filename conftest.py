"""
Pytest configuration and fixtures for the entire project
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# ============================================================================
# CRITICAL: Configure environment BEFORE any app imports
# ============================================================================

# Set test database URL if not already set
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Set Firebase mock credentials with all required fields
if 'FIREBASE_SERVICE_ACCOUNT_JSON' not in os.environ:
    os.environ['FIREBASE_SERVICE_ACCOUNT_JSON'] = '''{
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key-id",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEA2a2rwplBCXWGt8/VnvV1bEuQPAJK/32yUOqP6vD9hIh+d57\\nzP5xJCt7pYX2EYFOa3cLqRltWp7v0NPRz/0sB0MQMsZ2F8JKg45XQBJ7PZD9C8nE\\n5gKhMGVRrN/Cz9XqlG5F1w6H6FXMmm8VaqFp3qKA0YCOVp9qF1qL0Y0CAwEAAQKC\\nAQAkLvCQz0oYrj5+3u5qJ+5RgKqLvLvf4+/j0mFJu/W9vL8p5v0AWqW0+VJW8vZN\\npMQEb3fzPJj9RlNXvKnUOj1k7oKz1vqN1vVEqR5kPZHZcKw0Gy2U+OYVqJJ3S7kd\\nrSKwhGK5f9ZqDQXG1kGSwLm8KzGPtqYLqYhBNZECgYEA73pBCwYQVrV0LQEjNnWW\\ndhNZVlZ9kHPxNlm6a1Tc9y0xqPYCW8BqDDXJaLqW6vJQYKPMI/EvPhC3eCvWnBkC\\nIxECgYEA5rU0q4yEFvEXFBb7Z0CWLJS8o7eZYRQ8u5bFGJ/GhVmvL5U3FZSZccLD\\n+dqMlDw5VZBLZGBn5YMXfVMeNJkCgYBDqM4mRGMvn0F2I2h9S/5Ep5X8F5nkW1UX\\nYRRVr+Rr6/4F2nj0G0OwZLGEF7YB0Y9lU5QvF4VYPgKB0V9DQQJBAIq3vLM9y3fN\\nGo3kKLgaHMBpGQVHEIQ6mz/Z+Kd4A7Uk1/Fs2QECgYEAwdqFqPZ1V3N5QoC/HWNE\\nKBJNl3M7P8SmGQQg5DI80L0=\\n-----END RSA PRIVATE KEY-----\\n",
        "client_email": "firebase-test@test-project.iam.gserviceaccount.com",
        "client_id": "12345678",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test.iam.gserviceaccount.com"
    }'''

# Add backend directory to Python path so imports work from tests
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_init():
    """Mock Firebase Admin SDK initialization to prevent errors in CI/CD"""
    with patch('firebase_admin.credentials.Certificate') as mock_cert:
        with patch('firebase_admin.initialize_app') as mock_init:
            with patch('firebase_admin.get_app') as mock_get_app:
                with patch('firebase_admin.auth') as mock_auth:
                    # Mock certificate creation
                    mock_cert.return_value = MagicMock()
                    
                    # Mock the verify_id_token to return test user data
                    mock_auth.verify_id_token.return_value = {
                        'uid': 'test-user-123',
                        'email': 'test@example.com',
                        'email_verified': True
                    }
                    yield


@pytest.fixture(scope="session", autouse=True)
def mock_database_init():
    """Mock database initialization to prevent real database connections"""
    with patch('app.database.init_db'):
        yield


@pytest.fixture(autouse=True)
def mock_firebase_verify(monkeypatch):
    """Mock Firebase token verification for all tests"""
    def mock_verify_token(credentials):
        # Return mock user data
        return {
            'uid': 'test-user-123',
            'email': 'test@example.com',
            'email_verified': True
        }
    
    # Patch the verify function in security module
    import app.core.security
    monkeypatch.setattr(app.core.security, 'verify_firebase_token', mock_verify_token)
