"""
API Key Authentication Middleware

Provides secure API key validation with scopes (read/write permissions).
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings
from app.core.logger import setup_logger
from typing import Optional

logger = setup_logger()

# Header name for API key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyScope:
    """API Key permission scopes"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


def validate_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> dict:
    """
    Validate API key from request header.
    
    Args:
        api_key_header: API key from X-API-Key header
        
    Returns:
        dict: API key metadata with scope
        
    Raises:
        HTTPException: 401 if key is missing or invalid
    """
    if not api_key_header:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
        )
    
    # Validate against configured keys
    api_keys = settings.get_api_keys()
    
    if api_key_header not in api_keys:
        logger.warning(f"Invalid API key attempt: {api_key_header[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    # Get key metadata (scope)
    key_data = api_keys[api_key_header]
    logger.info(f"API key validated: {key_data.get('name', 'unknown')} (scope: {key_data.get('scope', 'read')})")
    
    return key_data


def require_scope(required_scope: str):
    """
    Dependency to check if API key has required scope.
    
    Usage:
        @router.post("/upload")
        async def upload(key_data: dict = Depends(require_scope(APIKeyScope.WRITE))):
            ...
    """
    async def scope_checker(key_data: dict = Security(validate_api_key)) -> dict:
        scope = key_data.get("scope", APIKeyScope.READ)
        
        # Admin has all permissions
        if scope == APIKeyScope.ADMIN:
            return key_data
        
        # Check if scope matches
        if scope != required_scope:
            logger.warning(f"Insufficient scope: {scope} (required: {required_scope})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}",
            )
        
        return key_data
    
    return scope_checker
