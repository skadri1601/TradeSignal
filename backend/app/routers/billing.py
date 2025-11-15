"""
Billing and subscription management endpoints.

Handles Stripe integration for premium subscriptions.
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import stripe

from app.database import get_db
from app.services.tier_service import TierService
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus


class CheckoutRequest(BaseModel):
    """Request model for creating checkout session."""
    tier: str

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Stripe Price IDs (create these in Stripe Dashboard)
STRIPE_PRICES = {
    "basic": os.getenv("STRIPE_PRICE_BASIC", "price_basic_monthly"),
    "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise_monthly"),
}


@router.get("/usage")
async def get_usage_stats(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current user's usage statistics and tier limits.

    Returns usage counts, limits, and remaining quota for the current billing period.
    """
    # TODO: Get user_id from authenticated session
    # For now, using placeholder user_id = 1
    user_id = 1

    usage_stats = await TierService.get_usage_stats(user_id, db)
    return usage_stats


@router.post("/create-checkout-session")
async def create_checkout_session(
    checkout_request: CheckoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription upgrade.

    Args:
        checkout_request: Request body with tier selection

    Returns:
        Stripe checkout session URL
    """
    tier = checkout_request.tier

    # Validate tier
    if tier not in STRIPE_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}. Must be one of: {list(STRIPE_PRICES.keys())}"
        )

    # TODO: Get user_id from authenticated session
    user_id = 1  # Placeholder

    # Check if Stripe is configured
    if not stripe.api_key or stripe.api_key.startswith("your-"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured. Please contact support."
        )

    try:
        # Get or create Stripe customer
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        customer_id = subscription.stripe_customer_id if subscription else None

        if not customer_id:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                metadata={"user_id": str(user_id)}
            )
            customer_id = customer.id

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": STRIPE_PRICES[tier],
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/pricing",
            metadata={
                "user_id": str(user_id),
                "tier": tier,
            },
        )

        logger.info(f"Created checkout session for user {user_id}, tier {tier}")

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing error: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhooks for subscription events.

    Events handled:
    - checkout.session.completed: Subscription created
    - customer.subscription.updated: Subscription changed
    - customer.subscription.deleted: Subscription canceled
    - invoice.payment_succeeded: Payment successful
    - invoice.payment_failed: Payment failed
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle event
    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Received Stripe webhook: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            # Payment successful, create subscription
            session = event_data
            user_id = int(session["metadata"]["user_id"])
            tier = session["metadata"]["tier"]
            customer_id = session["customer"]
            subscription_id = session["subscription"]

            # Get subscription details
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)

            # Create or update subscription in database
            result = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                # Update existing
                subscription.tier = tier
                subscription.status = SubscriptionStatus.ACTIVE.value
                subscription.stripe_customer_id = customer_id
                subscription.stripe_subscription_id = subscription_id
                subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
                subscription.is_active = True
            else:
                # Create new
                subscription = Subscription(
                    user_id=user_id,
                    tier=tier,
                    status=SubscriptionStatus.ACTIVE.value,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                    current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                    is_active=True
                )
                db.add(subscription)

            await db.commit()
            logger.info(f"Subscription created/updated for user {user_id}, tier {tier}")

        elif event_type == "customer.subscription.updated":
            # Subscription changed (upgrade/downgrade)
            stripe_subscription = event_data
            subscription_id = stripe_subscription["id"]

            result = await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.current_period_start = datetime.fromtimestamp(stripe_subscription["current_period_start"])
                subscription.current_period_end = datetime.fromtimestamp(stripe_subscription["current_period_end"])
                subscription.cancel_at_period_end = stripe_subscription.get("cancel_at_period_end", False)
                await db.commit()
                logger.info(f"Subscription updated: {subscription_id}")

        elif event_type == "customer.subscription.deleted":
            # Subscription canceled
            stripe_subscription = event_data
            subscription_id = stripe_subscription["id"]

            result = await db.execute(
                select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                subscription.status = SubscriptionStatus.CANCELED.value
                subscription.is_active = False
                await db.commit()
                logger.info(f"Subscription canceled: {subscription_id}")

        elif event_type == "invoice.payment_failed":
            # Payment failed
            invoice = event_data
            subscription_id = invoice.get("subscription")

            if subscription_id:
                result = await db.execute(
                    select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
                )
                subscription = result.scalar_one_or_none()

                if subscription:
                    subscription.status = SubscriptionStatus.PAST_DUE.value
                    await db.commit()
                    logger.warning(f"Payment failed for subscription: {subscription_id}")

        else:
            logger.info(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"received": True}


@router.post("/cancel-subscription")
async def cancel_subscription(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel user's subscription at end of billing period.

    Does not immediately revoke access - subscription remains active
    until the end of the current billing period.
    """
    # TODO: Get user_id from authenticated session
    user_id = 1  # Placeholder

    try:
        # Get user's subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        # Cancel subscription at period end in Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update database
        subscription.cancel_at_period_end = True
        await db.commit()

        logger.info(f"Subscription canceled for user {user_id} (effective at period end)")

        return {
            "message": "Subscription will be canceled at the end of the current billing period",
            "cancel_at": datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat(),
            "access_until": datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat()
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during cancellation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling subscription: {str(e)}"
        )


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information for all subscription tiers.

    Returns tier features, limits, and monthly pricing.
    """
    return {
        "tiers": {
            "free": {
                "name": "Free",
                "price": 0,
                "features": [
                    "5 AI requests per day",
                    "3 custom alerts",
                    "30 days historical data",
                    "Track up to 10 companies",
                    "Basic insider trading data"
                ]
            },
            "basic": {
                "name": "Basic",
                "price": 9.99,
                "features": [
                    "50 AI requests per day",
                    "20 custom alerts",
                    "1 year historical data",
                    "Track up to 50 companies",
                    "Real-time updates",
                    "Email notifications"
                ]
            },
            "pro": {
                "name": "Pro",
                "price": 29.99,
                "features": [
                    "500 AI requests per day",
                    "100 custom alerts",
                    "Unlimited historical data",
                    "Track unlimited companies",
                    "Real-time updates",
                    "API access",
                    "Advanced analytics",
                    "Priority support"
                ]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 99.99,
                "features": [
                    "Unlimited AI requests",
                    "Unlimited alerts",
                    "Full historical data access",
                    "Track unlimited companies",
                    "Real-time updates",
                    "Full API access",
                    "Advanced analytics",
                    "Priority support",
                    "Custom integrations",
                    "Dedicated account manager"
                ]
            }
        }
    }
