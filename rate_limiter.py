import time
import redis
from typing import Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token Bucket Rate Limiter using Redis for distributed rate limiting.

    TOKEN BUCKET ALGORITHM:
    - Each user/IP has a "bucket" with a maximum capacity of tokens
    - Tokens are added to the bucket at a constant rate
    - Each request consumes 1 token
    - If bucket is empty, request is rejected

    Why Token Bucket?
    - Allows burst traffic (bucket can accumulate tokens)
    - Smooth rate limiting over time
    - Easy to implement and understand
    - Works well in distributed systems with Redis

    Example with 100 requests/minute:
    - Bucket capacity: 100 tokens
    - Refill rate: 100 tokens per minute (1.67 tokens/second)
    - User can make 100 requests immediately, then must wait
    - Or spread them out over the minute
    """

    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
            self.use_redis = False
            # In-memory fallback
            self.buckets: Dict[str, Dict[str, float]] = {}  # {identifier: {tokens: int, last_refill: float}}

        self.max_tokens = settings.rate_limit_requests
        self.refill_rate = settings.rate_limit_requests / settings.rate_limit_window_seconds  # tokens per second

    def _get_bucket_key(self, identifier: str) -> str:
        """Generate Redis key for rate limit bucket"""
        return f"rate_limit:{identifier}"

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed based on token bucket algorithm.

        This implements the distributed token bucket using Redis atomic operations:
        1. Get current bucket state (tokens, last refill time)
        2. Calculate tokens to add based on time elapsed
        3. Update bucket with new token count
        4. Check if tokens available for request

        Uses Redis Lua script for atomicity to avoid race conditions.
        """
        if self.use_redis:
            return self._is_allowed_redis(identifier)
        else:
            return self._is_allowed_memory(identifier)

    def _is_allowed_redis(self, identifier: str) -> bool:
        """Redis-based rate limiting with Lua script for atomicity"""
        bucket_key = self._get_bucket_key(identifier)
        current_time = time.time()

        # Lua script for atomic token bucket operations
        lua_script = """
        local key = KEYS[1]
        local current_time = tonumber(ARGV[1])
        local max_tokens = tonumber(ARGV[2])
        local refill_rate = tonumber(ARGV[3])

        -- Get current bucket state
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1])
        local last_refill = tonumber(bucket[2])

        -- Initialize if doesn't exist
        if tokens == nil then
            tokens = max_tokens
            last_refill = current_time
        end

        -- Calculate tokens to add based on time elapsed
        local time_elapsed = current_time - last_refill
        local tokens_to_add = time_elapsed * refill_rate

        -- Update tokens (don't exceed max)
        tokens = math.min(max_tokens, tokens + tokens_to_add)

        -- Check if request can be served
        if tokens >= 1 then
            -- Consume 1 token
            tokens = tokens - 1
            -- Update bucket state
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
            redis.call('EXPIRE', key, 3600)  -- Expire after 1 hour
            return 1  -- Allowed
        else
            -- Update bucket state anyway
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
            redis.call('EXPIRE', key, 3600)
            return 0  -- Denied
        end
        """

        try:
            result = self.redis_client.eval(
                lua_script,
                1,  # Number of keys
                bucket_key,
                current_time,
                self.max_tokens,
                self.refill_rate
            )

            return result == 1

        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return True

    def _is_allowed_memory(self, identifier: str) -> bool:
        """In-memory fallback for rate limiting (not distributed)"""
        current_time = time.time()

        # Get or create bucket
        if identifier not in self.buckets:
            self.buckets[identifier] = {
                'tokens': self.max_tokens,
                'last_refill': current_time
            }

        bucket = self.buckets[identifier]

        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket['last_refill']
        tokens_to_add = time_elapsed * self.refill_rate

        # Update tokens (don't exceed max)
        bucket['tokens'] = min(self.max_tokens, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time

        # Check if request can be served
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        else:
            return False

    def get_remaining_tokens(self, identifier: str) -> int:
        """Get remaining tokens for a user/IP (for monitoring/debugging)"""
        if self.use_redis:
            bucket_key = self._get_bucket_key(identifier)
            try:
                bucket = self.redis_client.hmget(bucket_key, 'tokens', 'last_refill')
                tokens = int(bucket[0]) if bucket[0] else self.max_tokens
                return max(0, min(tokens, self.max_tokens))
            except Exception as e:
                logger.error(f"Error getting remaining tokens: {e}")
                return self.max_tokens
        else:
            if identifier in self.buckets:
                return max(0, int(self.buckets[identifier]['tokens']))
            return self.max_tokens

    def reset_bucket(self, identifier: str) -> None:
        """Reset rate limit bucket (for testing/admin)"""
        if self.use_redis:
            bucket_key = self._get_bucket_key(identifier)
            try:
                self.redis_client.delete(bucket_key)
            except Exception as e:
                logger.error(f"Error resetting bucket: {e}")
        else:
            if identifier in self.buckets:
                del self.buckets[identifier]
