"""
FinBERT API router.
Handles FinBERT SAE feature extraction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch
import numpy as np
import os

try:
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae
    from cloud_api.utils.serialization import serialize_array
except ImportError:
    # Fallback for when running from cloud_api directory
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae
    from cloud_api.utils.serialization import serialize_array

router = APIRouter(prefix="/finbert", tags=["FinBERT"])

# Global model cache
_finbert_model = None
_finbert_tokenizer = None
_finbert_sae = None
_finbert_config = None

# Configuration
FINBERT_MODEL_PATH = os.getenv("FINBERT_MODEL_PATH", "ProsusAI/finbert")
# Use local cloud_api paths (matching Docker /workspace/sae_models/ structure)
_default_sae_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sae_models", "finbert")
_default_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "finbert_sae_config.json")
FINBERT_SAE_PATH = os.getenv("FINBERT_SAE_PATH", _default_sae_path)
FINBERT_CONFIG_PATH = os.getenv("FINBERT_CONFIG_PATH", _default_config_path)
FINBERT_LAYER = int(os.getenv("FINBERT_LAYER", "10"))

class ExtractFeaturesRequest(BaseModel):
    text: str
    layer: int = 10

class LoadModelsRequest(BaseModel):
    model_path: Optional[str] = None
    sae_path: Optional[str] = None
    config_path: Optional[str] = None

@router.post("/extract_features")
async def extract_features(request: ExtractFeaturesRequest):
    """Extract FinBERT SAE features"""
    global _finbert_model, _finbert_tokenizer, _finbert_sae, _finbert_config
    
    try:
        if _finbert_model is None:
            _finbert_model, _finbert_tokenizer = load_transformers_model(
                FINBERT_MODEL_PATH, output_hidden_states=True
            )
        
        if _finbert_sae is None:
            _finbert_sae, _finbert_config = load_sae(FINBERT_SAE_PATH, FINBERT_CONFIG_PATH)
        
        device = get_device()
        
        # Tokenize
        tokens = _finbert_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(device)
        
        # Get hidden states
        with torch.no_grad():
            outputs = _finbert_model(**tokens, output_hidden_states=True)
            hidden_states = outputs.hidden_states[request.layer]
        
        # Encode through SAE
        if hasattr(_finbert_sae, 'encode'):
            # Flatten and encode
            flat = hidden_states.reshape(-1, hidden_states.shape[-1])
            feats = _finbert_sae.encode(flat.to(_finbert_sae.encoder.weight.dtype))
            mean_feats = feats.mean(dim=0).detach().cpu().float().numpy()
        else:
            # Fallback: return mean hidden states
            mean_feats = hidden_states.mean(dim=1).squeeze().cpu().numpy()
        
        features_serialized = serialize_array(mean_feats)
        return {"features": features_serialized}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

@router.post("/load_models")
async def load_models(request: LoadModelsRequest):
    """Load FinBERT models"""
    global _finbert_model, _finbert_tokenizer, _finbert_sae, _finbert_config
    
    try:
        model_path = request.model_path or FINBERT_MODEL_PATH
        sae_path = request.sae_path or FINBERT_SAE_PATH
        config_path = request.config_path or FINBERT_CONFIG_PATH
        
        _finbert_model, _finbert_tokenizer = load_transformers_model(model_path, output_hidden_states=True)
        _finbert_sae, _finbert_config = load_sae(sae_path, config_path)
        
        return {"status": "success", "message": "Models loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {str(e)}")

