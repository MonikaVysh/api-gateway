"""
Simple test to check imports
"""
print("Testing imports...")

try:
    from config import settings
    print("Config import successful")
    print(f"Rate limit requests: {settings.rate_limit_requests}")
except Exception as e:
    print(f"Config import failed: {e}")

try:
    from auth import create_access_token
    print("Auth import successful")
except Exception as e:
    print(f"Auth import failed: {e}")

try:
    from rate_limiter import RateLimiter
    print("Rate limiter import successful")
    rate_limiter = RateLimiter()
    print(f"Rate limiter initialized, using Redis: {rate_limiter.use_redis}")
except Exception as e:
    print(f"Rate limiter import failed: {e}")

print("All imports completed")