"""
Hallucination client wrapper.
"""
from typing import Dict, Any
from cloud_api.client.base_client import BaseClient
from cloud_api.api_functions import score_hallucination_tokens

class HallucinationClient(BaseClient):
    """Client for Hallucination API endpoints"""
    
    def score_tokens(self, text: str, max_tokens: int = 256, temperature: float = 0.7) -> Dict[str, Any]:
        """Call cloud API to score tokens with probes (returns raw scores)"""
        return score_hallucination_tokens(text, max_tokens, temperature)







