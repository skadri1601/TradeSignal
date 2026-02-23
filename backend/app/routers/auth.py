"""
Authentication and authorization endpoints.

Provides user registration, login, token refresh, and password reset functionality.
"""

from datetime import timedelta, datetime
from typing import Annotated

import secrets
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.models.user import User
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token_type,
    get_current_active_user,
)
from app.config import settings
from app.core.limiter import limiter
from app.services.supabase_auth_service import supabase_auth_service

router = APIRouter()


# Request/Response Schemas
class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


class UserResponse(BaseModel):
    """User response (excluding password)."""

    id: int
    email: str
    username: str
    full_name: str | None = None
    date_of_birth: str | None = None
    phone_number: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    role: str = "customer"
    stripe_subscription_tier: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response with access and refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Request to refresh access token using refresh token."""

    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Request to change user password."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


class ProfileUpdateRequest(BaseModel):
    """Request to update user profile."""

    full_name: str | None = None
    date_of_birth: str | None = None  # Format: YYYY-MM-DD
    phone_number: str | None = None
    bio: str | None = Field(None, max_length=500)
    avatar_url: str | None = None


class EmailUpdateRequest(BaseModel):
    """Request to update email address."""

    new_email: EmailStr
    password: str  # Require password confirmation


class ForgotPasswordRequest(BaseModel):
    """Request to initiate password reset."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request to reset password with token."""

    token: str
    new_password: str = Field(min_length=8, max_length=100)


logger = logging.getLogger(__name__)


@router.post("/clerk-sync", response_model=UserResponse)
async def clerk_sync(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )

    try:
        from jwt import PyJWKClient, decode as jwt_decode
        import re
        import base64

        clerk_issuer_match = re.search(
            r"pk_(?:test|live)_([a-zA-Z0-9]+)",
            settings.clerk_publishable_key or "",
        )
        if not clerk_issuer_match:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Clerk not configured",
            )

        raw_key = clerk_issuer_match.group(1)
        clerk_frontend_api = base64.b64decode(raw_key + "==").decode().rstrip("$")
        jwks_url = f"https://{clerk_frontend_api}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        clerk_payload = jwt_decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clerk token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token",
        )

    clerk_user_id = clerk_payload.get("sub")
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        result = await db.execute(
            select(User).filter(User.clerk_uid == clerk_user_id)
        )
        user = result.scalar_one_or_none()
    except (OperationalError, DatabaseError) as db_error:
        logger.error(f"Database error during clerk-sync lookup: {db_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable. Please retry.",
        )
    except SQLAlchemyError as db_error:
        logger.error(f"Database error during clerk-sync lookup: {db_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during sync.",
        )

    if not user:
        import httpx

        headers = {"Authorization": f"Bearer {settings.clerk_secret_key}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.clerk.com/v1/users/{clerk_user_id}",
                headers=headers,
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user from Clerk",
            )

        clerk_user = resp.json()
        email = (clerk_user.get("email_addresses") or [{}])[0].get(
            "email_address", ""
        )
        username = clerk_user.get("username") or email.split("@")[0]

        try:
            existing_email = await db.execute(
                select(User).filter(User.email == email)
            )
            existing = existing_email.scalar_one_or_none()
            if existing:
                existing.clerk_uid = clerk_user_id
                existing.auth_provider = "clerk"
                await db.commit()
                await db.refresh(existing)
                return existing

            existing_username = await db.execute(
                select(User).filter(User.username == username)
            )
            if existing_username.scalar_one_or_none():
                username = f"{username}_{clerk_user_id[:6]}"

            user = User(
                email=email,
                username=username,
                hashed_password="CLERK_MANAGED",
                clerk_uid=clerk_user_id,
                auth_provider="clerk",
                full_name=f"{clerk_user.get('first_name', '')} {clerk_user.get('last_name', '')}".strip() or None,
                avatar_url=clerk_user.get("image_url"),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        except (OperationalError, DatabaseError) as db_error:
            await db.rollback()
            logger.error(f"Database error during clerk-sync user creation: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database temporarily unavailable. Please retry.",
            )
        except SQLAlchemyError as db_error:
            await db.rollback()
            logger.error(f"Database error during clerk-sync user creation: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account during sync.",
            )

    return user


@router.post("/clerk-webhook", status_code=status.HTTP_200_OK)
async def clerk_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receive Clerk webhook events for user lifecycle management.
    Replaces the need for frontend clerk-sync on user creation/updates.
    """
    if not settings.clerk_webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    body = await request.body()
    headers_dict = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }

    from svix.webhooks import Webhook, WebhookVerificationError
    wh = Webhook(settings.clerk_webhook_secret)
    try:
        payload = wh.verify(body, headers_dict)
    except WebhookVerificationError:
        logger.warning("Clerk webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = payload.get("type", "")
    data = payload.get("data", {})
    clerk_user_id = data.get("id", "")

    if not clerk_user_id:
        return {"status": "ignored", "reason": "no user id"}

    if event_type == "user.created":
        existing = await db.execute(
            select(User).filter(User.clerk_uid == clerk_user_id)
        )
        if existing.scalar_one_or_none():
            return {"status": "ok", "action": "already_exists"}

        email = (data.get("email_addresses") or [{}])[0].get("email_address", "")
        username = data.get("username") or email.split("@")[0]
        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None
        avatar_url = data.get("image_url")

        existing_email = await db.execute(select(User).filter(User.email == email))
        existing_user = existing_email.scalar_one_or_none()
        if existing_user:
            existing_user.clerk_uid = clerk_user_id
            existing_user.auth_provider = "clerk"
            if full_name:
                existing_user.full_name = full_name
            if avatar_url:
                existing_user.avatar_url = avatar_url
            await db.commit()
            logger.info(f"Clerk webhook: linked existing user {existing_user.id} to clerk_uid {clerk_user_id}")
            return {"status": "ok", "action": "linked"}

        existing_username = await db.execute(select(User).filter(User.username == username))
        if existing_username.scalar_one_or_none():
            username = f"{username}_{clerk_user_id[:6]}"

        user = User(
            email=email,
            username=username,
            hashed_password="CLERK_MANAGED",
            clerk_uid=clerk_user_id,
            auth_provider="clerk",
            full_name=full_name,
            avatar_url=avatar_url,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        logger.info(f"Clerk webhook: created user {user.id} for clerk_uid {clerk_user_id}")
        return {"status": "ok", "action": "created"}

    elif event_type == "user.updated":
        result = await db.execute(select(User).filter(User.clerk_uid == clerk_user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"status": "ignored", "reason": "user_not_found"}

        email = (data.get("email_addresses") or [{}])[0].get("email_address", "")
        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None
        avatar_url = data.get("image_url")

        if email and email != user.email:
            user.email = email
        if full_name:
            user.full_name = full_name
        if avatar_url:
            user.avatar_url = avatar_url

        await db.commit()
        logger.info(f"Clerk webhook: updated user {user.id}")
        return {"status": "ok", "action": "updated"}

    elif event_type == "user.deleted":
        result = await db.execute(select(User).filter(User.clerk_uid == clerk_user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"status": "ignored", "reason": "user_not_found"}

        user.is_active = False
        await db.commit()
        logger.info(f"Clerk webhook: deactivated user {user.id}")
        return {"status": "ok", "action": "deactivated"}

    return {"status": "ignored", "reason": f"unhandled event: {event_type}"}


# Authentication Endpoints


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
async def register(
    request: Request, user_data: UserRegister, db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, username, password)
        db: Database session

    Returns:
        Created user object (without password)

    Raises:
        HTTPException 400: If email or username already exists
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("Registration attempt initiated")

        # Check if email already exists
        try:
            result = await db.execute(
                select(User).filter(User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                logger.warning(
                    f"Registration failed: Email already exists: {user_data.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
        except HTTPException:
            raise
        except (OperationalError, DatabaseError) as db_error:
            logger.error(
                f"Database connection error during registration: {db_error}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later.",
            )
        except SQLAlchemyError as db_error:
            logger.error(
                f"Database error during registration: {db_error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred. Please try again later.",
            )

        # Check if username already exists
        try:
            result = await db.execute(
                select(User).filter(User.username == user_data.username)
            )
            if result.scalar_one_or_none():
                logger.warning(
                    f"Registration failed: Username already taken: {user_data.username}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
        except HTTPException:
            raise
        except (OperationalError, DatabaseError) as db_error:
            logger.error(
                f"Database connection error during registration: {db_error}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later.",
            )
        except SQLAlchemyError as db_error:
            logger.error(
                f"Database error during registration: {db_error}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred. Please try again later.",
            )

        # Create new user with error handling
        # Try Supabase Auth for new users if configured
        try:
            logger.debug(f"Creating user: {user_data.email}")

            supabase_uid = None
            auth_provider = "custom"
            hashed_password = get_password_hash(user_data.password)

            # If Supabase Auth is configured, use it for new users
            if supabase_auth_service.is_configured:
                logger.info("Using Supabase Auth for new user registration")
                supabase_user = await supabase_auth_service.create_user(
                    email=user_data.email,
                    password=user_data.password
                )
                if supabase_user:
                    supabase_uid = supabase_user.id
                    auth_provider = "supabase"
                    hashed_password = "SUPABASE_MANAGED"  # Password managed by Supabase
                    logger.info(f"Supabase user created: {supabase_uid}")
                else:
                    # Fall back to custom auth if Supabase fails
                    logger.warning("Supabase user creation failed, falling back to custom auth")

            new_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=auth_provider == "supabase",  # Supabase handles email verification
                is_superuser=False,
                role="customer",  # Default role for new users
                auth_provider=auth_provider,
                supabase_uid=supabase_uid,
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info(
                f"User registered successfully: {new_user.email}, ID: {new_user.id}"
            )

            # Send welcome email (don't fail registration if email fails)
            try:
                from app.services.email_service import EmailService
                email_result = await EmailService.send_welcome_email(
                    email=new_user.email,
                    user_name=new_user.username
                )
                if email_result.get("status") == "error":
                    logger.warning(
                        f"Failed to send welcome email to {new_user.email}: {email_result.get('error')}"
                    )
                elif email_result.get("status") == "enqueued":
                    logger.info(f"Welcome email enqueued for {new_user.email}")
            except Exception as email_error:
                logger.warning(
                    f"Failed to send welcome email to {new_user.email}: {email_error}"
                )
                # Don't fail registration if email fails

            return new_user

        except SQLAlchemyError as db_error:
            await db.rollback()
            logger.error(f"Database error creating user: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account. Please try again later.",
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error creating user: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration. Please try again later.",
            )

    except HTTPException:
        # Re-raise HTTP exceptions (they're expected and properly formatted)
        raise
    except Exception:
        # Log unexpected errors with full stack trace
        logger.error(
            f"Unexpected error during registration for email: {user_data.email}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during registration. Please try again later.",
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    User login with email/username and password.

    Args:
        form_data: OAuth2 form with username (or email) and password
        db: Database session

    Returns:
        Access and refresh JWT tokens

    Raises:
        HTTPException 401: If credentials are invalid
    """
    logger = logging.getLogger(__name__)

    try:
        # Log login attempt (without password)
        logger.info("Login attempt for user (PII redacted)")

        # Try to find user by email or username with database error handling
        try:
            logger.debug(f"Executing database query for user: {form_data.username}")
            result = await db.execute(
                select(User).filter(
                    (User.email == form_data.username)
                    | (User.username == form_data.username)
                )
            )
            user = result.scalar_one_or_none()
            logger.debug(f"Database query completed, user found: {user is not None}")
        except (OperationalError, DatabaseError) as db_error:
            error_msg = str(db_error)
            logger.error(
                f"Database connection error during login: {error_msg}", exc_info=True
            )

            # Provide specific error messages based on error type
            if "gaierror" in error_msg or "getaddrinfo failed" in error_msg:
                detail = (
                    "Cannot reach database server (DNS resolution failed). "
                    "This may be a temporary network issue. Please try again in a moment."
                )
            elif "connection refused" in error_msg.lower():
                detail = "Database server is not accepting connections. Please try again later."
            elif "timeout" in error_msg.lower():
                detail = "Database connection timed out. Please try again."
            else:
                detail = "Database connection error. Please try again later."

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            )
        except SQLAlchemyError as db_error:
            logger.error(f"Database error during login: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred. Please try again later.",
            )

        # Verify user exists and password is correct
        if not user:
            logger.warning(
                f"Login failed: User not found for username/email: {form_data.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user account is active
        if not user.is_active:
            logger.warning(
                f"Login failed: Inactive account for user ID: {user.id}, email: {user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
            )

        # Route authentication based on auth_provider
        auth_provider = getattr(user, 'auth_provider', 'custom')

        if auth_provider == "supabase" and supabase_auth_service.is_configured:
            # Authenticate via Supabase Auth
            logger.debug(f"Using Supabase Auth for user ID: {user.id}")
            supabase_tokens = await supabase_auth_service.sign_in(
                email=user.email,
                password=form_data.password
            )
            if not supabase_tokens:
                logger.warning(f"Supabase login failed for user ID: {user.id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email/username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.info(f"Supabase login successful for user ID: {user.id}")
            return TokenResponse(
                access_token=supabase_tokens.access_token,
                refresh_token=supabase_tokens.refresh_token,
                token_type="bearer"
            )
        else:
            # Use custom JWT auth (existing users)
            # Verify password with error handling
            try:
                logger.debug(f"Verifying password for user ID: {user.id}")
                password_valid = verify_password(form_data.password, user.hashed_password)
            except Exception as pwd_error:
                logger.error(f"Error verifying password: {pwd_error}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred during authentication. Please try again.",
                )

            if not password_valid:
                logger.warning(
                    f"Login failed: Invalid password for user ID: {user.id}, email: {user.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email/username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Create access and refresh tokens with error handling
            try:
                logger.debug(f"Creating tokens for user ID: {user.id}")
                access_token = create_access_token(data={"sub": str(user.id)})
                refresh_token = create_refresh_token(data={"sub": str(user.id)})
                logger.debug(f"Tokens created successfully for user ID: {user.id}")
            except Exception as token_error:
                logger.error(f"Error creating tokens: {token_error}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while generating authentication tokens. Please try again.",
                )

            logger.info(f"Login successful for user ID: {user.id}, email: {user.email}")

            return TokenResponse(
                access_token=access_token, refresh_token=refresh_token, token_type="bearer"
            )
    except HTTPException:
        # Re-raise HTTP exceptions (they're expected and properly formatted)
        raise
    except SQLAlchemyError as db_error:
        # Catch any remaining database errors
        logger.error(
            f"Unhandled database error during login: {db_error}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later.",
        )
    except Exception:
        # Log unexpected errors with full stack trace
        logger.error(
            f"Unexpected error during login for username/email: {form_data.username}",
            exc_info=True,
        )
        # Log headers for debugging (safely)
        try:
            logger.debug(f"Request headers: {dict(request.headers)}")
        except Exception:
            pass
            
        # Always return a proper HTTP response, never an empty response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during login. Please try again later.",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Args:
        request: Request containing refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException 401: If refresh token is invalid
    """
    # Verify token is a refresh token
    payload = verify_token_type(request.refresh_token, expected_type="refresh")

    # Extract user ID (stored as string in JWT, convert to int)
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    # Get user from database
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    # Create new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from token

    Returns:
        Current user object (without password)
    """
    return current_user


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change current user's password.

    Args:
        request: Current and new password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If current password is incorrect
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile information.

    Args:
        profile_data: Profile fields to update
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user object
    """
    from datetime import datetime as dt

    # Update fields if provided
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

    if profile_data.date_of_birth is not None and profile_data.date_of_birth.strip():
        # Only process if date_of_birth is not None and not empty string
        try:
            current_user.date_of_birth = dt.strptime(
                profile_data.date_of_birth, "%Y-%m-%d"
            ).date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            )
    elif profile_data.date_of_birth is not None and not profile_data.date_of_birth.strip():
        # Empty string - set to None
        current_user.date_of_birth = None

    if profile_data.phone_number is not None:
        current_user.phone_number = profile_data.phone_number

    if profile_data.bio is not None:
        current_user.bio = profile_data.bio

    if profile_data.avatar_url is not None:
        current_user.avatar_url = profile_data.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return current_user


@router.put("/email")
async def update_email(
    email_data: EmailUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user's email address (requires password confirmation).

    Args:
        email_data: New email and password confirmation
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If password is incorrect or email already exists
    """
    # Verify password
    if not verify_password(email_data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    # Check if new email already exists
    result = await db.execute(select(User).filter(User.email == email_data.new_email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
        )

    # Update email and mark as unverified
    current_user.email = email_data.new_email
    current_user.is_verified = False  # Require re-verification
    await db.commit()

    return {
        "message": "Email updated successfully. Please verify your new email address."
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate password reset process.

    Generates a reset token and stores it in the database.
    In production, this would send an email with the reset link.
    For development, the token is logged to console.

    Args:
        request_data: Email address for password reset
        db: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)
    """
    # Find user by email
    result = await db.execute(select(User).filter(User.email == request_data.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration attacks
    if not user:
        logger.warning("Password reset requested for non-existent email (redacted)")
        return {"message": "If that email exists, a password reset link has been sent."}

    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    # Store token in database
    user.password_reset_token = reset_token
    user.password_reset_expires = reset_expires
    await db.commit()

    # In production, send email with reset link
    # For development, log the token
    # reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/reset-password/[REDACTED]"
    logger.info(f"Password reset requested for user ID: {user.id}")

    # SECURITY FIX: Do not log the token or the URL containing the token in production logs
    if settings.debug:
        logger.debug(f"DEV ONLY - Reset Token: {reset_token}")

    # Send email with reset link
    from app.services.email_service import EmailService
    email_result = await EmailService.send_password_reset_email(
        email=user.email,
        reset_token=reset_token,
        expires_hours=1,
    )
    
    if email_result.get("status") == "error":
        logger.error(f"Failed to send password reset email to {user.email}: {email_result.get('error')}")
    elif email_result.get("status") == "skipped":
        logger.warning(f"Email configuration missing. Password reset token generated but email not sent for {user.email}")

    return {"message": "If that email exists, a password reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using reset token.

    Args:
        request_data: Reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If token is invalid or expired
    """
    # Find user by reset token
    result = await db.execute(
        select(User).filter(User.password_reset_token == request_data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Check if token has expired
    if (
        user.password_reset_expires is None
        or user.password_reset_expires < datetime.utcnow()
    ):
        # Clear expired token
        user.password_reset_token = None
        user.password_reset_expires = None
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one.",
        )

    # Update password and clear reset token
    user.hashed_password = get_password_hash(request_data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    await db.commit()

    logger.info(f"Password reset successful for user ID: {user.id}")

    return {
        "message": "Password has been reset successfully. You can now login with your new password."
    }


@router.delete("/delete-account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user's account (soft delete - sets is_active to False).

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        No content (204)
    """
    # Soft delete - just deactivate the account
    current_user.is_active = False
    await db.commit()
