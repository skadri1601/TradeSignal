"""
Organization model for multi-user accounts and team management.

Supports seat-based licensing, team invites, and role hierarchy.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrganizationRole(str, Enum):
    """Organization member roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class OrganizationMember(Base):
    """
    Organization membership model.

    Links users to organizations with roles.
    """

    __tablename__ = "organization_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=OrganizationRole.VIEWER.value)

    # Invite tracking
    invited_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    invited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_organization_members_org_user", "organization_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember(org_id={self.organization_id}, user_id={self.user_id}, role={self.role})>"


class Organization(Base):
    """
    Organization model for team accounts.

    Attributes:
        id: Primary key
        name: Organization name
        slug: URL-friendly organization identifier
        owner_id: User who owns the organization
        subscription_tier: Organization subscription tier
        seat_limit: Maximum number of seats (licenses)
        seats_used: Current number of active seats
        created_at: When organization was created
        updated_at: When organization was last updated
    """

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Owner
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default="free"
    )
    seat_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    seats_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember", backref="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, seats={self.seats_used}/{self.seat_limit})>"


class OrganizationInvite(Base):
    """
    Organization invite model for team invitations.

    Attributes:
        id: Primary key
        organization_id: Organization being invited to
        email: Email address of invitee
        role: Role to assign upon acceptance
        invited_by: User who sent the invite
        token: Unique invite token
        expires_at: When invite expires
        accepted_at: When invite was accepted
        created_at: When invite was created
    """

    __tablename__ = "organization_invites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=OrganizationRole.VIEWER.value)

    invited_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Invite token
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Status
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<OrganizationInvite(org_id={self.organization_id}, email={self.email}, role={self.role})>"


class AuditLog(Base):
    """
    Audit log for organization activity tracking.

    Tracks user actions within organizations for compliance and security.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Action details
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Details
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON or text
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_audit_logs_org_created", "organization_id", "created_at"),
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"

