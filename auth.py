from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    JWT (JSON Web Token) is a compact, URL-safe means of representing claims
    to be transferred between two parties. In our case, it's used for authentication.

    Structure: Header.Payload.Signature
    - Header: Algorithm and token type
    - Payload: Claims (user data, expiration, etc.)
    - Signature: Cryptographic signature to verify authenticity
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)

    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    This function:
    1. Checks if the token signature is valid (not tampered)
    2. Decodes the payload to extract user data
    3. Checks if the token has expired

    Returns None if token is invalid or expired.
    """
    try:
        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        return payload

    except JWTError as e:
        # Token is invalid or expired
        logger.debug(f"JWT verification failed: {e}")
        return None


# Password hashing functions (included for future use)
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
