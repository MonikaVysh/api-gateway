import time
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Create a custom registry for our metrics
metrics_registry = CollectorRegistry()

# Request counter - tracks total requests
request_counter = Counter(
    'api_gateway_requests_total',
    'Total number of requests processed by the gateway',
    ['method', 'status', 'endpoint'],
    registry=metrics_registry
)

# Request latency histogram - tracks request duration
request_latency = Histogram(
    'api_gateway_request_duration_seconds',
    'Request processing duration in seconds',
    ['endpoint'],
    registry=metrics_registry
)

# Active connections gauge - tracks concurrent connections
active_connections = Gauge(
    'api_gateway_active_connections',
    'Number of active connections',
    registry=metrics_registry
)

# Rate limit counter - tracks rate limit violations
rate_limit_counter = Counter(
    'api_gateway_rate_limit_denied_total',
    'Total number of requests denied due to rate limiting',
    ['identifier'],
    registry=metrics_registry
)

# Backend service health gauge
backend_health = Gauge(
    'api_gateway_backend_health',
    'Backend service health status (1=healthy, 0=unhealthy)',
    ['service'],
    registry=metrics_registry
)


class RequestMetrics:
    """Context manager for tracking request metrics"""

    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        active_connections.inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        active_connections.dec()

        # Record latency
        request_latency.labels(endpoint=self.endpoint).observe(duration)

        # Determine status code
        if exc_type is not None:
            status_code = 500
        else:
            status_code = 200  # This should be set from response

        # Record request count
        request_counter.labels(
            method=self.method,
            status=status_code,
            endpoint=self.endpoint
        ).inc()

        return False  # Don't suppress exceptions


def record_rate_limit_violation(identifier: str) -> None:
    """Record a rate limit violation"""
    rate_limit_counter.labels(identifier=identifier).inc()


def update_backend_health(service: str, healthy: bool) -> None:
    """Update backend service health status"""
    backend_health.labels(service=service).set(1 if healthy else 0)
