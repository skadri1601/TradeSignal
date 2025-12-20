import { Hash } from 'lucide-react';

export interface ForumCategoryBadgeProps {
  category: string;
  size?: 'sm' | 'md';
  variant?: 'category' | 'tag';
  onClick?: () => void;
}

// Hash function to generate consistent colors for categories
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

function getCategoryColor(category: string): string {
  const hash = hashString(category);
  const colors = [
    'bg-purple-500/20 text-purple-300 border-purple-500/30',
    'bg-blue-500/20 text-blue-300 border-blue-500/30',
    'bg-green-500/20 text-green-300 border-green-500/30',
    'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    'bg-pink-500/20 text-pink-300 border-pink-500/30',
    'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
    'bg-orange-500/20 text-orange-300 border-orange-500/30',
    'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  ];
  return colors[hash % colors.length];
}

export default function ForumCategoryBadge({
  category,
  size = 'md',
  variant = 'category',
  onClick,
}: ForumCategoryBadgeProps) {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  const variantClasses = {
    category: 'font-semibold',
    tag: 'font-normal',
  };

  const colorClass = getCategoryColor(category);

  return (
    <button
      onClick={onClick}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${colorClass}
        inline-flex items-center gap-1
        rounded-full border
        transition-all duration-200
        ${onClick ? 'hover:scale-105 cursor-pointer' : 'cursor-default'}
      `}
      aria-label={`Filter by ${category}`}
    >
      {variant === 'category' && <Hash className="w-3 h-3" />}
      {category}
    </button>
  );
}

