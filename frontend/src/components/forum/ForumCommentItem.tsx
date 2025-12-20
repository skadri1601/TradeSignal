import { useState } from 'react';
import { ForumComment } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { Reply } from 'lucide-react';
import VoteButtons from './VoteButtons';

export interface ForumCommentItemProps {
  comment: ForumComment;
  depth: number;
  onReply: (parentId: number) => void;
  onVote: (commentId: number, voteType: 'up' | 'down') => void;
  userVote?: 'up' | 'down' | null;
  disabled?: boolean;
  showReplyForm?: boolean;
  onReplySubmit?: (parentId: number, content: string) => void;
  onReplyCancel?: () => void;
}

export default function ForumCommentItem({
  comment,
  depth,
  onReply,
  onVote,
  userVote = null,
  disabled = false,
  showReplyForm = false,
  onReplySubmit,
  onReplyCancel,
}: ForumCommentItemProps) {
  const [replyContent, setReplyContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const maxDepth = 3;

  const borderColors = [
    'border-l-purple-500/30',
    'border-l-blue-500/30',
    'border-l-green-500/30',
    'border-l-yellow-500/30',
  ];

  const borderColor = depth > 0 ? borderColors[Math.min(depth - 1, borderColors.length - 1)] : '';

  const voteCount = comment.upvotes - comment.downvotes;
  const timeAgo = formatDistanceToNow(new Date(comment.created_at), { addSuffix: true });

  const handleReplySubmit = async () => {
    if (!replyContent.trim() || !onReplySubmit) return;
    setIsSubmitting(true);
    try {
      await onReplySubmit(comment.id, replyContent);
      setReplyContent('');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Simple markdown-like rendering (basic support)
  const renderContent = (content: string) => {
    // Basic markdown: **bold**, *italic*, `code`
    let html = content
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code class="bg-black/30 px-1 py-0.5 rounded text-purple-300">$1</code>');
    return { __html: html };
  };

  return (
    <div
      className={`
        ${depth > 0 ? `ml-${Math.min(depth * 4, 12)} border-l-2 ${borderColor} pl-4` : ''}
        ${depth >= maxDepth ? 'opacity-75' : ''}
      `}
    >
      <div className="bg-gray-900/30 rounded-xl p-4 mb-3">
        <div className="flex gap-3">
          {/* Vote Section */}
          <div className="flex-shrink-0">
            <VoteButtons
              voteCount={voteCount}
              userVote={userVote}
              onUpvote={() => onVote(comment.id, 'up')}
              onDownvote={() => onVote(comment.id, 'down')}
              size="sm"
              disabled={disabled}
            />
          </div>

          {/* Content Section */}
          <div className="flex-1 min-w-0">
            {/* Author and Time */}
            <div className="flex items-center gap-2 mb-2 text-sm">
              <span className="text-purple-400 font-medium">
                {comment.author?.name || `User #${comment.author_id}`}
              </span>
              <span className="text-gray-500">•</span>
              <span className="text-gray-400">{timeAgo}</span>
            </div>

            {/* Comment Content */}
            <div
              className="text-gray-300 mb-3 prose prose-invert max-w-none"
              dangerouslySetInnerHTML={renderContent(comment.content)}
            />

            {/* Reply Button */}
            {depth < maxDepth && (
              <button
                onClick={() => onReply(comment.id)}
                disabled={disabled}
                className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300 transition-colors disabled:opacity-50"
                aria-label="Reply to comment"
              >
                <Reply className="w-4 h-4" />
                Reply
              </button>
            )}

            {/* Reply Form */}
            {showReplyForm && depth < maxDepth && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <textarea
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  placeholder="Write your reply..."
                  className="w-full px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all mb-2 min-h-[100px]"
                  rows={4}
                />
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleReplySubmit}
                    disabled={!replyContent.trim() || isSubmitting}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Reply'}
                  </button>
                  {onReplyCancel && (
                    <button
                      onClick={onReplyCancel}
                      className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm font-medium"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Nested Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-2">
          {comment.replies.map((reply) => (
            <ForumCommentItem
              key={reply.id}
              comment={reply}
              depth={depth + 1}
              onReply={onReply}
              onVote={onVote}
              userVote={null} // Would need to fetch user votes for replies
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </div>
  );
}

