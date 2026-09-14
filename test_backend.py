"""
Simple test backend service for testing the API Gateway.
Run this on port 8001 to test the gateway.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="Test Backend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Sample user endpoint"""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "service": "backend-1"
    }


@app.post("/users")
async def create_user(user_data: dict):
    """Sample create user endpoint"""
    return {
        "user_id": 123,
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "service": "backend-1"
    }


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Sample order endpoint"""
    return {
        "order_id": order_id,
        "user_id": 123,
        "total": 99.99,
        "status": "completed",
        "service": "backend-2"
    }


@app.get("/slow")
async def slow_endpoint():
    """Endpoint that takes time to test timeouts"""
    time.sleep(2)
    return {"message": "This was slow!"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "test-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)