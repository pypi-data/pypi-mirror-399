"""
Hallucination API router.
Handles hallucination probe scoring.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import torch
import numpy as np
import os
import json

from cloud_api.services.model_loader import load_transformers_model, get_device

router = APIRouter(prefix="/hallucination", tags=["Hallucination"])

# Global model cache
_hallucination_model = None
_hallucination_tokenizer = None
_hallucination_probes = {}

# Configuration
HALLUCINATION_MODEL_PATH = os.getenv("HALLUCINATION_MODEL_PATH", "meta-llama/Llama-2-7b-hf")
PROBE_PATH = os.getenv("PROBE_PATH", "/app/probes")

class ScoreTokensRequest(BaseModel):
    text: str
    max_tokens: int = 256
    temperature: float = 0.7

class LoadProbesRequest(BaseModel):
    probe_path: Optional[str] = None

@router.post("/score_tokens")
async def score_tokens(request: ScoreTokensRequest):
    """Score tokens with probes (returns raw scores)"""
    global _hallucination_model, _hallucination_tokenizer, _hallucination_probes
    
    try:
        if _hallucination_model is None:
            _hallucination_model, _hallucination_tokenizer = load_transformers_model(HALLUCINATION_MODEL_PATH)
        
        device = get_device()
        
        # Tokenize
        tokens = _hallucination_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=request.max_tokens
        ).to(device)
        
        # Generate and extract hidden states (simplified)
        with torch.no_grad():
            outputs = _hallucination_model(**tokens, output_hidden_states=True)
            # Use last layer hidden states
            hidden_states = outputs.hidden_states[-1]
        
        # Apply probes if loaded
        scores = {}
        if _hallucination_probes:
            # Apply probe scoring (simplified - actual implementation would use probe models)
            for probe_name, probe_model in _hallucination_probes.items():
                if hasattr(probe_model, '__call__'):
                    probe_scores = probe_model(hidden_states)
                    scores[probe_name] = probe_scores.cpu().numpy().tolist()
        else:
            # Fallback: return hidden state norms as scores
            scores["default"] = hidden_states.norm(dim=-1).cpu().numpy().tolist()
        
        return {
            "scores": scores,
            "token_ids": tokens["input_ids"][0].cpu().numpy().tolist()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring tokens: {str(e)}")

@router.post("/load_probes")
async def load_probes(request: LoadProbesRequest):
    """Load probe models"""
    global _hallucination_probes
    
    try:
        probe_path = request.probe_path or PROBE_PATH
        
        # Load probe models (simplified - actual implementation would load from files)
        # This is a placeholder - actual probe loading would depend on probe format
        if os.path.exists(probe_path):
            # Try to load probe files
            for file in os.listdir(probe_path):
                if file.endswith('.pt') or file.endswith('.pth'):
                    probe_file = os.path.join(probe_path, file)
                    try:
                        probe_state = torch.load(probe_file, map_location=get_device())
                        probe_name = os.path.splitext(file)[0]
                        _hallucination_probes[probe_name] = probe_state
                    except Exception as e:
                        print(f"Warning: Could not load probe {file}: {e}")
        
        return {
            "status": "success",
            "message": f"Loaded {len(_hallucination_probes)} probes",
            "probes": list(_hallucination_probes.keys())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading probes: {str(e)}")







