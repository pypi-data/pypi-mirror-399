"""
CoT Reasoning client wrapper.
"""
import numpy as np
from typing import Optional
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import extract_cot_features, generate_cot_text

class CoTClient(BaseClient):
    """Client for CoT Reasoning API endpoints"""
    
    def generate_cot(self, prompt: str, max_new_tokens: int = 2048) -> str:
        """Call cloud API to generate CoT text (model inference only)"""
        return generate_cot_text(prompt, max_new_tokens)
    
    def extract_features(self, text: str, layer: int = 28, trim_ratio: float = 0.0) -> np.ndarray:
        """Call cloud API to extract SAE features (returns raw numpy array)"""
        return extract_cot_features(text, layer, trim_ratio)







