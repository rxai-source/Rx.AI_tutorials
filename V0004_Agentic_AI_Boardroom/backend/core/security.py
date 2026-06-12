# backend/core/security.py
"""
JWT creation and validation utilities.
Also handles WebSocket JWT extraction from the Sec-WebSocket-Protocol header.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status

from core.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT. Raises HTTPException on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# WebSocket JWT extraction
# ---------------------------------------------------------------------------

def extract_jwt_from_ws_protocol(protocols: list[str]) -> Optional[str]:
    """
    Extract JWT token from the Sec-WebSocket-Protocol header.

    Convention:
        Sec-WebSocket-Protocol: bearer, <jwt_token>

    The client must send both values; the server echoes back "bearer" as the
    selected sub-protocol and reads the token from the second element.
    """
    if not protocols:
        return None

    # Look for the pattern: ["bearer", "<token>"]
    for i, proto in enumerate(protocols):
        if proto.lower() == "bearer" and i + 1 < len(protocols):
            return protocols[i + 1]

    # Fallback: if only one element and it looks like a JWT
    if len(protocols) == 1 and "." in protocols[0]:
        return protocols[0]

    return None


def validate_ws_token(protocols: list[str]) -> dict:
    """
    Validate a JWT embedded in the WebSocket sub-protocol header.
    Returns the decoded payload or raises HTTPException.
    """
    token = extract_jwt_from_ws_protocol(protocols)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing JWT in Sec-WebSocket-Protocol header",
        )
    return decode_access_token(token)
