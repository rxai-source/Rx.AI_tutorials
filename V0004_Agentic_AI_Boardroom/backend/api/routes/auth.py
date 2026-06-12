# backend/api/routes/auth.py
"""
Authentication routes.

POST /auth/token — issue a JWT access token.

In a production system, replace the stub user check with a real database lookup.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext

from api.schemas import TokenRequest, TokenResponse
from core.security import create_access_token
from core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# STUB user store — replace with a real DB in production
# ---------------------------------------------------------------------------
STUB_USERS: dict[str, str] = {
    "admin": pwd_context.hash("boardroom2024"),
    "demo": pwd_context.hash("demo1234"),
}


@router.post("/token", response_model=TokenResponse)
async def login(payload: TokenRequest) -> TokenResponse:
    """Issue a JWT token given valid credentials."""
    hashed = STUB_USERS.get(payload.username)
    if not hashed or not pwd_context.verify(payload.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": payload.username},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )
    return TokenResponse(access_token=token)
