# Production API Gateway

A production-grade API Gateway built with FastAPI, featuring JWT authentication, Redis-backed rate limiting, request proxying, and Prometheus metrics.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication with configurable expiration
- **Rate Limiting**: Token bucket algorithm with Redis for distributed rate limiting
- **Request Proxying**: Route requests to multiple backend services
- **Metrics & Monitoring**: Prometheus metrics for requests, latency, and errors
- **Request Logging**: Comprehensive logging for debugging and monitoring
- **Health Checks**: Health check endpoints for monitoring
- **CORS Support**: Configurable CORS middleware

## 🏗️ Architecture

```
Client → API Gateway → Backend Services
         ↓
    [JWT Auth]
    [Rate Limiting]
    [Request Logging]
    [Metrics Collection]
         ↓
         Redis (Rate Limiting)
```

## 📋 Prerequisites

- Python 3.8+
- Redis server
- Docker (optional, for containerization)

## 🛠️ Installation

1. Clone the repository and navigate to the project directory:
```bash
cd api-gateway
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start Redis server:
```bash
# Using Docker
docker run -d -p 6379:6379 redis

# Or install Redis locally
# Windows: Download from https://redis.io/download
# Mac: brew install redis && brew services start redis
# Linux: sudo apt-get install redis-server && sudo systemctl start redis
```

## 🚀 Running the Gateway

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Docker
```bash
docker build -t api-gateway .
docker run -p 8000:8000 --env-file .env api-gateway
```

## 🧪 Testing

### Start Test Backend Service
```bash
python test_backend.py
```

### Run Gateway Tests
```bash
python test_gateway.py
```

### Manual Testing with cURL

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Generate JWT Token:**
```python
from auth import create_access_token
token = create_access_token({"user_id": "123", "email": "user@example.com"})
print(token)
```

**Authenticated Request:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/users/123
```

**View Metrics:**
```bash
curl http://localhost:8000/metrics
```

## 📊 Metrics

The gateway exposes Prometheus metrics at `/metrics`:

- `api_gateway_requests_total`: Total requests processed
- `api_gateway_request_duration_seconds`: Request processing duration
- `api_gateway_active_connections`: Current active connections
- `api_gateway_rate_limit_denied_total`: Rate limit violations
- `api_gateway_backend_health`: Backend service health status

## 🔧 Configuration

Key environment variables (see `.env.example`):

- `GATEWAY_HOST`: Gateway host address (default: 0.0.0.0)
- `GATEWAY_PORT`: Gateway port (default: 8000)
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_WINDOW_SECONDS`: Time window in seconds (default: 60)
- `BACKEND_SERVICES`: Comma-separated list of backend service URLs

## 🎓 Key Concepts

### JWT Authentication
- Uses JSON Web Tokens for stateless authentication
- Tokens contain user claims and expiration time
- Cryptographically signed to prevent tampering

### Token Bucket Rate Limiting
- Each user/IP has a bucket of tokens
- Tokens refill at a constant rate
- Requests consume tokens
- Allows burst traffic while limiting overall rate

### Request Proxying
- Routes requests to appropriate backend services
- Preserves HTTP method, headers, and body
- Handles timeouts and connection errors
- Supports path-based routing

## 🚀 Production Deployment

For production deployment:

1. **Security**: Use strong JWT secret keys and HTTPS
2. **Scaling**: Run multiple gateway instances behind a load balancer
3. **Monitoring**: Set up Prometheus + Grafana for metrics visualization
4. **Logging**: Use centralized logging (ELK stack, CloudWatch, etc.)
5. **Redis**: Use Redis Cluster for high availability
6. **Circuit Breakers**: Implement circuit breakers for backend services
7. **Service Discovery**: Integrate with Consul, etcd, or Kubernetes service discovery

## 📝 Resume Impact

**Project Description:**
"Designed and implemented a production-grade API Gateway using FastAPI, featuring JWT authentication, Redis-backed distributed rate limiting (token bucket algorithm), request proxying to multiple backend services, and Prometheus metrics collection. The gateway handles cross-cutting concerns including security, rate limiting, observability, and request routing for microservices architectures."

**Key Technologies:**
- FastAPI, Redis, JWT, Prometheus, Docker
- Distributed systems patterns (rate limiting, token bucket)
- Security patterns (JWT authentication)
- Microservices architecture patterns

## 🤝 Contributing

This is a portfolio project. Feel free to fork and enhance with:
- Service discovery integration
- Circuit breaker patterns
- Request/response transformation
- WebSocket support
- GraphQL gateway capabilities

## 📄 License

MIT License