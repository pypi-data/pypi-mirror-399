"""
NeuronLens Engine class.
Wraps all frontend functions from api_functions.py with API key management.
Works standalone when cloud_api is not available (PyPI installation).
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Add cloud_api parent directory to path so we can import from it
# neuronlens is in cloud_api/neuronlens, so parent.parent is InterpUseCases_v2
_interp_dir = Path(__file__).parent.parent.parent
if str(_interp_dir) not in sys.path:
    sys.path.insert(0, str(_interp_dir))

from neuronlens.config import get_default_api_url, get_api_timeout, get_api_key_from_env
from neuronlens.api_client import APIClient

# Try to import base functions from cloud_api (for local development)
# If not available, we'll make HTTP requests directly (for PyPI installation)
_USE_CLOUD_API_FUNCTIONS = False
try:
    from cloud_api.api_functions import (
        analyze_agent_query as _analyze_agent_query,
        analyze_hallucination as _analyze_hallucination,
        analyze_slm_sentiment as _analyze_slm_sentiment,
        compare_probe_sae as _compare_probe_sae,
        extract_trading_signals as _extract_trading_signals,
        backtest_strategy as _backtest_strategy,
        analyze_reasoning as _analyze_reasoning,
        search_features as _search_features,
        steer_features as _steer_features,
    )
    _USE_CLOUD_API_FUNCTIONS = True
except ImportError:
    # cloud_api not available - will use direct HTTP requests
    _USE_CLOUD_API_FUNCTIONS = False
    import requests


class Engine:
    """
    NeuronLens Engine for accessing interpretability analysis functions.
    
    Usage:
        # With API key (cloud mode)
        engine = Engine(api_key="nlive_your_key")
        result = engine.analyze_agent_query("Get Tesla stock price")
        
        # Without API key (local mode)
        engine = Engine()
        result = engine.analyze_agent_query("Get Tesla stock price")
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize NeuronLens Engine.
        
        Args:
            api_key: Optional API key. If provided, uses cloud API.
                    If None, checks NEURONLENS_API_KEY environment variable.
            api_url: Optional API URL. If None, uses default based on api_key.
                    For cloud mode, should be the cloud API URL.
                    For local mode, defaults to http://localhost:8000
        """
        # Get API key from parameter or environment
        if api_key is None:
            api_key = get_api_key_from_env()
        self.api_key = api_key
        
        # Determine API URL
        if api_url is None:
            api_url = get_default_api_url(self.api_key)
            if api_url is None and self.api_key:
                raise ValueError(
                    "API key provided but no API URL found. "
                    "Please provide api_url parameter or set NEURONLENS_API_URL environment variable."
                )
        
        self.api_url = api_url
        self.timeout = get_api_timeout()
        
        # Create API client for request injection
        self._api_client = APIClient(api_key=self.api_key)
    
    def _call_with_api_key(self, func, *args, **kwargs):
        """
        Call a function with API key injection via requests.post patching.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments (api_url will be set if not provided)
        
        Returns:
            Function result
        """
        # Set api_url if not provided
        if 'api_url' not in kwargs:
            kwargs['api_url'] = self.api_url
        
        # If using cloud_api functions, patch requests.post to inject API key
        if _USE_CLOUD_API_FUNCTIONS:
            with self._api_client.patch_requests():
                return func(*args, **kwargs)
        else:
            # Direct HTTP request - API key already injected via api_client
            return func(*args, **kwargs)
    
    def _make_request(self, endpoint: str, json_data: dict) -> dict:
        """
        Make HTTP request directly to API endpoint with API key injection.
        Used when cloud_api is not available (PyPI installation).
        
        Args:
            endpoint: API endpoint path (e.g., "/slm_lens")
            json_data: Request JSON data
        
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.api_url}{endpoint}"
        headers = {}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        response = requests.post(url, json=json_data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def analyze_agent_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Analyze agent query with tool-intent tracing and R/A/G alignment.
        
        Args:
            query: User query to analyze
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with alignment_status, tool_called, intent_scores, top_features, etc.
        """
        return self._call_with_api_key(_analyze_agent_query, query, **kwargs)
    
    def analyze_hallucination(self, prompt: str, max_tokens: int = 256, 
                             temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Analyze hallucination with token-level scoring.
        
        Args:
            prompt: Prompt to analyze
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with token_details, hallucination scores, etc.
        """
        return self._call_with_api_key(
            _analyze_hallucination, 
            prompt, 
            max_tokens=max_tokens, 
            temperature=temperature,
            **kwargs
        )
    
    def analyze_slm_sentiment(self, text: str, top_n: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Analyze sentiment using SLM Lens with SAE feature attribution.
        
        Args:
            text: Text to analyze
            top_n: Number of top features to return
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with sentiment (predicted_label, confidence, probabilities) and top_features
        """
        if _USE_CLOUD_API_FUNCTIONS:
            return self._call_with_api_key(
                _analyze_slm_sentiment,
                text,
                top_n=top_n,
                **kwargs
            )
        else:
            # Direct HTTP request
            return self._make_request(
                "/slm_lens",
                {"action": "analyze_sentiment", "text": text, "top_n": top_n, "use_cloud": False}
            )
    
    def compare_probe_sae(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Compare probe-based vs SAE-based sentiment analysis.
        
        Args:
            text: Text to analyze
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with probe and SAE comparison results
        """
        return self._call_with_api_key(_compare_probe_sae, text, **kwargs)
    
    def extract_trading_signals(self, text: str, ticker: str, **kwargs) -> Dict[str, Any]:
        """
        Extract trading signals from news text.
        
        Args:
            text: News text to analyze
            ticker: Stock ticker symbol
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with extracted signals
        """
        return self._call_with_api_key(
            _extract_trading_signals,
            text,
            ticker,
            **kwargs
        )
    
    def backtest_strategy(self, ticker: str, signal_name: str, long_thr: float, 
                         short_thr: float, holding_days: int = 1, **kwargs) -> Dict[str, Any]:
        """
        Backtest a threshold-based trading strategy.
        
        Args:
            ticker: Stock ticker symbol
            signal_name: Name of the signal to use
            long_thr: Long threshold
            short_thr: Short threshold
            holding_days: Number of days to hold positions
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with equity_curve and metrics
        """
        return self._call_with_api_key(
            _backtest_strategy,
            ticker,
            signal_name,
            long_thr,
            short_thr,
            holding_days=holding_days,
            **kwargs
        )
    
    def analyze_reasoning(self, prompt: str, trim_ratio: float = 0.0, 
                          max_new_tokens: int = 2048, **kwargs) -> Dict[str, Any]:
        """
        Analyze reasoning with CoT faithfulness analysis.
        
        Args:
            prompt: Prompt to analyze
            trim_ratio: Ratio to trim from prompt
            max_new_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with reasoning analysis results
        """
        return self._call_with_api_key(
            _analyze_reasoning,
            prompt,
            trim_ratio=trim_ratio,
            max_new_tokens=max_new_tokens,
            **kwargs
        )
    
    def search_features(self, query: str, k: int = 10, layer: int = 16, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for features using semantic similarity.
        
        Args:
            query: Search query
            k: Number of features to return
            layer: Layer to search in
            **kwargs: Additional arguments passed to base function
        
        Returns:
            List of dictionaries with feature_id, score, and label
        """
        return self._call_with_api_key(
            _search_features,
            query,
            k=k,
            layer=layer,
            **kwargs
        )
    
    def steer_features(self, prompt: str, features: List[Dict[str, Any]], 
                      model: str = "meta-llama/Llama-2-7b-hf", **kwargs) -> Dict[str, Any]:
        """
        Apply feature steering and generate text.
        
        Args:
            prompt: Prompt to generate from
            features: List of feature dictionaries with "id" and "magnitude" keys
                     Magnitude range: -1.0 to +1.0 (positive = steer towards, negative = steer away)
            model: Model to use for generation
            **kwargs: Additional arguments passed to base function
        
        Returns:
            Dictionary with success, original_text, and steered_text
        """
        return self._call_with_api_key(
            _steer_features,
            prompt,
            features,
            model=model,
            **kwargs
        )

