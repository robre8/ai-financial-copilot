"""
Pytest configuration and fixtures for the entire project
"""
import sys
import os

# Add backend directory to Python path so imports work from tests
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
