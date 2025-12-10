interface AISkeletonProps {
  message?: string;
  showThinkingDots?: boolean;
  className?: string;
}

export default function AISkeleton({ 
  message = 'AI is thinking...',
  showThinkingDots = true,
  className = ''
}: AISkeletonProps) {
  return (
    <div className={`flex flex-col items-start space-y-3 ${className}`} aria-label="Loading AI analysis">
      {message && (
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <span>{message}</span>
          {showThinkingDots && (
            <div className="flex space-x-1" aria-hidden="true">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Thinking dots component for inline use
export function ThinkingDots({ className = '' }: { className?: string }) {
  return (
    <div className={`flex space-x-1 ${className}`} aria-hidden="true">
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }} />
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

