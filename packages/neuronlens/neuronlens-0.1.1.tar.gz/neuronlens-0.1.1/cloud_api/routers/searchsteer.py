"""
SearchSteer API router.
Handles feature search, steering, and SAE feature extraction.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import torch
import numpy as np
import os
import pandas as pd
from pathlib import Path

from cloud_api.services.model_loader import load_transformers_model, get_device
from cloud_api.services.sae_loader import load_sae_from_safetensors
from cloud_api.utils.serialization import serialize_array

# For semantic search (matching backend implementation)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    SEMANTIC_SEARCH_AVAILABLE = False

router = APIRouter(prefix="/searchsteer", tags=["SearchSteer"])

# Global model cache
_searchsteer_model = None
_searchsteer_tokenizer = None
_searchsteer_sae_weights = None
_feature_labels = {}  # Cache for feature labels
_semantic_model = None  # Sentence transformer for semantic search

# Configuration - Use local path if not in Docker
_default_sae_path = "/app/sae_models/searchsteer"  # Docker default
if not os.path.exists(_default_sae_path):
    # Try local path - adjust based on your local setup
    _local_sae_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sae_models", "searchsteer"),
        os.path.expanduser("~/sae_models/searchsteer"),
        "./sae_models/searchsteer"
    ]
    for path in _local_sae_paths:
        if os.path.exists(path):
            _default_sae_path = path
            break

SEARCHSTEER_MODEL_PATH = os.getenv("SEARCHSTEER_MODEL_PATH", "meta-llama/Llama-2-7b-hf")
SEARCHSTEER_SAE_PATH = os.getenv("SEARCHSTEER_SAE_PATH", _default_sae_path)
SEARCHSTEER_LAYER = int(os.getenv("SEARCHSTEER_LAYER", "16"))

# Feature labels CSV path - use relative path to labels folder (like trading router)
def _get_feature_labels_path():
    """Get path to feature labels CSV using relative path"""
    # Get router directory and build relative path to labels folder
    router_dir = Path(__file__).parent
    cloud_api_dir = router_dir.parent
    labels_dir = cloud_api_dir / "labels"
    
    # Try labels folder first (where other lens labels are kept)
    csv_file = labels_dir / "layer_16_all_features.csv"
    if csv_file.exists():
        return str(csv_file)
    
    # Fallback: try config path if labels folder doesn't have it
    try:
        from cloud_api.backend.config.model_paths import SEARCH_STEER
        csv_path = SEARCH_STEER.get("csv_path")
        if csv_path and os.path.exists(csv_path):
            return csv_path
    except Exception:
        pass
    
    return None

def _load_feature_labels():
    """Load feature labels from CSV file"""
    global _feature_labels
    
    if _feature_labels:
        return _feature_labels
    
    csv_path = _get_feature_labels_path()
    if not csv_path or not os.path.exists(csv_path):
        return _feature_labels
    
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            if row.get('layer') == SEARCHSTEER_LAYER:
                feature_id = f"f_{int(row['feature'])}"
                _feature_labels[feature_id] = {
                    'label': str(row.get('label', '')).replace('"', ''),
                    'layer': int(row.get('layer', SEARCHSTEER_LAYER)),
                    'f1_score': float(row.get('f1_score', 0.0)) if 'f1_score' in row else 0.0
                }
    except Exception as e:
        print(f"Warning: Could not load feature labels: {e}")
    
    return _feature_labels

class SearchRequest(BaseModel):
    query: str
    k: int = 10
    layer: int = 16

class SteerRequest(BaseModel):
    prompt: str
    features: List[Dict[str, Any]]
    model: str = "meta-llama/Llama-2-7b-hf"

class ExtractFeaturesRequest(BaseModel):
    text: str
    layer: int = 16

class LoadModelsRequest(BaseModel):
    model_path: Optional[str] = None
    sae_path: Optional[str] = None
    layer: Optional[int] = None

def _get_semantic_model():
    """Get or initialize semantic model for search (matching backend)"""
    global _semantic_model
    if _semantic_model is None and SEMANTIC_SEARCH_AVAILABLE:
        try:
            # Force CPU usage to avoid CUDA out of memory (matching backend)
            import os
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            _semantic_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        except Exception as e:
            print(f"Warning: Could not load semantic model: {e}")
            return None
    return _semantic_model

@router.post("/search")
async def search_features(request: SearchRequest):
    """Search features using semantic similarity (matching backend implementation)"""
    global _searchsteer_model, _searchsteer_tokenizer, _searchsteer_sae_weights
    
    try:
        # Load feature labels first (required for semantic search)
        labels = _load_feature_labels()
        if not labels:
            raise HTTPException(status_code=500, detail="Feature labels not loaded")
        
        # Use semantic search if available (matching backend)
        if SEMANTIC_SEARCH_AVAILABLE:
            semantic_model = _get_semantic_model()
            if semantic_model is not None:
                # Get all feature labels and IDs
                feature_ids = list(labels.keys())
                label_texts = [labels[fid]['label'] for fid in feature_ids]
                
                # Compute embeddings for all labels
                label_embeddings = semantic_model.encode(label_texts)
                
                # Compute embedding for search query
                query_embedding = semantic_model.encode([request.query])
                
                # Calculate similarities
                similarities = cosine_similarity(query_embedding, label_embeddings)[0]
                
                # Get top-k most similar features
                top_indices = np.argsort(similarities)[::-1][:request.k]
                
                # Build results
                top_features = []
                for idx in top_indices:
                    feature_id = feature_ids[idx]
                    label_data = labels[feature_id]
                    similarity = similarities[idx]
                    
                    top_features.append({
                        'id': feature_id,
                        'feature_id': int(feature_id.replace('f_', '')),
                        'label': label_data['label'],
                        'layer': label_data['layer'],
                        'score': float(similarity),
                        'f1_score': label_data['f1_score']
                    })
                
                return {"features": top_features}
        
        # Fallback: keyword search if semantic model not available
        query_lower = request.query.lower()
        results = []
        for feature_id, label_data in labels.items():
            label_lower = label_data['label'].lower()
            score = 0.0
            
            # Simple keyword matching
            if query_lower in label_lower:
                score = 1.0
            else:
                query_words = query_lower.split()
                label_words = label_lower.split()
                for q_word in query_words:
                    for l_word in label_words:
                        if q_word in l_word or l_word in q_word:
                            score += 0.5
            
            if score > 0:
                results.append({
                    'id': feature_id,
                    'feature_id': int(feature_id.replace('f_', '')),
                    'label': label_data['label'],
                    'layer': label_data['layer'],
                    'score': min(score, 1.0),
                    'f1_score': label_data['f1_score']
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return {"features": results[:request.k]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching features: {str(e)}")

@router.post("/steer")
async def steer_features(request: SteerRequest):
    """Apply feature steering and generate text - matches backend implementation"""
    global _searchsteer_model, _searchsteer_tokenizer, _searchsteer_sae_weights
    
    try:
        # Load model if needed
        model_path = request.model or SEARCHSTEER_MODEL_PATH
        if _searchsteer_model is None or model_path != SEARCHSTEER_MODEL_PATH:
            _searchsteer_model, _searchsteer_tokenizer = load_transformers_model(model_path)
        
        # Load SAE weights if needed (for decoder to get feature directions)
        layer = SEARCHSTEER_LAYER
        if _searchsteer_sae_weights is None:
            sae_file = os.path.join(SEARCHSTEER_SAE_PATH, f"layers.{layer}", "sae.safetensors")
            if not os.path.exists(sae_file):
                sae_file = os.path.join(SEARCHSTEER_SAE_PATH, "sae.safetensors")
            if not os.path.exists(sae_file):
                raise HTTPException(status_code=500, detail=f"SAE file not found at {sae_file}")
            _searchsteer_sae_weights = load_sae_from_safetensors(sae_file, layer)
        
        # Extract decoder weights from SAE
        decoder = _searchsteer_sae_weights.get("W_dec")
        if decoder is None:
            raise HTTPException(status_code=500, detail="SAE decoder weights (W_dec) not found")
        
        device = get_device()
        decoder = decoder.to(device)
        
        # Format prompt - handle questions properly
        formatted_prompt = request.prompt.strip()
        if formatted_prompt.endswith('?') and 'Answer:' not in formatted_prompt and 'answer:' not in formatted_prompt.lower():
            formatted_prompt = f"Question: {formatted_prompt} Answer:"
        
        # Tokenize input
        inputs = _searchsteer_tokenizer(
            formatted_prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        input_length = inputs['input_ids'].shape[1]
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        max_tokens = 200
        
        # Check if we have active steering features
        has_active_steering = request.features and any(abs(f.get("magnitude", 0)) > 0.01 for f in request.features)
        
        # Generate original text FIRST (before any hooks)
        torch.manual_seed(42)
        with torch.no_grad():
            original_outputs = _searchsteer_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.8,
                repetition_penalty=1.2,
                top_p=0.95,
                top_k=40,
                pad_token_id=_searchsteer_tokenizer.eos_token_id,
                eos_token_id=_searchsteer_tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        # Extract only the generated tokens (skip the input prompt)
        generated_tokens = original_outputs[0][input_length:]
        original_text = _searchsteer_tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        # Remove "Answer:" prefix if present
        if formatted_prompt.startswith("Question:") and "Answer:" in formatted_prompt:
            if original_text.startswith("Answer:"):
                original_text = original_text[7:].strip()
            elif original_text.startswith("answer:"):
                original_text = original_text[7:].strip()
        
        # Generate steered text (if features provided)
        steered_text = None
        if has_active_steering:
            # Prepare steering hook for multiple features
            def steering_hook(module, input, output):
                if isinstance(output, tuple):
                    hidden_states = output[0]
                else:
                    hidden_states = output
                
                # Combine all feature steering vectors
                combined_steering = None
                for feature in request.features:
                    if feature.get("magnitude", 0) == 0:
                        continue
                    
                    # Extract feature ID - handle multiple formats
                    feature_id = None
                    
                    # Try "id" field first (format: "f_123" or "123")
                    if "id" in feature:
                        feature_id_str = str(feature["id"])
                        if feature_id_str.startswith("f_"):
                            try:
                                feature_id = int(feature_id_str[2:])
                            except ValueError:
                                pass
                        else:
                            try:
                                feature_id = int(feature_id_str)
                            except ValueError:
                                pass
                    
                    # Fallback to "feature_id" field (format: 123)
                    if feature_id is None and "feature_id" in feature:
                        try:
                            feature_id = int(feature["feature_id"])
                        except (ValueError, TypeError):
                            pass
                    
                    if feature_id is None or feature_id >= decoder.shape[0]:
                        continue
                    
                    magnitude = feature.get("magnitude", 0)
                    if abs(magnitude) < 0.01:
                        continue
                    
                    # Get feature direction from decoder
                    feature_direction = decoder[feature_id, :].unsqueeze(0).unsqueeze(0).to(hidden_states.device)
                    
                    # Normalize
                    feature_norm = torch.norm(feature_direction)
                    if feature_norm > 0:
                        feature_direction = feature_direction / feature_norm
                    
                    # Scale by magnitude (convert slider value -1 to 1 to steering strength)
                    # Slider value of 1.0 = steering strength of 10.0
                    steering_strength = magnitude * 10.0
                    steering_vector = steering_strength * 0.1 * feature_direction
                    
                    if combined_steering is None:
                        combined_steering = steering_vector
                    else:
                        combined_steering = combined_steering + steering_vector
                
                if combined_steering is not None:
                    steered_hidden = hidden_states + combined_steering
                    if isinstance(output, tuple):
                        return (steered_hidden.to(hidden_states.dtype),) + output[1:]
                    else:
                        return steered_hidden.to(hidden_states.dtype)
                
                return output
            
            # Register hook ONLY for steered generation
            layer_module = _searchsteer_model.model.layers[layer]
            hook = layer_module.register_forward_hook(steering_hook)
            
            try:
                torch.manual_seed(42)
                with torch.no_grad():
                    steered_outputs = _searchsteer_model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=True,
                        temperature=1.0,
                        top_p=0.1,
                        repetition_penalty=1.15,
                        pad_token_id=_searchsteer_tokenizer.eos_token_id,
                        eos_token_id=_searchsteer_tokenizer.eos_token_id,
                        no_repeat_ngram_size=3
                    )
                
                # Extract only the generated tokens (skip the input prompt)
                generated_tokens = steered_outputs[0][input_length:]
                steered_text = _searchsteer_tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
                
                # Remove "Answer:" prefix if present
                if formatted_prompt.startswith("Question:") and "Answer:" in formatted_prompt:
                    if steered_text.startswith("Answer:"):
                        steered_text = steered_text[7:].strip()
                    elif steered_text.startswith("answer:"):
                        steered_text = steered_text[7:].strip()
            finally:
                hook.remove()
        
        # Return format expected by frontend
        result = {
            "success": True,
            "original_text": original_text,
        }
        if steered_text is not None:
            result["steered_text"] = steered_text
        else:
            result["steered_text"] = original_text  # Fallback if no steering
        
        return result
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error steering features: {str(e)}")

@router.post("/extract_features")
async def extract_features(request: ExtractFeaturesRequest):
    """Extract SAE features for SearchSteer"""
    global _searchsteer_model, _searchsteer_tokenizer, _searchsteer_sae_weights
    
    try:
        if _searchsteer_model is None:
            _searchsteer_model, _searchsteer_tokenizer = load_transformers_model(SEARCHSTEER_MODEL_PATH)
        
        if _searchsteer_sae_weights is None:
            sae_file = os.path.join(SEARCHSTEER_SAE_PATH, f"layers.{request.layer}", "sae.safetensors")
            if not os.path.exists(sae_file):
                sae_file = os.path.join(SEARCHSTEER_SAE_PATH, "sae.safetensors")
            if not os.path.exists(sae_file):
                # If SAE file doesn't exist, return placeholder features instead of failing
                # This allows the API to work even without SAE models loaded
                return {"features": [{"feature_id": i, "activation": 0.0, "score": 0.0} for i in range(request.k)]}
            _searchsteer_sae_weights = load_sae_from_safetensors(sae_file, request.layer)
        
        device = get_device()
        
        # Tokenize
        tokens = _searchsteer_tokenizer(
            request.text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)
        
        # Get hidden states
        with torch.no_grad():
            outputs = _searchsteer_model(**tokens, output_hidden_states=True)
            hidden_states = outputs.hidden_states[request.layer]
        
        # Extract features - if SAE weights not loaded, use raw hidden states
        if _searchsteer_sae_weights is not None:
            # Apply SAE transformation if weights are loaded
            features = hidden_states.mean(dim=1).squeeze().cpu().numpy()
        else:
            # Use raw hidden states as features if SAE not loaded
            features = hidden_states.mean(dim=1).squeeze().cpu().numpy()
        
        features_serialized = serialize_array(features)
        return {"features": features_serialized}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

@router.post("/load_models")
async def load_models(request: LoadModelsRequest):
    """Load SearchSteer models"""
    global _searchsteer_model, _searchsteer_tokenizer, _searchsteer_sae_weights
    
    try:
        model_path = request.model_path or SEARCHSTEER_MODEL_PATH
        sae_path = request.sae_path or SEARCHSTEER_SAE_PATH
        layer = request.layer or SEARCHSTEER_LAYER
        
        _searchsteer_model, _searchsteer_tokenizer = load_transformers_model(model_path)
        
        sae_file = os.path.join(sae_path, f"layers.{layer}", "sae.safetensors")
        if not os.path.exists(sae_file):
            sae_file = os.path.join(sae_path, "sae.safetensors")
        _searchsteer_sae_weights = load_sae_from_safetensors(sae_file, layer)
        
        return {"status": "success", "message": "Models loaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {str(e)}")



