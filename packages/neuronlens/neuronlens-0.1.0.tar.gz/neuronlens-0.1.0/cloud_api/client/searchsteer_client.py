"""
SearchSteer client wrapper.
"""
import numpy as np
from typing import List, Dict, Any
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import search_features, steer_features, extract_searchsteer_features

class SearchSteerClient(BaseClient):
    """Client for SearchSteer API endpoints"""
    
    def search_features(self, query: str, k: int = 10, layer: int = 16) -> List[Dict[str, Any]]:
        """Call cloud API to search features using semantic similarity"""
        return search_features(query, k, layer)
    
    def steer_features(self, prompt: str, features: List[Dict[str, Any]], model: str = "meta-llama/Llama-2-7b-hf") -> Dict[str, Any]:
        """Call cloud API to apply feature steering and generate text"""
        return steer_features(prompt, features, model)
    
    def extract_features(self, text: str, layer: int = 16) -> np.ndarray:
        """Call cloud API to extract SearchSteer SAE features"""
        return extract_searchsteer_features(text, layer)



