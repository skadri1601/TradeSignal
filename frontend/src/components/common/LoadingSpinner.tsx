interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: { ring: 'w-6 h-6', glow: '-inset-1.5' },
  md: { ring: 'w-8 h-8', glow: '-inset-2' },
  lg: { ring: 'w-12 h-12', glow: '-inset-3' },
};

export default function LoadingSpinner({ size = 'md' }: LoadingSpinnerProps) {
  const s = sizeMap[size];

  return (
    <div className="flex items-center justify-center">
      <style>{`
        @keyframes ls-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .ls-ring { animation: ls-spin 1.2s linear infinite; }
      `}</style>
      <div className="relative">
        <div className={`absolute ${s.glow} rounded-full bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-md animate-pulse`} />
        <svg className={`ls-ring ${s.ring} relative`} viewBox="0 0 40 40" fill="none">
          <defs>
            <linearGradient id="ls-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a855f7" />
              <stop offset="50%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
          </defs>
          <circle cx="20" cy="20" r="17" stroke="rgba(255,255,255,0.06)" strokeWidth="2.5" />
          <circle cx="20" cy="20" r="17" stroke="url(#ls-grad)" strokeWidth="2.5" strokeLinecap="round" strokeDasharray="80 27" />
        </svg>
      </div>
    </div>
  );
}
