"""
Order History API endpoints.

Provides access to payment/order history for users.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.payment import Payment
from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/", response_model=PaginatedResponse[dict])
@limiter.limit("30/minute")
async def get_order_history(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's order/payment history.

    Returns paginated list of all payment transactions including:
    - Subscription purchases
    - Upgrades/downgrades
    - Renewals
    - Refunds
    """
    # Get total count
    count_query = select(Payment).where(Payment.user_id == current_user.id)
    count_result = await db.execute(
        select(func.count()).select_from(count_query.subquery())
    )
    total = count_result.scalar() or 0

    # Get paginated payments
    query = (
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(desc(Payment.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    payments = result.scalars().all()

    # Format response
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

    return {"items": orders, "total": total, "skip": skip, "limit": limit}


@router.get("/{order_id}")
@limiter.limit("30/minute")
async def get_order_details(
    request: Request,
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific order.
    """
    result = await db.execute(
        select(Payment).where(
            Payment.id == order_id, Payment.user_id == current_user.id
        )
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return {
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
        "stripe_payment_intent_id": payment.stripe_payment_intent_id,
        "refunded_amount": float(payment.refunded_amount)
        if payment.refunded_amount
        else None,
        "refunded_at": payment.refunded_at.isoformat() if payment.refunded_at else None,
        "refund_reason": payment.refund_reason,
        "period_start": payment.period_start.isoformat()
        if payment.period_start
        else None,
        "period_end": payment.period_end.isoformat() if payment.period_end else None,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
    }
