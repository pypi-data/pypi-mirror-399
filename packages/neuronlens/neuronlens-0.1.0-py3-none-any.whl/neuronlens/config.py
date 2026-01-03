"""
Configuration management for NeuronLens package.
Handles API URL, timeout, and environment variable settings.
"""
import os
from typing import Optional


def get_default_api_url(api_key: Optional[str] = None) -> str:
    """
    Get default API URL based on whether API key is provided.
    
    Args:
        api_key: Optional API key. If provided, assumes cloud API.
    
    Returns:
        API URL string
    """
    # If API key provided, check for cloud API URL
    if api_key:
        # Priority 1: Environment variable
        api_url = os.environ.get('NEURONLENS_API_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # Priority 2: CLOUD_API_URL (for backward compatibility)
        api_url = os.environ.get('CLOUD_API_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # Priority 3: Default cloud API URL (should be set by user)
        # Return None to indicate user should provide it
        return None
    
    # No API key = local mode
    return "http://localhost:8000"


def get_api_timeout() -> int:
    """
    Get API timeout from environment variable or default.
    
    Returns:
        Timeout in seconds
    """
    return int(os.environ.get('NEURONLENS_API_TIMEOUT', '30'))


def get_api_key_from_env() -> Optional[str]:
    """
    Get API key from environment variable.
    
    Returns:
        API key string or None
    """
    # Check NEURONLENS_API_KEY first
    api_key = os.environ.get('NEURONLENS_API_KEY')
    if api_key:
        return api_key
    
    # Fallback to API_KEY for backward compatibility
    return os.environ.get('API_KEY')

