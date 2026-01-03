"""
API Client for NeuronLens package.
Wraps HTTP requests to automatically inject API keys.
"""
import requests
from typing import Optional, Dict, Any
from contextlib import contextmanager


class APIClient:
    """
    HTTP client that automatically injects API key headers.
    Uses context manager to temporarily patch requests.post in the cloud_api module.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            api_key: Optional API key to inject in requests
        """
        self.api_key = api_key
        self._original_post = None
    
    def _patched_post(self, url: str, json: Optional[Dict[str, Any]] = None, 
                     headers: Optional[Dict[str, Any]] = None, 
                     timeout: Optional[int] = None, **kwargs) -> requests.Response:
        """
        Patched version of requests.post that injects API key.
        
        Args:
            url: Request URL
            json: JSON payload
            headers: Request headers (API key will be added)
            timeout: Request timeout
            **kwargs: Additional arguments for requests.post
        
        Returns:
            Response object
        """
        # Prepare headers
        if headers is None:
            headers = {}
        
        # Inject API key if available
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        # Make request using original requests.post (stored in self._original_post)
        return self._original_post(
            url,
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
    
    @contextmanager
    def patch_requests(self):
        """
        Context manager to temporarily patch requests.post globally.
        This allows base functions in cloud_api.api_functions to use the patched version.
        """
        import requests as requests_module
        
        # Store original
        self._original_post = requests_module.post
        
        # Patch requests.post globally (since api_functions imports it at module level)
        requests_module.post = self._patched_post
        
        try:
            yield
        finally:
            # Restore original
            if self._original_post is not None:
                requests_module.post = self._original_post
                self._original_post = None

