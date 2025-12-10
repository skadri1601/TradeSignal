import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ticketsApi, Ticket } from '../api/tickets';
import { MessageSquare, Plus, Send, UserCheck, Clock, CheckCircle, XCircle } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function SupportPage() {
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Fetch tickets
  const { data: tickets, isLoading } = useQuery({
    queryKey: ['my-tickets'],
    queryFn: ticketsApi.getMyTickets,
    staleTime: 60 * 1000, // Consider fresh for 1 minute
    refetchInterval: 60 * 1000, // Auto-refresh every 1 minute (reduced from 15s)
    refetchOnWindowFocus: false,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: ticketsApi.createTicket,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tickets'] });
      setIsCreating(false);
    }
  });

  const replyMutation = useMutation({
    mutationFn: ({ id, message }: { id: number; message: string }) =>
      ticketsApi.replyToTicket(id, message),
    onSuccess: (newMessage, variables) => {
      queryClient.invalidateQueries({ queryKey: ['my-tickets'] });
      // Optimistic update for selected ticket
      if (selectedTicket && selectedTicket.id === variables.id) {
        setSelectedTicket({
          ...selectedTicket,
          messages: [...selectedTicket.messages, newMessage as any]
        });
      }
      setNewMessage('');
    }
  });

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedTicket?.messages]);

  // Helper for status badge
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'open': return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium flex items-center"><Clock className="w-3 h-3 mr-1"/> Open</span>;
      case 'answered': return <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium flex items-center"><UserCheck className="w-3 h-3 mr-1"/> Answered</span>;
      case 'closed': return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full font-medium flex items-center"><CheckCircle className="w-3 h-3 mr-1"/> Closed</span>;
      default: return null;
    }
  };

  if (isLoading) return <div className="h-screen flex items-center justify-center"><LoadingSpinner /></div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl h-[calc(100vh-100px)]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Support</h1>
          <p className="text-gray-500">Get help with your account or subscription</p>
        </div>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-black text-white px-4 py-2 rounded-lg font-medium flex items-center hover:bg-gray-800 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" /> New Ticket
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100%-80px)]">
        {/* Ticket List */}
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-gray-100 bg-gray-50">
            <h2 className="font-semibold text-gray-700">Your Tickets</h2>
          </div>
          <div className="flex-1 overflow-y-auto">
            {tickets?.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No tickets yet</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {tickets?.map((ticket) => (
                  <div
                    key={ticket.id}
                    onClick={() => setSelectedTicket(ticket)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${selectedTicket?.id === ticket.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-gray-900 truncate pr-2">{ticket.subject}</span>
                      <span className="text-xs text-gray-400 whitespace-nowrap">
                        {new Date(ticket.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-sm text-gray-500 truncate w-2/3">
                        {ticket.messages[ticket.messages.length - 1]?.message || 'No messages'}
                      </span>
                      {getStatusBadge(ticket.status)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-2 bg-white border border-gray-200 rounded-xl overflow-hidden flex flex-col">
          {selectedTicket ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <div>
                  <h2 className="font-bold text-gray-900">{selectedTicket.subject}</h2>
                  <p className="text-xs text-gray-500">Ticket #{selectedTicket.id}</p>
                </div>
                {getStatusBadge(selectedTicket.status)}
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
                {selectedTicket.messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.is_staff_reply ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${
                      msg.is_staff_reply 
                        ? 'bg-white border border-gray-200 text-gray-800' 
                        : 'bg-blue-600 text-white'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                      <p className={`text-[10px] mt-1 ${msg.is_staff_reply ? 'text-gray-400' : 'text-blue-200'}`}>
                        {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              {selectedTicket.status !== 'closed' && (
                <div className="p-4 bg-white border-t border-gray-100">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && newMessage.trim() && replyMutation.mutate({ id: selectedTicket.id, message: newMessage })}
                      placeholder="Type your message..."
                      className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                    />
                    <button
                      onClick={() => newMessage.trim() && replyMutation.mutate({ id: selectedTicket.id, message: newMessage })}
                      disabled={replyMutation.isPending || !newMessage.trim()}
                      className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <MessageSquare className="w-16 h-16 mb-4 opacity-20" />
              <p>Select a ticket to view conversation</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Ticket Modal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">New Support Ticket</h3>
              <button onClick={() => setIsCreating(false)}><XCircle className="w-6 h-6 text-gray-400 hover:text-gray-600" /></button>
            </div>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              createMutation.mutate({
                subject: formData.get('subject') as string,
                message: formData.get('message') as string,
                priority: formData.get('priority') as any
              });
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                  <input required name="subject" className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Brief description of issue" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select name="priority" className="w-full border border-gray-300 rounded-lg px-3 py-2 outline-none">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <textarea required name="message" rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Describe your issue in detail..." />
                </div>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="w-full bg-black text-white py-2 rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors"
                >
                  {createMutation.isPending ? 'Submitting...' : 'Submit Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
