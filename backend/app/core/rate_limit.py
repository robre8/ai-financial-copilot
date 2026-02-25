"""
Rate Limiting Configuration

Uses slowapi for request rate limiting per API key.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.core.logger import setup_logger

logger = setup_logger()


def get_api_key_identifier(request: Request) -> str:
    """
    Extract API key from request for rate limiting.
    Falls back to IP address if no API key present.
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # Use first 8 chars of API key as identifier
        return f"key:{api_key[:8]}"
    # Fallback to IP address
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_api_key_identifier,
    default_limits=["10/minute"],  # Default: 10 requests per minute
    storage_uri="memory://",  # In-memory storage (use Redis in production)
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting configured: 10 requests/minute per API key")
