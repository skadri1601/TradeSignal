import { ForumPost } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { MessageSquare, Eye, Pin } from 'lucide-react';
import VoteButtons from './VoteButtons';
import ForumCategoryBadge from './ForumCategoryBadge';

export interface ForumPostCardProps {
  post: ForumPost;
  onUpvote: () => void;
  onDownvote: () => void;
  onClick: () => void;
  userVote?: 'up' | 'down' | null;
  disabled?: boolean;
}

export default function ForumPostCard({
  post,
  onUpvote,
  onDownvote,
  onClick,
  userVote = null,
  disabled = false,
}: ForumPostCardProps) {
  const truncatedContent =
    post.content.length > 200 ? post.content.substring(0, 200) + '...' : post.content;

  const voteCount = post.upvotes - post.downvotes;
  const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true });

  return (
    <div
      onClick={onClick}
      className={`
        bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6
        hover:border-purple-500/30 transition-all duration-200 cursor-pointer
        ${post.is_pinned ? 'ring-2 ring-purple-500/20' : ''}
      `}
    >
      <div className="flex flex-col md:flex-row gap-4">
        {/* Vote Section */}
        <div className="flex-shrink-0">
          <div onClick={(e) => e.stopPropagation()}>
            <VoteButtons
              voteCount={voteCount}
              userVote={userVote}
              onUpvote={onUpvote}
              onDownvote={onDownvote}
              size="md"
              disabled={disabled}
            />
          </div>
        </div>

        {/* Content Section */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                {post.is_pinned && (
                  <Pin className="w-4 h-4 text-purple-400 flex-shrink-0" />
                )}
                <h3 className="text-lg font-bold text-white truncate">{post.title}</h3>
              </div>
            </div>
          </div>

          {/* Meta Info */}
          <div className="flex items-center gap-3 text-sm text-gray-400 mb-3 flex-wrap">
            <span>
              by{' '}
              <span className="text-purple-400 font-medium">
                {post.author?.name || `User #${post.author_id}`}
              </span>
            </span>
            <span>•</span>
            <span>{timeAgo}</span>
            {post.topic && (
              <>
                <span>•</span>
                <ForumCategoryBadge category={post.topic.name} size="sm" variant="category" />
              </>
            )}
          </div>

          {/* Tags */}
          {post.tags && post.tags.length > 0 && (
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              {post.tags.map((tag) => (
                <ForumCategoryBadge
                  key={tag}
                  category={tag}
                  size="sm"
                  variant="tag"
                  onClick={() => {
                    // Filter by tag would be handled by parent
                  }}
                />
              ))}
            </div>
          )}

          {/* Content Preview */}
          <p className="text-gray-300 mb-4 line-clamp-3">{truncatedContent}</p>

          {/* Footer Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4" />
              <span>{post.comment_count} comments</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              <span>{post.view_count} views</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

