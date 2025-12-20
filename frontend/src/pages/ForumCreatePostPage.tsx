/**
 * ForumCreatePostPage - Create new forum post
 *
 * Features:
 * - Topic selection
 * - Title and content validation
 * - Tag management (up to 5 tags)
 * - Preview mode
 * - Character count
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { forumApi, type CreatePostRequest } from '../api/forum';
import { ArrowLeft, Send, Eye, X } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function ForumCreatePostPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<CreatePostRequest>({
    topic_id: 0,
    title: '',
    content: '',
    tags: [],
  });
  const [tagInput, setTagInput] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch topics
  const { data: topics, isLoading: topicsLoading } = useQuery({
    queryKey: ['forum', 'topics'],
    queryFn: forumApi.getTopics,
  });

  // Create post mutation
  const createPostMutation = useMutation({
    mutationFn: forumApi.createPost,
    onSuccess: (data) => {
      navigate(`/forum/post/${data.id}`);
    },
    onError: (error: any) => {
      setErrors({
        submit: error.response?.data?.detail || 'Failed to create post. Please try again.',
      });
    },
  });

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.topic_id) {
      newErrors.topic = 'Please select a topic';
    }

    if (formData.title.trim().length < 10) {
      newErrors.title = 'Title must be at least 10 characters';
    } else if (formData.title.trim().length > 200) {
      newErrors.title = 'Title must be less than 200 characters';
    }

    if (formData.content.trim().length < 20) {
      newErrors.content = 'Content must be at least 20 characters';
    } else if (formData.content.trim().length > 10000) {
      newErrors.content = 'Content must be less than 10,000 characters';
    }

    if (formData.tags && formData.tags.length > 5) {
      newErrors.tags = 'Maximum 5 tags allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    createPostMutation.mutate(formData);
  };

  const handleAddTag = () => {
    if (!tagInput.trim()) return;

    const tag = tagInput.trim().toLowerCase().replace(/\s+/g, '-');

    if (formData.tags && formData.tags.includes(tag)) {
      setErrors({ ...errors, tags: 'Tag already added' });
      return;
    }

    if (formData.tags && formData.tags.length >= 5) {
      setErrors({ ...errors, tags: 'Maximum 5 tags allowed' });
      return;
    }

    setFormData({
      ...formData,
      tags: [...(formData.tags || []), tag],
    });
    setTagInput('');
    setErrors({ ...errors, tags: '' });
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags?.filter((tag) => tag !== tagToRemove) || [],
    });
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  if (topicsLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Loading topics...</p>
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

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Post</h1>
        <p className="text-gray-600">
          Share your insights and start a discussion with the community
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-lg p-8 shadow-sm">
        {/* Topic Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Topic <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.topic_id}
            onChange={(e) => setFormData({ ...formData, topic_id: Number(e.target.value) })}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
              errors.topic ? 'border-red-500' : 'border-gray-300'
            }`}
            required
          >
            <option value="">Select a topic...</option>
            {topics?.map((topic) => (
              <option key={topic.id} value={topic.id}>
                {topic.name}
              </option>
            ))}
          </select>
          {errors.topic && <p className="mt-1 text-sm text-red-600">{errors.topic}</p>}
        </div>

        {/* Title */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Enter a descriptive title for your post"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
              errors.title ? 'border-red-500' : 'border-gray-300'
            }`}
            required
            minLength={10}
            maxLength={200}
          />
          <div className="flex justify-between items-center mt-1">
            {errors.title ? (
              <p className="text-sm text-red-600">{errors.title}</p>
            ) : (
              <p className="text-sm text-gray-500">Minimum 10 characters</p>
            )}
            <span className="text-sm text-gray-500">{formData.title.length}/200</span>
          </div>
        </div>

        {/* Tags */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags (Optional)
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={handleTagInputKeyPress}
              placeholder="Add tags (e.g., options, swing-trading)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={formData.tags && formData.tags.length >= 5}
            />
            <button
              type="button"
              onClick={handleAddTag}
              disabled={!tagInput.trim() || (formData.tags && formData.tags.length >= 5)}
              className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add Tag
            </button>
          </div>
          {formData.tags && formData.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full"
                >
                  #{tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-blue-900"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
          {errors.tags ? (
            <p className="text-sm text-red-600">{errors.tags}</p>
          ) : (
            <p className="text-sm text-gray-500">
              {formData.tags ? formData.tags.length : 0}/5 tags used
            </p>
          )}
        </div>

        {/* Content */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Content <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="inline-flex items-center gap-2 px-3 py-1 text-sm text-purple-600 hover:bg-purple-50 rounded-lg transition-all"
            >
              <Eye className="w-4 h-4" />
              {showPreview ? 'Edit' : 'Preview'}
            </button>
          </div>

          {showPreview ? (
            <div className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 min-h-[300px]">
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap text-gray-800">
                  {formData.content || 'Nothing to preview yet...'}
                </p>
              </div>
            </div>
          ) : (
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="Share your thoughts, analysis, or questions with the community..."
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none ${
                errors.content ? 'border-red-500' : 'border-gray-300'
              }`}
              rows={15}
              required
              minLength={20}
              maxLength={10000}
            />
          )}

          <div className="flex justify-between items-center mt-1">
            {errors.content ? (
              <p className="text-sm text-red-600">{errors.content}</p>
            ) : (
              <p className="text-sm text-gray-500">Minimum 20 characters</p>
            )}
            <span className="text-sm text-gray-500">{formData.content.length}/10,000</span>
          </div>
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{errors.submit}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={createPostMutation.isPending}
            className="btn-primary inline-flex items-center gap-2 flex-1"
          >
            {createPostMutation.isPending ? (
              <>
                <LoadingSpinner />
                Creating Post...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Create Post
              </>
            )}
          </button>
          <Link
            to="/forum"
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all"
          >
            Cancel
          </Link>
        </div>

        {/* Guidelines */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Community Guidelines</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Be respectful and constructive in your discussions</li>
            <li>• Stay on topic and provide value to the community</li>
            <li>• No spam, self-promotion, or misleading information</li>
            <li>• Back up claims with data or credible sources when possible</li>
            <li>• Use appropriate tags to help others find your post</li>
          </ul>
        </div>
      </form>
    </div>
  );
}
