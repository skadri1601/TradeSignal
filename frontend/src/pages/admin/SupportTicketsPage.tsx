import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ExternalLink, X, Mail, Users, CreditCard, Activity
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { ticketsApi, Ticket as TicketType } from '../../api/tickets';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi } from '../../api/admin'; // Needed for UserDetailModal (nested)

// User Detail Modal (User 360) - Copied from AdminDashboardPage.tsx for context, but should be a shared component
// For now, keeping it here for self-containment, but ideally this would be a single shared component
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

export default function SupportTicketsPage() {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // State
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  
  // Fetch Tickets
  const { data: ticketsData, isLoading: ticketsLoading } = useQuery({
    queryKey: ['admin-tickets'],
    queryFn: () => ticketsApi.getAllTickets(),
    enabled: isAuthenticated && (user?.is_superuser || user?.role === 'support'),
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
    <div className="min-h-screen bg-gray-950 p-8 text-white">
        <div className="max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-8">Support Tickets</h1>

            <div className="flex gap-6 h-[600px]">
                {/* Ticket List */}
                <div className="w-1/3 bg-gray-900/50 backdrop-blur-sm rounded-xl shadow border border-white/10 overflow-hidden flex flex-col">
                <div className="p-4 border-b border-gray-700 bg-gray-800 font-semibold text-white">All Tickets</div>
                <div className="overflow-y-auto flex-1">
                    {ticketsLoading ? (
                    <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div></div>
                    ) : (
                    <div className="divide-y divide-gray-700">
                        {ticketsData?.map(t => (
                        <div 
                            key={t.id} 
                            onClick={() => setSelectedTicket(t)}
                            className={`p-4 cursor-pointer hover:bg-gray-800 transition-colors ${selectedTicket?.id === t.id ? 'bg-gray-800 border-l-4 border-purple-600' : ''}`}
                        >
                            <div className="flex justify-between mb-1">
                            <span className="font-medium text-sm text-white truncate w-2/3">{t.subject}</span>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase ${
                                t.status === 'open' ? 'bg-green-500/20 text-green-300' : 
                                t.status === 'answered' ? 'bg-blue-500/20 text-blue-300' : 'bg-gray-500/20 text-gray-300'
                            }`}>{t.status}</span>
                            </div>
                            <div className="flex justify-between text-xs text-gray-400">
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
                <div className="flex-1 bg-gray-900/50 backdrop-blur-sm rounded-xl shadow border border-white/10 overflow-hidden flex flex-col">
                {selectedTicket ? (
                    <>
                    <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800">
                        <div>
                        <h3 className="font-bold text-white">{selectedTicket.subject}</h3>
                        <p className="text-xs text-gray-400">User ID: {selectedTicket.user_id} • Priority: {selectedTicket.priority}</p>
                        </div>
                        <div className="flex gap-2">
                        <button onClick={() => setSelectedUserId(selectedTicket.user_id)} className="px-3 py-1.5 text-xs bg-gray-800 text-gray-300 border border-gray-700 rounded-md hover:bg-gray-700">
                            View User
                        </button>
                        {selectedTicket.status !== 'closed' && (
                            <button 
                            onClick={() => closeTicketMutation.mutate({id: selectedTicket.id})}
                            className="px-3 py-1.5 text-xs bg-purple-600 text-white rounded-md hover:bg-purple-700"
                            >
                            Close Ticket
                            </button>
                        )}
                        </div>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
                        {/* Use a fresh fetch for messages if needed, but selectedTicket comes with them */}
                        {selectedTicket.messages.map(m => (
                        <div key={m.id} className={`flex ${m.is_staff_reply ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] p-3 rounded-lg text-sm ${
                            m.is_staff_reply ? 'bg-blue-600 text-white' : 'bg-gray-800 border border-gray-700 text-white'
                            }`}>
                            <p>{m.message}</p>
                            <p className={`text-[10px] mt-1 ${m.is_staff_reply ? 'text-blue-200' : 'text-gray-400'}`}>
                                {new Date(m.created_at).toLocaleString()}
                            </p>
                            </div>
                        </div>
                        ))}
                    </div>

                    <div className="p-4 border-t border-gray-700 bg-gray-900/50">
                        <textarea 
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        className="w-full border border-gray-700 rounded-lg p-3 text-sm focus:ring-2 focus:ring-purple-500 outline-none bg-gray-800 text-white"
                        placeholder="Type your reply..."
                        rows={3}
                        />
                        <div className="mt-2 flex justify-end">
                        <button 
                            onClick={() => replyMutation.mutate({id: selectedTicket.id, message: replyText})}
                            disabled={!replyText.trim() || replyMutation.isPending}
                            className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50"
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

            {/* User Detail Modal */}
            {selectedUserId && (
                <UserDetailModal userId={selectedUserId} onClose={() => setSelectedUserId(null)} />
            )}
        </div>
    </div>
  );
}
