"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

# Password hashing
# Configure bcrypt to handle password validation properly
# Handle bcrypt version compatibility issues
try:
    import bcrypt

    # Suppress bcrypt version warnings for newer bcrypt versions
    if hasattr(bcrypt, "__version__"):
        pass  # Newer bcrypt version
except ImportError:
    pass

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=12
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    # Truncate password to 72 bytes for bcrypt compatibility
    # (bcrypt has a 72-byte limit)
    password_bytes = password.encode("utf-8")[:72]
    password_truncated = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password_truncated)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: Payload data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    # Validate token format before attempting to decode
    # JWT tokens must have 3 segments separated by dots: header.payload.signature
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token has proper JWT format (3 segments)
    token_parts = token.split(".")
    if len(token_parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token segments are not empty
    if not all(part.strip() for part in token_parts):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        # Log the error for debugging but return generic message to client
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Validate token exists and is not empty
    if not token or not token.strip():
        raise credentials_exception

    # Decode token (this will raise HTTPException if invalid)
    try:
        payload = decode_token(token)
    except HTTPException:
        # Re-raise HTTPException as-is (already has proper 401 status)
        raise
    except Exception as e:
        # Log unexpected errors but return 401 to client
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error decoding token: {e}", exc_info=True)
        raise credentials_exception

    # Extract user ID from token (stored as string, convert to int)
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # Get user from database
    from sqlalchemy import select

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are active.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Active User object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify they have verified their email.

    Args:
        current_user: Current active user

    Returns:
        Verified User object

    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email to access this resource.",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify they are a superuser.

    Args:
        current_user: Current active user

    Returns:
        Superuser User object

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def get_current_support_or_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify they are support or super_admin.
    Support can manage users, super_admin can manage everything.

    Args:
        current_user: Current active user

    Returns:
        Support or Super Admin User object

    Raises:
        HTTPException: If user is not support or super_admin
    """
    if current_user.role not in ["support", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Support or Super Admin access required.",
        )
    return current_user


async def get_current_super_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify they are super_admin.
    Only super_admin can manage support admins.

    Args:
        current_user: Current active user

    Returns:
        Super Admin User object

    Raises:
        HTTPException: If user is not super_admin
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Super Admin access required.",
        )
    return current_user


def verify_token_type(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Verify token is of the expected type (access or refresh).

    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token type doesn't match
    """
    payload = decode_token(token)
    token_type = payload.get("type", "access")  # Default to access if not specified

    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
