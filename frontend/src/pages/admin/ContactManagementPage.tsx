import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Mail, Search, Filter, Eye, CheckCircle, MessageSquare,
  X, Calendar, Building, Phone, User, Globe, Lock
} from 'lucide-react';
import { contactsApi } from '../../api/contacts';
import { useAuth } from '../../contexts/AuthContext';

type TabType = 'public' | 'authenticated' | 'all';
type StatusFilter = 'all' | 'new' | 'read' | 'replied';

function ContactDetailModal({ 
  contactId, 
  onClose 
}: { 
  contactId: number | null; 
  onClose: () => void;
}) {
  const queryClient = useQueryClient();

  const { data: contact, isLoading } = useQuery({
    queryKey: ['contact-detail', contactId],
    queryFn: () => contactsApi.getContactDetail(contactId!),
    enabled: !!contactId,
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: 'new' | 'read' | 'replied') =>
      contactsApi.updateContactStatus(contactId!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contact-detail', contactId] });
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
    },
  });

  if (!contactId) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900/90 backdrop-blur-md rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-xl border border-white/10">
        <div className="p-6 border-b border-gray-700 flex justify-between items-center sticky top-0 bg-gray-900/90 z-10">
          <h2 className="text-xl font-bold text-white">Contact Details</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-full text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {isLoading ? (
          <div className="p-12 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        ) : contact ? (
          <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-start gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                contact.is_public ? 'bg-blue-500/20' : 'bg-purple-500/20'
              }`}>
                {contact.is_public ? (
                  <Globe className="w-6 h-6 text-blue-400" />
                ) : (
                  <Lock className="w-6 h-6 text-purple-400" />
                )}
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-white">{contact.name}</h3>
                <p className="text-gray-400">{contact.email}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    contact.status === 'new' ? 'bg-yellow-500/20 text-yellow-300' :
                    contact.status === 'read' ? 'bg-blue-500/20 text-blue-300' :
                    'bg-green-500/20 text-green-300'
                  }`}>
                    {contact.status.charAt(0).toUpperCase() + contact.status.slice(1)}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    contact.is_public ? 'bg-blue-500/20 text-blue-300' : 'bg-purple-500/20 text-purple-300'
                  }`}>
                    {contact.is_public ? 'Public' : 'Authenticated'}
                  </span>
                </div>
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contact.company_name && (
                <div className="flex items-start gap-3">
                  <Building className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-400">Company</p>
                    <p className="font-medium text-white">{contact.company_name}</p>
                  </div>
                </div>
              )}
              {contact.phone && (
                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-400">Phone</p>
                    <p className="font-medium text-white">{contact.phone}</p>
                  </div>
                </div>
              )}
              {contact.user_email && (
                <div className="flex items-start gap-3">
                  <User className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-400">User Account</p>
                    <p className="font-medium text-white">{contact.user_email}</p>
                  </div>
                </div>
              )}
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-400">Submitted</p>
                  <p className="font-medium text-white">
                    {new Date(contact.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Message */}
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <p className="text-sm text-gray-400 mb-2">Message</p>
              <p className="text-white whitespace-pre-wrap">{contact.message}</p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t border-white/10">
              {contact.status !== 'read' && (
                <button
                  onClick={() => updateStatusMutation.mutate('read')}
                  disabled={updateStatusMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  Mark as Read
                </button>
              )}
              {contact.status !== 'replied' && (
                <button
                  onClick={() => updateStatusMutation.mutate('replied')}
                  disabled={updateStatusMutation.isPending}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  <MessageSquare className="w-4 h-4" />
                  Mark as Replied
                </button>
              )}
              <a
                href={`mailto:${contact.email}`}
                className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
              >
                <Mail className="w-4 h-4" />
                Reply via Email
              </a>
            </div>
          </div>
        ) : (
          <div className="p-6 text-red-400">Failed to load contact details</div>
        )}
      </div>
    </div>
  );
}

export default function ContactManagementPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>(
    user?.role === 'super_admin' ? 'all' : 'authenticated'
  );
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [selectedContact, setSelectedContact] = useState<number | null>(null);
  const pageSize = 20;

  const isSuperAdmin = user?.role === 'super_admin';

  // Query based on active tab
  const publicQuery = useQuery({
    queryKey: ['contacts', 'public', page, search, statusFilter],
    queryFn: () => contactsApi.getPublicContacts(page, pageSize, search || undefined, statusFilter !== 'all' ? statusFilter : undefined),
    enabled: activeTab === 'public' || activeTab === 'all',
  });

  const authenticatedQuery = useQuery({
    queryKey: ['contacts', 'authenticated', page, search, statusFilter],
    queryFn: () => contactsApi.getAuthenticatedContacts(page, pageSize, search || undefined, statusFilter !== 'all' ? statusFilter : undefined),
    enabled: activeTab === 'authenticated' || activeTab === 'all',
  });

  const allQuery = useQuery({
    queryKey: ['contacts', 'all', page, search, statusFilter],
    queryFn: () => contactsApi.getAllContacts(page, pageSize, search || undefined, statusFilter !== 'all' ? statusFilter : undefined),
    enabled: activeTab === 'all',
  });

  const currentData = activeTab === 'all' 
    ? allQuery.data 
    : activeTab === 'public' 
    ? publicQuery.data 
    : authenticatedQuery.data;

  const isLoading = activeTab === 'all'
    ? allQuery.isLoading
    : activeTab === 'public'
    ? publicQuery.isLoading
    : authenticatedQuery.isLoading;

  const contacts = currentData?.contacts || [];
  const total = currentData?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Contact Management</h1>
        <p className="mt-2 text-gray-400">
          Manage public inquiries and authenticated user contact submissions
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="flex space-x-8">
          {isSuperAdmin && (
            <>
              <button
                onClick={() => {
                  setActiveTab('all');
                  setPage(1);
                }}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'all'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
                }`}
              >
                All Contacts
              </button>
              <button
                onClick={() => {
                  setActiveTab('public');
                  setPage(1);
                }}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'public'
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
                }`}
              >
                Public Inquiries
              </button>
            </>
          )}
          <button
            onClick={() => {
              setActiveTab('authenticated');
              setPage(1);
            }}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'authenticated'
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-700'
            }`}
          >
            User Inquiries
          </button>
        </nav>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as StatusFilter);
              setPage(1);
            }}
            className="pl-10 pr-4 py-2 rounded-lg border border-gray-700 bg-gray-800 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm appearance-none"
          >
            <option value="all">All Status</option>
            <option value="new">New</option>
            <option value="read">Read</option>
            <option value="replied">Replied</option>
          </select>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-white/10 overflow-hidden">
        {isLoading ? (
          <div className="p-12 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        ) : contacts.length === 0 ? (
          <div className="p-12 text-center text-gray-400">
            <Mail className="w-12 h-12 mx-auto mb-4 text-gray-500" />
            <p>No contacts found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800 border-b border-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-gray-900/50 divide-y divide-gray-700">
                  {contacts.map((contact) => (
                    <tr key={contact.id} className="hover:bg-gray-800 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-white">{contact.name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-gray-400">{contact.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-gray-400">{contact.company_name || '-'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          contact.is_public
                            ? 'bg-blue-500/20 text-blue-300'
                            : 'bg-purple-500/20 text-purple-300'
                        }`}>
                          {contact.is_public ? 'Public' : 'User'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          contact.status === 'new'
                            ? 'bg-yellow-500/20 text-yellow-300'
                            : contact.status === 'read'
                            ? 'bg-blue-500/20 text-blue-300'
                            : 'bg-green-500/20 text-green-300'
                        }`}>
                          {contact.status.charAt(0).toUpperCase() + contact.status.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                        {new Date(contact.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => setSelectedContact(contact.id)}
                          className="text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1 transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-700 flex items-center justify-between">
                <div className="text-sm text-gray-400">
                  Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} contacts
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-300 hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Detail Modal */}
      {selectedContact && (
        <ContactDetailModal
          contactId={selectedContact}
          onClose={() => setSelectedContact(null)}
        />
      )}
    </div>
  );
}
