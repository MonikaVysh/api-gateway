from rate_limiter import RateLimiter

# Test rate limiter initialization
print("Initializing rate limiter...")
rate_limiter = RateLimiter()
print(f"Using Redis: {rate_limiter.use_redis}")

# Test basic functionality
print("\nTesting rate limiting...")
user_id = "test_user"
result1 = rate_limiter.is_allowed(user_id)
print(f"First request: {result1}")

result2 = rate_limiter.is_allowed(user_id)
print(f"Second request: {result2}")

remaining = rate_limiter.get_remaining_tokens(user_id)
print(f"Remaining tokens: {remaining}")

print("Rate limiter test completed")