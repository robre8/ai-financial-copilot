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

# Set Firebase mock credentials
if 'FIREBASE_SERVICE_ACCOUNT_JSON' not in os.environ:
    os.environ['FIREBASE_SERVICE_ACCOUNT_JSON'] = '{"type":"service_account","project_id":"test-project"}'

# Add backend directory to Python path so imports work from tests
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_init():
    """Mock Firebase Admin SDK initialization to prevent errors in CI/CD"""
    with patch('firebase_admin.initialize_app'):
        with patch('firebase_admin.get_app'):
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
