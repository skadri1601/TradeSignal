"""
Organization Service for multi-user account management.

Handles:
- Organization creation and management
- Team invites with email verification
- Seat-based licensing
- Role hierarchy (Admin, Analyst, Viewer)
- Audit logging
"""

import logging
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.organization import (
    Organization,
    OrganizationMember,
    OrganizationInvite,
    OrganizationRole,
    AuditLog,
)
from app.models.user import User

logger = logging.getLogger(__name__)


class OrganizationService:
    """Service for managing organizations and team accounts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(
        self, owner_id: int, name: str, description: Optional[str] = None
    ) -> Organization:
        """
        Create a new organization.

        Args:
            owner_id: User ID of the organization owner
            name: Organization name
            description: Optional description

        Returns:
            Created Organization
        """
        # Generate slug from name
        slug = self._generate_slug(name)

        # Check if slug exists
        existing = await self.db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        if existing.scalar_one_or_none():
            # Append number if exists
            counter = 1
            while True:
                new_slug = f"{slug}-{counter}"
                check = await self.db.execute(
                    select(Organization).where(Organization.slug == new_slug)
                )
                if not check.scalar_one_or_none():
                    slug = new_slug
                    break
                counter += 1

        organization = Organization(
            name=name,
            slug=slug,
            owner_id=owner_id,
            description=description,
            seat_limit=1,  # Default, can be upgraded
            seats_used=1,  # Owner counts as one seat
        )

        self.db.add(organization)
        await self.db.flush()

        # Add owner as admin member
        member = OrganizationMember(
            organization_id=organization.id,
            user_id=owner_id,
            role=OrganizationRole.ADMIN.value,
            joined_at=datetime.utcnow(),
        )
        self.db.add(member)

        # Log creation
        await self._log_audit(
            organization_id=organization.id,
            user_id=owner_id,
            action="organization.created",
            resource_type="organization",
            resource_id=organization.id,
        )

        await self.db.commit()
        await self.db.refresh(organization)

        return organization

    async def invite_member(
        self,
        organization_id: int,
        email: str,
        role: str,
        invited_by: int,
    ) -> OrganizationInvite:
        """
        Invite a user to join an organization.

        Args:
            organization_id: Organization ID
            email: Email address of invitee
            role: Role to assign (admin, analyst, viewer)
            invited_by: User ID who sent the invite

        Returns:
            Created OrganizationInvite
        """
        # Check if user already a member
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            # Check if already a member
            member_check = await self.db.execute(
                select(OrganizationMember).where(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user.id,
                )
            )
            if member_check.scalar_one_or_none():
                raise ValueError("User is already a member of this organization")

        # Check seat limit
        org = await self.db.get(Organization, organization_id)
        if org.seats_used >= org.seat_limit:
            raise ValueError("Organization has reached its seat limit")

        # Generate invite token
        token = secrets.token_urlsafe(32)

        # Create invite (expires in 7 days)
        invite = OrganizationInvite(
            organization_id=organization_id,
            email=email,
            role=role,
            invited_by=invited_by,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )

        self.db.add(invite)

        # Log invitation
        await self._log_audit(
            organization_id=organization_id,
            user_id=invited_by,
            action="member.invited",
            resource_type="invite",
            resource_id=invite.id,
            details=f"Invited {email} as {role}",
        )

        await self.db.commit()
        await self.db.refresh(invite)

        return invite

    async def accept_invite(self, token: str, user_id: int) -> OrganizationMember:
        """
        Accept an organization invite.

        Args:
            token: Invite token
            user_id: User ID accepting the invite

        Returns:
            Created OrganizationMember
        """
        # Find invite
        result = await self.db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.token == token,
                OrganizationInvite.accepted_at.is_(None),
                OrganizationInvite.expires_at > datetime.utcnow(),
            )
        )
        invite = result.scalar_one_or_none()

        if not invite:
            raise ValueError("Invalid or expired invite token")

        # Verify email matches
        user = await self.db.get(User, user_id)
        if user.email.lower() != invite.email.lower():
            raise ValueError("Invite email does not match user email")

        # Check if already a member
        existing = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == invite.organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("User is already a member of this organization")

        # Check seat limit
        org = await self.db.get(Organization, invite.organization_id)
        if org.seats_used >= org.seat_limit:
            raise ValueError("Organization has reached its seat limit")

        # Create member
        member = OrganizationMember(
            organization_id=invite.organization_id,
            user_id=user_id,
            role=invite.role,
            invited_by=invite.invited_by,
            invited_at=invite.created_at,
            joined_at=datetime.utcnow(),
        )
        self.db.add(member)

        # Update seat count
        org.seats_used += 1

        # Mark invite as accepted
        invite.accepted_at = datetime.utcnow()

        # Log acceptance
        await self._log_audit(
            organization_id=invite.organization_id,
            user_id=user_id,
            action="member.joined",
            resource_type="member",
            resource_id=member.id,
        )

        await self.db.commit()
        await self.db.refresh(member)

        return member

    async def remove_member(
        self, organization_id: int, user_id: int, removed_by: int
    ) -> None:
        """
        Remove a member from an organization.

        Args:
            organization_id: Organization ID
            user_id: User ID to remove
            removed_by: User ID performing the removal
        """
        # Get member
        result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            raise ValueError("User is not a member of this organization")

        # Don't allow removing owner
        org = await self.db.get(Organization, organization_id)
        if org.owner_id == user_id:
            raise ValueError("Cannot remove organization owner")

        # Deactivate member
        member.is_active = False

        # Update seat count
        org.seats_used = max(0, org.seats_used - 1)

        # Log removal
        await self._log_audit(
            organization_id=organization_id,
            user_id=removed_by,
            action="member.removed",
            resource_type="member",
            resource_id=member.id,
            details=f"Removed user {user_id}",
        )

        await self.db.commit()

    async def update_member_role(
        self,
        organization_id: int,
        user_id: int,
        new_role: str,
        updated_by: int,
    ) -> OrganizationMember:
        """
        Update a member's role.

        Args:
            organization_id: Organization ID
            user_id: User ID to update
            new_role: New role (admin, analyst, viewer)
            updated_by: User ID performing the update

        Returns:
            Updated OrganizationMember
        """
        result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()

        if not member:
            raise ValueError("User is not a member of this organization")

        old_role = member.role
        member.role = new_role

        # Log role change
        await self._log_audit(
            organization_id=organization_id,
            user_id=updated_by,
            action="member.role_updated",
            resource_type="member",
            resource_id=member.id,
            details=f"Role changed from {old_role} to {new_role}",
        )

        await self.db.commit()
        await self.db.refresh(member)

        return member

    async def get_user_organizations(self, user_id: int) -> List[Organization]:
        """Get all organizations a user belongs to."""
        result = await self.db.execute(
            select(Organization)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_organization_members(
        self, organization_id: int
    ) -> List[OrganizationMember]:
        """Get all active members of an organization."""
        result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def _log_audit(
        self,
        organization_id: Optional[int],
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Log an audit event."""
        log_entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log_entry)

    @staticmethod
    def _generate_slug(name: str) -> str:
        """Generate URL-friendly slug from organization name."""
        import re

        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = re.sub(r"^-+|-+$", "", slug)
        return slug[:100]  # Limit length

