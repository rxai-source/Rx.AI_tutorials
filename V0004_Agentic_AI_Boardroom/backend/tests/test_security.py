# backend/tests/test_security.py
"""
Unit tests for JWT creation, validation, and WebSocket protocol extraction.
"""

import pytest
from datetime import timedelta
from fastapi import HTTPException

from core.security import (
    create_access_token,
    decode_access_token,
    extract_jwt_from_ws_protocol,
    validate_ws_token,
)


def test_create_and_decode_token():
    """Tokens should round-trip through create → decode."""
    token = create_access_token({"sub": "testuser"})
    payload = decode_access_token(token)
    assert payload["sub"] == "testuser"


def test_invalid_token_raises():
    """Invalid token should raise HTTPException 401."""
    with pytest.raises(HTTPException) as exc:
        decode_access_token("not.a.valid.token")
    assert exc.value.status_code == 401


def test_extract_jwt_bearer_protocol():
    """Should extract JWT from ['bearer', '<token>'] pattern."""
    token = create_access_token({"sub": "wsuser"})
    extracted = extract_jwt_from_ws_protocol(["bearer", token])
    assert extracted == token


def test_extract_jwt_single_token():
    """Should extract JWT when only the token is provided (fallback)."""
    token = create_access_token({"sub": "wsuser"})
    extracted = extract_jwt_from_ws_protocol([token])
    assert extracted == token


def test_extract_jwt_empty_protocols():
    """Should return None for empty protocol list."""
    assert extract_jwt_from_ws_protocol([]) is None


def test_validate_ws_token_valid():
    """Valid token in protocol list should return decoded payload."""
    token = create_access_token({"sub": "wsuser"})
    payload = validate_ws_token(["bearer", token])
    assert payload["sub"] == "wsuser"


def test_validate_ws_token_missing_raises():
    """Missing token in protocol list should raise HTTPException 403."""
    with pytest.raises(HTTPException) as exc:
        validate_ws_token([])
    assert exc.value.status_code == 403
