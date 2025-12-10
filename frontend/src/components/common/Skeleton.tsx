interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
}

export default function Skeleton({ 
  width = '100%', 
  height = '1rem', 
  className = '',
  rounded = 'md'
}: SkeletonProps) {
  const widthStyle = typeof width === 'number' ? `${width}px` : width;
  const heightStyle = typeof height === 'number' ? `${height}px` : height;
  
  const roundedClass = {
    none: '',
    sm: 'rounded-sm',
    md: 'rounded',
    lg: 'rounded-lg',
    full: 'rounded-full'
  }[rounded];

  return (
    <div
      className={`bg-gray-200 animate-pulse ${roundedClass} ${className}`}
      style={{ width: widthStyle, height: heightStyle }}
      aria-hidden="true"
    />
  );
}

