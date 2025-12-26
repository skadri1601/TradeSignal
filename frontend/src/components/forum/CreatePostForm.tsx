import { useState } from 'react';
import { Bold, Italic, Link, Code, Eye, Edit2, X } from 'lucide-react';

export interface CreatePostFormProps {
  readonly onSubmit: (data: {
    title: string;
    content: string;
    category: string;
    tags: string[];
  }) => Promise<void>;
  readonly onCancel: () => void;
  readonly categories: string[];
  readonly initialData?: {
    title?: string;
    content?: string;
    category?: string;
    tags?: string[];
  };
}

export default function CreatePostForm({
  onSubmit,
  onCancel,
  categories,
  initialData,
}: CreatePostFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [content, setContent] = useState(initialData?.content || '');
  const [selectedCategory, setSelectedCategory] = useState(initialData?.category || categories[0] || '');
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [previewMode, setPreviewMode] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const maxTitleLength = 200;
  const maxTags = 5;

  const handleAddTag = () => {
    const trimmed = tagInput.trim();
    if (trimmed && tags.length < maxTags && !tags.includes(trimmed)) {
      setTags([...tags, trimmed]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const insertMarkdown = (before: string, after: string = '') => {
    const textarea = document.getElementById('post-content') as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);
    const newText = content.substring(0, start) + before + selectedText + after + content.substring(end);
    setContent(newText);

    // Restore cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + before.length, start + before.length + selectedText.length);
    }, 0);
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > maxTitleLength) {
      newErrors.title = `Title must be ${maxTitleLength} characters or less`;
    }

    if (!content.trim()) {
      newErrors.content = 'Content is required';
    }

    if (!selectedCategory) {
      newErrors.category = 'Category is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        title: title.trim(),
        content: content.trim(),
        category: selectedCategory,
        tags,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Simple markdown preview
  // Input length limit to prevent ReDoS attacks
  const MAX_PREVIEW_LENGTH = 50000;
  const renderPreview = (text: string) => {
    // Truncate input to prevent ReDoS attacks
    const safeText = text.length > MAX_PREVIEW_LENGTH ? text.substring(0, MAX_PREVIEW_LENGTH) : text;

    // Use negated character classes to prevent catastrophic backtracking
    // These patterns cannot backtrack because [^X]+ matches a specific character class
    const html = safeText
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-black/30 px-1 py-0.5 rounded text-purple-300">$1</code>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-purple-400 hover:underline">$1</a>')
      .replaceAll('\n', '<br />');
    return { __html: html };
  };

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Create New Post</h2>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-white transition-colors"
          aria-label="Cancel"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title Input */}
        <div>
          <label htmlFor="post-title" className="block text-sm font-medium text-gray-300 mb-2">
            Title <span className="text-red-400">*</span>
          </label>
          <input
            id="post-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={maxTitleLength}
            className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="Enter post title..."
          />
          <div className="flex items-center justify-between mt-1">
            {errors.title && <p className="text-sm text-red-400">{errors.title}</p>}
            <p className="text-xs text-gray-400 ml-auto">
              {title.length}/{maxTitleLength}
            </p>
          </div>
        </div>

        {/* Category Dropdown */}
        <div>
          <label htmlFor="post-category" className="block text-sm font-medium text-gray-300 mb-2">
            Category <span className="text-red-400">*</span>
          </label>
          <select
            id="post-category"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          {errors.category && <p className="text-sm text-red-400 mt-1">{errors.category}</p>}
        </div>

        {/* Tags Input */}
        <div>
          <label htmlFor="post-tags" className="block text-sm font-medium text-gray-300 mb-2">
            Tags ({tags.length}/{maxTags})
          </label>
          <div className="flex items-center gap-2 mb-2">
            <input
              id="post-tags"
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagInputKeyDown}
              placeholder="Add tags (comma-separated, max 5)"
              className="flex-1 px-4 py-2 bg-black/50 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              disabled={tags.length >= maxTags}
            />
            <button
              type="button"
              onClick={handleAddTag}
              disabled={tags.length >= maxTags || !tagInput.trim()}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Add
            </button>
          </div>
          {tags.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-red-400 transition-colors"
                    aria-label={`Remove tag ${tag}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Content Editor/Preview - Two Column on Desktop */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label htmlFor="post-content" className="block text-sm font-medium text-gray-300">
              Content <span className="text-red-400">*</span>
            </label>
            <button
              type="button"
              onClick={() => setPreviewMode(!previewMode)}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
            >
              {previewMode ? (
                <>
                  <Edit2 className="w-4 h-4" />
                  Edit
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4" />
                  Preview
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Editor */}
            <div className={previewMode ? 'hidden lg:block' : ''}>
              <div className="flex items-center gap-1 p-2 bg-black/30 rounded-t-lg border-b border-white/10">
                <button
                  type="button"
                  onClick={() => insertMarkdown('**', '**')}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Bold"
                  aria-label="Bold"
                >
                  <Bold className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => insertMarkdown('*', '*')}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Italic"
                  aria-label="Italic"
                >
                  <Italic className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => insertMarkdown('[', '](url)')}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Link"
                  aria-label="Link"
                >
                  <Link className="w-4 h-4 text-gray-400" />
                </button>
                <button
                  type="button"
                  onClick={() => insertMarkdown('`', '`')}
                  className="p-1.5 hover:bg-white/10 rounded transition-colors"
                  title="Code"
                  aria-label="Code"
                >
                  <Code className="w-4 h-4 text-gray-400" />
                </button>
              </div>
              <textarea
                id="post-content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full px-4 py-3 bg-black/50 border border-white/10 rounded-b-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all min-h-[300px] font-mono text-sm"
                placeholder="Write your post content... (Supports markdown: **bold**, *italic*, `code`, [links](url))"
                rows={15}
              />
              {errors.content && <p className="text-sm text-red-400 mt-1">{errors.content}</p>}
            </div>

            {/* Preview */}
            <div className={previewMode ? 'lg:col-span-2' : 'hidden lg:block'}>
              <div className="p-4 bg-black/30 rounded-lg border border-white/10 min-h-[300px]">
                <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase">Preview</h3>
                {content ? (
                  <div
                    className="prose prose-invert max-w-none text-gray-300"
                    dangerouslySetInnerHTML={renderPreview(content)}
                  />
                ) : (
                  <p className="text-gray-500 italic">Preview will appear here...</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isSubmitting ? 'Submitting...' : 'Create Post'}
          </button>
        </div>
      </form>
    </div>
  );
}

