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

# Always set test database URL for testing (override any environment setting)
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Always set Firebase mock credentials - simple JSON that won't cause parsing errors
# The actual mock will prevent Firebase from being initialized anyway
os.environ['FIREBASE_SERVICE_ACCOUNT_JSON'] = '{}'

# Add backend directory to Python path so imports work from tests
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_init():
    """Mock Firebase Admin SDK BEFORE importing app to prevent initialization errors"""
    # Patch firebase_admin modules BEFORE app tries to import them
    with patch('firebase_admin.credentials.Certificate') as mock_cert:
        with patch('firebase_admin.initialize_app') as mock_init:
            with patch('firebase_admin.get_app') as mock_get_app:
                with patch('firebase_admin.auth') as mock_auth:
                    # Make sure Certificate returns a mock object
                    mock_cert.return_value = MagicMock()
                    # Make sure initialize_app doesn't fail
                    mock_init.return_value = MagicMock()
                    
                    # Setup get_app to return a mock app
                    mock_app = MagicMock()
                    mock_get_app.return_value = mock_app
                    
                    # Mock verify_id_token to return test user data
                    mock_auth.verify_id_token = MagicMock(return_value={
                        'uid': 'test-user-123',
                        'email': 'test@example.com',
                        'email_verified': True
                    })
                    
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
