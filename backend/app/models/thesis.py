"""
Thesis Publishing Platform models.

Rich text editor, image embedding, tag system, quality curation, reputation scoring.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Thesis(Base):
    """
    Thesis/Research publication model.

    User-generated investment research and analysis.
    """

    __tablename__ = "theses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Rich text/HTML
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    ticker: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Engagement metrics
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    share_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Quality metrics
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # 0-100
    reputation_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # Author reputation

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )  # draft, published, archived
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_curated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Moderation
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moderation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tags: Mapped[list["ThesisTag"]] = relationship(
        "ThesisTag", secondary="thesis_tag_associations", back_populates="theses"
    )
    images: Mapped[list["ThesisImage"]] = relationship(
        "ThesisImage", back_populates="thesis", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Thesis(id={self.id}, title={self.title[:50]}, author_id={self.author_id})>"


class ThesisTag(Base):
    """
    Thesis tag model.

    Categorization and discovery tags.
    """

    __tablename__ = "thesis_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Usage stats
    thesis_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    theses: Mapped[list["Thesis"]] = relationship(
        "Thesis", secondary="thesis_tag_associations", back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<ThesisTag(id={self.id}, name={self.name})>"


class ThesisTagAssociation(Base):
    """Association table for thesis-tag many-to-many relationship."""

    __tablename__ = "thesis_tag_associations"

    thesis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theses.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("thesis_tags.id", ondelete="CASCADE"), primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class ThesisImage(Base):
    """
    Thesis image model.

    Embedded images in thesis content.
    """

    __tablename__ = "thesis_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    thesis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Image details
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ordering
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    thesis: Mapped["Thesis"] = relationship("Thesis", back_populates="images")

    def __repr__(self) -> str:
        return f"<ThesisImage(id={self.id}, thesis_id={self.thesis_id})>"


class ThesisVote(Base):
    """
    Thesis vote model (upvote/downvote).
    """

    __tablename__ = "thesis_votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    thesis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    vote_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "upvote" or "downvote"

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_thesis_votes_thesis_user", "thesis_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ThesisVote(id={self.id}, thesis_id={self.thesis_id}, vote_type={self.vote_type})>"


class ThesisComment(Base):
    """
    Thesis comment model.

    Comments on published theses.
    """

    __tablename__ = "thesis_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    thesis_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("theses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Threading
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("thesis_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Engagement
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Moderation
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_thesis_comments_thesis_created", "thesis_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ThesisComment(id={self.id}, thesis_id={self.thesis_id})>"


class UserReputation(Base):
    """
    User reputation score model.

    Tracks author reputation based on thesis quality and engagement.
    """

    __tablename__ = "user_reputations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Reputation metrics
    reputation_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0.0, nullable=False)  # 0-100

    # Breakdown
    thesis_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Timestamps
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserReputation(user_id={self.user_id}, score={self.reputation_score})>"

