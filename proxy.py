import httpx
from typing import Any
from fastapi import Request
from config import settings
import logging

logger = logging.getLogger(__name__)


async def proxy_request(request: Request, path: str) -> dict[str, Any]:
    """
    Proxy request to backend service.

    This function:
    1. Selects appropriate backend service (round-robin or sticky)
    2. Forwards the request with headers, body, method
    3. Returns the backend response

    In production, you'd want:
    - Service discovery (Consul, etcd)
    - Load balancing strategies
    - Circuit breakers
    - Retry logic
    - Request/response transformation
    """

    # Select backend service (simple round-robin for now)
    backend_url = _select_backend_service(path)

    # Prepare request details
    method = request.method
    headers = dict(request.headers)

    # Remove hop-by-hop headers that shouldn't be forwarded
    hop_by_hop_headers = ['host', 'connection', 'keep-alive', 'transfer-encoding']
    for header in hop_by_hop_headers:
        headers.pop(header, None)

    # Add gateway identification
    headers['X-Gateway-Forwarded-By'] = 'api-gateway'

    # Get request body if present
    body = None
    if method in ['POST', 'PUT', 'PATCH']:
        body = await request.body()

    # Construct target URL
    target_url = f"{backend_url}/{path}"

    logger.info(f"Proxying {method} request to {target_url}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward the request
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )

            # Return response data
            response_data: dict[str, Any] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "backend_service": backend_url
            }
            return response_data

    except httpx.TimeoutException:
        logger.error(f"Timeout proxying to {backend_url}")
        return {
            "status_code": 504,
            "body": {"error": "Backend service timeout"},
            "backend_service": backend_url
        }
    except httpx.ConnectError:
        logger.error(f"Connection error to {backend_url}")
        return {
            "status_code": 503,
            "body": {"error": "Backend service unavailable"},
            "backend_service": backend_url
        }
    except Exception as e:
        logger.error(f"Error proxying request: {e}")
        return {
            "status_code": 500,
            "body": {"error": "Internal proxy error"},
            "backend_service": backend_url
        }


def _select_backend_service(path: str) -> str:
    """
    Select backend service based on path or load balancing.

    Simple implementation:
    - Route based on path prefix
    - Or round-robin among available services

    In production, use:
    - Service discovery
    - Health checks
    - Load balancing algorithms
    - Circuit breakers
    """
    backend_services = settings.backend_services_list

    # Simple path-based routing
    if backend_services and path.startswith('users'):
        return backend_services[0]
    elif len(backend_services) > 1 and path.startswith('orders'):
        return backend_services[1]
    else:
        # Default to first service (or empty list handling)
        return backend_services[0] if backend_services else "http://localhost:8001"
