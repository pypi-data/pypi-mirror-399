"""
Configuration management for NeuronLens package.
Handles API URL, timeout, and environment variable settings.
"""
import os
import json
from pathlib import Path
from typing import Optional


def _get_config_file_path() -> Path:
    """Get path to neuronlens config.json file"""
    return Path(__file__).parent / "config.json"


def _load_config() -> dict:
    """Load configuration from config.json file"""
    config_file = _get_config_file_path()
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_default_api_url(api_key: Optional[str] = None) -> str:
    """
    Get default API URL based on whether API key is provided.
    When API key is provided, automatically detects ngrok URL from config file.
    
    Args:
        api_key: Optional API key. If provided, assumes cloud API via ngrok.
    
    Returns:
        API URL string
    """
    # If API key provided, automatically detect ngrok URL
    if api_key:
        # Priority 1: Config file (config.json in neuronlens directory)
        config = _load_config()
        api_url = config.get('api_url')
        if api_url and api_url != "https://your-ngrok-url.ngrok-free.dev":
            return api_url.rstrip('/')
        
        # Priority 2: Environment variable
        api_url = os.environ.get('NEURONLENS_API_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # Priority 3: CLOUD_API_URL (for backward compatibility)
        api_url = os.environ.get('CLOUD_API_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # Priority 4: Auto-detect ngrok URL from .ngrok_url file
        ngrok_file = Path(__file__).parent.parent.parent / ".ngrok_url"
        if ngrok_file.exists():
            return open(ngrok_file).read().strip()
        
        # Priority 5: Auto-detect from ngrok API
        try:
            import requests
            tunnels = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2).json().get("tunnels", [])
            if tunnels:
                return tunnels[0].get("public_url", "")
        except:
            pass
        
        # Priority 6: Environment variable API_URL
        api_url = os.environ.get('API_URL')
        if api_url:
            return api_url.rstrip('/')
        
        # If still no URL found, raise error
        raise ValueError(
            "API key provided but no API URL found. "
            "Please set api_url in cloud_api/neuronlens/config.json or set NEURONLENS_API_URL environment variable."
        )
    
    # No API key = local mode
    return "http://localhost:8000"


def get_api_timeout() -> int:
    """
    Get API timeout from config file, environment variable, or default.
    
    Returns:
        Timeout in seconds
    """
    # Priority 1: Config file
    config = _load_config()
    timeout = config.get('timeout')
    if timeout:
        return int(timeout)
    
    # Priority 2: Environment variable
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

