"""
Simple test script for neuronlens package.
"""
import os
from pathlib import Path
import neuronlens

# Load .env file from parent directory (cloud_api/.env)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
    except ImportError:
        print("Warning: python-dotenv not installed. Install with: pip install neuronlens[all]")

# Get API key from environment
NEURONLENS_API_KEY = os.getenv("API_KEY")
if not NEURONLENS_API_KEY:
    raise ValueError("API_KEY not found in .env file. Please add API_KEY=your_key to cloud_api/.env")

engine = neuronlens.Engine(api_key=NEURONLENS_API_KEY)

result = engine.analyze_slm_sentiment("Strong quarterly earnings exceeded expectations", top_n=5)
print(f"Sentiment: {result['sentiment']['predicted_label']}")
print(f"Confidence: {result['sentiment']['confidence']:.3f}")
