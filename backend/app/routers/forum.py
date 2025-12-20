"""
Forum API Router.
Provides endpoints for forum topics, posts, comments, votes, and moderation.
"""

from typing import List, Optional, Literal
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_manager
from app.core.security import get_current_user
from app.models.user import User
from app.services.forum_service import ForumService
from app.schemas.forum import (
    ForumTopicCreate,
    ForumTopicResponse,
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostResponse,
    PaginatedPostsResponse,
    ForumCommentCreate,
    ForumCommentUpdate,
    ForumCommentResponse,
    ForumVoteRequest,
    ForumModerationAction,
    ForumModerationLogResponse,
)

router = APIRouter(prefix="/api/v1/forum", tags=["forum"])

# Constants
POST_NOT_FOUND = "Post not found"


# ============================================================================
# TOPICS ENDPOINTS
# ============================================================================

@router.get("/topics", response_model=List[ForumTopicResponse])
async def get_topics(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Get all forum topics.

    Public endpoint - no authentication required.
    """
    # Get all topics (ForumService doesn't have a get_all method, so we'll query directly)
    from app.models.forum import ForumTopic
    from sqlalchemy import select

    query = select(ForumTopic).order_by(ForumTopic.name)

    if is_active is not None:
        query = query.where(ForumTopic.is_active == is_active)

    result = await db.execute(query)
    topics = result.scalars().all()

    return topics


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: ForumTopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Create a new forum topic.

    Requires authentication. Only admins should create topics in production.
    """
    forum_service = ForumService(db)

    # Create topic
    topic = await forum_service.create_topic(
        name=topic_data.name,
        description=topic_data.description,
        created_by_id=current_user.id,
    )

    return topic


# ============================================================================
# POSTS ENDPOINTS
# ============================================================================

@router.get("/posts", response_model=PaginatedPostsResponse)
async def get_posts(
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    sort_by: Literal["created_at", "upvotes", "comment_count"] = Query(
        "created_at", description="Sort order"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Get paginated list of forum posts.

    Supports filtering by topic, sorting, and pagination.
    Public endpoint but returns user's vote status if authenticated.
    """
    forum_service = ForumService(db)

    # Get posts
    posts = await forum_service.get_posts(
        topic_id=topic_id,
        sort_by=sort_by,
        limit=per_page,
        offset=(page - 1) * per_page,
    )

    # Count total posts
    from app.models.forum import ForumPost
    from sqlalchemy import select, func

    count_query = select(func.count(ForumPost.id))
    if topic_id:
        count_query = count_query.where(ForumPost.topic_id == topic_id)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Build response with user votes
    post_responses = []
    for post in posts:
        # Get user's vote if authenticated
        user_vote = None
        if current_user:
            from app.models.forum import ForumVote
            vote_result = await db.execute(
                select(ForumVote).where(
                    ForumVote.user_id == current_user.id,
                    ForumVote.post_id == post.id,
                )
            )
            vote = vote_result.scalar_one_or_none()
            if vote:
                user_vote = vote.vote_type

        # Get author name
        from app.models.user import User as UserModel
        author_result = await db.execute(
            select(UserModel).where(UserModel.id == post.author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown"

        post_responses.append(
            ForumPostResponse(
                id=post.id,
                topic_id=post.topic_id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                author_name=author_name,
                tags=post.tags or [],
                upvotes=post.upvotes,
                downvotes=post.downvotes,
                vote_count=post.upvotes - post.downvotes,
                comment_count=post.comment_count,
                view_count=post.view_count,
                is_pinned=post.is_pinned,
                is_locked=post.is_locked,
                is_deleted=post.is_deleted,
                spam_score=post.spam_score,
                user_vote=user_vote,
                created_at=post.created_at,
                updated_at=post.updated_at,
                last_comment_at=post.last_comment_at,
            )
        )

    return PaginatedPostsResponse(
        posts=post_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page,
    )


@router.get("/posts/{post_id}", response_model=ForumPostResponse)
async def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Get a single forum post by ID.

    Public endpoint but returns user's vote status if authenticated.
    """
    from app.models.forum import ForumPost, ForumVote
    from app.models.user import User as UserModel
    from sqlalchemy import select

    # Get post
    result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=POST_NOT_FOUND)

    # Get user's vote if authenticated
    user_vote = None
    if current_user:
        vote_result = await db.execute(
            select(ForumVote).where(
                ForumVote.user_id == current_user.id,
                ForumVote.post_id == post.id,
            )
        )
        vote = vote_result.scalar_one_or_none()
        if vote:
            user_vote = vote.vote_type

    # Get author name
    author_result = await db.execute(
        select(UserModel).where(UserModel.id == post.author_id)
    )
    author = author_result.scalar_one_or_none()
    author_name = author.username if author else "Unknown"

    # Increment view count
    post.view_count += 1
    await db.commit()

    return ForumPostResponse(
        id=post.id,
        topic_id=post.topic_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=author_name,
        tags=post.tags or [],
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        vote_count=post.upvotes - post.downvotes,
        comment_count=post.comment_count,
        view_count=post.view_count,
        is_pinned=post.is_pinned,
        is_locked=post.is_locked,
        is_deleted=post.is_deleted,
        spam_score=post.spam_score,
        user_vote=user_vote,
        created_at=post.created_at,
        updated_at=post.updated_at,
        last_comment_at=post.last_comment_at,
    )


@router.post("/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Create a new forum post.

    Requires authentication.
    """
    forum_service = ForumService(db)

    # Create post
    post = await forum_service.create_post(
        topic_id=post_data.topic_id,
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id,
        tags=post_data.tags,
    )

    # Get author name
    from app.models.user import User as UserModel
    from sqlalchemy import select

    author_result = await db.execute(
        select(UserModel).where(UserModel.id == current_user.id)
    )
    author = author_result.scalar_one()

    return ForumPostResponse(
        id=post.id,
        topic_id=post.topic_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=author.username,
        tags=post.tags or [],
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        vote_count=post.upvotes - post.downvotes,
        comment_count=post.comment_count,
        view_count=post.view_count,
        is_pinned=post.is_pinned,
        is_locked=post.is_locked,
        is_deleted=post.is_deleted,
        spam_score=post.spam_score,
        user_vote=None,
        created_at=post.created_at,
        updated_at=post.updated_at,
        last_comment_at=post.last_comment_at,
    )


@router.put("/posts/{post_id}", response_model=ForumPostResponse)
async def update_post(
    post_id: int,
    post_data: ForumPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Update a forum post.

    Requires authentication. Only post owner can update.
    """
    from app.models.forum import ForumPost
    from app.models.user import User as UserModel
    from sqlalchemy import select
    from datetime import datetime

    # Get post
    result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=POST_NOT_FOUND)

    # Check ownership
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    # Update fields
    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.tags is not None:
        post.tags = post_data.tags

    post.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(post)

    # Get author name
    author_result = await db.execute(
        select(UserModel).where(UserModel.id == current_user.id)
    )
    author = author_result.scalar_one()

    return ForumPostResponse(
        id=post.id,
        topic_id=post.topic_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=author.username,
        tags=post.tags or [],
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        vote_count=post.upvotes - post.downvotes,
        comment_count=post.comment_count,
        view_count=post.view_count,
        is_pinned=post.is_pinned,
        is_locked=post.is_locked,
        is_deleted=post.is_deleted,
        spam_score=post.spam_score,
        user_vote=None,
        created_at=post.created_at,
        updated_at=post.updated_at,
        last_comment_at=post.last_comment_at,
    )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Delete a forum post.

    Requires authentication. Only post owner or moderator can delete.
    """
    from app.models.forum import ForumPost
    from sqlalchemy import select

    # Get post
    result = await db.execute(select(ForumPost).where(ForumPost.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail=POST_NOT_FOUND)

    # Check ownership or moderator status
    is_moderator = current_user.is_superuser or current_user.role in ["super_admin", "support"]

    if post.author_id != current_user.id and not is_moderator:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    # Soft delete
    post.is_deleted = True
    post.deleted_at = datetime.now(timezone.utc)

    await db.commit()


# ============================================================================
# COMMENTS ENDPOINTS
# ============================================================================

@router.get("/posts/{post_id}/comments", response_model=List[ForumCommentResponse])
async def get_comments(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Get all comments for a post.

    Returns comments in hierarchical order with nested replies.
    Public endpoint but returns user's vote status if authenticated.
    """
    forum_service = ForumService(db)

    # Get comments
    comments = await forum_service.get_comments(post_id=post_id)

    # Build comment tree
    comment_map = {}
    root_comments = []

    from app.models.forum import ForumVote
    from app.models.user import User as UserModel
    from sqlalchemy import select

    for comment in comments:
        # Get user's vote if authenticated
        user_vote = None
        if current_user:
            vote_result = await db.execute(
                select(ForumVote).where(
                    ForumVote.user_id == current_user.id,
                    ForumVote.comment_id == comment.id,
                )
            )
            vote = vote_result.scalar_one_or_none()
            if vote:
                user_vote = vote.vote_type

        # Get author name
        author_result = await db.execute(
            select(UserModel).where(UserModel.id == comment.author_id)
        )
        author = author_result.scalar_one_or_none()
        author_name = author.username if author else "Unknown"

        comment_response = ForumCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            content=comment.content,
            author_id=comment.author_id,
            author_name=author_name,
            upvotes=comment.upvotes,
            downvotes=comment.downvotes,
            vote_count=comment.upvotes - comment.downvotes,
            depth=comment.depth,
            is_deleted=comment.is_deleted,
            user_vote=user_vote,
            reply_count=0,  # Will be calculated
            replies=[],
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )

        comment_map[comment.id] = comment_response

        if comment.parent_id is None:
            root_comments.append(comment_response)
        else:
            if comment.parent_id in comment_map:
                comment_map[comment.parent_id].replies.append(comment_response)
                comment_map[comment.parent_id].reply_count += 1

    return root_comments


@router.post("/comments", response_model=ForumCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: ForumCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Create a new comment on a post.

    Requires authentication.
    """
    forum_service = ForumService(db)

    # Create comment
    comment = await forum_service.create_comment(
        post_id=comment_data.post_id,
        author_id=current_user.id,
        content=comment_data.content,
        parent_id=comment_data.parent_id,
    )

    # Get author name
    from app.models.user import User as UserModel
    from sqlalchemy import select

    author_result = await db.execute(
        select(UserModel).where(UserModel.id == current_user.id)
    )
    author = author_result.scalar_one()

    return ForumCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        content=comment.content,
        author_id=comment.author_id,
        author_name=author.username,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        vote_count=comment.upvotes - comment.downvotes,
        depth=comment.depth,
        is_deleted=comment.is_deleted,
        user_vote=None,
        reply_count=0,
        replies=[],
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Delete a comment.

    Requires authentication. Only comment owner or moderator can delete.
    """
    from app.models.forum import ForumComment
    from sqlalchemy import select

    # Get comment
    result = await db.execute(select(ForumComment).where(ForumComment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check ownership or moderator status
    is_moderator = current_user.is_superuser or current_user.role in ["super_admin", "support"]

    if comment.author_id != current_user.id and not is_moderator:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    # Soft delete
    comment.is_deleted = True
    comment.deleted_at = datetime.now(timezone.utc)

    await db.commit()


# ============================================================================
# VOTES ENDPOINTS
# ============================================================================

@router.post("/votes", status_code=status.HTTP_201_CREATED)
async def create_vote(
    vote_data: ForumVoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Cast a vote on a post or comment.

    Requires authentication.
    Supports upvote/downvote toggle logic.
    """
    forum_service = ForumService(db)

    # Create or update vote
    await forum_service.vote(
        user_id=current_user.id,
        target_type=vote_data.target_type,
        target_id=vote_data.target_id,
        vote_type=vote_data.vote_type,
    )

    return {"message": "Vote recorded successfully"}


# ============================================================================
# MODERATION ENDPOINTS
# ============================================================================

@router.post("/posts/{post_id}/moderate", status_code=status.HTTP_200_OK)
async def moderate_post(
    post_id: int,
    moderation_data: ForumModerationAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Perform moderation action on a post.

    Requires authentication and moderator role.
    """
    # Check moderator status
    is_moderator = current_user.is_superuser or current_user.role in ["super_admin", "support"]

    if not is_moderator:
        raise HTTPException(status_code=403, detail="Not authorized to moderate posts")

    forum_service = ForumService(db)

    # Moderate post
    await forum_service.moderate_post(
        post_id=post_id,
        moderator_id=current_user.id,
        action=moderation_data.action,
        reason=moderation_data.reason,
    )

    return {"message": f"Post moderated: {moderation_data.action}"}


@router.get("/moderation/logs", response_model=List[ForumModerationLogResponse])
async def get_moderation_logs(
    limit: int = Query(50, ge=1, le=100, description="Number of logs to retrieve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(db_manager.get_session),
):
    """
    Get moderation logs.

    Requires authentication and moderator role.
    """
    # Check moderator status
    is_moderator = current_user.is_superuser or current_user.role in ["super_admin", "support"]

    if not is_moderator:
        raise HTTPException(status_code=403, detail="Not authorized to view moderation logs")

    from app.models.forum import ForumModerationLog
    from app.models.user import User as UserModel
    from sqlalchemy import select

    # Get logs
    result = await db.execute(
        select(ForumModerationLog)
        .order_by(ForumModerationLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    # Build response with moderator names
    log_responses = []
    for log in logs:
        moderator_result = await db.execute(
            select(UserModel).where(UserModel.id == log.moderator_id)
        )
        moderator = moderator_result.scalar_one_or_none()
        moderator_name = moderator.username if moderator else "Unknown"

        log_responses.append(
            ForumModerationLogResponse(
                id=log.id,
                moderator_id=log.moderator_id,
                moderator_name=moderator_name,
                target_type=log.target_type,
                target_id=log.target_id,
                action=log.action,
                reason=log.reason,
                created_at=log.created_at,
            )
        )

    return log_responses
