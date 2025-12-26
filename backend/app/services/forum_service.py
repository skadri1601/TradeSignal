"""
Forum Service for community discussions.

Handles:
- Topic management
- Post creation and moderation
- Threaded comments
- Upvote/downvote system
- Spam detection
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, case, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.forum import (
    ForumTopic,
    ForumPost,
    ForumComment,
    ForumVote,
    ForumModerationLog,
)
from app.models.user import User

logger = logging.getLogger(__name__)


class ForumService:
    """Service for managing community forums."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_topic(
        self, name: str, description: Optional[str] = None, created_by_id: Optional[int] = None
    ) -> ForumTopic:
        """Create a new forum topic."""
        slug = self._generate_slug(name)

        # Check if slug exists
        existing = await self.db.execute(
            select(ForumTopic).where(ForumTopic.slug == slug)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Topic with slug '{slug}' already exists")

        topic = ForumTopic(name=name, slug=slug, description=description, created_by_id=created_by_id)
        self.db.add(topic)
        await self.db.commit()
        await self.db.refresh(topic)

        return topic

    async def create_post(
        self, topic_id: int, author_id: int, title: str, content: str
    ) -> ForumPost:
        """Create a new forum post."""
        # Check topic exists
        topic = await self.db.get(ForumTopic, topic_id)
        if not topic:
            raise ValueError("Topic not found")

        # Spam detection
        spam_score = self._detect_spam(title, content)

        post = ForumPost(
            topic_id=topic_id,
            author_id=author_id,
            title=title,
            content=content,
            spam_score=spam_score,
            is_flagged=spam_score > 0.7 if spam_score else False,
        )
        self.db.add(post)

        # Update topic stats
        topic.post_count += 1
        topic.last_post_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(post)

        return post

    async def create_comment(
        self, post_id: int, author_id: int, content: str, parent_id: Optional[int] = None
    ) -> ForumComment:
        """Create a threaded comment."""
        # Check post exists
        post = await self.db.get(ForumPost, post_id)
        if not post:
            raise ValueError("Post not found")

        if post.is_locked:
            raise ValueError("Post is locked")

        # Calculate depth
        depth = 0
        if parent_id:
            parent = await self.db.get(ForumComment, parent_id)
            if not parent:
                raise ValueError("Parent comment not found")
            depth = parent.depth + 1
            if depth > 5:  # Limit nesting
                raise ValueError("Maximum comment depth exceeded")

        comment = ForumComment(
            post_id=post_id,
            author_id=author_id,
            parent_id=parent_id,
            depth=depth,
            content=content,
        )
        self.db.add(comment)

        # Update post stats
        post.comment_count += 1
        post.last_comment_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(comment)

        return comment

    async def vote(
        self, user_id: int, post_id: Optional[int] = None, comment_id: Optional[int] = None, vote_type: str = "upvote"
    ) -> Dict[str, Any]:
        """Cast a vote on a post or comment."""
        try:
            if not post_id and not comment_id:
                raise ValueError("Must specify either post_id or comment_id")
            if post_id and comment_id:
                raise ValueError("Cannot vote on both post and comment")

            # Check if vote already exists
            if post_id:
                existing = await self.db.execute(
                    select(ForumVote).where(
                        ForumVote.user_id == user_id, ForumVote.post_id == post_id
                    )
                )
                target = await self.db.get(ForumPost, post_id)
            else:
                existing = await self.db.execute(
                    select(ForumVote).where(
                        ForumVote.user_id == user_id, ForumVote.comment_id == comment_id
                    )
                )
                target = await self.db.get(ForumComment, comment_id)

            if not target:
                raise ValueError("Target not found")

            existing_vote = existing.scalar_one_or_none()
            is_toggle = False

            if existing_vote:
                # Update existing vote
                if existing_vote.vote_type == vote_type:
                    # Same vote - remove it (toggle off)
                    is_toggle = True
                    await self.db.execute(
                        delete(ForumVote).where(ForumVote.id == existing_vote.id)
                    )
                    if vote_type == "upvote":
                        target.upvotes = max(0, target.upvotes - 1)
                    else:
                        target.downvotes = max(0, target.downvotes - 1)
                else:
                    # Change vote
                    if existing_vote.vote_type == "upvote":
                        target.upvotes = max(0, target.upvotes - 1)
                        target.downvotes += 1
                    else:
                        target.downvotes = max(0, target.downvotes - 1)
                        target.upvotes += 1
                    existing_vote.vote_type = vote_type
            else:
                # New vote
                vote = ForumVote(
                    user_id=user_id,
                    post_id=post_id,
                    comment_id=comment_id,
                    vote_type=vote_type,
                )
                self.db.add(vote)

                if vote_type == "upvote":
                    target.upvotes += 1
                else:
                    target.downvotes += 1

            await self.db.commit()
            return {"status": "success", "vote_type": vote_type if not is_toggle else None}

        except ValueError as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=409, detail="Vote conflict")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Vote operation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_posts(
        self,
        topic_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at",
    ) -> List[ForumPost]:
        """Get forum posts with pagination."""
        query = select(ForumPost).where(ForumPost.is_deleted.is_(False))

        if topic_id:
            query = query.where(ForumPost.topic_id == topic_id)

        # Sorting
        if sort_by == "created_at":
            query = query.order_by(desc(ForumPost.created_at))
        elif sort_by == "upvotes":
            query = query.order_by(desc(ForumPost.upvotes))
        elif sort_by == "comments":
            query = query.order_by(desc(ForumPost.comment_count))
        else:
            query = query.order_by(desc(ForumPost.created_at))

        # Pinned posts first
        query = query.order_by(desc(ForumPost.is_pinned))

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_comments(
        self, post_id: int, limit: int = 50, offset: int = 0
    ) -> List[ForumComment]:
        """Get comments for a post (threaded)."""
        query = (
            select(ForumComment)
            .where(
                ForumComment.post_id == post_id,
                ForumComment.is_deleted.is_(False),
            )
            .order_by(ForumComment.depth, ForumComment.created_at)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def moderate_post(
        self,
        post_id: int,
        moderator_id: int,
        action: str,
        reason: Optional[str] = None,
    ) -> ForumModerationLog:
        """Perform moderation action on a post."""
        post = await self.db.get(ForumPost, post_id)
        if not post:
            raise ValueError("Post not found")

        # Apply action
        if action == "delete":
            post.is_deleted = True
            post.deleted_at = datetime.now(timezone.utc)
        elif action == "lock":
            post.is_locked = True
        elif action == "unlock":
            post.is_locked = False
        elif action == "pin":
            post.is_pinned = True
        elif action == "unpin":
            post.is_pinned = False
        elif action == "flag":
            post.is_flagged = True

        # Log action
        log = ForumModerationLog(
            moderator_id=moderator_id,
            post_id=post_id,
            action=action,
            reason=reason,
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(log)

        return log

    def _detect_spam(self, title: str, content: str) -> float:
        """
        Simple spam detection.

        Returns spam score 0-1 (higher = more likely spam).
        """
        score = 0.0

        # Check for excessive links
        link_count = len(re.findall(r"http[s]?://", content))
        if link_count > 3:
            score += 0.3

        # Check for excessive caps
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        if caps_ratio > 0.5:
            score += 0.2

        # Check for common spam words
        spam_words = ["free", "click here", "limited time", "act now"]
        content_lower = content.lower()
        for word in spam_words:
            if word in content_lower:
                score += 0.1

        return min(1.0, score)

    @staticmethod
    def _generate_slug(name: str) -> str:
        """Generate URL-friendly slug."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = re.sub(r"^-+|-+$", "", slug)
        return slug[:100]

