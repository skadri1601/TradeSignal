import Skeleton from './Skeleton';

interface CardSkeletonProps {
  headerLines?: number;
  contentLines?: number;
  showFooter?: boolean;
  className?: string;
}

export default function CardSkeleton({ 
  headerLines = 1,
  contentLines = 3,
  showFooter = false,
  className = ''
}: CardSkeletonProps) {
  return (
    <div className={`card ${className}`} aria-label="Loading content">
      {/* Header */}
      <div className="space-y-2 mb-4">
        {Array.from({ length: headerLines }).map((_, i) => (
          <Skeleton 
            key={i}
            width={i === 0 ? '60%' : '40%'}
            height="1.25rem"
            className="mb-1"
          />
        ))}
      </div>

      {/* Content */}
      <div className="space-y-2 mb-4">
        {Array.from({ length: contentLines }).map((_, i) => (
          <Skeleton 
            key={i}
            width={i === contentLines - 1 ? '80%' : '100%'}
            height="1rem"
          />
        ))}
      </div>

      {/* Footer */}
      {showFooter && (
        <div className="pt-4 border-t border-gray-200">
          <Skeleton width="40%" height="0.875rem" />
        </div>
      )}
    </div>
  );
}

