"""
Test JWT authentication functionality independently
"""
from auth import create_access_token, verify_jwt_token
import time

def test_jwt_creation_and_verification():
    """Test JWT token creation and verification"""
    print("=== Testing JWT Authentication ===\n")

    # Create test user data
    user_data = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "role": "user"
    }

    print(f"Creating token for user: {user_data}")
    token = create_access_token(user_data)
    print(f"Token created: {token[:50]}...")
    print(f"Full token: {token}\n")

    # Verify the token
    print("Verifying token...")
    verified_data = verify_jwt_token(f"Bearer {token}")

    if verified_data:
        print("Token verification successful!")
        print(f"Verified user data: {verified_data}")
    else:
        print("Token verification failed!")

    # Test with invalid token
    print("\nTesting with invalid token...")
    invalid_result = verify_jwt_token("Bearer invalid_token_12345")
    if invalid_result is None:
        print("Invalid token correctly rejected")
    else:
        print("Invalid token was incorrectly accepted")

    # Test with expired token (create one with very short expiration)
    print("\nTesting token expiration...")
    from datetime import timedelta
    expired_token = create_access_token(user_data, expires_delta=timedelta(seconds=-1))
    expired_result = verify_jwt_token(f"Bearer {expired_token}")
    if expired_result is None:
        print("Expired token correctly rejected")
    else:
        print("Expired token was incorrectly accepted")

if __name__ == "__main__":
    test_jwt_creation_and_verification()
