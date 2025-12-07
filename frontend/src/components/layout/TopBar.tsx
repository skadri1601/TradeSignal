/**
 * Top Bar Component - User info and stats
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ChevronDown, User, UserCircle, CreditCard, LogOut, HelpCircle } from 'lucide-react';
import { getSubscription } from '../../api/billing';
import type { SubscriptionResponse } from '../../api/billing';

export default function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);

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

  // Fetch subscription tier
  useEffect(() => {
    const fetchSubscription = async () => {
      if (user) {
        try {
          const sub = await getSubscription();
          setSubscription(sub);
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

    fetchSubscription();
  }, [user]);

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
    if (badge === 'ADMIN') return 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white';
    if (badge === 'ENTERPRISE') return 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white';
    if (badge === 'PRO') return 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white';
    if (badge === 'PLUS') return 'bg-gradient-to-r from-green-500 to-emerald-600 text-white';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-8 py-4">
      <div className="flex items-center justify-between">
        {/* Welcome Message & Quick Stats */}
        <div>
          <p className="text-sm font-medium text-gray-900">
            {getGreeting()}, {user?.username || 'Trader'}!
          </p>
          <p className="text-xs text-gray-500">
            Track insider trades and make informed investment decisions
          </p>
        </div>

        {/* User Profile with Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="flex items-center justify-end space-x-2">
                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getTierBadgeStyle()}`}>
                  {getTierBadge()}
                </span>
                {user?.is_verified && (
                  <span className="text-green-500 text-xs flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                    Verified
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
            </div>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 hover:bg-gray-50 rounded-lg p-2 transition-colors"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.username?.[0]?.toUpperCase() || <User className="w-5 h-5" />}
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
            </button>
          </div>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <button
                onClick={() => {
                  navigate('/profile');
                  setIsDropdownOpen(false);
                }}
                className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <UserCircle className="w-5 h-5 text-gray-400" />
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
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <CreditCard className="w-5 h-5 text-gray-400" />
                    <span>Membership & Billing</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/orders');
                      setIsDropdownOpen(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <CreditCard className="w-5 h-5 text-gray-400" />
                    <span>Order History</span>
                  </button>
                  <button
                    onClick={() => {
                      navigate('/contact');
                      setIsDropdownOpen(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <HelpCircle className="w-5 h-5 text-gray-400" />
                    <span>Contact Support</span>
                  </button>
                </>
              )}

              <div className="border-t border-gray-200 my-1"></div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center space-x-3 px-4 py-3 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-5 h-5" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
