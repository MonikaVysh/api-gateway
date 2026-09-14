"""
Test script to demonstrate API Gateway functionality.
This script tests JWT auth, rate limiting, and proxying.
"""
import requests
import time
import json
from auth import create_access_token

# Gateway configuration
GATEWAY_URL = "http://localhost:8000"


def test_health_check():
    """Test gateway health endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{GATEWAY_URL}/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")


def test_jwt_token_creation():
    """Test JWT token creation"""
    print("\n=== Testing JWT Token Creation ===")
    
    # Create a sample token
    user_data = {
        "user_id": "12345",
        "email": "user@example.com",
        "role": "user"
    }
    
    token = create_access_token(user_data)
    print(f"Generated JWT token: {token[:50]}...")
    print(f"Full token: {token}")
    
    return token


def test_authenticated_request(token):
    """Test authenticated request through gateway"""
    print("\n=== Testing Authenticated Request ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Try to access a protected endpoint
        response = requests.get(
            f"{GATEWAY_URL}/api/v1/users/123",
            headers=headers
        )
        print(f"Authenticated request status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Request failed (backend might not be running): {e}")


def test_rate_limiting(token):
    """Test rate limiting functionality"""
    print("\n=== Testing Rate Limiting ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Make multiple requests to test rate limiting
    print("Making 10 rapid requests...")
    for i in range(10):
        try:
            response = requests.get(
                f"{GATEWAY_URL}/api/v1/users/123",
                headers=headers,
                timeout=5
            )
            print(f"Request {i+1}: {response.status_code}")
        except Exception as e:
            print(f"Request {i+1}: Failed - {e}")
    
    print("Rate limiting test complete")


def test_unauthenticated_request():
    """Test request without authentication"""
    print("\n=== Testing Unauthenticated Request ===")
    
    try:
        response = requests.get(f"{GATEWAY_URL}/api/v1/users/123")
        print(f"Unauthenticated request status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Request failed: {e}")


def test_metrics():
    """Test metrics endpoint"""
    print("\n=== Testing Metrics Endpoint ===")
    
    response = requests.get(f"{GATEWAY_URL}/metrics")
    print(f"Metrics status: {response.status_code}")
    print("Sample metrics:")
    print(response.text[:500])  # Print first 500 chars


def main():
    """Run all tests"""
    print("API Gateway Test Suite")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test JWT token creation
    token = test_jwt_token_creation()
    
    # Test unauthenticated request (should fail)
    test_unauthenticated_request()
    
    # Test authenticated request
    test_authenticated_request(token)
    
    # Test rate limiting
    test_rate_limiting(token)
    
    # Test metrics
    test_metrics()
    
    print("\n" + "=" * 50)
    print("Test suite complete!")


if __name__ == "__main__":
    main()