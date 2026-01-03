"""
CoT Reasoning API router.
Handles CoT text generation and SAE feature extraction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch
import numpy as np
import sys
import os
from pathlib import Path

from cloud_api.services.model_loader import load_language_model, get_device
from cloud_api.services.sae_loader import load_sae, setup_dictionary_learning_path
from cloud_api.utils.serialization import serialize_array

router = APIRouter(prefix="/cot", tags=["CoT Reasoning"])

# Global model cache (module-level)
_cot_model = None
_cot_tokenizer = None
_cot_sae = None
_cot_config = None

# Configuration paths (should be set via environment variables or config)
COT_MODEL_PATH = os.getenv("COT_MODEL_PATH", "nvidia/NVIDIA-Nemotron-Nano-9B-v2")
COT_SAE_PATH = os.getenv("COT_SAE_PATH", "/app/sae_models/nemotron")
COT_CONFIG_PATH = os.getenv("COT_CONFIG_PATH", "/app/configs/nemotron_sae_config.json")
COT_LAYER = int(os.getenv("COT_LAYER", "28"))

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 2048
    thinking_budget: Optional[int] = None

class ExtractFeaturesRequest(BaseModel):
    text: str
    layer: int = 28
    trim_ratio: float = 0.0

class LoadModelsRequest(BaseModel):
    model_path: Optional[str] = None
    sae_path: Optional[str] = None
    config_path: Optional[str] = None

@router.post("/generate")
async def generate_cot(request: GenerateRequest):
    """Generate CoT text using model inference"""
    global _cot_model, _cot_tokenizer
    
    try:
        if _cot_model is None:
            _cot_model, _cot_tokenizer = load_language_model(COT_MODEL_PATH)
        
        # Use chat template
        messages = [
            {"role": "system", "content": "/think"},
            {"role": "user", "content": request.prompt},
        ]
        
        formatted_prompt = _cot_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        gen_kwargs = {
            "max_new_tokens": request.max_new_tokens,
            "do_sample": True,
            "temperature": 0.7,
            "scan": False,
            "validate": False
        }
        
        if request.thinking_budget is not None:
            gen_kwargs["thinking_budget"] = request.thinking_budget
        
        with torch.no_grad():
            with _cot_model.generate(formatted_prompt, **gen_kwargs) as gen:
                out = _cot_model.generator.output.save()
        
        # Extract generated text
        generated_ids = out.value
        if isinstance(generated_ids, torch.Tensor):
            generated_ids = generated_ids[0].cpu().tolist()
        elif isinstance(generated_ids, (list, tuple)):
            generated_ids = generated_ids[0]
            if isinstance(generated_ids, torch.Tensor):
                generated_ids = generated_ids.cpu().tolist()
        
        full_text = _cot_tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        # Get generated portion
        if full_text.startswith(formatted_prompt):
            generated_only = full_text[len(formatted_prompt):].strip()
        else:
            generated_only = full_text
        
        # Extract CoT from tags
        import re
        cot_match = re.search(r'<think>(.*?)</think>', generated_only, re.DOTALL)
        if not cot_match:
            cot_match = re.search(r'<think>(.*?)</think>', generated_only, re.DOTALL)
        if cot_match:
            cot_text = cot_match.group(1).strip()
            if cot_text and cot_text != "..." and len(cot_text) > 3:
                return {"generated_text": cot_text}
        
        return {"generated_text": generated_only}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CoT: {str(e)}")

@router.post("/extract_features")
async def extract_features(request: ExtractFeaturesRequest):
    """Extract SAE features from text (returns raw features)"""
    global _cot_model, _cot_tokenizer, _cot_sae, _cot_config
    
    try:
        if _cot_model is None:
            _cot_model, _cot_tokenizer = load_language_model(COT_MODEL_PATH)
        
        if _cot_sae is None:
            _cot_sae, _cot_config = load_sae(COT_SAE_PATH, COT_CONFIG_PATH)
        
        device = get_device()
        layer = request.layer
        
        # Tokenize
        tokens = _cot_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=False
        ).to(device)
        
        # Extract hidden states
        with torch.no_grad():
            with _cot_model.trace(tokens, scan=False, validate=False):
                hidden_states = _cot_model.backbone.layers[layer].output[0].save()
        
        hidden_states_tensor = hidden_states.value
        if isinstance(hidden_states_tensor, tuple):
            hidden_states_tensor = hidden_states_tensor[0]
        
        if len(hidden_states_tensor.shape) == 3:
            activations = hidden_states_tensor[0]  # [T, d]
        else:
            activations = hidden_states_tensor
        
        # Apply trim_ratio if specified
        T = activations.shape[0]
        if request.trim_ratio > 0 and T > 4:
            start = int(T * request.trim_ratio)
            end = int(T * (1 - request.trim_ratio))
            activations = activations[start:end]
        
        # Encode through SAE
        flat = activations.reshape(-1, activations.shape[-1])
        
        # Handle different SAE formats
        if hasattr(_cot_sae, 'encode'):
            feats = _cot_sae.encode(flat.to(_cot_sae.encoder.weight.dtype))
        else:
            # Fallback: return activations directly (no SAE encoding)
            feats = flat
        
        mean_feats = feats.mean(dim=0).detach().cpu().float().numpy()
        
        # Serialize for JSON
        features_serialized = serialize_array(mean_feats)
        
        return {"features": features_serialized}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

@router.post("/load_models")
async def load_models(request: LoadModelsRequest):
    """Load models (returns success/failure)"""
    global _cot_model, _cot_tokenizer, _cot_sae, _cot_config
    
    try:
        model_path = request.model_path or COT_MODEL_PATH
        sae_path = request.sae_path or COT_SAE_PATH
        config_path = request.config_path or COT_CONFIG_PATH
        
        _cot_model, _cot_tokenizer = load_language_model(model_path)
        _cot_sae, _cot_config = load_sae(sae_path, config_path)
        
        return {"status": "success", "message": "Models loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {str(e)}")







