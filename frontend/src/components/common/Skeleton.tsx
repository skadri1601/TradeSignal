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
    md: 'rounded-2xl',
    lg: 'rounded-2xl',
    full: 'rounded-full'
  }[rounded];

  return (
    <>
      <style>{`
        @keyframes sk-shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
        .sk-shimmer::after {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, transparent 0%, rgba(139,92,246,0.06) 30%, rgba(59,130,246,0.08) 50%, rgba(139,92,246,0.06) 70%, transparent 100%);
          animation: sk-shimmer 2s ease-in-out infinite;
        }
      `}</style>
      <div
        className={`sk-shimmer relative overflow-hidden border border-white/5 bg-white/[0.04] backdrop-blur-sm ${roundedClass} ${className}`}
        style={{ width: widthStyle, height: heightStyle }}
        aria-hidden="true"
      />
    </>
  );
}
