"""
NumPy array serialization utilities.
Handles small, medium, and large arrays with appropriate methods.
"""
import numpy as np
import base64
import json
from typing import Dict, Any, Union

def serialize_array(arr: np.ndarray, max_size_mb: int = 1) -> Dict[str, Any]:
    """
    Serialize numpy array based on size.
    
    Args:
        arr: NumPy array to serialize
        max_size_mb: Maximum size in MB for base64 encoding (default 1MB)
    
    Returns:
        Dictionary with serialization info:
        - type: "base64" or "file"
        - data: base64 encoded string (if type="base64")
        - size: size in bytes (if type="file")
        - shape: array shape
        - dtype: array dtype as string
    """
    size_mb = arr.nbytes / (1024 * 1024)
    
    if size_mb < max_size_mb:
        # Small arrays: base64 encode
        return {
            "type": "base64",
            "data": base64.b64encode(arr.tobytes()).decode('utf-8'),
            "shape": list(arr.shape),
            "dtype": str(arr.dtype)
        }
    else:
        # Large arrays: indicate file upload needed
        return {
            "type": "file",
            "size": arr.nbytes,
            "shape": list(arr.shape),
            "dtype": str(arr.dtype)
        }

def deserialize_array(data: Dict[str, Any]) -> np.ndarray:
    """
    Deserialize numpy array from dictionary.
    
    Args:
        data: Dictionary with serialization info
    
    Returns:
        NumPy array
    """
    if data["type"] == "base64":
        arr_bytes = base64.b64decode(data["data"])
        arr = np.frombuffer(arr_bytes, dtype=np.dtype(data["dtype"]))
        return arr.reshape(data["shape"])
    else:
        raise ValueError("File-based deserialization not yet implemented. Use base64 for now.")

def serialize_for_json(obj: Any) -> Any:
    """
    Recursively serialize objects for JSON compatibility.
    Converts numpy arrays, numpy scalars, etc.
    """
    if isinstance(obj, np.ndarray):
        return serialize_array(obj)
    elif isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: serialize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj

