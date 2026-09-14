from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from config import settings
from auth import verify_jwt_token, create_access_token
from rate_limiter import RateLimiter
from proxy import proxy_request
from prometheus_client import generate_latest
from metrics import metrics_registry

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
rate_limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting API Gateway...")
    logger.info(f"Backend services: {settings.backend_services_list}")
    yield
    # Shutdown
    logger.info("Shutting down API Gateway...")


# Create FastAPI app
app = FastAPI(
    title="Production API Gateway",
    description="API Gateway with JWT Auth, Rate Limiting, and Metrics",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-gateway"}


@app.post("/token")
async def get_token():
    """Generate a test JWT token for demo purposes"""
    user_data = {
        "user_id": "demo_user",
        "email": "demo@example.com",
        "role": "user"
    }
    token = create_access_token(user_data)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(metrics_registry), media_type="text/plain")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_handler(request: Request, path: str):
    """
    Main gateway handler that processes all requests through:
    1. JWT Authentication
    2. Rate Limiting
    3. Request Proxying
    4. Response Logging
    """
    client_ip = request.client.host
    request_id = request.headers.get("X-Request-ID", "unknown")

    logger.info(f"Request {request_id}: {request.method} {path} from {client_ip}")

    try:
        # Skip auth, rate limiting, and proxying for health/token/metrics endpoints
        public_endpoints = ["health", "token", "metrics"]

        if path not in public_endpoints:
            # Step 1: JWT Authentication
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Missing authorization header")

            user_data = verify_jwt_token(auth_header)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            request.state.user = user_data
            logger.info(f"Request {request_id}: Authenticated user {user_data.get('user_id')}")

            # Step 2: Rate Limiting
            identifier = request.state.user.get("user_id") if hasattr(request.state, "user") else client_ip
            if not rate_limiter.is_allowed(identifier):
                logger.warning(f"Request {request_id}: Rate limit exceeded for {identifier}")
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )

            # Step 3: Proxy the request to backend service
            response = await proxy_request(request, path)

            # Step 4: Log response
            logger.info(f"Request {request_id}: Completed with status {response.get('status_code', 'unknown')}")

            return response
        else:
            return {"message": "Gateway endpoint"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request {request_id}: Error - {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=True
    )
