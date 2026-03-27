"""
Authentication and authorization endpoints.

Clerk is the sole auth provider. This module handles Clerk token sync,
webhook events, user profile management, and account deletion.
"""

import base64
import logging
import re
from datetime import datetime as dt

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request
from jwt import PyJWKClient, decode as jwt_decode
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError
from svix.webhooks import Webhook, WebhookVerificationError

from app.config import settings
from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


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


class ProfileUpdateRequest(BaseModel):
    """Request to update user profile."""

    full_name: str | None = None
    date_of_birth: str | None = None
    phone_number: str | None = None
    bio: str | None = Field(None, max_length=500)
    avatar_url: str | None = None


def _resolve_clerk_jwks_url() -> str:
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
    return f"https://{clerk_frontend_api}/.well-known/jwks.json"


def _verify_clerk_token(token: str) -> dict:
    jwks_url = _resolve_clerk_jwks_url()
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt_decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        options={"verify_exp": True},
    )


async def _fetch_clerk_user(clerk_user_id: str) -> dict:
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
    return resp.json()


def _extract_clerk_user_fields(clerk_user: dict) -> tuple[str, str, str | None, str | None]:
    email = (clerk_user.get("email_addresses") or [{}])[0].get("email_address", "")
    username = clerk_user.get("username") or email.split("@")[0]
    full_name = f"{clerk_user.get('first_name', '')} {clerk_user.get('last_name', '')}".strip() or None
    avatar_url = clerk_user.get("image_url")
    return email, username, full_name, avatar_url


async def _find_or_create_user(
    db: AsyncSession,
    clerk_user_id: str,
    email: str,
    username: str,
    full_name: str | None,
    avatar_url: str | None,
) -> User:
    existing_email = await db.execute(select(User).filter(User.email == email))
    existing = existing_email.scalar_one_or_none()
    if existing:
        existing.clerk_uid = clerk_user_id
        existing.auth_provider = "clerk"
        await db.commit()
        await db.refresh(existing)
        return existing

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
    await db.refresh(user)
    return user


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
        clerk_payload = _verify_clerk_token(token)
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
        clerk_user = await _fetch_clerk_user(clerk_user_id)
        email, username, full_name, avatar_url = _extract_clerk_user_fields(clerk_user)

        try:
            user = await _find_or_create_user(db, clerk_user_id, email, username, full_name, avatar_url)
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
    if not settings.clerk_webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    body = await request.body()
    headers_dict = {
        "svix-id": request.headers.get("svix-id", ""),
        "svix-timestamp": request.headers.get("svix-timestamp", ""),
        "svix-signature": request.headers.get("svix-signature", ""),
    }

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
        return await _handle_webhook_user_created(db, data, clerk_user_id)
    elif event_type == "user.updated":
        return await _handle_webhook_user_updated(db, data, clerk_user_id)
    elif event_type == "user.deleted":
        return await _handle_webhook_user_deleted(db, clerk_user_id)

    return {"status": "ignored", "reason": f"unhandled event: {event_type}"}


async def _handle_webhook_user_created(db: AsyncSession, data: dict, clerk_user_id: str) -> dict:
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


async def _handle_webhook_user_updated(db: AsyncSession, data: dict, clerk_user_id: str) -> dict:
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


async def _handle_webhook_user_deleted(db: AsyncSession, clerk_user_id: str) -> dict:
    result = await db.execute(select(User).filter(User.clerk_uid == clerk_user_id))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "ignored", "reason": "user_not_found"}

    user.is_active = False
    await db.commit()
    logger.info(f"Clerk webhook: deactivated user {user.id}")
    return {"status": "ok", "action": "deactivated"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name

    if profile_data.date_of_birth is not None and profile_data.date_of_birth.strip():
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


@router.delete("/delete-account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_active = False
    await db.commit()
