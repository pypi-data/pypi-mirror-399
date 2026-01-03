"""Minimal SLM Lens API test script - tests via ngrok URL"""
import requests
import os
from pathlib import Path

# Load .env file from parent directory (cloud_api/.env)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
    except ImportError:
        print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
else:
    print(f"Warning: .env file not found at {env_path}")

# Get API key from .env file
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file. Please add API_KEY=your_key to cloud_api/.env")

# Get ngrok URL from file or ngrok API
def get_ngrok_url():
    # Try reading from .ngrok_url file first
    ngrok_file = Path(__file__).parent.parent / ".ngrok_url"
    if ngrok_file.exists():
        with open(ngrok_file) as f:
            url = f.read().strip()
            if url:
                return url
    
    # Fallback: try ngrok API
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if response.status_code == 200:
            tunnels = response.json().get("tunnels", [])
            if tunnels:
                return tunnels[0].get("public_url", "")
    except:
        pass
    
    return os.getenv("API_URL", "http://localhost:8000")

API_URL = get_ngrok_url()

print(f"Testing API at: {API_URL}")
print(f"Using API Key: {API_KEY[:10]}...{API_KEY[-4:] if len(API_KEY) > 14 else 'XXXX'}")

r = requests.post(
    f"{API_URL}/slm_lens",
    headers={"X-API-Key": API_KEY},
    json={"action": "analyze_sentiment", "text": "Strong quarterly earnings exceeded expectations", "top_n": 10}
)
print(r.json())

