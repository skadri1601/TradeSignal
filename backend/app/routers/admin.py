"""
Admin Dashboard API Router
Endpoints for user management and system administration
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel, EmailStr

from app.database import get_db

logger = logging.getLogger(__name__)
from app.core.security import get_current_support_or_superuser, get_current_super_admin
from app.models.user import User
from app.models.payment import Payment
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.contact_submission import ContactSubmission

router = APIRouter()


# Response Models
class UserListItem(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    stripe_subscription_tier: str | None
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    date_of_birth: str | None
    phone_number: str | None
    bio: str | None
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    stripe_subscription_tier: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    users: list[UserListItem]


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    free_tier: int
    basic_tier: int
    pro_tier: int
    total_revenue_estimate: float


class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role: Optional[str] = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    role: str = "customer"


# Admin Endpoints


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get system-wide statistics for admin dashboard
    """
    # Total users
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar() or 0

    # Active users
    active_result = await db.execute(
        select(func.count(User.id)).where(User.is_active.is_(True))
    )
    active_users = active_result.scalar() or 0

    # Verified users
    verified_result = await db.execute(
        select(func.count(User.id)).where(User.is_verified.is_(True))
    )
    verified_users = verified_result.scalar() or 0

    # Tier counts - get from subscriptions table
    # Free tier: users without subscription or with free tier
    free_result = await db.execute(
        select(func.count(User.id))
        .outerjoin(Subscription, User.id == Subscription.user_id)
        .where((Subscription.id.is_(None)) | (Subscription.tier == "free"))
    )
    free_tier = free_result.scalar() or 0

    # Basic/Plus tier
    basic_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.tier.in_(["basic", "plus"])
        )
    )
    basic_tier = basic_result.scalar() or 0

    # Pro tier
    pro_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.tier == "pro")
    )
    pro_tier = pro_result.scalar() or 0

    # Revenue estimate (basic=$9, pro=$29)
    total_revenue = (basic_tier * 9) + (pro_tier * 29)

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        verified_users=verified_users,
        free_tier=free_tier,
        basic_tier=basic_tier,
        pro_tier=pro_tier,
        total_revenue_estimate=float(total_revenue),
    )


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tier: Optional[str] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with pagination and filtering
    """
    # Build query
    query = select(User)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_pattern))
            | (User.username.ilike(search_pattern))
            | (User.full_name.ilike(search_pattern))
        )

    if tier:
        if tier == "free":
            # Users without subscription or with free tier
            query = query.outerjoin(
                Subscription, User.id == Subscription.user_id
            ).where((Subscription.id.is_(None)) | (Subscription.tier == "free"))
        else:
            # Users with specific tier
            query = query.join(Subscription, User.id == Subscription.user_id).where(
                Subscription.tier == tier
            )

    if active_only:
        query = query.where(User.is_active.is_(True))

    # Get total count - need to handle joins properly
    # If we have joins, count distinct users
    if tier:
        # If filtering by tier, count distinct users from the joined query
        count_query = select(func.count(func.distinct(User.id)))
        if tier == "free":
            count_query = count_query.select_from(
                User.outerjoin(Subscription, User.id == Subscription.user_id)
            ).where((Subscription.id.is_(None)) | (Subscription.tier == "free"))
        else:
            count_query = count_query.select_from(
                User.join(Subscription, User.id == Subscription.user_id)
            ).where(Subscription.tier == tier)

        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                (User.email.ilike(search_pattern))
                | (User.username.ilike(search_pattern))
                | (User.full_name.ilike(search_pattern))
            )

        if active_only:
            count_query = count_query.where(User.is_active.is_(True))
    else:
        # No tier filter, count directly from User
        count_query = select(func.count(User.id))
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                (User.email.ilike(search_pattern))
                | (User.username.ilike(search_pattern))
                | (User.full_name.ilike(search_pattern))
            )
        if active_only:
            count_query = count_query.where(User.is_active.is_(True))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Get subscription tiers for users
    user_list = []
    for user in users:
        # Get subscription tier
        sub_result = await db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = sub_result.scalar_one_or_none()

        # Create user list item
        user_item = UserListItem(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            stripe_subscription_tier=subscription.tier if subscription else None,
            stripe_customer_id=subscription.stripe_customer_id
            if subscription
            else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        user_list.append(user_item)

    return UserListResponse(
        total=total, page=page, page_size=page_size, users=user_list
    )


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific user
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserDetail.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user status (active, verified, superuser)
    """
    # Prevent self-demotion
    if user_id == current_user.id and update_data.is_superuser is False:
        raise HTTPException(
            status_code=400, detail="Cannot remove your own superuser status"
        )

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent support from modifying roles or superuser status
    if current_user.role == "support":
        if update_data.role is not None or update_data.is_superuser is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Support admins cannot modify user roles or superuser status",
            )
        # Support cannot modify support or super_admin users
        if user.role in ["support", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Support admins cannot modify other admins",
            )

    # Prevent changing super_admin role (only super_admin can do this)
    if user.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify super admin users",
        )

    # Update fields
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.is_verified is not None:
        user.is_verified = update_data.is_verified
    if update_data.is_superuser is not None and current_user.role == "super_admin":
        user.is_superuser = update_data.is_superuser
    if update_data.role is not None and current_user.role == "super_admin":
        # Only super_admin can change roles
        if update_data.role not in ["customer", "support", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be: customer, support, or super_admin",
            )
        user.role = update_data.role
        # Sync is_superuser with role
        if update_data.role == "super_admin":
            user.is_superuser = True
        elif update_data.role == "support":
            user.is_superuser = (
                True  # Support also needs is_superuser for backward compatibility
            )
        else:
            user.is_superuser = False

    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return UserDetail.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    permanent: bool = Query(
        False, description="Permanently delete user (default: soft delete)"
    ),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user (soft delete by default, permanent if specified).
    Support can only soft delete. Super Admin can do both.
    """
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account via admin panel",
        )

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Support cannot delete super_admin or other support admins
    if current_user.role == "support":
        if user.role in ["support", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Support admins cannot delete other admins",
            )
        if permanent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Support admins can only soft delete users",
            )

    # Super admin cannot permanently delete other super admins
    if permanent and user.role == "super_admin" and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot permanently delete super admin accounts",
        )

    if permanent:
        # Permanent deletion (super admin only, except super admins)
        await db.delete(user)
        await db.commit()
        return {"message": "User permanently deleted", "user_id": user_id}
    else:
        # Soft delete
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await db.commit()
        return {"message": "User deactivated", "user_id": user_id}


# User Search and Billing Endpoints (for Support/Admin)


@router.get("/users/search")
async def search_user(
    query: str = Query(..., description="Search by email, username, or full name"),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for a user by email, username, or full name.
    Returns user details including subscription and billing info.
    """
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(User)
        .where(
            (User.email.ilike(search_pattern))
            | (User.username.ilike(search_pattern))
            | (User.full_name.ilike(search_pattern))
        )
        .limit(10)
    )
    users = result.scalars().all()

    if not users:
        raise HTTPException(
            status_code=404, detail="No users found matching the search query"
        )

    # If single user, return detailed info
    if len(users) == 1:
        user = users[0]
        # Get subscription
        sub_result = await db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = sub_result.scalar_one_or_none()

        # Get payment count
        payment_count_result = await db.execute(
            select(func.count(Payment.id)).where(Payment.user_id == user.id)
        )
        payment_count = payment_count_result.scalar() or 0

        return {
            "user": UserDetail.model_validate(user),
            "subscription": {
                "tier": subscription.tier if subscription else "free",
                "status": subscription.status if subscription else "inactive",
                "is_active": subscription.is_active if subscription else False,
                "current_period_end": subscription.current_period_end.isoformat()
                if subscription and subscription.current_period_end
                else None,
            }
            if subscription
            else None,
            "payment_count": payment_count,
        }

    # Multiple users - return list
    return {
        "users": [UserListItem.model_validate(u) for u in users],
        "count": len(users),
    }


@router.get("/users/{user_id}/billing")
async def get_user_billing_history(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get billing/order history for a specific user.
    Support and Super Admin can access this.
    """
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get subscription
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = sub_result.scalar_one_or_none()

    # Get payment history
    count_query = select(Payment).where(Payment.user_id == user_id)
    count_result = await db.execute(
        select(func.count()).select_from(count_query.subquery())
    )
    total = count_result.scalar() or 0

    payments_query = (
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(desc(Payment.created_at))
        .offset(skip)
        .limit(limit)
    )
    payments_result = await db.execute(payments_query)
    payments = payments_result.scalars().all()

    # Format payments
    orders = []
    for payment in payments:
        orders.append(
            {
                "id": payment.id,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "payment_type": payment.payment_type,
                "status": payment.status,
                "tier": payment.tier,
                "tier_before": payment.tier_before,
                "description": payment.description,
                "receipt_url": payment.receipt_url,
                "invoice_url": payment.invoice_url,
                "refunded_amount": float(payment.refunded_amount)
                if payment.refunded_amount
                else None,
                "refunded_at": payment.refunded_at.isoformat()
                if payment.refunded_at
                else None,
                "period_start": payment.period_start.isoformat()
                if payment.period_start
                else None,
                "period_end": payment.period_end.isoformat()
                if payment.period_end
                else None,
                "created_at": payment.created_at.isoformat(),
            }
        )

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
        },
        "subscription": {
            "tier": subscription.tier if subscription else "free",
            "status": subscription.status if subscription else "inactive",
            "is_active": subscription.is_active if subscription else False,
            "current_period_start": subscription.current_period_start.isoformat()
            if subscription and subscription.current_period_start
            else None,
            "current_period_end": subscription.current_period_end.isoformat()
            if subscription and subscription.current_period_end
            else None,
        }
        if subscription
        else None,
        "orders": {"items": orders, "total": total, "skip": skip, "limit": limit},
    }


# Super Admin Only - Manage Support Admins


@router.get("/support-admins")
async def list_support_admins(
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    List all support admins. Super Admin only.
    """
    result = await db.execute(
        select(User).where(User.role == "support").order_by(User.created_at.desc())
    )
    support_admins = result.scalars().all()

    return {
        "support_admins": [
            UserListItem.model_validate(admin) for admin in support_admins
        ],
        "count": len(support_admins),
    }


@router.post("/support-admins/{user_id}")
async def promote_to_support(
    user_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Promote a user to support admin. Super Admin only.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot change super admin role")

    user.role = "support"
    user.is_superuser = True  # Keep for backward compatibility
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return {
        "message": f"User {user.email} promoted to support admin",
        "user": UserDetail.model_validate(user),
    }


@router.delete("/support-admins/{user_id}")
async def demote_from_support(
    user_id: int,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Demote a support admin to customer. Super Admin only.
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot demote yourself")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "support":
        raise HTTPException(status_code=400, detail="User is not a support admin")

    user.role = "customer"
    user.is_superuser = False
    user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)

    return {
        "message": f"User {user.email} demoted to customer",
        "user": UserDetail.model_validate(user),
    }


# Contact Management Endpoints

class ContactSubmissionItem(BaseModel):
    """Contact submission list item."""

    id: int
    user_id: int | None
    name: str
    company_name: str | None
    email: str
    phone: str | None
    message: str
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactSubmissionDetail(BaseModel):
    """Contact submission detail with user info."""

    id: int
    user_id: int | None
    user_email: str | None
    user_username: str | None
    name: str
    company_name: str | None
    email: str
    phone: str | None
    message: str
    is_public: bool
    ip_address: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """Contact list response."""

    total: int
    page: int
    page_size: int
    contacts: list[ContactSubmissionItem]


@router.get("/contacts/public", response_model=ContactListResponse)
async def get_public_contacts(
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):
    """
    Get public contact submissions. Super Admin only.
    """
    query = select(ContactSubmission).where(ContactSubmission.is_public == True)

    # Search filter
    if search:
        query = query.where(
            (ContactSubmission.name.ilike(f"%{search}%"))
            | (ContactSubmission.email.ilike(f"%{search}%"))
        )

    # Status filter
    if status_filter:
        query = query.where(ContactSubmission.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(desc(ContactSubmission.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size)

    result = await db.execute(query)
    contacts = result.scalars().all()

    return ContactListResponse(
        total=total,
        page=page,
        page_size=page_size,
        contacts=[ContactSubmissionItem.model_validate(c) for c in contacts],
    )


@router.get("/contacts/authenticated", response_model=ContactListResponse)
async def get_authenticated_contacts(
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):
    """
    Get authenticated contact submissions. Super Admin and Support Admin.
    """
    query = select(ContactSubmission).where(ContactSubmission.is_public == False)

    # Search filter
    if search:
        query = query.where(
            (ContactSubmission.name.ilike(f"%{search}%"))
            | (ContactSubmission.email.ilike(f"%{search}%"))
        )

    # Status filter
    if status_filter:
        query = query.where(ContactSubmission.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(desc(ContactSubmission.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size)

    result = await db.execute(query)
    contacts = result.scalars().all()

    return ContactListResponse(
        total=total,
        page=page,
        page_size=page_size,
        contacts=[ContactSubmissionItem.model_validate(c) for c in contacts],
    )


@router.get("/contacts/all", response_model=ContactListResponse)
async def get_all_contacts(
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    is_public_filter: Optional[bool] = Query(None),
):
    """
    Get all contact submissions (both public and authenticated). Super Admin only.
    """
    query = select(ContactSubmission)

    # Public filter
    if is_public_filter is not None:
        query = query.where(ContactSubmission.is_public == is_public_filter)

    # Search filter
    if search:
        query = query.where(
            (ContactSubmission.name.ilike(f"%{search}%"))
            | (ContactSubmission.email.ilike(f"%{search}%"))
        )

    # Status filter
    if status_filter:
        query = query.where(ContactSubmission.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(desc(ContactSubmission.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size)

    result = await db.execute(query)
    contacts = result.scalars().all()

    return ContactListResponse(
        total=total,
        page=page,
        page_size=page_size,
        contacts=[ContactSubmissionItem.model_validate(c) for c in contacts],
    )


@router.get("/contacts/{contact_id}", response_model=ContactSubmissionDetail)
async def get_contact_detail(
    contact_id: int,
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get contact submission detail. Super Admin and Support Admin.
    Support admins can only see authenticated contacts.
    """
    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    # Support admins can only see authenticated contacts
    if current_user.role == "support" and contact.is_public:
        raise HTTPException(
            status_code=403, detail="Access denied. Support admins can only view authenticated contacts."
        )

    # Get user info if available
    user_email = None
    user_username = None
    if contact.user_id:
        try:
            user_result = await db.execute(select(User).where(User.id == contact.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user_email = user.email
                user_username = user.username
        except Exception as e:
            logger.error(f"Error fetching user info for contact {contact_id}: {e}", exc_info=True)
            # Continue without user info if there's an error

    # Create detail response manually to avoid validation issues with optional fields
    try:
        detail = ContactSubmissionDetail(
            id=contact.id,
            user_id=contact.user_id,
            user_email=user_email,
            user_username=user_username,
            name=contact.name,
            company_name=contact.company_name,
            email=contact.email,
            phone=contact.phone,
            message=contact.message,
            is_public=contact.is_public,
            ip_address=contact.ip_address,
            status=contact.status,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )
        return detail
    except Exception as e:
        logger.error(f"Error creating ContactSubmissionDetail for contact {contact_id}: {e}", exc_info=True)
        logger.error(f"  Contact data: id={contact.id}, user_id={contact.user_id}, is_public={contact.is_public}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving contact details. Please try again later.",
        )


@router.patch("/contacts/{contact_id}/status")
async def update_contact_status(
    contact_id: int,
    status: str = Query(..., description="New status: new, read, replied"),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Update contact submission status. Super Admin and Support Admin.
    """
    if status not in ["new", "read", "replied"]:
        raise HTTPException(
            status_code=400, detail="Invalid status. Must be: new, read, or replied"
        )

    result = await db.execute(
        select(ContactSubmission).where(ContactSubmission.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact submission not found")

    # Support admins can only update authenticated contacts
    if current_user.role == "support" and contact.is_public:
        raise HTTPException(
            status_code=403, detail="Access denied. Support admins can only update authenticated contacts."
        )

    contact.status = status
    contact.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(contact)

    return {
        "message": f"Contact submission status updated to {status}",
        "contact": ContactSubmissionItem.model_validate(contact),
    }


# Feature Flags Management (Super Admin Only)

class FeatureFlagUpdate(BaseModel):
    """Request model for updating feature flags."""

    enabled: bool
    description: Optional[str] = None


@router.get("/feature-flags")
async def get_feature_flags(
    current_user: User = Depends(get_current_super_admin),
):
    """
    Get all feature flags and their current status.
    Super Admin only.
    """
    from app.config import settings

    return {
        "feature_flags": {
            "enable_ai_insights": {
                "enabled": settings.enable_ai_insights,
                "description": "Enable AI-powered trade insights",
            },
            "enable_webhooks": {
                "enabled": settings.enable_webhooks,
                "description": "Enable webhook notifications",
            },
            "enable_email_alerts": {
                "enabled": settings.enable_email_alerts,
                "description": "Enable email alert notifications",
            },
            "enable_push_notifications": {
                "enabled": settings.enable_push_notifications,
                "description": "Enable browser push notifications",
            },
        },
        "note": "Feature flags are managed via environment variables. Changes require application restart.",
    }


@router.get("/subscription-analytics")
async def get_subscription_analytics(
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """
    Get subscription analytics including conversion rates, churn, and revenue.
    Super Admin only.
    """
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total subscriptions by tier
    tier_counts = {}
    for tier in ["free", "basic", "plus", "pro", "enterprise"]:
        result = await db.execute(
            select(func.count(Subscription.id)).where(
                Subscription.tier == tier, Subscription.is_active.is_(True)
            )
        )
        tier_counts[tier] = result.scalar() or 0

    # New subscriptions in period
    new_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.created_at >= cutoff_date,
            Subscription.tier != "free",
        )
    )
    new_subscriptions = new_subs_result.scalar() or 0

    # Cancellations in period
    canceled_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.updated_at >= cutoff_date,
            Subscription.status == SubscriptionStatus.CANCELED.value,
        )
    )
    canceled_subscriptions = canceled_subs_result.scalar() or 0

    # Revenue estimate (using pricing from /pricing endpoint)
    pricing = {
        "plus": {"monthly": 9, "yearly": 90},
        "pro": {"monthly": 29, "yearly": 290},
        "enterprise": {"monthly": 99, "yearly": 990},
    }

    # Get subscriptions with billing period
    active_paid_subs = await db.execute(
        select(Subscription).where(
            Subscription.tier.in_(["plus", "pro", "enterprise"]),
            Subscription.is_active.is_(True),
        )
    )
    paid_subscriptions = active_paid_subs.scalars().all()

    monthly_revenue = 0
    yearly_revenue = 0
    for sub in paid_subscriptions:
        tier = sub.tier
        period = sub.billing_period or "monthly"
        if tier in pricing:
            if period == "yearly":
                yearly_revenue += pricing[tier]["yearly"]
            else:
                monthly_revenue += pricing[tier]["monthly"]

    total_mrr = monthly_revenue + (yearly_revenue / 12)
    total_arr = (monthly_revenue * 12) + yearly_revenue

    # Conversion rate (new paid / total new users)
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= cutoff_date)
    )
    new_users = new_users_result.scalar() or 0

    conversion_rate = (new_subscriptions / new_users * 100) if new_users > 0 else 0

    # Churn rate
    total_active_paid = sum(
        tier_counts.get(tier, 0) for tier in ["plus", "pro", "enterprise"]
    )
    churn_rate = (
        (canceled_subscriptions / total_active_paid * 100) if total_active_paid > 0 else 0
    )

    return {
        "period_days": days,
        "tier_distribution": tier_counts,
        "new_subscriptions": new_subscriptions,
        "canceled_subscriptions": canceled_subscriptions,
        "new_users": new_users,
        "conversion_rate": round(conversion_rate, 2),
        "churn_rate": round(churn_rate, 2),
        "revenue": {
            "monthly_recurring_revenue": round(total_mrr, 2),
            "annual_recurring_revenue": round(total_arr, 2),
            "monthly_subscriptions": monthly_revenue,
            "yearly_subscriptions": yearly_revenue,
        },
    }