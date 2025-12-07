import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, CreditCard, Activity, Search, 
  ExternalLink, X, Mail
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { adminApi } from '../api/admin';
import { ticketsApi, Ticket as TicketType } from '../api/tickets';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

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
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white z-10">
          <h2 className="text-xl font-bold text-gray-900">User 360° View</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full"><X className="w-5 h-5" /></button>
        </div>

        {isLoading ? (
          <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
        ) : error ? (
          <div className="p-6 text-red-600">Failed to load user data</div>
        ) : data ? (
          <div className="p-6 space-y-8">
            {/* Header Profile */}
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                {data.user.username[0].toUpperCase()}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900">{data.user.full_name || 'No Name'}</h3>
                <div className="flex items-center text-gray-500 mt-1 space-x-4">
                  <span className="flex items-center"><Users className="w-4 h-4 mr-1" /> {data.user.username}</span>
                  <span className="flex items-center"><Mail className="w-4 h-4 mr-1" /> {data.user.email}</span>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    data.subscription?.tier === 'pro' ? 'bg-purple-100 text-purple-700' :
                    data.subscription?.tier === 'plus' ? 'bg-blue-100 text-blue-700' :
                    data.subscription?.tier === 'enterprise' ? 'bg-orange-100 text-orange-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {data.subscription?.tier || 'Free'} Plan
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    data.subscription?.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {data.subscription?.status || 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Subscription Details */}
              <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center"><CreditCard className="w-4 h-4 mr-2" /> Subscription</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Current Tier</span>
                    <span className="font-medium">{data.subscription?.tier || 'Free'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Status</span>
                    <span className="font-medium capitalize">{data.subscription?.status || 'None'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Period End</span>
                    <span className="font-medium">
                      {data.subscription?.current_period_end ? new Date(data.subscription.current_period_end).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Auto-Renew</span>
                    <span className="font-medium">{data.subscription?.is_active ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              </div>

              {/* Stats/Usage (Mocked for now based on tier) */}
              <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center"><Activity className="w-4 h-4 mr-2" /> Activity Overview</h4>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total Payments</span>
                    <span className="font-medium">{data.orders.total}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Lifetime Value</span>
                    <span className="font-medium text-green-600">
                      ${data.orders.items.reduce((acc, item) => acc + item.amount, 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Last Active</span>
                    <span className="font-medium">Today</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment History */}
            <div>
              <h4 className="font-bold text-lg text-gray-900 mb-4">Payment History</h4>
              <div className="border rounded-xl overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invoice</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.orders.items.length === 0 ? (
                      <tr><td colSpan={4} className="px-6 py-4 text-center text-gray-500">No payment history</td></tr>
                    ) : (
                      data.orders.items.map((order) => (
                        <tr key={order.id}>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {new Date(order.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            ${order.amount.toFixed(2)} {order.currency.toUpperCase()}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 text-xs rounded-full font-medium uppercase ${
                              order.status === 'succeeded' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                            }`}>
                              {order.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-blue-600">
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
  const queryClient = useQueryClient();
  
  // State
  const [activeTab, setActiveTab] = useState<'users' | 'tickets'>('users');
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
    enabled: activeTab === 'users',
  });

  // Fetch Tickets
  const { data: ticketsData, isLoading: ticketsLoading } = useQuery({
    queryKey: ['admin-tickets'],
    queryFn: () => ticketsApi.getAllTickets(),
    enabled: activeTab === 'tickets',
    refetchInterval: 30000,
  });

  // Ticket Reply Mutation
  const [selectedTicket, setSelectedTicket] = useState<TicketType | null>(null);
  const [replyText, setReplyText] = useState('');
  
  const replyMutation = useMutation({
    mutationFn: ({ id, message }: { id: number; message: string }) => ticketsApi.replyToTicket(id, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-tickets'] });
      setSelectedTicket(null);
      setReplyText('');
    }
  });

  const closeTicketMutation = useMutation({
    mutationFn: ({ id }: { id: number }) => ticketsApi.updateStatus(id, 'closed'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-tickets'] });
    }
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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <div className="flex space-x-4">
            <button 
              onClick={() => setActiveTab('users')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'users' ? 'bg-black text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
            >
              Users
            </button>
            <button 
              onClick={() => setActiveTab('tickets')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'tickets' ? 'bg-black text-white' : 'bg-white text-gray-600 hover:bg-gray-100'}`}
            >
              Support Tickets
            </button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-lg"><Users className="w-6 h-6 text-blue-600"/></div>
              <span className="text-green-600 text-sm font-medium">+12%</span>
            </div>
            <h3 className="text-2xl font-bold">{stats?.total_users || 0}</h3>
            <p className="text-gray-500 text-sm">Total Users</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-lg"><CreditCard className="w-6 h-6 text-purple-600"/></div>
              <span className="text-green-600 text-sm font-medium">+8%</span>
            </div>
            <h3 className="text-2xl font-bold">${stats?.total_revenue_estimate.toLocaleString() || 0}</h3>
            <p className="text-gray-500 text-sm">Est. Monthly Revenue</p>
          </div>
          {/* Add more stat cards here */}
        </div>

        {/* Content Area */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-bold">User Management</h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"/>
                <input 
                  type="text" 
                  placeholder="Search users..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 border rounded-lg text-sm w-64"
                />
              </div>
            </div>
            
            {usersLoading ? (
              <div className="p-12 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {userData?.users.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedUserId(u.id)}>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold mr-3">
                            {u.username[0].toUpperCase()}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">{u.username}</div>
                            <div className="text-xs text-gray-500">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs rounded-full font-medium capitalize ${
                          u.stripe_subscription_tier === 'pro' ? 'bg-purple-100 text-purple-700' : 
                          u.stripe_subscription_tier === 'plus' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {u.stripe_subscription_tier || 'Free'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium" onClick={(e) => { e.stopPropagation(); setSelectedUserId(u.id); }}>
                          View 360°
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'tickets' && (
          <div className="flex gap-6 h-[600px]">
            {/* Ticket List */}
            <div className="w-1/3 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              <div className="p-4 border-b bg-gray-50 font-semibold text-gray-700">All Tickets</div>
              <div className="overflow-y-auto flex-1">
                {ticketsLoading ? (
                  <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div></div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {ticketsData?.map(t => (
                      <div 
                        key={t.id} 
                        onClick={() => setSelectedTicket(t)}
                        className={`p-4 cursor-pointer hover:bg-gray-50 ${selectedTicket?.id === t.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''}`}
                      >
                        <div className="flex justify-between mb-1">
                          <span className="font-medium text-sm text-gray-900 truncate w-2/3">{t.subject}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase ${
                            t.status === 'open' ? 'bg-green-100 text-green-700' : 
                            t.status === 'answered' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                          }`}>{t.status}</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>User #{t.user_id}</span>
                          <span>{new Date(t.updated_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Ticket Detail */}
            <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              {selectedTicket ? (
                <>
                  <div className="p-4 border-b flex justify-between items-center bg-gray-50">
                    <div>
                      <h3 className="font-bold text-gray-900">{selectedTicket.subject}</h3>
                      <p className="text-xs text-gray-500">User ID: {selectedTicket.user_id} • Priority: {selectedTicket.priority}</p>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setSelectedUserId(selectedTicket.user_id)} className="px-3 py-1.5 text-xs bg-white border rounded-md hover:bg-gray-50">
                        View User
                      </button>
                      {selectedTicket.status !== 'closed' && (
                        <button 
                          onClick={() => closeTicketMutation.mutate({id: selectedTicket.id})}
                          className="px-3 py-1.5 text-xs bg-gray-800 text-white rounded-md hover:bg-black"
                        >
                          Close Ticket
                        </button>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
                    {/* Use a fresh fetch for messages if needed, but selectedTicket comes with them */}
                    {selectedTicket.messages.map(m => (
                      <div key={m.id} className={`flex ${m.is_staff_reply ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg text-sm ${
                          m.is_staff_reply ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-gray-800'
                        }`}>
                          <p>{m.message}</p>
                          <p className={`text-[10px] mt-1 ${m.is_staff_reply ? 'text-blue-200' : 'text-gray-400'}`}>
                            {new Date(m.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="p-4 border-t bg-white">
                    <textarea 
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      className="w-full border rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="Type your reply..."
                      rows={3}
                    />
                    <div className="mt-2 flex justify-end">
                      <button 
                        onClick={() => replyMutation.mutate({id: selectedTicket.id, message: replyText})}
                        disabled={!replyText.trim() || replyMutation.isPending}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                      >
                        Send Reply
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-400">
                  Select a ticket to view details
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* User Detail Modal */}
      {selectedUserId && (
        <UserDetailModal userId={selectedUserId} onClose={() => setSelectedUserId(null)} />
      )}
    </div>
  );
}