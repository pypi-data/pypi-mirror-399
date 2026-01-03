"""
Simple test script for neuronlens package.
Tests against ngrok URL with API key authentication.
"""
import os
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path, override=True)

# Get API key and URL
NEURONLENS_API_KEY = os.getenv("API_KEY")
if not NEURONLENS_API_KEY:
    raise ValueError("API_KEY not found in .env file")

# Get ngrok URL
def get_ngrok_url():
    ngrok_file = Path(__file__).parent.parent / ".ngrok_url"
    if ngrok_file.exists():
        return open(ngrok_file).read().strip()
    try:
        import requests
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2).json().get("tunnels", [])
        if tunnels:
            return tunnels[0].get("public_url", "")
    except:
        pass
    return os.getenv("API_URL")

API_URL = get_ngrok_url()
if not API_URL:
    raise ValueError("No ngrok URL found. Please start ngrok or set API_URL in .env")

# Use neuronlens
import neuronlens
engine = neuronlens.Engine(api_key=NEURONLENS_API_KEY, api_url=API_URL)

# Simple test
result = engine.analyze_slm_sentiment("Strong quarterly earnings exceeded expectations", top_n=5)
print(f"Sentiment: {result['sentiment']['predicted_label']}")
print(f"Confidence: {result['sentiment']['confidence']:.3f}")
