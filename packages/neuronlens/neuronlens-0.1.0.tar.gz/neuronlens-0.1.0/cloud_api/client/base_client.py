"""
Base client with common functionality for all module clients.
"""
import requests
from typing import Optional, Dict, Any
from cloud_api.config import get_api_url, get_api_timeout, get_retry_attempts

class BaseClient:
    """Base client class with common HTTP request handling"""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize base client.
        
        Args:
            api_url: Optional API URL. If None, uses centralized config.
        """
        self.api_url = api_url.rstrip('/') if api_url else get_api_url()
        self.timeout = get_api_timeout()
        self.retry_attempts = get_retry_attempts()
    
    def _post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request with retry logic"""
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(url, json=json_data, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)
        
        raise RuntimeError(f"Failed to make request after {self.retry_attempts} attempts")
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request with retry logic"""
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise
                import time
                time.sleep(2 ** attempt)
        
        raise RuntimeError(f"Failed to make request after {self.retry_attempts} attempts")







