"""
Centralized model loading and caching service.
Handles loading and caching of LLM models for cloud API.
"""
import torch
import os
import sys
from typing import Dict, Optional, Tuple
from pathlib import Path

# Global model cache
_model_cache: Dict[str, any] = {}

def get_device():
    """Get the best available device: CUDA > CPU (MPS not typically on cloud GPU)"""
    if torch.cuda.is_available():
        return "cuda:0"
    else:
        return "cpu"

def load_language_model(model_path: str, device: Optional[str] = None) -> Tuple[any, any]:
    """
    Load language model with caching.
    
    Args:
        model_path: HuggingFace model path or local path
        device: Device to load on (defaults to auto-detect)
    
    Returns:
        Tuple of (model, tokenizer)
    """
    if device is None:
        device = get_device()
    
    cache_key = f"{model_path}_{device}"
    
    if cache_key in _model_cache:
        print(f"✓ Using cached model {model_path} on {device}")
        return _model_cache[cache_key]
    
    from nnsight import LanguageModel
    
    # Get HuggingFace token from environment
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    
    # Set cache directory to workspace if available (for persistent storage)
    # Try HF_HOME first, then check for Docker workspace, then local project cache
    cache_dir = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE")
    if not cache_dir:
        # Check Docker workspace path first
        if os.path.exists("/workspace/.cache/huggingface"):
            cache_dir = "/workspace/.cache/huggingface"
        else:
            # Use local project cache (matching Docker structure)
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            local_cache = project_root / '.cache' / 'huggingface'
            if local_cache.exists():
                cache_dir = str(local_cache)
        # Set environment variable so nnsight/transformers uses it
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
    
    # Use appropriate dtype for device
    model_dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32
    
    print(f"Loading model {model_path} on {device} (first time, will cache)...")
    if cache_dir:
        print(f"Using cache directory: {cache_dir}")
    
    model = LanguageModel(
        model_path,
        device_map={"": device} if not device.startswith("cuda") else "auto",
        trust_remote_code=True,
        dtype=model_dtype,
        token=hf_token
    )
    
    if model.tokenizer.pad_token is None:
        model.tokenizer.pad_token = model.tokenizer.eos_token
    
    _model_cache[cache_key] = (model, model.tokenizer)
    return model, model.tokenizer

def load_transformers_model(model_path: str, device: Optional[str] = None, 
                           output_hidden_states: bool = True) -> Tuple[any, any]:
    """
    Load transformers model (for FinBERT, etc.) with caching.
    
    Args:
        model_path: HuggingFace model path
        device: Device to load on
        output_hidden_states: Whether to output hidden states
    
    Returns:
        Tuple of (model, tokenizer)
    """
    if device is None:
        device = get_device()
    
    cache_key = f"{model_path}_{device}_{output_hidden_states}"
    
    if cache_key in _model_cache:
        print(f"✓ Using cached transformers model {model_path} on {device}")
        return _model_cache[cache_key]
    
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
    
    # Get HuggingFace token from environment
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    
    # Set cache directory to workspace if available (for persistent storage)
    # Try HF_HOME first, then check for Docker workspace, then local project cache
    cache_dir = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE")
    if not cache_dir:
        # Check Docker workspace path first
        if os.path.exists("/workspace/.cache/huggingface"):
            cache_dir = "/workspace/.cache/huggingface"
        else:
            # Use local project cache (matching Docker structure)
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            local_cache = project_root / '.cache' / 'huggingface'
            if local_cache.exists():
                cache_dir = str(local_cache)
        # Set environment variable so transformers uses it
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
    
    print(f"Loading transformers model {model_path} on {device} (first time, will cache)...")
    if cache_dir:
        print(f"Using cache directory: {cache_dir}")
    
    # Determine model type from path
    if "finbert" in model_path.lower():
        from transformers import AutoModelForSequenceClassification
        model_kwargs = {
            "output_hidden_states": output_hidden_states,
            "torch_dtype": torch.float32 if device == "cpu" else torch.float16,
            "trust_remote_code": True,
        }
        if hf_token:
            model_kwargs["token"] = hf_token
        if cache_dir:
            model_kwargs["cache_dir"] = cache_dir
        model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            **model_kwargs
        ).to(device)
    else:
        # Default to AutoModelForCausalLM
        model_kwargs = {
            "torch_dtype": torch.float16 if device.startswith("cuda") else torch.float32,
            "device_map": "auto" if device.startswith("cuda") else None,
            "trust_remote_code": True,
        }
        if hf_token:
            model_kwargs["token"] = hf_token
        if cache_dir:
            model_kwargs["cache_dir"] = cache_dir
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            **model_kwargs
        )
        if not device.startswith("cuda"):
            model = model.to(device)
    
    tokenizer_kwargs = {"trust_remote_code": True}
    if hf_token:
        tokenizer_kwargs["token"] = hf_token
    if cache_dir:
        tokenizer_kwargs["cache_dir"] = cache_dir
    tokenizer = AutoTokenizer.from_pretrained(model_path, **tokenizer_kwargs)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token if hasattr(tokenizer, 'eos_token') else tokenizer.unk_token
    
    model.eval()
    _model_cache[cache_key] = (model, tokenizer)
    return model, tokenizer

def clear_model_cache():
    """Clear the model cache (useful for memory management)"""
    global _model_cache
    _model_cache.clear()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

