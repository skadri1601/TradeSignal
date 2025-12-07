import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { useAuth, getAccessToken } from '../contexts/AuthContext';

interface UsageData {
  tier: string;
  limits: {
    ai_requests_per_day: number;
  };
  usage: {
    ai_requests: number;
  };
  remaining: {
    ai_requests: number;
  };
  reset_at: string;
}

export default function UsageStats() {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState<{hours: number, minutes: number} | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchUsage = async () => {
      try {
        const token = getAccessToken();
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/billing/usage`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.ok) {
          const jsonData = await response.json();
          setData(jsonData);
        }
      } catch (error) {
        console.error('Failed to fetch usage stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsage();
    
    const interval = setInterval(fetchUsage, 60000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  useEffect(() => {
    if (!data?.reset_at) return;

    const updateTimer = () => {
      const now = new Date();
      const resetDate = new Date(data.reset_at);
      const diffMs = resetDate.getTime() - now.getTime();
      
      if (diffMs > 0) {
        setTimeRemaining({
          hours: Math.floor(diffMs / (1000 * 60 * 60)),
          minutes: Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
        });
      } else {
        setTimeRemaining(null);
      }
    };

    updateTimer();
    const timer = setInterval(updateTimer, 60000);
    return () => clearInterval(timer);
  }, [data?.reset_at]);

  if (loading || !data) return null;

  const { limits, usage } = data;
  const limit = limits.ai_requests_per_day;
  const current = usage.ai_requests;
  
  // -1 means unlimited
  if (limit === -1) return null;

  const percentage = Math.min((current / limit) * 100, 100);
  const isLimitReached = current >= limit;

  return (
    <div className="mt-4 px-4">
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wider">
            Daily AI Quota
          </span>
          <span className="text-xs font-medium text-gray-500">
            {current} / {limit}
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              isLimitReached ? 'bg-red-500' : 
              percentage > 80 ? 'bg-yellow-500' : 'bg-blue-600'
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Status Text */}
        {isLimitReached ? (
          <div className="text-xs text-red-600 flex flex-col gap-1">
            <div className="flex items-center font-medium">
              <AlertCircle className="w-3 h-3 mr-1" />
              Limit Reached
            </div>
            {timeRemaining && (
              <span className="text-gray-500">
                Resets in {timeRemaining.hours}h {timeRemaining.minutes}m
              </span>
            )}
            <Link to="/pricing" className="text-blue-600 hover:underline font-medium mt-1">
              Upgrade for more →
            </Link>
          </div>
        ) : (
          <div className="flex items-center justify-between">
             <span className="text-xs text-gray-500">
               {limit - current} requests left
             </span>
             {percentage > 80 && (
               <Link to="/pricing" className="text-xs text-blue-600 hover:underline font-medium">
                 Upgrade
               </Link>
             )}
          </div>
        )}
      </div>
    </div>
  );
}
