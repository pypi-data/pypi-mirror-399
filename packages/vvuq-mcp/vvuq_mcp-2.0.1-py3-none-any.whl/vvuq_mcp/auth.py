"""
API Key Authentication for VVUQ HTTP API

Provides secure API key validation using FastAPI security utilities.
Keys are stored in environment variables for security.
"""

import os
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# API Key header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_keys() -> set[str]:
    """
    Load valid API keys from environment.
    
    Returns:
        Set of valid API keys
    """
    # Primary API key from environment
    primary_key = os.getenv("VVUQ_API_KEY")
    
    # Additional keys (comma-separated)
    additional_keys = os.getenv("VVUQ_API_KEYS", "")
    
    keys = set()
    if primary_key:
        keys.add(primary_key)
    
    if additional_keys:
        for key in additional_keys.split(","):
            key = key.strip()
            if key:
                keys.add(key)
    
    return keys


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        Valid API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    valid_keys = get_api_keys()
    
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No API keys configured. Set VVUQ_API_KEY environment variable."
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header."
        )
    
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return api_key


def generate_api_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure API key.
    
    Args:
        length: Length of the key in bytes (will be hex-encoded to 2x length)
        
    Returns:
        Hex-encoded API key
    """
    return secrets.token_hex(length)


if __name__ == "__main__":
    # Generate a new API key when run directly
    print("=" * 70)
    print("🔑 VVUQ API Key Generator")
    print("=" * 70)
    print()
    
    key = generate_api_key()
    print(f"Generated API Key: {key}")
    print()
    print("Add this to your .env file:")
    print(f"VVUQ_API_KEY={key}")
    print()
    print("=" * 70)
