/**
 * Company Logo Component
 * Displays company initials in a colored square
 */

interface CompanyLogoProps {
  ticker: string;
  companyName?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeMap = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
  xl: 'w-16 h-16 text-lg',
};

// Generate a consistent color based on ticker
const getColorForTicker = (ticker: string): string => {
  const colors = [
    'bg-blue-500',
    'bg-indigo-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-red-500',
    'bg-orange-500',
    'bg-yellow-500',
    'bg-green-500',
    'bg-teal-500',
    'bg-cyan-500',
  ];
  
  // Use ticker to consistently pick a color
  const index = ticker.charCodeAt(0) % colors.length;
  return colors[index];
};

export default function CompanyLogo({
  ticker,
  companyName,
  size = 'md',
  className = ''
}: CompanyLogoProps) {
  // Get first 2 letters of ticker for initials
  const initials = ticker?.toUpperCase().slice(0, 2) || 'N/A';
  const bgColor = getColorForTicker(ticker || '');

  return (
    <div 
      className={`${sizeMap[size]} ${bgColor} ${className} rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm`}
      title={companyName || ticker}
    >
      <span className="text-white font-bold">
        {initials}
      </span>
    </div>
  );
}
