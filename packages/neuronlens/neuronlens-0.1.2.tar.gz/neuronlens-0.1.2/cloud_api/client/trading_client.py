"""
Trading client wrapper.
"""
import numpy as np
from typing import Optional, Dict, Any
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import extract_trading_features, compute_trading_signal, get_trading_feature_labels

class TradingClient(BaseClient):
    """Client for Trading API endpoints"""
    
    def extract_features(self, text: str, ticker: Optional[str] = None, layer: int = 19) -> np.ndarray:
        """Call cloud API to extract trading SAE features"""
        return extract_trading_features(text, ticker, layer)
    
    def compute_signal(self, features: np.ndarray, ticker: str) -> Dict[str, Any]:
        """Compute trading signal (NOTE: Analysis logic should stay local)"""
        return compute_trading_signal(features, ticker)
    
    def get_feature_labels(self) -> Dict[int, str]:
        """Get trading feature labels"""
        return get_trading_feature_labels()







