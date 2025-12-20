/**
 * ForumPostPage - Single post view with comments
 *
 * Features:
 * - Display full post content
 * - Hierarchical threaded comments (up to 5 levels)
 * - Vote on posts and comments
 * - Reply to comments
 * - Edit/delete own posts and comments
 */

import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { forumApi, type ForumComment } from '../api/forum';
import { useAuth } from '../contexts/AuthContext';
import {
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Eye,
  ArrowLeft,
  Reply,
  Edit,
  Trash2,
  Send,
} from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function ForumPostPage() {
  const { postId } = useParams<{ postId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [replyTo, setReplyTo] = useState<number | null>(null);
  const [replyContent, setReplyContent] = useState('');
  const [commentContent, setCommentContent] = useState('');

  // Fetch post
  const {
    data: post,
    isLoading: postLoading,
    error: postError,
  } = useQuery({
    queryKey: ['forum', 'post', postId],
    queryFn: () => forumApi.getPost(Number(postId)),
    enabled: !!postId,
  });

  // Fetch comments
  const {
    data: comments,
    isLoading: commentsLoading,
  } = useQuery({
    queryKey: ['forum', 'comments', postId],
    queryFn: () => forumApi.getComments(Number(postId)),
    enabled: !!postId,
  });

  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: async ({
      targetType,
      targetId,
      voteType,
    }: {
      targetType: 'post' | 'comment';
      targetId: number;
      voteType: 'upvote' | 'downvote';
    }) => forumApi.vote({ target_type: targetType, target_id: targetId, vote_type: voteType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forum', 'post', postId] });
      queryClient.invalidateQueries({ queryKey: ['forum', 'comments', postId] });
    },
  });

  // Create comment mutation
  const createCommentMutation = useMutation({
    mutationFn: forumApi.createComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forum', 'comments', postId] });
      queryClient.invalidateQueries({ queryKey: ['forum', 'post', postId] });
      setCommentContent('');
      setReplyContent('');
      setReplyTo(null);
    },
  });

  // Delete post mutation
  const deletePostMutation = useMutation({
    mutationFn: forumApi.deletePost,
    onSuccess: () => {
      navigate('/forum');
    },
  });

  // Delete comment mutation
  const deleteCommentMutation = useMutation({
    mutationFn: forumApi.deleteComment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forum', 'comments', postId] });
      queryClient.invalidateQueries({ queryKey: ['forum', 'post', postId] });
    },
  });

  const handleVote = (
    targetType: 'post' | 'comment',
    targetId: number,
    voteType: 'upvote' | 'downvote'
  ) => {
    voteMutation.mutate({ targetType, targetId, voteType });
  };

  const handleCommentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentContent.trim() || !postId) return;

    createCommentMutation.mutate({
      post_id: Number(postId),
      content: commentContent,
    });
  };

  const handleReplySubmit = (parentId: number) => {
    if (!replyContent.trim() || !postId) return;

    createCommentMutation.mutate({
      post_id: Number(postId),
      parent_id: parentId,
      content: replyContent,
    });
  };

  const handleDeletePost = () => {
    if (window.confirm('Are you sure you want to delete this post?')) {
      deletePostMutation.mutate(Number(postId));
    }
  };

  const handleDeleteComment = (commentId: number) => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      deleteCommentMutation.mutate(commentId);
    }
  };

  if (postLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Loading post...</p>
      </div>
    );
  }

  if (postError || !post) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">Failed to load post. It may have been deleted.</p>
          <Link to="/forum" className="btn-primary mt-4 inline-block">
            Back to Forum
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Back Button */}
      <Link
        to="/forum"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Forum
      </Link>

      {/* Post Card */}
      <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm mb-6">
        {/* Post Header */}
        <div className="flex items-start gap-2 mb-4">
          {post.is_pinned && (
            <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded">
              PINNED
            </span>
          )}
          {post.is_locked && (
            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded">
              LOCKED
            </span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">{post.title}</h1>

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Post Content */}
        <div className="prose max-w-none mb-6">
          <p className="text-gray-800 whitespace-pre-wrap">{post.content}</p>
        </div>

        {/* Meta Info */}
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-6 pb-6 border-b border-gray-200">
          <span className="font-medium text-gray-900">{post.author_name}</span>
          <span>•</span>
          <span>{new Date(post.created_at).toLocaleDateString()}</span>
          <span>•</span>
          <div className="flex items-center gap-1">
            <Eye className="w-4 h-4" />
            {post.view_count} views
          </div>
        </div>

        {/* Vote & Actions */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => handleVote('post', post.id, 'upvote')}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                post.user_vote === 'upvote'
                  ? 'bg-green-100 text-green-600'
                  : 'hover:bg-gray-100 text-gray-600'
              }`}
            >
              <ThumbsUp className="w-4 h-4" />
              <span>{post.upvotes}</span>
            </button>
            <button
              onClick={() => handleVote('post', post.id, 'downvote')}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                post.user_vote === 'downvote'
                  ? 'bg-red-100 text-red-600'
                  : 'hover:bg-gray-100 text-gray-600'
              }`}
            >
              <ThumbsDown className="w-4 h-4" />
              <span>{post.downvotes}</span>
            </button>
            <div className="flex items-center gap-2 px-4 py-2 text-gray-600">
              <MessageSquare className="w-4 h-4" />
              <span>{post.comment_count} comments</span>
            </div>
          </div>

          {/* Author Actions */}
          {user?.id === post.author_id && (
            <div className="flex gap-2">
              <Link
                to={`/forum/edit/${post.id}`}
                className="inline-flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
              >
                <Edit className="w-4 h-4" />
                Edit
              </Link>
              <button
                onClick={handleDeletePost}
                className="inline-flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Comments Section */}
      <div className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Comments ({post.comment_count})
        </h2>

        {/* Comment Form */}
        {!post.is_locked && (
          <form onSubmit={handleCommentSubmit} className="mb-8">
            <textarea
              value={commentContent}
              onChange={(e) => setCommentContent(e.target.value)}
              placeholder="Share your thoughts..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={4}
              required
              minLength={1}
              maxLength={2000}
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-gray-500">
                {commentContent.length}/2000 characters
              </span>
              <button
                type="submit"
                disabled={!commentContent.trim() || createCommentMutation.isPending}
                className="btn-primary inline-flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Post Comment
              </button>
            </div>
          </form>
        )}

        {/* Comments List */}
        {commentsLoading && (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        )}

        {comments && comments.length === 0 && (
          <p className="text-center text-gray-500 py-8">
            No comments yet. Be the first to comment!
          </p>
        )}

        {comments && comments.length > 0 && (
          <div className="space-y-6">
            {comments.map((comment) => (
              <CommentThread
                key={comment.id}
                comment={comment}
                postId={Number(postId!)}
                currentUserId={user?.id}
                isLocked={post.is_locked}
                onVote={handleVote}
                onReply={(commentId) => setReplyTo(commentId)}
                onDelete={handleDeleteComment}
                replyTo={replyTo}
                replyContent={replyContent}
                setReplyContent={setReplyContent}
                onReplySubmit={handleReplySubmit}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// COMMENT THREAD COMPONENT
// ============================================================================

interface CommentThreadProps {
  comment: ForumComment;
  postId: number;
  currentUserId?: number;
  isLocked: boolean;
  onVote: (targetType: 'post' | 'comment', targetId: number, voteType: 'upvote' | 'downvote') => void;
  onReply: (commentId: number) => void;
  onDelete: (commentId: number) => void;
  replyTo: number | null;
  replyContent: string;
  setReplyContent: (content: string) => void;
  onReplySubmit: (parentId: number) => void;
}

function CommentThread({
  comment,
  currentUserId,
  isLocked,
  onVote,
  onReply,
  onDelete,
  replyTo,
  replyContent,
  setReplyContent,
  onReplySubmit,
}: CommentThreadProps) {
  const isReplyingToThis = replyTo === comment.id;

  return (
    <div className={`${comment.depth > 0 ? 'ml-8 pl-4 border-l-2 border-gray-200' : ''}`}>
      <div className="flex gap-4">
        {/* Vote Section */}
        <div className="flex flex-col items-center gap-2">
          <button
            onClick={() => onVote('comment', comment.id, 'upvote')}
            className={`p-1 rounded transition-all ${
              comment.user_vote === 'upvote'
                ? 'text-green-600'
                : 'text-gray-400 hover:text-green-600'
            }`}
          >
            <ThumbsUp className="w-4 h-4" />
          </button>
          <span
            className={`text-sm font-semibold ${
              comment.vote_count > 0
                ? 'text-green-600'
                : comment.vote_count < 0
                ? 'text-red-600'
                : 'text-gray-600'
            }`}
          >
            {comment.vote_count}
          </span>
          <button
            onClick={() => onVote('comment', comment.id, 'downvote')}
            className={`p-1 rounded transition-all ${
              comment.user_vote === 'downvote'
                ? 'text-red-600'
                : 'text-gray-400 hover:text-red-600'
            }`}
          >
            <ThumbsDown className="w-4 h-4" />
          </button>
        </div>

        {/* Comment Content */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-gray-900">{comment.author_name}</span>
            <span className="text-sm text-gray-500">
              {new Date(comment.created_at).toLocaleDateString()}
            </span>
            {comment.is_deleted && (
              <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-semibold rounded">
                DELETED
              </span>
            )}
          </div>

          <p className="text-gray-800 mb-3 whitespace-pre-wrap">
            {comment.is_deleted ? '[Comment deleted]' : comment.content}
          </p>

          {/* Comment Actions */}
          {!comment.is_deleted && (
            <div className="flex gap-4 text-sm">
              {!isLocked && comment.depth < 4 && (
                <button
                  onClick={() => onReply(comment.id)}
                  className="text-purple-600 hover:text-purple-700 inline-flex items-center gap-1"
                >
                  <Reply className="w-3 h-3" />
                  Reply
                </button>
              )}
              {currentUserId === comment.author_id && (
                <button
                  onClick={() => onDelete(comment.id)}
                  className="text-red-600 hover:text-red-700 inline-flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" />
                  Delete
                </button>
              )}
            </div>
          )}

          {/* Reply Form */}
          {isReplyingToThis && (
            <div className="mt-4">
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Write your reply..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
                required
                minLength={1}
                maxLength={2000}
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => onReplySubmit(comment.id)}
                  disabled={!replyContent.trim()}
                  className="btn-primary text-sm"
                >
                  Post Reply
                </button>
                <button
                  onClick={() => {
                    onReply(0);
                    setReplyContent('');
                  }}
                  className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Nested Replies */}
          {comment.replies && comment.replies.length > 0 && (
            <div className="mt-6 space-y-6">
              {comment.replies.map((reply) => (
                <CommentThread
                  key={reply.id}
                  comment={reply}
                  postId={0}
                  currentUserId={currentUserId}
                  isLocked={isLocked}
                  onVote={onVote}
                  onReply={onReply}
                  onDelete={onDelete}
                  replyTo={replyTo}
                  replyContent={replyContent}
                  setReplyContent={setReplyContent}
                  onReplySubmit={onReplySubmit}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
