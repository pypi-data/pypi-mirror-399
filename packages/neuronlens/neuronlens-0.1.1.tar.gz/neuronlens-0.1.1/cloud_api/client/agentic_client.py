"""
AgenticTracing client wrapper.
"""
import numpy as np
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import extract_agent_features, generate_agent_response

class AgenticClient(BaseClient):
    """Client for AgenticTracing API endpoints"""
    
    def extract_features(self, text: str, layer: int = 19) -> np.ndarray:
        """Call cloud API to extract agent SAE features"""
        return extract_agent_features(text, layer)
    
    def generate_response(self, query: str) -> str:
        """Call cloud API to generate agent response"""
        return generate_agent_response(query)







