"""
Pydantic schemas for Forum API.
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ForumTopicCreate(BaseModel):
    """Schema for creating a new forum topic."""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ForumPostCreate(BaseModel):
    """Schema for creating a new forum post."""
    topic_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=10, max_length=200)
    content: str = Field(..., min_length=20, max_length=10000)
    tags: List[str] = Field(default_factory=list, max_items=5)


class ForumPostUpdate(BaseModel):
    """Schema for updating a forum post."""
    title: Optional[str] = Field(None, min_length=10, max_length=200)
    content: Optional[str] = Field(None, min_length=20, max_length=10000)
    tags: Optional[List[str]] = Field(None, max_items=5)


class ForumCommentCreate(BaseModel):
    """Schema for creating a new comment."""
    post_id: int = Field(..., gt=0)
    parent_id: Optional[int] = Field(None, gt=0)
    content: str = Field(..., min_length=1, max_length=2000)


class ForumCommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: str = Field(..., min_length=1, max_length=2000)


class ForumVoteRequest(BaseModel):
    """Schema for voting on a post or comment."""
    target_type: Literal["post", "comment"]
    target_id: int = Field(..., gt=0)
    vote_type: Literal["upvote", "downvote"]


class ForumModerationAction(BaseModel):
    """Schema for moderating a post or comment."""
    action: Literal["delete", "lock", "unlock", "pin", "unpin", "flag"]
    reason: Optional[str] = Field(None, max_length=500)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ForumTopicResponse(BaseModel):
    """Schema for forum topic response."""
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    post_count: int
    last_post_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ForumPostResponse(BaseModel):
    """Schema for forum post response."""
    id: int
    topic_id: int
    title: str
    content: str
    author_id: int
    author_name: str
    tags: List[str]
    upvotes: int
    downvotes: int
    vote_count: int  # upvotes - downvotes
    comment_count: int
    view_count: int
    is_pinned: bool
    is_locked: bool
    is_deleted: bool
    spam_score: float
    user_vote: Optional[Literal["upvote", "downvote"]]  # Current user's vote
    created_at: datetime
    updated_at: Optional[datetime]
    last_comment_at: Optional[datetime]

    class Config:
        from_attributes = True


class ForumCommentResponse(BaseModel):
    """Schema for forum comment response."""
    id: int
    post_id: int
    parent_id: Optional[int]
    content: str
    author_id: int
    author_name: str
    upvotes: int
    downvotes: int
    vote_count: int  # upvotes - downvotes
    depth: int
    is_deleted: bool
    user_vote: Optional[Literal["upvote", "downvote"]]
    reply_count: int
    replies: List['ForumCommentResponse'] = []  # Nested comments
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Enable forward references for nested comments
ForumCommentResponse.model_rebuild()


class PaginatedPostsResponse(BaseModel):
    """Schema for paginated posts response."""
    posts: List[ForumPostResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ForumModerationLogResponse(BaseModel):
    """Schema for moderation log response."""
    id: int
    moderator_id: int
    moderator_name: str
    target_type: str
    target_id: int
    action: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
