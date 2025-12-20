/**
 * ForumPage - Community forum list view
 *
 * Features:
 * - List all forum posts with pagination
 * - Filter by topic, tags, author
 * - Sort by recent, popular, trending
 * - Create new post button
 * - Vote on posts
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { forumApi, type ForumPost } from '../api/forum';
import { MessageSquare, ThumbsUp, ThumbsDown, Eye, Clock, TrendingUp, Plus, Filter } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function ForumPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();

  const [selectedTopic, setSelectedTopic] = useState<number | undefined>(
    searchParams.get('topic') ? Number(searchParams.get('topic')) : undefined
  );
  const [sortBy, setSortBy] = useState<'recent' | 'popular' | 'trending'>(
    (searchParams.get('sort') as any) || 'recent'
  );
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

  // Fetch topics
  const { data: topics } = useQuery({
    queryKey: ['forum', 'topics'],
    queryFn: forumApi.getTopics,
  });

  // Fetch posts
  const {
    data: postsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['forum', 'posts', { topic: selectedTopic, sort: sortBy, page }],
    queryFn: () =>
      forumApi.getPosts({
        topic_id: selectedTopic,
        sort_by: sortBy,
        page,
        per_page: 20,
      }),
  });

  // Vote mutation
  const voteMutation = useMutation({
    mutationFn: async ({ postId, voteType }: { postId: number; voteType: 'upvote' | 'downvote' }) =>
      forumApi.vote({ target_type: 'post', target_id: postId, vote_type: voteType }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forum', 'posts'] });
    },
  });

  const handleTopicChange = (topicId: number | undefined) => {
    setSelectedTopic(topicId);
    setPage(1);
    if (topicId) {
      searchParams.set('topic', String(topicId));
    } else {
      searchParams.delete('topic');
    }
    searchParams.set('page', '1');
    setSearchParams(searchParams);
  };

  const handleSortChange = (newSort: 'recent' | 'popular' | 'trending') => {
    setSortBy(newSort);
    setPage(1);
    searchParams.set('sort', newSort);
    searchParams.set('page', '1');
    setSearchParams(searchParams);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    searchParams.set('page', String(newPage));
    setSearchParams(searchParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleVote = (postId: number, voteType: 'upvote' | 'downvote') => {
    voteMutation.mutate({ postId, voteType });
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">Community Forum</h1>
              <p className="text-gray-400 mt-2">
                Share insights, discuss strategies, and learn from other traders
              </p>
            </div>
            <Link
              to="/forum/create"
              className="btn-primary inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Post
            </Link>
          </div>

          {/* Filters */}
          <div className="bg-white/5 border border-white/10 rounded-lg p-4 shadow-sm">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Topic Filter */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  <Filter className="w-4 h-4 inline mr-1" />
                  Topic
                </label>
                <select
                  value={selectedTopic || ''}
                  onChange={(e) => handleTopicChange(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">All Topics</option>
                  {topics?.map((topic) => (
                    <option key={topic.id} value={topic.id} className="bg-gray-900">
                      {topic.name} ({topic.post_count})
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort By */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-400 mb-2">Sort By</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSortChange('recent')}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                      sortBy === 'recent'
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <Clock className="w-4 h-4 inline mr-1" />
                    Recent
                  </button>
                  <button
                    onClick={() => handleSortChange('popular')}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                      sortBy === 'popular'
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <ThumbsUp className="w-4 h-4 inline mr-1" />
                    Popular
                  </button>
                  <button
                    onClick={() => handleSortChange('trending')}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                      sortBy === 'trending'
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <TrendingUp className="w-4 h-4 inline mr-1" />
                    Trending
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-16">
            <LoadingSpinner />
            <p className="mt-4 text-gray-400">Loading posts...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-6 text-center">
            <p className="text-red-400">Failed to load posts. Please try again later.</p>
          </div>
        )}

        {/* Posts List */}
        {postsData && !isLoading && (
          <>
            {postsData.posts.length === 0 ? (
              <div className="text-center py-16 bg-white/5 border border-white/10 rounded-lg">
                <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No posts yet</h3>
                <p className="text-gray-400 mb-6">Be the first to start a discussion!</p>
                <Link to="/forum/create" className="btn-primary inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors">
                  <Plus className="w-4 h-4" />
                  Create First Post
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {postsData.posts.map((post) => (
                  <ForumPostCard
                    key={post.id}
                    post={post}
                    onVote={handleVote}
                  />
                ))}
              </div>
            )}

            {/* Pagination */}
            {postsData.total_pages > 1 && (
              <div className="mt-8 flex justify-center gap-2">
                <button
                  onClick={() => handlePageChange(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 border border-white/10 rounded-lg text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/5 hover:text-white transition-colors"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-400">
                  Page {page} of {postsData.total_pages}
                </span>
                <button
                  onClick={() => handlePageChange(page + 1)}
                  disabled={page === postsData.total_pages}
                  className="px-4 py-2 border border-white/10 rounded-lg text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/5 hover:text-white transition-colors"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// FORUM POST CARD COMPONENT
// ============================================================================

interface ForumPostCardProps {
  post: ForumPost;
  onVote: (postId: number, voteType: 'upvote' | 'downvote') => void;
}

function ForumPostCard({ post, onVote }: ForumPostCardProps) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-6 shadow-sm hover:bg-white/10 transition-colors">
      <div className="flex gap-4">
        {/* Vote Section */}
        <div className="flex flex-col items-center gap-2">
          <button
            onClick={() => onVote(post.id, 'upvote')}
            className={`p-2 rounded-lg transition-all ${
              post.user_vote === 'upvote'
                ? 'bg-green-500/20 text-green-400'
                : 'hover:bg-white/10 text-gray-500 hover:text-gray-300'
            }`}
            title="Upvote"
          >
            <ThumbsUp className="w-5 h-5" />
          </button>
          <span className={`font-bold ${post.vote_count > 0 ? 'text-green-400' : post.vote_count < 0 ? 'text-red-400' : 'text-gray-400'}`}>
            {post.vote_count}
          </span>
          <button
            onClick={() => onVote(post.id, 'downvote')}
            className={`p-2 rounded-lg transition-all ${
              post.user_vote === 'downvote'
                ? 'bg-red-500/20 text-red-400'
                : 'hover:bg-white/10 text-gray-500 hover:text-gray-300'
            }`}
            title="Downvote"
          >
            <ThumbsDown className="w-5 h-5" />
          </button>
        </div>

        {/* Post Content */}
        <div className="flex-1">
          <Link to={`/forum/post/${post.id}`} className="block group">
            <div className="flex items-start gap-2 mb-2">
              {post.is_pinned && (
                <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs font-semibold rounded">
                  PINNED
                </span>
              )}
              {post.is_locked && (
                <span className="px-2 py-1 bg-yellow-500/20 text-yellow-300 text-xs font-semibold rounded">
                  LOCKED
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold text-white group-hover:text-purple-400 transition-colors mb-2">
              {post.title}
            </h3>
          </Link>

          {/* Tags */}
          {post.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs font-medium rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Post Preview */}
          <p className="text-gray-300 mb-4 line-clamp-2">{post.content}</p>

          {/* Meta Info */}
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="font-medium text-gray-400">{post.author_name}</span>
            <span className="text-gray-600">•</span>
            <span>{new Date(post.created_at).toLocaleDateString()}</span>
            <span className="text-gray-600">•</span>
            <div className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4" />
              {post.comment_count} comments
            </div>
            <span className="text-gray-600">•</span>
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              {post.view_count} views
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}