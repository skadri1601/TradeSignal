/**
 * Admin Dashboard Page
 * User management and system statistics
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users,
  UserCheck,
  DollarSign,
  Search,
  Trash2,
  Shield,
  ShieldCheck,
  ShieldOff,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { useAuth, getAccessToken } from '../contexts/AuthContext';
import { useCustomAlert } from '../hooks/useCustomAlert';
import { useCustomConfirm } from '../hooks/useCustomConfirm';
import CustomAlert from '../components/common/CustomAlert';
import CustomConfirm from '../components/common/CustomConfirm';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AdminStats {
  total_users: number;
  active_users: number;
  verified_users: number;
  free_tier: number;
  basic_tier: number;
  pro_tier: number;
  total_revenue_estimate: number;
}

interface UserListItem {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  stripe_subscription_tier: string | null;
  stripe_customer_id: string | null;
  created_at: string;
  updated_at: string;
}

interface UserListResponse {
  total: number;
  page: number;
  page_size: number;
  users: UserListItem[];
}

export default function AdminDashboard() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { alertState, showAlert, hideAlert } = useCustomAlert();
  const { confirmState, showConfirm, hideConfirm } = useCustomConfirm();

  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTier, setFilterTier] = useState<string>('');
  const [activeOnly, setActiveOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Check if user is admin
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    if (!user?.is_superuser) {
      navigate('/');
      return;
    }
  }, [isAuthenticated, user, navigate]);

  // Fetch stats
  const fetchStats = useCallback(async () => {
    try {
      const token = getAccessToken();
      const response = await fetch(`${API_URL}/api/v1/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch stats');

      const data = await response.json();
      setStats(data);
    } catch (err: any) {
      console.error('Error fetching stats:', err);
      setError('Failed to load statistics');
    }
  }, []);

  // Fetch users
  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const token = getAccessToken();
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
        ...(searchQuery && { search: searchQuery }),
        ...(filterTier && { tier: filterTier }),
        ...(activeOnly && { active_only: 'true' })
      });

      const response = await fetch(`${API_URL}/api/v1/admin/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch users');

      const data: UserListResponse = await response.json();
      setUsers(data.users);
      setTotalUsers(data.total);
    } catch (err: any) {
      console.error('Error fetching users:', err);
      setError('Failed to load users');
    } finally {
      setIsLoading(false);
    }
  }, [activeOnly, currentPage, filterTier, pageSize, searchQuery]);

  // Initial load
  useEffect(() => {
    if (user?.is_superuser) {
      fetchStats();
      fetchUsers();
    }
  }, [user?.is_superuser, fetchStats, fetchUsers]);

  // Reload users when filters change
  useEffect(() => {
    if (user?.is_superuser) {
      fetchUsers();
    }
  }, [user?.is_superuser, fetchUsers]);

  // Toggle user active status
  const toggleUserActive = async (userId: number, currentStatus: boolean) => {
    showConfirm(
      `Are you sure you want to ${currentStatus ? 'deactivate' : 'activate'} this user?`,
      async () => {
        try {
      const token = getAccessToken();
      const response = await fetch(`${API_URL}/api/v1/admin/users/${userId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ is_active: !currentStatus })
      });

      if (!response.ok) throw new Error('Failed to update user');

          await fetchUsers();
          await fetchStats();
        } catch (err: any) {
          showAlert('Failed to update user status', { type: 'error', title: 'TradeSignal' });
        }
      },
      { type: 'warning', title: 'TradeSignal' }
    );
  };

  // Delete user
  const deleteUser = async (userId: number, permanent: boolean = false) => {
    const confirmMessage = permanent
      ? 'Are you sure you want to PERMANENTLY DELETE this user? This cannot be undone!'
      : 'Are you sure you want to deactivate this user?';

    showConfirm(
      confirmMessage,
      async () => {
        try {
      const token = getAccessToken();
      const response = await fetch(`${API_URL}/api/v1/admin/users/${userId}?permanent=${permanent}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to delete user');

          await fetchUsers();
          await fetchStats();
        } catch (err: any) {
          showAlert('Failed to delete user', { type: 'error', title: 'TradeSignal' });
        }
      },
      {
        type: permanent ? 'danger' : 'warning',
        title: 'TradeSignal',
        confirmText: permanent ? 'Delete Permanently' : 'Deactivate'
      }
    );
  };

  if (!user?.is_superuser) {
    return null;
  }

  const totalPages = Math.ceil(totalUsers / pageSize);

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Shield className="w-8 h-8 mr-3 text-blue-600" />
            Admin Dashboard
          </h1>
          <p className="text-gray-600">Manage users and view system statistics</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start">
            <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-blue-100 rounded-lg p-3">
                  <Users className="w-6 h-6 text-blue-600" />
                </div>
                <span className="text-2xl font-bold text-gray-900">{stats.total_users}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-600">Total Users</h3>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-green-100 rounded-lg p-3">
                  <UserCheck className="w-6 h-6 text-green-600" />
                </div>
                <span className="text-2xl font-bold text-gray-900">{stats.active_users}</span>
              </div>
              <h3 className="text-sm font-medium text-gray-600">Active Users</h3>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-purple-100 rounded-lg p-3">
                  <ShieldCheck className="w-6 h-6 text-purple-600" />
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.basic_tier + stats.pro_tier}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600">Paid Subscribers</h3>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-yellow-100 rounded-lg p-3">
                  <DollarSign className="w-6 h-6 text-yellow-600" />
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  ${stats.total_revenue_estimate.toLocaleString()}
                </span>
              </div>
              <h3 className="text-sm font-medium text-gray-600">Monthly Revenue</h3>
            </div>
          </div>
        )}

        {/* Tier Breakdown */}
        {stats && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Subscription Tiers</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">{stats.free_tier}</div>
                <div className="text-sm text-gray-600">Free</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">{stats.basic_tier}</div>
                <div className="text-sm text-gray-600">Basic ($9/mo)</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">{stats.pro_tier}</div>
                <div className="text-sm text-gray-600">Pro ($29/mo)</div>
              </div>
            </div>
          </div>
        )}

        {/* User Management */}
        <div className="bg-white rounded-lg shadow">
          {/* Filters */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by email, username, or name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Tier Filter */}
              <div className="w-full md:w-48">
                <select
                  value={filterTier}
                  onChange={(e) => setFilterTier(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Tiers</option>
                  <option value="free">Free</option>
                  <option value="basic">Basic</option>
                  <option value="pro">Pro</option>
                </select>
              </div>

              {/* Active Only Toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(e) => setActiveOnly(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Active Only</span>
              </label>
            </div>
          </div>

          {/* Users Table */}
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                No users found
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="flex items-center gap-2">
                            <div className="font-medium text-gray-900">{user.username}</div>
                            {user.is_superuser && (
                              <Shield className="w-4 h-4 text-blue-600" />
                            )}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                          {user.full_name && (
                            <div className="text-xs text-gray-400">{user.full_name}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          user.stripe_subscription_tier === 'pro'
                            ? 'bg-purple-100 text-purple-800'
                            : user.stripe_subscription_tier === 'basic'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.stripe_subscription_tier || 'Free'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          {user.is_active ? (
                            <span className="flex items-center text-sm text-green-600">
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Active
                            </span>
                          ) : (
                            <span className="flex items-center text-sm text-red-600">
                              <XCircle className="w-4 h-4 mr-1" />
                              Inactive
                            </span>
                          )}
                          {user.is_verified && (
                            <span className="text-xs text-blue-600">Verified</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => toggleUserActive(user.id, user.is_active)}
                            className={`p-2 rounded-lg transition-colors ${
                              user.is_active
                                ? 'hover:bg-red-50 text-red-600'
                                : 'hover:bg-green-50 text-green-600'
                            }`}
                            title={user.is_active ? 'Deactivate' : 'Activate'}
                          >
                            {user.is_active ? <ShieldOff className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                          </button>
                          <button
                            onClick={() => deleteUser(user.id, false)}
                            className="p-2 hover:bg-red-50 text-red-600 rounded-lg transition-colors"
                            title="Deactivate User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers} users
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-sm text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Custom Alert Modal */}
      <CustomAlert
        show={alertState.show}
        message={alertState.message}
        title={alertState.title || 'TradeSignal'}
        type={alertState.type}
        onClose={hideAlert}
      />

      {/* Custom Confirm Modal */}
      <CustomConfirm
        show={confirmState.show}
        message={confirmState.message}
        title={confirmState.title || 'TradeSignal'}
        type={confirmState.type}
        confirmText={confirmState.confirmText}
        cancelText={confirmState.cancelText}
        onConfirm={confirmState.onConfirm || (() => {})}
        onCancel={hideConfirm}
      />
    </div>
  );
}
