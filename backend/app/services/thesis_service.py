"""
Thesis Publishing Service.

Handles:
- Thesis creation and publishing
- Tag management
- Image embedding
- Quality curation
- Reputation scoring
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.models.thesis import (
    Thesis,
    ThesisTag,
    ThesisTagAssociation,
    ThesisImage,
    ThesisVote,
    ThesisComment,
    UserReputation,
)

logger = logging.getLogger(__name__)


class ThesisService:
    """Service for thesis publishing and management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_thesis(
        self,
        author_id: int,
        title: str,
        content: str,
        excerpt: Optional[str] = None,
        ticker: Optional[str] = None,
        company_id: Optional[int] = None,
        tag_names: Optional[List[str]] = None,
    ) -> Thesis:
        """Create a new thesis."""
        slug = self._generate_slug(title)

        # Check if slug exists
        existing = await self.db.execute(
            select(Thesis).where(Thesis.slug == slug)
        )
        if existing.scalar_one_or_none():
            # Append timestamp if exists
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

        thesis = Thesis(
            author_id=author_id,
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt or self._generate_excerpt(content),
            ticker=ticker.upper() if ticker else None,
            company_id=company_id,
            status="draft",
        )
        self.db.add(thesis)
        await self.db.flush()

        # Add tags
        if tag_names:
            await self._add_tags_to_thesis(thesis.id, tag_names)

        # Calculate initial quality score
        quality_score = await self._calculate_quality_score(thesis)
        thesis.quality_score = quality_score

        await self.db.commit()
        await self.db.refresh(thesis)

        return thesis

    async def publish_thesis(self, thesis_id: int) -> Thesis:
        """Publish a thesis."""
        thesis = await self.db.get(Thesis, thesis_id)
        if not thesis:
            raise ValueError("Thesis not found")

        if thesis.status == "published":
            return thesis  # Already published

        thesis.status = "published"
        thesis.published_at = datetime.utcnow()

        # Update author reputation
        await self._update_author_reputation(thesis.author_id)

        await self.db.commit()
        await self.db.refresh(thesis)

        return thesis

    async def add_image(
        self, thesis_id: int, url: str, alt_text: Optional[str] = None, caption: Optional[str] = None
    ) -> ThesisImage:
        """Add an image to a thesis."""
        thesis = await self.db.get(Thesis, thesis_id)
        if not thesis:
            raise ValueError("Thesis not found")

        # Get next display order
        result = await self.db.execute(
            select(func.max(ThesisImage.display_order)).where(
                ThesisImage.thesis_id == thesis_id
            )
        )
        max_order = result.scalar_one() or 0

        image = ThesisImage(
            thesis_id=thesis_id,
            url=url,
            alt_text=alt_text,
            caption=caption,
            display_order=max_order + 1,
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)

        return image

    async def vote_thesis(
        self, thesis_id: int, user_id: int, vote_type: str
    ) -> ThesisVote:
        """Vote on a thesis."""
        thesis = await self.db.get(Thesis, thesis_id)
        if not thesis:
            raise ValueError("Thesis not found")

        # Check if vote exists
        result = await self.db.execute(
            select(ThesisVote).where(
                ThesisVote.thesis_id == thesis_id, ThesisVote.user_id == user_id
            )
        )
        existing_vote = result.scalar_one_or_none()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote
                if vote_type == "upvote":
                    thesis.upvotes = max(0, thesis.upvotes - 1)
                else:
                    thesis.downvotes = max(0, thesis.downvotes - 1)
                await self.db.delete(existing_vote)
            else:
                # Change vote
                if existing_vote.vote_type == "upvote":
                    thesis.upvotes = max(0, thesis.upvotes - 1)
                    thesis.downvotes += 1
                else:
                    thesis.downvotes = max(0, thesis.downvotes - 1)
                    thesis.upvotes += 1
                existing_vote.vote_type = vote_type
                await self.db.commit()
                await self.db.refresh(existing_vote)
                return existing_vote
        else:
            # New vote
            vote = ThesisVote(
                thesis_id=thesis_id, user_id=user_id, vote_type=vote_type
            )
            self.db.add(vote)

            if vote_type == "upvote":
                thesis.upvotes += 1
            else:
                thesis.downvotes += 1

        await self.db.commit()
        if not existing_vote:
            await self.db.refresh(vote)
            return vote

    async def add_comment(
        self, thesis_id: int, author_id: int, content: str, parent_id: Optional[int] = None
    ) -> ThesisComment:
        """Add a comment to a thesis."""
        thesis = await self.db.get(Thesis, thesis_id)
        if not thesis:
            raise ValueError("Thesis not found")

        comment = ThesisComment(
            thesis_id=thesis_id,
            author_id=author_id,
            parent_id=parent_id,
            content=content,
        )
        self.db.add(comment)

        # Update thesis comment count
        thesis.comment_count += 1

        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    async def get_featured_theses(self, limit: int = 10) -> List[Thesis]:
        """Get featured theses."""
        result = await self.db.execute(
            select(Thesis)
            .where(
                Thesis.status == "published",
                Thesis.is_featured.is_(True),
            )
            .order_by(desc(Thesis.published_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_theses_by_ticker(
        self, ticker: str, limit: int = 20, offset: int = 0
    ) -> List[Thesis]:
        """Get theses for a specific ticker."""
        result = await self.db.execute(
            select(Thesis)
            .where(
                Thesis.ticker == ticker.upper(),
                Thesis.status == "published",
            )
            .order_by(desc(Thesis.published_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def _add_tags_to_thesis(self, thesis_id: int, tag_names: List[str]) -> None:
        """Add tags to a thesis."""
        for tag_name in tag_names:
            # Get or create tag
            result = await self.db.execute(
                select(ThesisTag).where(ThesisTag.name == tag_name.lower())
            )
            tag = result.scalar_one_or_none()

            if not tag:
                tag = ThesisTag(
                    name=tag_name.lower(),
                    slug=self._generate_slug(tag_name),
                )
                self.db.add(tag)
                await self.db.flush()

            # Check if association exists
            result = await self.db.execute(
                select(ThesisTagAssociation).where(
                    ThesisTagAssociation.thesis_id == thesis_id,
                    ThesisTagAssociation.tag_id == tag.id,
                )
            )
            if not result.scalar_one_or_none():
                association = ThesisTagAssociation(thesis_id=thesis_id, tag_id=tag.id)
                self.db.add(association)
                tag.thesis_count += 1

    async def _calculate_quality_score(self, thesis: Thesis) -> float:
        """
        Calculate quality score for a thesis (0-100).

        Factors:
        - Content length
        - Structure (headings, paragraphs)
        - Images
        - Tags
        - Company/ticker association
        """
        score = 0.0

        # Content length (0-30 points)
        content_length = len(thesis.content)
        if content_length > 5000:
            score += 30
        elif content_length > 2000:
            score += 20
        elif content_length > 1000:
            score += 10

        # Structure (0-20 points)
        heading_count = thesis.content.count("<h") + thesis.content.count("#")
        if heading_count >= 3:
            score += 20
        elif heading_count >= 1:
            score += 10

        # Images (0-15 points)
        image_count = len(thesis.images) if hasattr(thesis, "images") else 0
        score += min(15, image_count * 5)

        # Tags (0-15 points)
        tag_count = len(thesis.tags) if hasattr(thesis, "tags") else 0
        score += min(15, tag_count * 5)

        # Company association (0-20 points)
        if thesis.ticker or thesis.company_id:
            score += 20

        return min(100.0, score)

    async def _update_author_reputation(self, user_id: int) -> None:
        """Update author reputation score."""
        # Get user's theses
        result = await self.db.execute(
            select(Thesis).where(
                Thesis.author_id == user_id, Thesis.status == "published"
            )
        )
        theses = result.scalars().all()

        # Calculate metrics
        thesis_count = len(theses)
        total_views = sum(t.views for t in theses)
        total_upvotes = sum(t.upvotes for t in theses)
        avg_quality = (
            sum(t.quality_score for t in theses if t.quality_score) / thesis_count
            if thesis_count > 0
            else None
        )

        # Calculate reputation score (0-100)
        reputation_score = 0.0
        if thesis_count > 0:
            # Base score from quality
            if avg_quality:
                reputation_score += avg_quality * 0.4

            # Engagement score (0-40 points)
            engagement_score = min(40.0, (total_upvotes / max(total_views, 1)) * 100)
            reputation_score += engagement_score * 0.4

            # Volume score (0-20 points)
            volume_score = min(20.0, thesis_count * 2)
            reputation_score += volume_score * 0.2

        # Get or create reputation record
        result = await self.db.execute(
            select(UserReputation).where(UserReputation.user_id == user_id)
        )
        reputation = result.scalar_one_or_none()

        if not reputation:
            reputation = UserReputation(user_id=user_id)
            self.db.add(reputation)

        reputation.reputation_score = min(100.0, reputation_score)
        reputation.thesis_count = thesis_count
        reputation.total_views = total_views
        reputation.total_upvotes = total_upvotes
        reputation.average_quality_score = avg_quality
        reputation.calculated_at = datetime.utcnow()

        await self.db.commit()

    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """Generate excerpt from content."""
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", content)
        text = text.strip()

        if len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length].rsplit(" ", 1)[0]
        return truncated + "..."

    @staticmethod
    def _generate_slug(text: str) -> str:
        """Generate URL-friendly slug."""
        slug = text.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = re.sub(r"^-+|-+$", "", slug)
        return slug[:255]

