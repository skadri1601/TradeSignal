import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, CreditCard, Activity, Search,
  ExternalLink, X, Mail
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { adminApi } from '../api/admin';
import { useQuery } from '@tanstack/react-query';

// --- Components ---

// User Detail Modal (User 360)
function UserDetailModal({ userId, onClose }: { userId: number; onClose: () => void }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-user-billing', userId],
    queryFn: () => adminApi.getUserBilling(userId),
  });

  if (!userId) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900/90 backdrop-blur-md rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl border border-white/10">
        <div className="p-6 border-b border-gray-700 flex justify-between items-center sticky top-0 bg-gray-900/90 z-10">
          <h2 className="text-xl font-bold text-white">User 360° View</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-full text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
        </div>

        {isLoading ? (
          <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>
        ) : error ? (
          <div className="p-6 text-red-400">Failed to load user data</div>
        ) : data ? (
          <div className="p-6 space-y-8">
            {/* Header Profile */}
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                {data.user.username[0].toUpperCase()}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">{data.user.full_name || 'No Name'}</h3>
                <div className="flex items-center text-gray-400 mt-1 space-x-4">
                  <span className="flex items-center"><Users className="w-4 h-4 mr-1" /> {data.user.username}</span>
                  <span className="flex items-center"><Mail className="w-4 h-4 mr-1" /> {data.user.email}</span>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    data.subscription?.tier === 'pro' ? 'bg-purple-500/20 text-purple-300' :
                    data.subscription?.tier === 'plus' ? 'bg-blue-500/20 text-blue-300' :
                    data.subscription?.tier === 'enterprise' ? 'bg-orange-500/20 text-orange-300' :
                    'bg-gray-500/20 text-gray-300'
                  }`}>
                    {data.subscription?.tier || 'Free'} Plan
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    data.subscription?.status === 'active' ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'
                  }`}>
                    {data.subscription?.status || 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Subscription Details */}
              <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-white/10">
                <h4 className="font-semibold text-white mb-4 flex items-center"><CreditCard className="w-4 h-4 mr-2" /> Subscription</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Tier</span>
                    <span className="font-medium text-white">{data.subscription?.tier || 'Free'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status</span>
                    <span className="font-medium text-white capitalize">{data.subscription?.status || 'None'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Period End</span>
                    <span className="font-medium text-white">
                      {data.subscription?.current_period_end ? new Date(data.subscription.current_period_end).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Auto-Renew</span>
                    <span className="font-medium text-white">{data.subscription?.is_active ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>

              {/* Stats/Usage (Mocked for now based on tier) */}
              <div className="bg-gray-900/50 backdrop-blur-sm p-5 rounded-xl border border-white/10">
                <h4 className="font-semibold text-white mb-4 flex items-center"><Activity className="w-4 h-4 mr-2" /> Activity Overview</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Payments</span>
                    <span className="font-medium text-white">{data.orders.total}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Lifetime Value</span>
                    <span className="font-medium text-green-400">
                      ${data.orders.items.reduce((acc, item) => acc + item.amount, 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Last Active</span>
                    <span className="font-medium text-white">Today</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment History */}
            <div>
              <h4 className="font-bold text-lg text-white mb-4">Payment History</h4>
              <div className="border border-white/10 rounded-xl overflow-hidden">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead className="bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Invoice</th>
                    </tr>
                  </thead>
                  <tbody className="bg-gray-900/50 divide-y divide-gray-700">
                    {data.orders.items.length === 0 ? (
                      <tr><td colSpan={4} className="px-6 py-4 text-center text-gray-400">No payment history</td></tr>
                    ) : (
                      data.orders.items.map((order) => (
                        <tr key={order.id} className="hover:bg-gray-800 transition-colors">
                          <td className="px-6 py-4 text-sm text-white">
                            {new Date(order.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-sm font-medium text-white">
                            ${order.amount.toFixed(2)} {order.currency.toUpperCase()}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 text-xs rounded-full font-medium uppercase ${
                              order.status === 'succeeded' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-purple-400">
                            {order.receipt_url && (
                              <a href={order.receipt_url} target="_blank" rel="noreferrer" className="flex items-center hover:underline">
                                View <ExternalLink className="w-3 h-3 ml-1" />
                              </a>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

// Admin Dashboard Page
export default function AdminDashboardPage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  // State
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch Stats
  const { data: stats } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminApi.getStats,
    enabled: isAuthenticated && (user?.is_superuser || user?.role === 'support'),
  });

  // Fetch Users
  const { data: userData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users', searchQuery],
    queryFn: () => adminApi.getUsers(1, 50, searchQuery || undefined),
    enabled: true,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (user && !user.is_superuser && user.role !== 'support') {
      navigate('/dashboard');
    }
  }, [isAuthenticated, user, navigate]);

  return (
    <div className="min-h-screen bg-gray-950 p-8 text-white">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
          <div className="flex space-x-4">
            <button 
              onClick={() => {}} // No longer switches tabs, just a placeholder
              className={`px-4 py-2 rounded-lg font-medium transition-colors bg-purple-600 text-white hover:bg-purple-700`} // Always active style for users tab
            >
              Users
            </button>
            {/* Support Tickets and Contact Management links are now in the sidebar */}
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-900/50 backdrop-blur-sm p-6 rounded-xl shadow border border-white/10">
            <div className="flex justify-between mb-4">
              <div className="p-3 bg-blue-500/20 rounded-lg"><Users className="w-6 h-6 text-blue-400"/></div>
              <span className="text-green-400 text-sm font-medium">+12%</span>
            </div>
            <h3 className="text-2xl font-bold text-white">{stats?.total_users || 0}</h3>
            <p className="text-gray-400 text-sm">Total Users</p>
          </div>
          <div className="bg-gray-900/50 backdrop-blur-sm p-6 rounded-xl shadow border border-white/10">
            <div className="flex justify-between mb-4">
              <div className="p-3 bg-purple-500/20 rounded-lg"><CreditCard className="w-6 h-6 text-purple-400"/></div>
              <span className="text-green-400 text-sm font-medium">+8%</span>
            </div>
            <h3 className="text-2xl font-bold text-white">${stats?.total_revenue_estimate.toLocaleString() || 0}</h3>
            <p className="text-gray-400 text-sm">Est. Monthly Revenue</p>
          </div>
          {/* Add more stat cards here */}
        </div>

        {/* Content Area */}
        {/* Only User Management section remains */}
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl shadow border border-white/10 overflow-hidden">
            <div className="p-6 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-bold text-white">User Management</h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"/>
                <input 
                  type="text" 
                  placeholder="Search users..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-700 rounded-lg text-sm w-64 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
            </div>
            
            {usersLoading ? (
              <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Plan</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Joined</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-300 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700 bg-gray-900/50">
                  {userData?.users.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-800 cursor-pointer transition-colors" onClick={() => setSelectedUserId(u.id)}>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold mr-3 text-white">
                            {u.username[0].toUpperCase()}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-white">{u.username}</div>
                            <div className="text-xs text-gray-400">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${u.is_active ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium capitalize ${
                          u.stripe_subscription_tier === 'pro' ? 'bg-purple-500/20 text-purple-300' : 
                          u.stripe_subscription_tier === 'plus' ? 'bg-blue-500/20 text-blue-300' : 'bg-gray-500/20 text-gray-300'
                        }`}>
                          {u.stripe_subscription_tier || 'Free'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-purple-400 hover:text-purple-300 text-sm font-medium" onClick={(e) => { e.stopPropagation(); setSelectedUserId(u.id); }}>
                          View 360°
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

      </div>

      {/* User Detail Modal */}
      {selectedUserId && (
        <UserDetailModal userId={selectedUserId} onClose={() => setSelectedUserId(null)} />
      )}
    </div>
  );
}
