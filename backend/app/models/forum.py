"""
Community Forums models.

Topic boards, threaded comments, upvote/downvote, moderation tools.
"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer as SQLInteger

from app.database import Base


class ForumTopic(Base):
    """
    Forum topic/board model.

    Categories for organizing discussions.
    """

    __tablename__ = "forum_topics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    # Moderation
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Statistics
    post_count: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)
    last_post_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ForumTopic(id={self.id}, name={self.name})>"


class ForumPost(Base):
    """
    Forum post model.

    Main posts in topic boards.
    """

    __tablename__ = "forum_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Engagement metrics
    upvotes: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)

    # Moderation
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Spam detection
    spam_score: Mapped[float | None] = mapped_column(SQLInteger, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    last_comment_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_forum_posts_topic_created", "topic_id", "created_at"),
        Index("ix_forum_posts_author_created", "author_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ForumPost(id={self.id}, title={self.title[:50]})>"


class ForumComment(Base):
    """
    Forum comment model.

    Threaded comments on posts.
    """

    __tablename__ = "forum_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Threading
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("forum_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    depth: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)  # Thread depth

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Engagement
    upvotes: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(SQLInteger, default=0, nullable=False)

    # Moderation
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        Index("ix_forum_comments_post_created", "post_id", "created_at"),
        Index("ix_forum_comments_author_created", "author_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ForumComment(id={self.id}, post_id={self.post_id})>"


class ForumVote(Base):
    """
    Forum vote model (upvote/downvote).

    Tracks user votes on posts and comments.
    """

    __tablename__ = "forum_votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Vote target (post or comment)
    post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=True, index=True
    )
    comment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("forum_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Vote type
    vote_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # "upvote" or "downvote"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (
        Index("ix_forum_votes_user_post", "user_id", "post_id", unique=True),
        Index("ix_forum_votes_user_comment", "user_id", "comment_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ForumVote(id={self.id}, vote_type={self.vote_type})>"


class ForumModerationLog(Base):
    """
    Forum moderation log.

    Tracks moderation actions for audit purposes.
    """

    __tablename__ = "forum_moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    moderator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Target
    post_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("forum_posts.id", ondelete="SET NULL"), nullable=True
    )
    comment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("forum_comments.id", ondelete="SET NULL"), nullable=True
    )

    # Action
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<ForumModerationLog(id={self.id}, action={self.action})>"

