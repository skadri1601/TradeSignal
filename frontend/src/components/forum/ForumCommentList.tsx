import { useState, useRef } from 'react';
import { ForumComment } from '../../types';
import ForumCommentItem from './ForumCommentItem';
import { MessageSquare, Loader2 } from 'lucide-react';
import CardSkeleton from '../common/CardSkeleton';

export interface ForumCommentListProps {
  comments: ForumComment[];
  postId: number;
  onCommentSubmit: (content: string, parentId?: number) => Promise<void>;
  isLoading?: boolean;
  sortBy?: 'newest' | 'oldest' | 'top';
}

export default function ForumCommentList({
  comments,
  onCommentSubmit,
  isLoading = false,
  sortBy: initialSortBy = 'newest',
}: ForumCommentListProps) {
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'top'>(initialSortBy);
  const [currentPage, setCurrentPage] = useState(1);
  const [newCommentContent, setNewCommentContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const commentsPerPage = 20;
  const newCommentRef = useRef<HTMLDivElement>(null);

  // Sort comments
  const sortedComments = [...comments].sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    } else if (sortBy === 'oldest') {
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    } else {
      // top voted
      const scoreA = a.upvotes - a.downvotes;
      const scoreB = b.upvotes - b.downvotes;
      return scoreB - scoreA;
    }
  });

  // Filter top-level comments (no parent)
  const topLevelComments = sortedComments.filter((c) => !c.parent_id);

  // Pagination
  const totalPages = Math.ceil(topLevelComments.length / commentsPerPage);
  const paginatedComments = topLevelComments.slice(
    (currentPage - 1) * commentsPerPage,
    currentPage * commentsPerPage
  );

  // Build comment tree
  const buildCommentTree = (parentId: number | null): ForumComment[] => {
    return sortedComments
      .filter((c) => c.parent_id === parentId)
      .map((comment) => ({
        ...comment,
        replies: buildCommentTree(comment.id),
      }));
  };

  const commentTree = paginatedComments.map((comment) => ({
    ...comment,
    replies: buildCommentTree(comment.id),
  }));

  const handleSubmit = async () => {
    if (!newCommentContent.trim()) return;
    setIsSubmitting(true);
    try {
      await onCommentSubmit(newCommentContent);
      setNewCommentContent('');
      // Scroll to new comment after a brief delay
      setTimeout(() => {
        newCommentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 100);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReplySubmit = async (parentId: number, content: string) => {
    await onCommentSubmit(content, parentId);
    setReplyingTo(null);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Comment Form - Sticky at top */}
      <div className="sticky top-4 z-10 bg-gray-900/95 backdrop-blur-sm rounded-2xl border border-white/10 p-6 shadow-lg">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-purple-400" />
          Add a Comment
        </h3>
        <textarea
          value={newCommentContent}
          onChange={(e) => setNewCommentContent(e.target.value)}
          placeholder="Write your comment..."
          className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all mb-3 min-h-[120px]"
          rows={5}
        />
        <div className="flex items-center justify-between">
          <p className="text-xs text-gray-400">
            Supports <strong>**bold**</strong>, <em>*italic*</em>, and <code>`code`</code>
          </p>
          <button
            onClick={handleSubmit}
            disabled={!newCommentContent.trim() || isSubmitting}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Submitting...
              </>
            ) : (
              'Post Comment'
            )}
          </button>
        </div>
      </div>

      {/* Sort Controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold text-white">
          {comments.length} {comments.length === 1 ? 'Comment' : 'Comments'}
        </h4>
        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-400">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value as 'newest' | 'oldest' | 'top');
              setCurrentPage(1);
            }}
            className="px-3 py-1.5 bg-black/50 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="top">Top Voted</option>
          </select>
        </div>
      </div>

      {/* Comments List */}
      {commentTree.length === 0 ? (
        <div className="text-center py-12 bg-gray-900/30 rounded-2xl border border-white/10">
          <MessageSquare className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No comments yet</h3>
          <p className="text-sm text-gray-400">Be the first to comment!</p>
        </div>
      ) : (
        <>
          <div ref={newCommentRef} className="space-y-4">
            {commentTree.map((comment) => (
              <ForumCommentItem
                key={comment.id}
                comment={comment}
                depth={0}
                onReply={(parentId) => setReplyingTo(parentId)}
                onVote={(commentId, voteType) => {
                  // Handle vote - would call API
                  console.log('Vote', commentId, voteType);
                }}
                showReplyForm={replyingTo === comment.id}
                onReplySubmit={handleReplySubmit}
                onReplyCancel={() => setReplyingTo(null)}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Previous
              </button>
              <span className="text-sm text-gray-400">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

