/**
 * Forum API Client
 *
 * Provides TypeScript methods to interact with the Forum API endpoints.
 */

import apiClient from './client';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface ForumTopic {
  id: number;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  post_count: number;
  last_post_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ForumPost {
  id: number;
  topic_id: number;
  title: string;
  content: string;
  author_id: number;
  author_name: string;
  tags: string[];
  upvotes: number;
  downvotes: number;
  vote_count: number;
  comment_count: number;
  view_count: number;
  is_pinned: boolean;
  is_locked: boolean;
  is_deleted: boolean;
  spam_score: number;
  user_vote?: 'upvote' | 'downvote';
  created_at: string;
  updated_at?: string;
  last_comment_at?: string;
}

export interface ForumComment {
  id: number;
  post_id: number;
  parent_id?: number;
  content: string;
  author_id: number;
  author_name: string;
  upvotes: number;
  downvotes: number;
  vote_count: number;
  depth: number;
  is_deleted: boolean;
  user_vote?: 'upvote' | 'downvote';
  reply_count: number;
  replies: ForumComment[];
  created_at: string;
  updated_at?: string;
}

export interface PaginatedPostsResponse {
  posts: ForumPost[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ForumModerationLog {
  id: number;
  moderator_id: number;
  moderator_name: string;
  target_type: string;
  target_id: number;
  action: string;
  reason?: string;
  created_at: string;
}

export interface CreateTopicRequest {
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface CreatePostRequest {
  topic_id: number;
  title: string;
  content: string;
  tags?: string[];
}

export interface UpdatePostRequest {
  title?: string;
  content?: string;
  tags?: string[];
}

export interface CreateCommentRequest {
  post_id: number;
  parent_id?: number;
  content: string;
}

export interface VoteRequest {
  target_type: 'post' | 'comment';
  target_id: number;
  vote_type: 'upvote' | 'downvote';
}

export interface ModerateRequest {
  action: 'delete' | 'lock' | 'unlock' | 'pin' | 'unpin' | 'flag';
  reason?: string;
}

export interface GetPostsParams {
  topic_id?: number;
  author_id?: number;
  tags?: string[];
  sort_by?: 'recent' | 'popular' | 'trending';
  page?: number;
  per_page?: number;
}

// ============================================================================
// API CLIENT
// ============================================================================

/**
 * Forum API - Provides methods to interact with forum endpoints
 */
export const forumApi = {
  // =========================================================================
  // TOPICS
  // =========================================================================

  /**
   * Get all forum topics
   */
  getTopics: async (): Promise<ForumTopic[]> => {
    const response = await apiClient.get<ForumTopic[]>('/api/v1/forum/topics');
    return response.data;
  },

  /**
   * Create a new forum topic (admin only)
   */
  createTopic: async (data: CreateTopicRequest): Promise<ForumTopic> => {
    const response = await apiClient.post<ForumTopic>('/api/v1/forum/topics', data);
    return response.data;
  },

  // =========================================================================
  // POSTS
  // =========================================================================

  /**
   * Get paginated posts with filtering and sorting
   */
  getPosts: async (params?: GetPostsParams): Promise<PaginatedPostsResponse> => {
    const response = await apiClient.get<PaginatedPostsResponse>('/api/v1/forum/posts', {
      params: {
        topic_id: params?.topic_id,
        author_id: params?.author_id,
        tags: params?.tags?.join(','),
        sort_by: params?.sort_by || 'recent',
        page: params?.page || 1,
        per_page: params?.per_page || 20,
      },
    });
    return response.data;
  },

  /**
   * Get a single post by ID
   */
  getPost: async (postId: number): Promise<ForumPost> => {
    const response = await apiClient.get<ForumPost>(`/api/v1/forum/posts/${postId}`);
    return response.data;
  },

  /**
   * Create a new forum post
   */
  createPost: async (data: CreatePostRequest): Promise<ForumPost> => {
    const response = await apiClient.post<ForumPost>('/api/v1/forum/posts', data);
    return response.data;
  },

  /**
   * Update an existing post (author only)
   */
  updatePost: async (postId: number, data: UpdatePostRequest): Promise<ForumPost> => {
    const response = await apiClient.put<ForumPost>(`/api/v1/forum/posts/${postId}`, data);
    return response.data;
  },

  /**
   * Delete a post (soft delete - author or moderator only)
   */
  deletePost: async (postId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/forum/posts/${postId}`);
  },

  // =========================================================================
  // COMMENTS
  // =========================================================================

  /**
   * Get all comments for a post (hierarchical structure)
   */
  getComments: async (postId: number): Promise<ForumComment[]> => {
    const response = await apiClient.get<ForumComment[]>(`/api/v1/forum/posts/${postId}/comments`);
    return response.data;
  },

  /**
   * Create a new comment or reply
   */
  createComment: async (data: CreateCommentRequest): Promise<ForumComment> => {
    const response = await apiClient.post<ForumComment>('/api/v1/forum/comments', data);
    return response.data;
  },

  /**
   * Delete a comment (soft delete - author or moderator only)
   */
  deleteComment: async (commentId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/forum/comments/${commentId}`);
  },

  // =========================================================================
  // VOTING
  // =========================================================================

  /**
   * Vote on a post or comment (upvote/downvote)
   * Toggling: clicking same vote type removes vote
   */
  vote: async (data: VoteRequest): Promise<void> => {
    await apiClient.post('/api/v1/forum/votes', data);
  },

  // =========================================================================
  // MODERATION
  // =========================================================================

  /**
   * Moderate a post (moderator only)
   * Actions: delete, lock, unlock, pin, unpin, flag
   */
  moderatePost: async (postId: number, data: ModerateRequest): Promise<void> => {
    await apiClient.post(`/api/v1/forum/posts/${postId}/moderate`, data);
  },

  /**
   * Get moderation logs (moderator only)
   */
  getModerationLogs: async (
    limit?: number,
    offset?: number
  ): Promise<ForumModerationLog[]> => {
    const response = await apiClient.get<ForumModerationLog[]>(
      '/api/v1/forum/moderation/logs',
      {
        params: { limit, offset },
      }
    );
    return response.data;
  },
};

export default forumApi;
