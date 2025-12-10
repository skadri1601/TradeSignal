/**
 * Top Bar Component - User info and stats - Dark Mode
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ChevronDown, User, UserCircle, CreditCard, LogOut, MessageSquare, Zap } from 'lucide-react';
import { getSubscription, getUsageStats } from '../../api/billing';
import type { SubscriptionResponse, UsageStats } from '../../api/billing';

export default function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch subscription tier and usage stats
  useEffect(() => {
    const fetchData = async () => {
      if (user) {
        try {
          const [sub, stats] = await Promise.all([
            getSubscription(),
            getUsageStats().catch(() => null)
          ]);
          setSubscription(sub);
          setUsageStats(stats);
        } catch (error) {
          // Default to free tier on error
          setSubscription({
            tier: 'free',
            status: 'inactive',
            is_active: false,
            current_period_start: null,
            current_period_end: null,
            cancel_at_period_end: false
          });
        }
      }
    };

    fetchData();
  }, [user, isDropdownOpen]); // Re-fetch when dropdown opens to keep usage fresh

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Get time-based greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // Get subscription tier display
  const getTierBadge = () => {
    if (user?.is_superuser) return 'ADMIN';
    if (!subscription || !subscription.is_active) return 'FREE';
    const tier = subscription.tier.toUpperCase();
    return tier === 'PLUS' ? 'PLUS' : tier === 'PRO' ? 'PRO' : tier === 'ENTERPRISE' ? 'ENTERPRISE' : 'FREE';
  };

  const getTierBadgeStyle = () => {
    const badge = getTierBadge();
    if (badge === 'ADMIN') return 'bg-purple-500/20 text-purple-300 border border-purple-500/30';
    if (badge === 'ENTERPRISE') return 'bg-blue-500/20 text-blue-300 border border-blue-500/30';
    if (badge === 'PRO') return 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30';
    if (badge === 'PLUS') return 'bg-green-500/20 text-green-300 border border-green-500/30';
    return 'bg-gray-800 text-gray-400 border border-gray-700';
  };

  const getUsagePercentage = () => {
    if (!usageStats) return 0;
    const limit = usageStats.limits.ai_requests_per_day;
    if (limit === -1) return 0; // Unlimited
    return (usageStats.usage.ai_requests / limit) * 100;
  };

  return (
    <header className="bg-black border-b border-white/10 px-8 py-4">
      <div className="flex items-center justify-between">
        {/* Welcome Message & Quick Stats */}
        <div>
          <p className="text-sm font-medium text-white">
            {getGreeting()}, {user?.username || 'Trader'}!
          </p>
          <p className="text-xs text-gray-400">
            Track insider trades and make informed investment decisions
          </p>
        </div>

        {/* User Profile with Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <div className="flex items-center space-x-4">
            <div className="text-right hidden md:block">
              <div className="flex items-center justify-end space-x-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wide ${getTierBadgeStyle()}`}>
                  {getTierBadge()}
                </span>
                {user?.is_verified && (
                  <span className="text-green-400 text-xs flex items-center">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
                    Verified
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
            </div>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 hover:bg-white/5 rounded-lg p-2 transition-colors border border-transparent hover:border-white/10"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-lg shadow-purple-500/20">
                {user?.username?.[0]?.toUpperCase() || <User className="w-5 h-5" />}
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>
          </div>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-[#0f0f1a] rounded-xl shadow-2xl border border-white/10 py-1 z-50 overflow-hidden">
              {/* AI Usage Stats */}
              {usageStats && (
                <div className="px-4 py-3 border-b border-white/5 bg-white/[0.02]">
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center space-x-2">
                      <Zap className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                      <span className="text-xs font-medium text-gray-300">Daily AI Usage</span>
                    </div>
                    <span className="text-xs font-mono text-gray-400">
                      <span className="text-white">{usageStats.usage.ai_requests}</span>
                      <span className="opacity-50">/</span>
                      {usageStats.limits.ai_requests_per_day === -1 ? '∞' : usageStats.limits.ai_requests_per_day}
                    </span>
                  </div>
                  {usageStats.limits.ai_requests_per_day !== -1 && (
                    <div className="w-full bg-gray-800 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full transition-all duration-500 ${
                          getUsagePercentage() > 90 ? 'bg-red-500' : 'bg-gradient-to-r from-purple-500 to-blue-500'
                        }`}
                        style={{ width: `${Math.min(getUsagePercentage(), 100)}%` }}
                      ></div>
                    </div>
                  )}
                  {usageStats.limits.ai_requests_per_day === -1 && (
                    <p className="text-[10px] text-green-400 mt-1">Unlimited Pro Access</p>
                  )}
                </div>
              )}

              <button
                onClick={() => {
                  navigate('/profile');
                  setIsDropdownOpen(false);
                }}
                className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
              >
                <UserCircle className="w-4 h-4 text-gray-500 group-hover:text-white" />
                <span>Edit Profile</span>
              </button>

              {/* Hide Membership & Billing for admins */}
              {!user?.is_superuser && (
                <>
                  <button
                    onClick={() => {
                      navigate('/pricing');
                      setIsDropdownOpen(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
                  >
                    <CreditCard className="w-4 h-4 text-gray-500 group-hover:text-white" />
                    <span>Membership & Billing</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/orders');
                      setIsDropdownOpen(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
                  >
                    <CreditCard className="w-4 h-4 text-gray-500 group-hover:text-white" />
                    <span>Order History</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/support');
                      setIsDropdownOpen(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors"
                  >
                    <MessageSquare className="w-4 h-4 text-gray-500 group-hover:text-white" />
                    <span>Support</span>
                  </button>
                </>
              )}

              <div className="border-t border-white/10 my-1"></div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}