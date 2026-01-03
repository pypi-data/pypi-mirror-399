"""
AgenticTracing API router.
Handles agent SAE feature extraction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch
import numpy as np
import os
import sys
import subprocess
import requests
import time

try:
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae_from_safetensors
    from cloud_api.utils.serialization import serialize_array
except ImportError:
    # Fallback for when running from cloud_api directory
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(parent_dir))
    from cloud_api.services.model_loader import load_transformers_model, get_device
    from cloud_api.services.sae_loader import load_sae_from_safetensors
    from cloud_api.utils.serialization import serialize_array

def _check_vllm_available():
    """Check if vLLM server is available - fast check"""
    try:
        response = requests.get("http://localhost:8003/v1/health", timeout=1)  # Reduced timeout
        return response.status_code == 200
    except:
        return False

def _check_ollama_available():
    """Check if Ollama server is available - fast check with caching"""
    global _ollama_available_cache, _ollama_cache_time
    import time as time_module
    
    # Use cached result if still valid
    current_time = time_module.time()
    if _ollama_available_cache is not None and (current_time - _ollama_cache_time) < OLLAMA_CACHE_TTL:
        return _ollama_available_cache
    
    # Check Ollama availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=0.5)  # Very fast timeout
        available = response.status_code == 200
    except:
        available = False
    
    # Cache the result
    _ollama_available_cache = available
    _ollama_cache_time = current_time
    return available

def _ensure_ollama_running():
    """Auto-start Ollama if not running, returns True if available"""
    # Fast check first
    if _check_ollama_available():
        return True
    try:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Reduced wait time
        return _check_ollama_available()
    except:
        return False

router = APIRouter(prefix="/agentic", tags=["AgenticTracing"])

# Global model cache
_agentic_model = None
_agentic_tokenizer = None
_agentic_sae_weights = None

# Cache Ollama availability (check once, reuse)
_ollama_available_cache = None
_ollama_cache_time = 0
OLLAMA_CACHE_TTL = 30  # Cache for 30 seconds

# Configuration
AGENTIC_MODEL_PATH = os.getenv("AGENTIC_MODEL_PATH", "meta-llama/Llama-3.1-8B-Instruct")
# Use local cloud_api paths (matching Docker /workspace/sae_models/ structure)
_default_sae_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sae_models", "agentic")
AGENTIC_SAE_PATH = os.getenv("AGENTIC_SAE_PATH", _default_sae_path)
AGENTIC_LAYER = int(os.getenv("AGENTIC_LAYER", "19"))

class ExtractFeaturesRequest(BaseModel):
    text: str
    layer: int = 19

class GenerateRequest(BaseModel):
    query: str
    max_new_tokens: int = 256  # Reduced default for faster responses

class LoadModelsRequest(BaseModel):
    model_path: Optional[str] = None
    sae_path: Optional[str] = None
    layer: Optional[int] = None

@router.post("/extract_features")
def extract_features(request: ExtractFeaturesRequest):  # Changed to sync
    """Extract SAE features from agent execution - returns placeholder if models not loaded"""
    global _agentic_model, _agentic_tokenizer, _agentic_sae_weights
    
    # Fast path: If models not loaded, return placeholder (models load on first /generate call)
    # This avoids blocking on slow model loading
    if _agentic_model is None or _agentic_tokenizer is None:
        # Return placeholder features (400 dims matching SAE output)
        # Note: This indicates models need to be loaded via /agentic/load_models endpoint
        placeholder = np.zeros(400, dtype=np.float32)
        features_serialized = serialize_array(placeholder)
        import sys
        print(f"⚠️  Models not loaded. Call /agentic/load_models first. Model path: {AGENTIC_MODEL_PATH}, SAE path: {AGENTIC_SAE_PATH}", file=sys.stderr)
        return {"features": features_serialized}
    
    try:
        # Models are loaded, proceed with feature extraction
        if _agentic_sae_weights is None:
            sae_file = os.path.join(AGENTIC_SAE_PATH, f"layers.{request.layer}", "sae.safetensors")
            if not os.path.exists(sae_file):
                sae_file = os.path.join(AGENTIC_SAE_PATH, "sae.safetensors")
            if os.path.exists(sae_file):
                _agentic_sae_weights = load_sae_from_safetensors(sae_file, request.layer)
            else:
                # SAE not found, return mean hidden states
                device = get_device()
                tokens = _agentic_tokenizer(
                    request.text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                ).to(device)
                with torch.no_grad():
                    outputs = _agentic_model(**tokens, output_hidden_states=True)
                    hidden_states = outputs.hidden_states[request.layer]
                features = hidden_states.mean(dim=1).squeeze().cpu().numpy()
                features_serialized = serialize_array(features)
                return {"features": features_serialized}
        
        device = get_device()
        
        # Tokenize
        tokens = _agentic_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=256  # Reduced for speed
        ).to(device)
        
        # Get hidden states
        with torch.no_grad():
            outputs = _agentic_model(**tokens, output_hidden_states=True)
            hidden_states = outputs.hidden_states[request.layer]
        
        # Apply SAE encoder if weights are loaded
        if _agentic_sae_weights is not None:
            # Use SAE encoder to get feature activations
            encoder = _agentic_sae_weights["encoder"].to(hidden_states.device).to(hidden_states.dtype)
            encoder_bias = _agentic_sae_weights.get("encoder_bias", torch.zeros(encoder.shape[0], device=hidden_states.device, dtype=hidden_states.dtype))
            
            # Compute feature activations: (hidden_states @ encoder.T) + bias
            feature_activations = torch.matmul(hidden_states, encoder.T) + encoder_bias
            feature_activations = torch.relu(feature_activations)  # ReLU activation
            
            # Take max over sequence dimension
            features = feature_activations.max(dim=1)[0].squeeze(0).cpu().numpy().astype(np.float32)
        else:
            # Fallback: mean hidden states (not actual SAE features)
            features = hidden_states.mean(dim=1).squeeze().cpu().numpy().astype(np.float32)
        
        features_serialized = serialize_array(features)
        return {"features": features_serialized}
    
    except Exception as e:
        # On error, return placeholder instead of failing
        placeholder = np.zeros(400, dtype=np.float32)
        features_serialized = serialize_array(placeholder)
        return {"features": features_serialized}

@router.post("/generate")
def generate_response(request: GenerateRequest):  # Changed to sync for speed
    """Generate agent response - auto-starts Ollama if not running"""
    global _agentic_model, _agentic_tokenizer
    
    # Ensure Ollama is running before proceeding
    if not _ensure_ollama_running():
        raise HTTPException(
            status_code=503, 
            detail="Ollama server not available and could not be started. Please ensure Ollama is installed and try again."
        )
    
    # Generate response with Ollama
    try:
        # Use Ollama API directly - no availability check for speed
        ollama_model = os.getenv("AGENT_LENS_OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "llama3.1:8b"))
        payload = {
            "model": ollama_model,
            "prompt": request.query,
            "options": {
                "temperature": 0.7,
                "num_predict": request.max_new_tokens
            },
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120  # Increased to 2 minutes for model inference
        )
        response.raise_for_status()
        result = response.json()
        return {"response": result.get("response", "")}
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama request timed out")
    except requests.exceptions.ConnectionError:
        # Only check availability if connection fails
        if not _check_ollama_available():
            raise HTTPException(status_code=503, detail="Ollama server not available")
        raise HTTPException(status_code=500, detail="Ollama connection error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/load_models")
async def load_models(request: LoadModelsRequest):
    """Load agentic models"""
    global _agentic_model, _agentic_tokenizer, _agentic_sae_weights
    
    try:
        model_path = request.model_path or AGENTIC_MODEL_PATH
        sae_path = request.sae_path or AGENTIC_SAE_PATH
        layer = request.layer or AGENTIC_LAYER
        
        _agentic_model, _agentic_tokenizer = load_transformers_model(model_path)
        
        sae_file = os.path.join(sae_path, f"layers.{layer}", "sae.safetensors")
        if not os.path.exists(sae_file):
            sae_file = os.path.join(sae_path, "sae.safetensors")
        _agentic_sae_weights = load_sae_from_safetensors(sae_file, layer)
        
        return {"status": "success", "message": "Models loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {str(e)}")

