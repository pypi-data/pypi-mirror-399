#!/usr/bin/env python3
"""
Test script for API key authentication.
Tests various authentication scenarios.
"""
import requests
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Default API URL (can be overridden with environment variable)
API_URL = os.environ.get("API_URL", "http://localhost:8000")
TEST_API_KEY = os.environ.get("TEST_API_KEY", "nlive_XXXX")  # Replace with a valid API key from your database

def test_health_endpoint():
    """Test that health endpoint works without authentication."""
    print("\n🧪 Test 1: Health endpoint (no auth required)")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, "Health endpoint should return 200"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_missing_api_key():
    """Test that requests without API key are rejected."""
    print("\n🧪 Test 2: Missing API key (should fail)")
    try:
        # Try to access a protected endpoint without API key
        response = requests.get(f"{API_URL}/cot/generate")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 401, "Should return 401 Unauthorized"
        assert "Missing API Key" in response.json().get("error", ""), "Should mention missing API key"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_invalid_api_key():
    """Test that invalid API keys are rejected."""
    print("\n🧪 Test 3: Invalid API key (should fail)")
    try:
        response = requests.get(
            f"{API_URL}/health",
            headers={"X-API-Key": "invalid_key_12345"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 401, "Should return 401 Unauthorized"
        assert "Invalid" in response.json().get("error", ""), "Should mention invalid API key"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def test_valid_api_key_header():
    """Test that valid API key in header works."""
    print("\n🧪 Test 4: Valid API key in X-API-Key header")
    try:
        response = requests.get(
            f"{API_URL}/health",
            headers={"X-API-Key": TEST_API_KEY}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, "Should return 200 OK with valid key"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        print(f"   ⚠️  Note: Make sure TEST_API_KEY is set to a valid key from your database")
        return False

def test_api_key_query_param():
    """Test that API key in query parameter works (fallback)."""
    print("\n🧪 Test 5: API key in query parameter (fallback)")
    try:
        response = requests.get(
            f"{API_URL}/health?api_key={TEST_API_KEY}"
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, "Should return 200 OK with valid key in query param"
        print("   ✅ PASSED")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        print(f"   ⚠️  Note: Make sure TEST_API_KEY is set to a valid key from your database")
        return False

def test_protected_endpoint():
    """Test accessing a protected endpoint with valid API key."""
    print("\n🧪 Test 6: Protected endpoint with valid API key")
    try:
        # Try accessing a real endpoint (even if it fails due to missing params, auth should work)
        response = requests.post(
            f"{API_URL}/cot/generate",
            headers={"X-API-Key": TEST_API_KEY},
            json={"prompt": "test"}
        )
        print(f"   Status: {response.status_code}")
        # Should not be 401 (auth should pass, even if endpoint returns error for other reasons)
        assert response.status_code != 401, "Should not return 401 (auth passed)"
        print(f"   ✅ PASSED (Auth successful, endpoint returned {response.status_code})")
        return True
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False

def main():
    """Run all authentication tests."""
    print("=" * 60)
    print("API Key Authentication Test Suite")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Test API Key: {TEST_API_KEY[:10]}..." if len(TEST_API_KEY) > 10 else f"Test API Key: {TEST_API_KEY}")
    print("=" * 60)
    
    tests = [
        test_health_endpoint,
        test_missing_api_key,
        test_invalid_api_key,
        test_valid_api_key_header,
        test_api_key_query_param,
        test_protected_endpoint,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


