"""
Test rate limiting functionality independently
"""
from rate_limiter import RateLimiter
import time

def test_rate_limiter():
    """Test rate limiting with in-memory fallback"""
    print("=== Testing Rate Limiter ===\n")
    
    # Initialize rate limiter (will use in-memory since Redis might not be available)
    rate_limiter = RateLimiter()
    
    # Test basic rate limiting
    print("Testing basic rate limiting (10 requests per 60 seconds)...")
    user_id = "test_user_123"
    
    # Make 10 requests (should all be allowed)
    allowed_count = 0
    denied_count = 0
    for i in range(10):
        if rate_limiter.is_allowed(user_id):
            allowed_count += 1
            print(f"Request {i+1}: Allowed")
        else:
            denied_count += 1
            print(f"Request {i+1}: Denied")
    
    print(f"\nResults: {allowed_count} allowed, {denied_count} denied")
    
    # Next request should be denied
    print("\nTesting request beyond limit...")
    if rate_limiter.is_allowed(user_id):
        print("Request was allowed (unexpected)")
    else:
        print("Request was correctly denied (rate limit exceeded)")
    
    # Check remaining tokens
    remaining = rate_limiter.get_remaining_tokens(user_id)
    print(f"Remaining tokens: {remaining}")
    
    # Test with different user (should have fresh bucket)
    print("\nTesting with different user ID...")
    user_id_2 = "test_user_456"
    if rate_limiter.is_allowed(user_id_2):
        print("Request for new user allowed (correct)")
    else:
        print("Request for new user denied (unexpected)")
    
    # Test bucket reset
    print("\nTesting bucket reset...")
    rate_limiter.reset_bucket(user_id)
    remaining_after_reset = rate_limiter.get_remaining_tokens(user_id)
    print(f"Remaining tokens after reset: {remaining_after_reset}")
    
    if rate_limiter.is_allowed(user_id):
        print("Request after reset allowed (correct)")
    else:
        print("Request after reset denied (unexpected)")

if __name__ == "__main__":
    test_rate_limiter()