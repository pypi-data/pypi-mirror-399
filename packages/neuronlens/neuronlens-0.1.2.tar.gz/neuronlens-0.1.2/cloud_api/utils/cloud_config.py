"""
Centralized cloud API configuration for InterpUseCases_v2
Reads from environment variables, config file, or uses defaults
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional

def get_cloud_api_config() -> Dict:
    """
    Get cloud API config with priority: env var > config file > defaults
    
    Returns:
        Dictionary with keys: use_cloud_api, api_url, timeout, retry_attempts
    """
    # Priority 1: Environment variables
    use_cloud_api_env = os.getenv('USE_CLOUD_API', '').lower()
    use_cloud_api = use_cloud_api_env == 'true' if use_cloud_api_env else None
    api_url = os.getenv('CLOUD_API_URL')
    
    # Priority 2: Config file (only if env vars not set)
    config_file = Path(__file__).parent.parent / 'cloud_config.json'
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                if use_cloud_api is None:  # Only use file if env not set
                    use_cloud_api = config.get('use_cloud_api', False)
                if not api_url:
                    api_url = config.get('api_url')
        except Exception as e:
            print(f"Warning: Could not read cloud_config.json: {e}")
    
    # Priority 3: Defaults
    return {
        'use_cloud_api': use_cloud_api if use_cloud_api is not None else False,
        'api_url': api_url,
        'timeout': 30,
        'retry_attempts': 3
    }

def get_use_cloud_api(default: Optional[bool] = None) -> bool:
    """
    Get use_cloud_api flag from central config
    
    Args:
        default: If provided, this takes precedence (for function parameter override)
    
    Returns:
        Boolean indicating whether to use cloud API
    """
    if default is not None:
        return default
    config = get_cloud_api_config()
    return config['use_cloud_api']

def get_api_url(default: Optional[str] = None) -> Optional[str]:
    """
    Get API URL from central config
    
    Args:
        default: If provided, this takes precedence (for function parameter override)
    
    Returns:
        API URL string or None
    """
    if default is not None:
        return default
    config = get_cloud_api_config()
    return config['api_url']

