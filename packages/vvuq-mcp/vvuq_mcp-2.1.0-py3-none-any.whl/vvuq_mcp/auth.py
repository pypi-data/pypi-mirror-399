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

from vvuq_mcp.secret_manager import get_secret

# API Key header name
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_keys() -> set[str]:
    """
    Load valid API keys from environment.
    
    Returns:
        Set of valid API keys
    """
    # Primary API key from Secret Manager (or env)
    primary_key = get_secret("vvuq-api-key")
    
    # Additional keys (comma-separated list from Secret Manager)
    # We store the list directly in the secret "axiomatic-api-key" for now,
    # or potentially "vvuq-allowed-keys" if created later.
    # The user specifically asked for "axiomatic_api_key" from secrets.
    axiomatic_key = get_secret("axiomatic-api-key")
    
    # Additional keys from environment (legacy support)
    additional_keys_env = os.getenv("VVUQ_API_KEYS", "")
    
    keys = set()
    if primary_key:
        keys.add(primary_key)
    
    if axiomatic_key:
        keys.add(axiomatic_key)
    
    if additional_keys_env:
        for key in additional_keys_env.split(","):
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
