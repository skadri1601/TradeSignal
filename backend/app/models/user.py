"""
User model for authentication and user management.
"""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.subscription import Subscription
    from app.models.notification import Notification



class User(Base):
    """
    User account model.

    Attributes:
        id: Primary key
        email: User email (unique)
        username: Username (unique)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        date_of_birth: User's date of birth
        phone_number: User's phone number
        bio: User biography/description
        avatar_url: URL to user's profile picture
        is_active: Whether account is active
        is_verified: Whether email is verified
        is_superuser: Whether user has admin privileges
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile fields
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Role field: 'customer' (default), 'support' (manages users), 'super_admin' (manages everything)
    role: Mapped[str] = mapped_column(
        String(20), default="customer", nullable=False, index=True
    )

    # Auth provider: 'custom' (our JWT), 'supabase' (Supabase Auth), or 'clerk' (Clerk Auth)
    auth_provider: Mapped[str] = mapped_column(
        String(20), default="custom", nullable=False
    )
    # Supabase user ID (UUID from Supabase auth.users table)
    supabase_uid: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, unique=True, index=True
    )
    # Clerk user ID (from Clerk auth)
    clerk_uid: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )

    # Password reset fields
    password_reset_token: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="user", uselist=False, lazy="selectin"
    )
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")

    @property
    def stripe_subscription_tier(self) -> Optional[str]:
        if self.subscription:
            return self.subscription.tier
        return None

    @property
    def subscription_tier(self) -> str:
        """Get user's subscription tier, defaulting to 'free' if no subscription."""
        if self.subscription:
            return self.subscription.tier
        return "free"

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
