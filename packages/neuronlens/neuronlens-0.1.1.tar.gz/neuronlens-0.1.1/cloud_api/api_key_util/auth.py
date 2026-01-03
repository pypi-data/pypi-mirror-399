"""
API Key Authentication Middleware for FastAPI.
Validates API keys from X-API-Key header or api_key query parameter.
"""
import os
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from cloud_api.api_key_util.db import validate_api_key

logger = logging.getLogger(__name__)

# Endpoints that don't require authentication
PUBLIC_ENDPOINTS = ["/", "/health", "/ping", "/docs", "/openapi.json", "/redoc"]

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to authenticate requests using API keys."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.auth_enabled = os.environ.get("API_AUTH_ENABLED", "true").lower() == "true"
        logger.info(f"API Key Authentication: {'ENABLED' if self.auth_enabled else 'DISABLED'}")
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication if disabled
        if not self.auth_enabled:
            return await call_next(request)
        
        # Skip authentication for public endpoints
        if request.url.path in PUBLIC_ENDPOINTS:
            return await call_next(request)
        
        # Extract API key from header (preferred) or query parameter
        api_key = None
        
        # Try X-API-Key header first
        api_key = request.headers.get("X-API-Key")
        
        # Fallback to query parameter
        if not api_key:
            api_key = request.query_params.get("api_key")
        
        # Check if API key is provided
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing API Key", "detail": "Please provide an API key via X-API-Key header or api_key query parameter"}
            )
        
        # Validate API key
        if not validate_api_key(api_key):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or Inactive API Key", "detail": "The provided API key is invalid, expired, or disabled"}
            )
        
        # API key is valid, proceed with request
        response = await call_next(request)
        return response


