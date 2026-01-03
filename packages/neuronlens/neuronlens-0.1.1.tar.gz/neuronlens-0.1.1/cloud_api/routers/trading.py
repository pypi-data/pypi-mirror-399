"""
Trading API router.
Handles trading SAE feature extraction and feature labels.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import torch
import numpy as np
import os
import pandas as pd
from safetensors import safe_open

try:
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae_from_safetensors
    from cloud_api.utils.serialization import serialize_array
except ImportError:
    # Fallback for when running from cloud_api directory
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae_from_safetensors
    from cloud_api.utils.serialization import serialize_array

router = APIRouter(prefix="/trading", tags=["Trading"])

# Global model cache
_trading_model = None
_trading_tokenizer = None
_trading_sae_weights = None
_feature_labels = {}

# Path resolution - use environment variables or relative paths (like backend.py)
def resolve_path(env_var: str, docker_fallback: str, relative_fallback: str = None) -> str:
    """Resolve path from env var, Docker fallback, or relative path"""
    # Try environment variable first
    path = os.getenv(env_var)
    if path and os.path.exists(path):
        return path
    
    # Try Docker fallback (for cloud deployment)
    if os.path.exists(docker_fallback):
        return docker_fallback
    
    # Try relative fallback (for local Mac development)
    if relative_fallback:
        router_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = os.path.join(router_dir, relative_fallback)
        if os.path.exists(rel_path):
            return rel_path
        # Try going up to project root
        project_root = os.path.dirname(os.path.dirname(router_dir))
        rel_path = os.path.join(project_root, relative_fallback)
        if os.path.exists(rel_path):
            return rel_path
    
    # Return the Docker path as default (will fail gracefully if not found)
    return docker_fallback

# Configuration
TRADING_MODEL_PATH = os.getenv("TRADING_MODEL_PATH", "meta-llama/Llama-3.1-8B-Instruct")
TRADING_SAE_PATH = resolve_path(
    'SAE_MODEL_PATH',
    '/app/sae_models/trading',  # Docker fallback
    '../../saetrain/trained_models/llama3.1_8b_layer19_k32_latents400_lmsys_chat1m_multiGPU'  # Local fallback
)
TRADING_LAYER = int(os.getenv("TRADING_LAYER", "19"))
FEATURE_LABELS_PATH = resolve_path(
    'FEATURE_LABELS_PATH',
    '/app/labels/layer_19_all_features.csv',  # Docker fallback
    '../../Trading_with_stats/layer_19_all_features.csv'  # Local fallback
)

class ExtractFeaturesRequest(BaseModel):
    text: str
    ticker: Optional[str] = None
    layer: int = 19

class LoadModelsRequest(BaseModel):
    model_path: Optional[str] = None
    sae_path: Optional[str] = None
    layer: Optional[int] = None

def _load_feature_labels():
    """Load feature labels from CSV"""
    global _feature_labels
    
    if _feature_labels:
        return _feature_labels
    
    if os.path.exists(FEATURE_LABELS_PATH):
        try:
            df = pd.read_csv(FEATURE_LABELS_PATH)
            if 'layer' in df.columns:
                df = df[df['layer'] == TRADING_LAYER]
            
            feature_col = None
            label_col = None
            for col in df.columns:
                if 'feature' in col.lower() and feature_col is None:
                    feature_col = col
                if 'label' in col.lower() and label_col is None:
                    label_col = col
            
            if feature_col and label_col:
                for _, row in df.iterrows():
                    try:
                        feature_idx = int(row[feature_col])
                        label = str(row[label_col])
                        if pd.notna(label) and label.strip():
                            _feature_labels[feature_idx] = label
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"Warning: Could not load feature labels: {e}")
    
    return _feature_labels

@router.post("/extract_features")
async def extract_features(request: ExtractFeaturesRequest):
    """Extract SAE features from news text"""
    global _trading_model, _trading_tokenizer, _trading_sae_weights
    
    try:
        if _trading_model is None:
            _trading_model, _trading_tokenizer = load_transformers_model(TRADING_MODEL_PATH)
        
        if _trading_sae_weights is None:
            # Try multiple path patterns (like backend.py does)
            sae_file = os.path.join(TRADING_SAE_PATH, f"layers.{request.layer}", "sae.safetensors")
            if not os.path.exists(sae_file):
                sae_file = os.path.join(TRADING_SAE_PATH, "sae.safetensors")
            if not os.path.exists(sae_file):
                # Try alternative: directly in SAE_PATH
                sae_file = TRADING_SAE_PATH
                if not os.path.exists(sae_file) or not sae_file.endswith('.safetensors'):
                    raise FileNotFoundError(f"SAE model not found. Tried: {os.path.join(TRADING_SAE_PATH, f'layers.{request.layer}', 'sae.safetensors')}, {os.path.join(TRADING_SAE_PATH, 'sae.safetensors')}")
            _trading_sae_weights = load_sae_from_safetensors(sae_file, request.layer)
        
        device = get_device()
        
        # Tokenize
        tokens = _trading_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)
        
        # Get hidden states
        with torch.no_grad():
            outputs = _trading_model(**tokens, output_hidden_states=True)
            hidden_states = outputs.hidden_states[request.layer]
        
        # Extract features (simplified - actual implementation would use SAE weights)
        # For now, return mean hidden states as features
        features = hidden_states.mean(dim=1).squeeze().cpu().numpy()
        
        features_serialized = serialize_array(features)
        return {"features": features_serialized}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

@router.get("/feature_labels")
async def get_feature_labels():
    """Get feature labels (static file)"""
    labels = _load_feature_labels()
    return labels

@router.post("/load_models")
async def load_models(request: LoadModelsRequest):
    """Load trading models"""
    global _trading_model, _trading_tokenizer, _trading_sae_weights
    
    try:
        model_path = request.model_path or TRADING_MODEL_PATH
        sae_path = request.sae_path or TRADING_SAE_PATH
        layer = request.layer or TRADING_LAYER
        
        _trading_model, _trading_tokenizer = load_transformers_model(model_path)
        
        sae_file = os.path.join(sae_path, f"layers.{layer}", "sae.safetensors")
        if not os.path.exists(sae_file):
            sae_file = os.path.join(sae_path, "sae.safetensors")
        _trading_sae_weights = load_sae_from_safetensors(sae_file, layer)
        
        return {"status": "success", "message": "Models loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {str(e)}")



