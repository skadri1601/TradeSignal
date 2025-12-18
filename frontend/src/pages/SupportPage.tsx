import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ticketsApi, Ticket } from '../api/tickets';
import { MessageSquare, Plus, Send, UserCheck, Clock, CheckCircle, XCircle, HelpCircle, ChevronRight, Shield } from 'lucide-react';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { motion, AnimatePresence } from 'framer-motion';

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
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
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
      if (selectedTicket && selectedTicket.id === variables.id) {
        setSelectedTicket({
          ...selectedTicket,
          messages: [...selectedTicket.messages, newMessage as any]
        });
      }
      setNewMessage('');
    }
  });

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedTicket?.messages]);

  // Status Badges (Dark Mode Styled)
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'open': return (
        <span className="bg-green-500/10 text-green-400 border border-green-500/20 text-xs px-2.5 py-1 rounded-full font-medium flex items-center shadow-[0_0_10px_rgba(34,197,94,0.1)]">
          <Clock className="w-3 h-3 mr-1.5"/> Open
        </span>
      );
      case 'answered': return (
        <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs px-2.5 py-1 rounded-full font-medium flex items-center shadow-[0_0_10px_rgba(59,130,246,0.1)]">
          <UserCheck className="w-3 h-3 mr-1.5"/> Answered
        </span>
      );
      case 'closed': return (
        <span className="bg-gray-500/10 text-gray-400 border border-gray-500/20 text-xs px-2.5 py-1 rounded-full font-medium flex items-center">
          <CheckCircle className="w-3 h-3 mr-1.5"/> Closed
        </span>
      );
      default: return null;
    }
  };

  if (isLoading) return <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center"><LoadingSpinner /></div>;

  return (
    <div className="min-h-screen bg-[#0a0a0a] pt-24 px-4 pb-12 font-sans selection:bg-purple-500/30 selection:text-white">
      <div className="max-w-7xl mx-auto h-[calc(100vh-140px)] flex flex-col">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg shadow-lg shadow-purple-900/20">
                <HelpCircle className="w-6 h-6 text-white" />
              </div>
              Support Center
            </h1>
            <p className="text-gray-400 text-lg">
              Expert assistance for your trading journey.
            </p>
          </div>
          <button
            onClick={() => setIsCreating(true)}
            className="group relative inline-flex items-center justify-center px-6 py-3 font-semibold text-white transition-all duration-200 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 hover:border-white/20 hover:scale-105 active:scale-95 focus:outline-none"
          >
            <span className="mr-2 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent group-hover:text-white transition-colors">
              <Plus className="w-5 h-5" />
            </span>
            New Ticket
          </button>
        </div>

        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
          {/* Ticket List Panel */}
          <div className="lg:col-span-4 bg-[#0f0f1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
            <div className="p-5 border-b border-white/5 bg-white/[0.02]">
              <h2 className="font-semibold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-purple-400" />
                Your Tickets
              </h2>
            </div>
            
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {tickets?.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center p-8 text-center text-gray-500">
                  <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4 border border-white/5">
                    <MessageSquare className="w-8 h-8 opacity-40" />
                  </div>
                  <p className="text-sm font-medium text-gray-400">No support tickets found</p>
                  <p className="text-xs text-gray-600 mt-1">Create one to get started</p>
                </div>
              ) : (
                <div className="divide-y divide-white/5">
                  {tickets?.map((ticket) => (
                    <div
                      key={ticket.id}
                      onClick={() => {
                        console.log("Ticket clicked:", ticket.id);
                        setSelectedTicket(ticket);
                      }}
                      className={`p-5 cursor-pointer transition-all duration-200 group border-l-2 ${
                        selectedTicket?.id === ticket.id 
                          ? 'bg-white/[0.03] border-purple-500' 
                          : 'bg-transparent border-transparent hover:bg-white/[0.02] hover:border-gray-700'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className={`font-medium truncate pr-4 text-sm ${selectedTicket?.id === ticket.id ? 'text-white' : 'text-gray-300 group-hover:text-white'}`}>
                          {ticket.subject}
                        </span>
                        <span className="text-[10px] text-gray-500 font-mono whitespace-nowrap bg-black/30 px-1.5 py-0.5 rounded">
                          {new Date(ticket.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        </span>
                      </div>
                      <div className="flex justify-between items-end mt-3">
                        <p className="text-xs text-gray-500 truncate w-2/3 pr-2">
                          {ticket.messages[ticket.messages.length - 1]?.message || 'No messages'}
                        </p>
                        <div className="transform scale-90 origin-right">
                           {getStatusBadge(ticket.status)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Chat Panel */}
          <div className="lg:col-span-8 bg-[#0f0f1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden flex flex-col shadow-2xl relative">
            {selectedTicket ? (
              <>
                {/* Chat Header */}
                <div className="p-5 border-b border-white/5 bg-white/[0.02] flex justify-between items-center z-10">
                  <div className="flex flex-col">
                    <h2 className="font-bold text-lg text-white tracking-wide">{selectedTicket.subject}</h2>
                    <div className="flex items-center gap-3 mt-1">
                       <span className="text-[10px] font-mono text-gray-500">#{selectedTicket.id.toString().padStart(6, '0')}</span>
                       <span className="w-1 h-1 bg-gray-600 rounded-full"></span>
                       <span className="text-xs text-gray-400 capitalize">{selectedTicket.priority} Priority</span>
                    </div>
                  </div>
                  {getStatusBadge(selectedTicket.status)}
                </div>

                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-[url('/images/grid-pattern.svg')] bg-repeat opacity-95">
                  {selectedTicket.messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.is_staff_reply ? 'justify-start' : 'justify-end'}`}>
                      <div className={`max-w-[85%] lg:max-w-[70%] rounded-2xl px-5 py-4 shadow-lg backdrop-blur-sm border ${
                        msg.is_staff_reply 
                          ? 'bg-[#1a1a2e]/90 border-white/10 text-gray-200 rounded-tl-none' 
                          : 'bg-gradient-to-br from-purple-600 to-indigo-600 border-transparent text-white rounded-tr-none'
                      }`}>
                        {msg.is_staff_reply && (
                           <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/5">
                              <Shield className="w-3 h-3 text-purple-400" />
                              <span className="text-[10px] font-bold text-purple-300 uppercase tracking-wider">Support Team</span>
                           </div>
                        )}
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                        <p className={`text-[10px] mt-2 text-right ${msg.is_staff_reply ? 'text-gray-500' : 'text-purple-200/70'}`}>
                          {new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                {selectedTicket.status !== 'closed' ? (
                  <div className="p-5 bg-[#0f0f1a] border-t border-white/10 z-10">
                    <div className="relative flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl p-2 focus-within:ring-2 focus-within:ring-purple-500/50 focus-within:border-purple-500/50 transition-all">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && newMessage.trim() && replyMutation.mutate({ id: selectedTicket.id, message: newMessage })}
                        placeholder="Type your message..."
                        className="flex-1 bg-transparent border-none text-white placeholder-gray-500 text-sm px-3 focus:ring-0 outline-none"
                      />
                      <button
                        onClick={() => newMessage.trim() && replyMutation.mutate({ id: selectedTicket.id, message: newMessage })}
                        disabled={replyMutation.isPending || !newMessage.trim()}
                        className="p-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-purple-900/20"
                      >
                        {replyMutation.isPending ? (
                           <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                           <Send className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-red-500/5 border-t border-red-500/10 text-center">
                    <p className="text-sm text-red-400 flex items-center justify-center gap-2">
                      <XCircle className="w-4 h-4" /> This ticket is closed. Open a new ticket for further assistance.
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-500 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-20">
                <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-6 border border-white/5 backdrop-blur-sm">
                   <MessageSquare className="w-10 h-10 text-gray-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-300 mb-2">Select a Ticket</h3>
                <p className="text-gray-500 max-w-xs text-center">Choose a ticket from the left sidebar to view the conversation details.</p>
              </div>
            )}
          </div>
        </div>

        {/* Create Ticket Modal */}
        <AnimatePresence>
          {isCreating && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            >
              <motion.div 
                initial={{ scale: 0.9, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 20 }}
                className="bg-[#0f0f1a] border border-white/10 rounded-2xl max-w-lg w-full p-8 shadow-2xl relative"
              >
                <div className="flex justify-between items-center mb-8">
                  <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                     <span className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center text-purple-400 border border-purple-500/20">
                        <Plus className="w-5 h-5" />
                     </span>
                     New Ticket
                  </h3>
                  <button onClick={() => setIsCreating(false)} className="text-gray-400 hover:text-white transition-colors bg-white/5 p-2 rounded-full hover:bg-white/10">
                    <XCircle className="w-6 h-6" />
                  </button>
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
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Subject</label>
                      <input 
                        required 
                        name="subject" 
                        className="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500/50 focus:border-transparent outline-none transition-all" 
                        placeholder="Brief description of the issue" 
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Priority</label>
                      <div className="relative">
                        <select name="priority" className="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white appearance-none focus:ring-2 focus:ring-purple-500/50 outline-none">
                          <option value="low">Low Priority</option>
                          <option value="medium">Medium Priority</option>
                          <option value="high">High Priority</option>
                        </select>
                        <ChevronRight className="w-4 h-4 text-gray-500 absolute right-4 top-1/2 -translate-y-1/2 rotate-90" />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">Message</label>
                      <textarea 
                        required 
                        name="message" 
                        rows={5} 
                        className="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 focus:ring-2 focus:ring-purple-500/50 focus:border-transparent outline-none transition-all resize-none" 
                        placeholder="Describe your issue in detail..." 
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={createMutation.isPending}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white py-4 rounded-xl font-bold tracking-wide shadow-lg shadow-purple-900/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
                    >
                      {createMutation.isPending ? (
                        <div className="flex items-center justify-center gap-2">
                           <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                           Submitting...
                        </div>
                      ) : 'Submit Ticket'}
                    </button>
                  </div>
                </form>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}