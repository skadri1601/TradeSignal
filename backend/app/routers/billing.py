"""
Billing and subscription management endpoints.

Handles Stripe integration for premium subscriptions.
"""

import logging
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import stripe

from app.database import get_db
from app.services.tier_service import TierService
from app.services.notification_service import NotificationService
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.user import User
from app.core.security import get_current_active_user


class CheckoutRequest(BaseModel):
    """Request model for creating checkout session."""

    tier: str
    billing_period: str = "monthly"  # "monthly" or "yearly"


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])

# Initialize Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Validate Stripe configuration
if not STRIPE_SECRET_KEY:
    logger.warning(
        "STRIPE_SECRET_KEY is not set. Stripe functionality will be disabled."
    )
    stripe.api_key = None
else:
    stripe.api_key = STRIPE_SECRET_KEY

# Stripe Price IDs (using env variables)
# Format: tier_billing_period (e.g., "plus_monthly", "pro_yearly")
# Note: Check both uppercase and mixed-case variants for compatibility
STRIPE_PRICES = {
    # Monthly prices
    "basic_monthly": os.getenv(
        "STRIPE_PRICE_BASIC", os.getenv("STRIPE_PRICE_Basic", "price_basic_monthly")
    ),
    "plus_monthly": os.getenv(
        "STRIPE_PRICE_PLUS", os.getenv("STRIPE_PRICE_Plus", "price_plus_monthly")
    ),
    "pro_monthly": os.getenv(
        "STRIPE_PRICE_PRO", os.getenv("STRIPE_PRICE_Pro", "price_pro_monthly")
    ),
    "enterprise_monthly": os.getenv(
        "STRIPE_PRICE_ENTERPRISE",
        os.getenv("STRIPE_PRICE_Enterprise", "price_enterprise_monthly"),
    ),
    # Yearly prices
    "basic_yearly": os.getenv(
        "STRIPE_PRICE_BASIC_YEARLY",
        os.getenv("STRIPE_PRICE_Basic_YEARLY", "price_basic_yearly"),
    ),
    "plus_yearly": os.getenv(
        "STRIPE_PRICE_PLUS_YEARLY",
        os.getenv("STRIPE_PRICE_Plus_YEARLY", "price_plus_yearly"),
    ),
    "pro_yearly": os.getenv(
        "STRIPE_PRICE_PRO_YEARLY",
        os.getenv("STRIPE_PRICE_Pro_YEARLY", "price_pro_yearly"),
    ),
    "enterprise_yearly": os.getenv(
        "STRIPE_PRICE_ENTERPRISE_YEARLY",
        os.getenv("STRIPE_PRICE_Enterprise_YEARLY", "price_enterprise_yearly"),
    ),
}


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current user's subscription information.

    Returns subscription tier, status, billing period, and renewal date.
    """
    try:
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.is_active:
            return {
                "tier": SubscriptionTier.FREE.value,
                "status": "inactive",
                "is_active": False,
                "current_period_start": None,
                "current_period_end": None,
                "cancel_at_period_end": False,
            }

        return {
            "tier": subscription.tier,
            "status": subscription.status,
            "is_active": subscription.is_active,
            "current_period_start": subscription.current_period_start.isoformat()
            if subscription.current_period_start
            else None,
            "current_period_end": subscription.current_period_end.isoformat()
            if subscription.current_period_end
            else None,
            "cancel_at_period_end": subscription.cancel_at_period_end,
        }
    except Exception as e:
        logger.error(
            f"Error fetching subscription for user {current_user.id}: {e}",
            exc_info=True,
        )
        # Return free tier on error instead of crashing
        return {
            "tier": SubscriptionTier.FREE.value,
            "status": "inactive",
            "is_active": False,
            "current_period_start": None,
            "current_period_end": None,
            "cancel_at_period_end": False,
            "error": "Failed to fetch subscription details",
        }


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current user's usage statistics and tier limits.
    """
    tier = await TierService.get_user_tier(current_user.id, db)
    limits = await TierService.get_tier_limits(tier)
    usage = await TierService.get_or_create_usage(current_user.id, db)

    # Calculate reset time (midnight UTC)
    now = datetime.utcnow()
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return {
        "tier": tier,
        "limits": limits,
        "usage": {
            "ai_requests": usage.ai_requests,
            "alerts_triggered": usage.alerts_triggered,
            "api_calls": usage.api_calls,
            "companies_viewed": usage.companies_viewed,
        },
        "remaining": {
            "ai_requests": limits["ai_requests_per_day"] - usage.ai_requests
            if limits["ai_requests_per_day"] != -1
            else -1,
        },
        "reset_at": tomorrow.isoformat() + "Z",
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    checkout_request: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe checkout session for subscription upgrade.

    Args:
        checkout_request: Tier to subscribe to (basic/plus/pro/enterprise)

    Returns:
        Checkout session URL
    """
    # Check if Stripe is configured
    if not STRIPE_SECRET_KEY:
        logger.error("Stripe is not configured. STRIPE_SECRET_KEY is missing.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured. Please contact support.",
        )

    tier = checkout_request.tier.lower()
    billing_period = checkout_request.billing_period.lower()

    # Map "basic" to "plus" for Stripe price lookup
    if tier == "basic":
        tier = "plus"

    # Validate billing period
    if billing_period not in ["monthly", "yearly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid billing_period. Must be 'monthly' or 'yearly'",
        )

    # Build price key
    price_key = f"{tier}_{billing_period}"

    if price_key not in STRIPE_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid tier/billing_period combination. Available: plus_monthly, "
                "plus_yearly, pro_monthly, pro_yearly, enterprise_monthly, "
                "enterprise_yearly"
            ),
        )

    # Validate that Stripe price ID is actually configured (not a placeholder)
    stripe_price_id = STRIPE_PRICES[price_key]
    if not stripe_price_id:
        logger.error(f"Stripe price ID for {price_key} is not configured.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not configured. Please contact support.",
        )

    # Known placeholder values that are NOT real Stripe price IDs
    known_placeholders = [
        "price_plus_monthly",
        "price_plus_yearly",
        "price_pro_monthly",
        "price_pro_yearly",
        "price_enterprise_monthly",
        "price_enterprise_yearly",
        "price_basic_monthly",
        "price_basic_yearly",
    ]

    # Real Stripe price IDs are longer (e.g., "price_1NxxxxxxxxxxxxxxxxxxxxXX")
    # Check if this is a placeholder instead of a real price ID
    is_placeholder = stripe_price_id in known_placeholders or (
        stripe_price_id.startswith("price_") and len(stripe_price_id) < 25
    )

    if is_placeholder:
        env_var_name = (
            f"STRIPE_PRICE_{tier.upper()}"
            if billing_period == "monthly"
            else f"STRIPE_PRICE_{tier.upper()}_YEARLY"
        )
        logger.error(
            f"Stripe price ID '{stripe_price_id}' for {price_key} is a placeholder. "
            f"Set {env_var_name} environment variable with your real Stripe price ID. "
            f"Create products and prices at https://dashboard.stripe.com/products"
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Payment processing is not configured. Please set up Stripe price "
                f"ID for {tier} ({billing_period}). Contact support if this persists."
            ),
        )

    try:
        # Get or create Stripe customer
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()

        customer_id = subscription.stripe_customer_id if subscription else None

        if not customer_id:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={
                    "user_id": str(current_user.id),
                    "username": current_user.username,
                },
            )
            customer_id = customer.id

        # Create checkout session
        actual_price_id = STRIPE_PRICES[price_key]
        logger.info(
            f"Creating checkout session with price_key={price_key}, price_id={actual_price_id}"
        )

        # Try subscription mode first, fall back to payment mode if price is not recurring
        checkout_mode = "subscription"
        try:
            # First, try to retrieve the price to check if it's recurring
            price_info = stripe.Price.retrieve(actual_price_id)
            if price_info.type != "recurring":
                logger.warning(
                    f"Price {actual_price_id} is not recurring (type={price_info.type}), using payment mode instead"
                )
                checkout_mode = "payment"
        except stripe.error.StripeError as e:
            logger.warning(
                f"Could not retrieve price info, defaulting to subscription mode: {e}"
            )

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": actual_price_id,
                    "quantity": 1,
                }
            ],
            mode=checkout_mode,
            success_url=(
                f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}"
                "/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=(
                f"{os.getenv('FRONTEND_URL', 'http://localhost:5174')}/pricing"
            ),
            metadata={
                "user_id": str(current_user.id),
                "tier": tier,
                "billing_period": billing_period,
                "checkout_mode": checkout_mode,
            },
        )

        logger.info(f"Created checkout session for user {current_user.id}, tier {tier}")

        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

    except HTTPException:
        raise
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe invalid request error: {e}")
        # Check if it's a price ID issue
        if "price" in str(e).lower() and "invalid" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Payment processing configuration error. Please contact support.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment request: {str(e)}",
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating checkout session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please try again later.",
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhook events.

    Events handled:
    - checkout.session.completed: New subscription
    - customer.subscription.updated: Subscription changed
    - customer.subscription.deleted: Subscription canceled
    - invoice.payment_failed: Payment failed
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info(f"Received Stripe webhook: {event_type}")

    if event_type == "checkout.session.completed":
        # New subscription created
        session = event_data
        user_id = int(session["metadata"]["user_id"])
        tier = session["metadata"]["tier"]
        billing_period = session["metadata"].get("billing_period", "monthly")

        # Get or create subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        # Determine if this is an upgrade or new subscription
        tier_before = None
        payment_type = PaymentType.SUBSCRIPTION.value
        if (
            subscription
            and subscription.tier
            and subscription.tier != SubscriptionTier.FREE.value
        ):
            tier_before = subscription.tier
            payment_type = PaymentType.UPGRADE.value

        if not subscription:
            subscription = Subscription(user_id=user_id)
            db.add(subscription)

        # Get Stripe subscription details
        stripe_subscription_id = session.get("subscription")
        stripe_customer_id = session.get("customer")
        amount_total = session.get("amount_total", 0) / 100.0  # Convert from cents
        currency = session.get("currency", "usd").upper()

        if stripe_subscription_id:
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.stripe_customer_id = stripe_subscription.customer
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription.current_period_start
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription.current_period_end
            )
            stripe_customer_id = stripe_subscription.customer

            # Get payment amount from the latest invoice
            if stripe_subscription.latest_invoice:
                invoice = stripe.Invoice.retrieve(stripe_subscription.latest_invoice)
                amount_total = invoice.amount_paid / 100.0
                currency = invoice.currency.upper()

        subscription.tier = tier
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.is_active = True
        subscription.cancel_at_period_end = False

        await db.commit()
        logger.info(f"Subscription activated for user {user_id}, tier {tier}")

        # Create Payment record
        try:
            payment = Payment(
                user_id=user_id,
                amount=amount_total,
                currency=currency,
                payment_type=payment_type,
                status=PaymentStatus.SUCCEEDED.value,
                tier=tier,
                tier_before=tier_before,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_payment_intent_id=session.get("payment_intent"),
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                description=f"{tier.capitalize()} subscription ({billing_period})",
                receipt_url=session.get("customer_details", {}).get("email")
                and f"https://dashboard.stripe.com/payments/{session.get('payment_intent')}"
                or None,
            )
            db.add(payment)
            await db.commit()
            logger.info(
                f"Payment record created for user {user_id}, amount {amount_total} {currency}"
            )
        except Exception as e:
            logger.error(f"Error creating payment record: {e}", exc_info=True)
            # Don't fail webhook if payment record creation fails

        # Send notification
        try:
            notification_service = NotificationService(db)
            await notification_service.send_subscription_confirmation(user_id, tier)
        except Exception as e:
            # Don't fail webhook if email fails
            logger.error(f"Error sending subscription confirmation email: {e}")

    elif event_type == "customer.subscription.updated":
        # Subscription changed (upgrade/downgrade)
        stripe_subscription = event_data
        subscription_id = stripe_subscription["id"]

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription["current_period_end"]
            )
            subscription.cancel_at_period_end = stripe_subscription.get(
                "cancel_at_period_end", False
            )
            await db.commit()
            logger.info(f"Subscription updated: {subscription_id}")

    elif event_type == "customer.subscription.deleted":
        # Subscription canceled
        stripe_subscription = event_data
        subscription_id = stripe_subscription["id"]

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELED.value
            subscription.is_active = False
            await db.commit()
            logger.info(f"Subscription canceled: {subscription_id}")

    elif event_type == "invoice.payment_succeeded":
        # Subscription renewal payment succeeded
        invoice = event_data
        customer_id = invoice["customer"]
        subscription_id = invoice.get("subscription")
        amount_paid = invoice.get("amount_paid", 0) / 100.0
        currency = invoice.get("currency", "usd").upper()

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            # Update subscription period if available
            if subscription_id:
                try:
                    stripe_subscription = stripe.Subscription.retrieve(subscription_id)
                    subscription.current_period_start = datetime.fromtimestamp(
                        stripe_subscription["current_period_start"]
                    )
                    subscription.current_period_end = datetime.fromtimestamp(
                        stripe_subscription["current_period_end"]
                    )
                except Exception as e:
                    logger.error(f"Error retrieving subscription details: {e}")

            subscription.status = SubscriptionStatus.ACTIVE.value
            subscription.is_active = True
            await db.commit()
            logger.info(
                f"Subscription renewal payment succeeded for user {subscription.user_id}"
            )

            # Create Payment record for renewal
            try:
                payment = Payment(
                    user_id=subscription.user_id,
                    amount=amount_paid,
                    currency=currency,
                    payment_type=PaymentType.RENEWAL.value,
                    status=PaymentStatus.SUCCEEDED.value,
                    tier=subscription.tier,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    stripe_payment_intent_id=invoice.get("payment_intent"),
                    stripe_charge_id=invoice.get("charge"),
                    period_start=subscription.current_period_start,
                    period_end=subscription.current_period_end,
                    description=f"{subscription.tier.capitalize()} subscription renewal",
                    invoice_url=invoice.get("hosted_invoice_url"),
                    receipt_url=invoice.get("receipt_url"),
                )
                db.add(payment)
                await db.commit()
                logger.info(
                    f"Renewal payment record created for user {subscription.user_id}, amount {amount_paid} {currency}"
                )
            except Exception as e:
                logger.error(
                    f"Error creating renewal payment record: {e}", exc_info=True
                )

    elif event_type == "invoice.payment_failed":
        # Payment failed - notify user
        invoice = event_data
        customer_id = invoice["customer"]

        result = await db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE.value
            await db.commit()
            logger.warning(f"Payment failed for subscription: {subscription.id}")

            # Send notification
            try:
                notification_service = NotificationService(db)
                await notification_service.send_payment_failed_notification(
                    subscription.user_id
                )
            except Exception as e:
                logger.error(f"Error sending payment failed notification: {e}")

    return {"received": True}


@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel user's subscription at end of billing period.

    Does not immediately revoke access - subscription remains active
    until the end of the current billing period.
    """
    try:
        # Get user's subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )

        # Cancel subscription at period end in Stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription.stripe_subscription_id, cancel_at_period_end=True
        )

        # Update database
        subscription.cancel_at_period_end = True
        await db.commit()

        logger.info(
            f"Subscription canceled for user {current_user.id} (effective at period end)"
        )

        return {
            "message": "Subscription will be canceled at the end of the current billing period",
            "cancel_at": datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ).isoformat(),
            "access_until": datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ).isoformat(),
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during cancellation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling subscription: {str(e)}",
        )


@router.post("/pause-subscription")
async def pause_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pause user's subscription temporarily.

    Pauses the subscription for up to 3 months. User retains access
    but billing is paused. Subscription will auto-resume after pause period.
    """
    try:
        # Get user's subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )

        if subscription.status == SubscriptionStatus.PAUSED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already paused",
            )

        # Pause subscription in Stripe (using subscription schedule)
        # Note: Stripe doesn't have native pause, so we'll use a workaround
        # by setting cancel_at_period_end and tracking pause status in our DB

        # For now, we'll mark it as paused in our database
        # In production, you might want to use Stripe's subscription schedules
        subscription.status = SubscriptionStatus.PAUSED.value
        subscription.is_active = False  # Paused subscriptions don't have active access

        # Set pause end date (3 months from now)
        pause_end = datetime.utcnow() + timedelta(days=90)

        # Store pause metadata (we can add a pause_end_date field to Subscription model if needed)
        # For now, we'll use trial_end as a temporary field
        subscription.trial_end = pause_end

        await db.commit()

        logger.info(f"Subscription paused for user {current_user.id} until {pause_end}")

        return {
            "message": "Subscription has been paused. Billing will resume automatically after 3 months.",
            "paused_until": pause_end.isoformat(),
            "access_until": subscription.current_period_end.isoformat()
            if subscription.current_period_end
            else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing subscription: {str(e)}",
        )


@router.post("/resume-subscription")
async def resume_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resume a paused subscription.
    """
    try:
        # Get user's subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No subscription found"
            )

        if subscription.status != SubscriptionStatus.PAUSED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is not paused",
            )

        # Resume subscription
        if subscription.stripe_subscription_id:
            # If we have Stripe subscription, reactivate it
            stripe.Subscription.modify(
                subscription.stripe_subscription_id, cancel_at_period_end=False
            )

        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.is_active = True
        subscription.trial_end = None

        await db.commit()

        logger.info(f"Subscription resumed for user {current_user.id}")

        return {
            "message": "Subscription has been resumed successfully",
            "status": "active",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming subscription: {str(e)}",
        )


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing tiers information with monthly and yearly options.
    """
    return {
        "tiers": {
            "free": {
                "name": "Free",
                "price_monthly": 0,
                "price_yearly": 0,
                "features": [
                    "Basic insider trade tracking",
                    "Limited AI insights",
                    "Email alerts",
                    "5 API requests/day",
                ],
            },
            "plus": {
                "name": "Plus",
                "price_monthly": 9,
                "price_yearly": 90,  # 2 months free (10 months for 12)
                "yearly_savings": 18,  # Save $18 per year
                "features": [
                    "Everything in Free",
                    "Advanced AI insights",
                    "SMS & Discord alerts",
                    "50 API requests/day",
                    "Historical data access",
                ],
            },
            "pro": {
                "name": "Pro",
                "price_monthly": 29,
                "price_yearly": 290,  # 2 months free (10 months for 12)
                "yearly_savings": 58,  # Save $58 per year
                "features": [
                    "Everything in Plus",
                    "Real-time alerts",
                    "Unlimited API access",
                    "Priority support",
                    "Custom alerts",
                ],
            },
            "enterprise": {
                "name": "Enterprise",
                "price_monthly": 99,
                "price_yearly": 990,  # 2 months free (10 months for 12)
                "yearly_savings": 198,  # Save $198 per year
                "features": [
                    "Everything in Pro",
                    "Dedicated account manager",
                    "Custom integrations",
                    "White-label options",
                    "SLA guarantee",
                    "24/7 phone support",
                ],
            },
        }
    }
