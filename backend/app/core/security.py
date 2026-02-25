"""
API Key Authentication Middleware

Provides secure API key validation with scopes (read/write permissions).
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logger import setup_logger
from typing import Optional
import json
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

logger = setup_logger()

# Header name for API key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
BEARER_AUTH = HTTPBearer(auto_error=False)


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


def _init_firebase():
    if firebase_admin._apps:
        return

    service_account_json = settings.FIREBASE_SERVICE_ACCOUNT_JSON
    if not service_account_json:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_SERVICE_ACCOUNT_JSON is missing",
        )

    try:
        credentials_info = json.loads(service_account_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FIREBASE_SERVICE_ACCOUNT_JSON must be valid JSON",
        )

    cred = credentials.Certificate(credentials_info)
    firebase_admin.initialize_app(cred)


def verify_firebase_token(
    credentials_data: HTTPAuthorizationCredentials = Security(BEARER_AUTH),
) -> dict:
    if not credentials_data or credentials_data.scheme.lower() != "bearer":
        logger.warning("Missing Bearer token in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token. Include 'Authorization: Bearer <token>' header.",
        )

    _init_firebase()

    try:
        decoded_token = firebase_auth.verify_id_token(credentials_data.credentials)
        return decoded_token
    except Exception:
        logger.warning("Invalid Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


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
