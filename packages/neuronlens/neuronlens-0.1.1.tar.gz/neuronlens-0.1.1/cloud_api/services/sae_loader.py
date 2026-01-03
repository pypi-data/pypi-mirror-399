"""
Centralized SAE loading and caching service.
Handles loading and caching of SAE models for cloud API.
"""
import torch
import json
import os
import sys
from typing import Dict, Optional, Tuple, Any
from pathlib import Path

# Global SAE cache
_sae_cache: Dict[str, any] = {}

def get_device():
    """Get the best available device: CUDA > CPU"""
    if torch.cuda.is_available():
        return "cuda:0"
    else:
        return "cpu"

def setup_dictionary_learning_path():
    """Setup dictionary learning module path"""
    # Try relative path first
    script_dir = Path(__file__).parent.parent.parent.resolve()
    relative_dict_learning = script_dir / "EndtoEnd" / "train" / "DictionaryLearning"
    hardcoded_dict_learning = "/home/nvidia/Documents/Hariom/InterpUseCases_autointerp/EndtoEnd/train/DictionaryLearning"
    
    if relative_dict_learning.exists():
        dict_learning_dir = str(relative_dict_learning.resolve())
    elif os.path.exists(hardcoded_dict_learning):
        dict_learning_dir = hardcoded_dict_learning
    else:
        # Try to find in common locations
        dict_learning_dir = hardcoded_dict_learning
    
    if dict_learning_dir not in sys.path:
        sys.path.insert(0, dict_learning_dir)
    
    # Setup module hierarchy
    sys.modules["dictionary_learning.trainers"] = type(sys)("dictionary_learning.trainers")
    
    import importlib.util
    
    trainer_path = os.path.join(dict_learning_dir, "trainers", "trainer.py")
    if os.path.exists(trainer_path):
        trainer_spec = importlib.util.spec_from_file_location("dictionary_learning.trainers.trainer", trainer_path)
        trainer_module = importlib.util.module_from_spec(trainer_spec)
        sys.modules["dictionary_learning.trainers.trainer"] = trainer_module
        trainer_spec.loader.exec_module(trainer_module)
    
    batch_top_k_path = os.path.join(dict_learning_dir, "trainers", "batch_top_k.py")
    if os.path.exists(batch_top_k_path):
        spec = importlib.util.spec_from_file_location("dictionary_learning.trainers.batch_top_k", batch_top_k_path)
        batch_top_k_module = importlib.util.module_from_spec(spec)
        sys.modules["dictionary_learning.trainers.batch_top_k"] = batch_top_k_module
        spec.loader.exec_module(batch_top_k_module)
        
        return batch_top_k_module.BatchTopKSAE
    
    return None

def load_sae(sae_path: str, config_path: str, device: Optional[str] = None, 
             k: Optional[int] = None) -> Tuple[any, Dict[str, Any]]:
    """
    Load SAE model with caching.
    
    Args:
        sae_path: Path to SAE model directory or file
        config_path: Path to SAE config JSON file
        device: Device to load on (defaults to auto-detect)
        k: Top-K sparsity (optional, read from config if not provided)
    
    Returns:
        Tuple of (sae_model, config_dict)
    """
    if device is None:
        device = get_device()
    
    cache_key = f"{sae_path}_{device}"
    
    if cache_key in _sae_cache:
        return _sae_cache[cache_key]
    
    print(f"Loading SAE from {sae_path} on {device}...")
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    trainer_config = config.get("trainer", {})
    dict_size = trainer_config.get("dict_size", 35840)
    k = k or trainer_config.get("k", 64)
    activation_dim = trainer_config.get("activation_dim", 2048)
    
    # Try to load using BatchTopKSAE
    BatchTopKSAE = setup_dictionary_learning_path()
    
    if BatchTopKSAE is not None:
        try:
            sae = BatchTopKSAE.from_pretrained(sae_path, device=device)
            sae_dtype = torch.float32 if device == "cpu" else torch.bfloat16
            sae = sae.to(sae_dtype)
            sae.eval()
        except Exception as e:
            print(f"Warning: BatchTopKSAE.from_pretrained failed: {e}, trying manual load")
            sae = None
    else:
        sae = None
    
    # Fallback: manual loading from safetensors or .pt file
    if sae is None:
        from safetensors import safe_open
        
        # Try safetensors first
        if os.path.isdir(sae_path):
            sae_file = os.path.join(sae_path, "sae.safetensors")
            if not os.path.exists(sae_file):
                # Try layers.X/sae.safetensors pattern
                for layer_dir in os.listdir(sae_path):
                    layer_path = os.path.join(sae_path, layer_dir)
                    if os.path.isdir(layer_path):
                        potential_file = os.path.join(layer_path, "sae.safetensors")
                        if os.path.exists(potential_file):
                            sae_file = potential_file
                            break
        else:
            sae_file = sae_path
        
        if os.path.exists(sae_file) and sae_file.endswith('.safetensors'):
            # Load from safetensors
            sae_weights = {}
            load_device = "cpu" if device == "mps" else device
            with safe_open(sae_file, framework="pt", device=load_device) as f:
                for key in f.keys():
                    tensor = f.get_tensor(key)
                    if device == "mps":
                        tensor = tensor.to(device)
                    sae_weights[key] = tensor
            
            # Create minimal SAE wrapper (for API compatibility)
            # In production, you'd want to create proper BatchTopKSAE instance
            sae = {
                "weights": sae_weights,
                "dict_size": dict_size,
                "k": k,
                "activation_dim": activation_dim
            }
        else:
            # Try .pt file
            pt_file = sae_path if sae_path.endswith('.pt') else os.path.join(sae_path, "ae.pt")
            if os.path.exists(pt_file):
                sae_state = torch.load(pt_file, map_location=device)
                sae = {
                    "state_dict": sae_state,
                    "dict_size": dict_size,
                    "k": k,
                    "activation_dim": activation_dim
                }
            else:
                raise FileNotFoundError(f"SAE file not found at {sae_path}")
    
    _sae_cache[cache_key] = (sae, config)
    return sae, config

def load_sae_from_safetensors(sae_file: str, layer: int, device: Optional[str] = None) -> Dict[str, torch.Tensor]:
    """
    Load SAE weights from safetensors file (for Trading, AgenticTracing, etc.)
    
    Args:
        sae_file: Path to safetensors file
        layer: Layer number
        device: Device to load on
    
    Returns:
        Dictionary of SAE weights with normalized keys:
        - "encoder" (from "encoder.weight")
        - "encoder_bias" (from "encoder.bias")
        - "decoder" (from "W_dec")
        - "decoder_bias" (from "b_dec")
    """
    if device is None:
        device = get_device()
    
    cache_key = f"{sae_file}_{layer}_{device}"
    
    if cache_key in _sae_cache:
        return _sae_cache[cache_key]
    
    from safetensors import safe_open
    
    print(f"Loading SAE weights from {sae_file} for layer {layer} on {device}...")
    
    sae_weights = {}
    load_device = "cpu" if device == "mps" else device
    
    with safe_open(sae_file, framework="pt", device=load_device) as f:
        # Map safetensors keys to normalized keys (matching agent_lens_backend format)
        # Keep both original and normalized keys for backward compatibility
        key_mapping = {
            "encoder.weight": "encoder",
            "encoder.bias": "encoder_bias",
            "W_dec": "decoder",
            "b_dec": "decoder_bias"
        }
        
        for safetensors_key in f.keys():
            tensor = f.get_tensor(safetensors_key)
            if device == "mps":
                tensor = tensor.to(device)
            
            # Store with original key (for backward compatibility with searchsteer, etc.)
            sae_weights[safetensors_key] = tensor
            
            # Also store with normalized key if mapping exists (for agentic router)
            if safetensors_key in key_mapping:
                normalized_key = key_mapping[safetensors_key]
                sae_weights[normalized_key] = tensor
    
    _sae_cache[cache_key] = sae_weights
    return sae_weights

def clear_sae_cache():
    """Clear the SAE cache"""
    global _sae_cache
    _sae_cache.clear()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()




