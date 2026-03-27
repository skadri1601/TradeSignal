"""
Security utilities for authentication and authorization.
"""

import base64
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jwt import PyJWKClient, decode as jwt_decode
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.api_key import UserAPIKey
from app.models.user import User
from app.services.api_key_service import APIKeyService
from app.services.supabase_auth_service import supabase_auth_service

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=12
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

INVALID_CREDENTIALS_MESSAGE = "Could not validate credentials"
ERROR_INVALID_API_KEY = "Invalid API key"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]
    password_truncated = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password_truncated)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS_MESSAGE,
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_parts = token.split(".")
    if len(token_parts) != 3 or not all(part.strip() for part in token_parts):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS_MESSAGE,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as e:
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS_MESSAGE,
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(token: str, expected_type: str = "access") -> dict[str, Any]:
    payload = decode_token(token)
    token_type = payload.get("type", "access")

    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def _resolve_clerk_jwks_url() -> str | None:
    clerk_issuer_match = re.search(
        r"pk_(?:test|live)_([a-zA-Z0-9]+)",
        settings.clerk_publishable_key or "",
    )
    if not clerk_issuer_match:
        return None
    raw_key = clerk_issuer_match.group(1)
    clerk_frontend_api = base64.b64decode(raw_key + "==").decode().rstrip("$")
    return f"https://{clerk_frontend_api}/.well-known/jwks.json"


def _verify_clerk_token(token: str) -> dict | None:
    jwks_url = _resolve_clerk_jwks_url()
    if not jwks_url:
        return None
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt_decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        options={"verify_exp": True},
    )


async def _try_custom_jwt(token: str, db: AsyncSession) -> Optional[User]:
    try:
        payload = decode_token(token)
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    except (HTTPException, ValueError, TypeError):
        return None
    except Exception as e:
        logger.debug(f"Custom JWT decode failed: {e}")
        return None


async def _try_clerk_token(token: str, db: AsyncSession) -> Optional[User]:
    if not settings.clerk_secret_key:
        return None
    try:
        clerk_payload = _verify_clerk_token(token)
        if not clerk_payload:
            return None
        clerk_user_id = clerk_payload.get("sub")
        if not clerk_user_id:
            return None
        result = await db.execute(
            select(User).filter(User.clerk_uid == clerk_user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"Clerk token validated for user ID: {user.id}")
        return user
    except Exception as e:
        logger.debug(f"Clerk token validation failed: {e}")
        return None


async def _try_supabase_token(token: str, db: AsyncSession) -> Optional[User]:
    if not supabase_auth_service.is_configured:
        return None
    try:
        supabase_user = await supabase_auth_service.get_user(token)
        if not supabase_user:
            return None
        result = await db.execute(
            select(User).filter(User.supabase_uid == supabase_user["id"])
        )
        user = result.scalar_one_or_none()
        if user:
            logger.debug(f"Supabase token validated for user ID: {user.id}")
        return user
    except Exception as e:
        logger.debug(f"Supabase token validation failed: {e}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INVALID_CREDENTIALS_MESSAGE,
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token or not token.strip():
        raise credentials_exception

    user = await _try_custom_jwt(token, db)
    if user is None:
        user = await _try_clerk_token(token, db)
    if user is None:
        user = await _try_supabase_token(token, db)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this resource.",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.is_superuser and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_current_support_or_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in ["support", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Support or Super Admin access required.",
        )
    return current_user


async def get_current_super_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Super Admin access required.",
        )
    return current_user


async def _get_user_by_api_key(db: AsyncSession, x_api_key: str) -> User:
    api_key_service = APIKeyService(db)
    key_record = await api_key_service.validate_api_key(x_api_key)

    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_API_KEY,
        )

    if not await api_key_service.check_rate_limit(key_record.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    result = await db.execute(select(User).where(User.id == key_record.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_API_KEY,
        )

    return user


async def get_api_key_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not x_api_key:
        return None

    try:
        return await _get_user_by_api_key(db, x_api_key)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API key: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_API_KEY,
        )


async def get_current_user_flexible(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if x_api_key:
        try:
            return await _get_user_by_api_key(db, x_api_key)
        except HTTPException:
            raise
        except Exception:
            pass

    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            return await get_current_user(token, db)
        except HTTPException:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
