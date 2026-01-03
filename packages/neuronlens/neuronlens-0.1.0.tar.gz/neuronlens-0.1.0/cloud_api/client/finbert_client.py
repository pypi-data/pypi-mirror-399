"""
FinBERT client wrapper.
"""
import numpy as np
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import extract_finbert_features

class FinBERTClient(BaseClient):
    """Client for FinBERT API endpoints"""
    
    def extract_features(self, text: str, layer: int = 10) -> np.ndarray:
        """Call cloud API to extract FinBERT SAE features"""
        return extract_finbert_features(text, layer)







