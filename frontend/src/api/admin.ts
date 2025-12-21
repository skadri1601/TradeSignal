import { getAccessToken } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.tradesignal.capital';

function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

export interface AdminStats {
  total_users: number;
  active_users: number;
  verified_users: number;
  free_tier: number;
  basic_tier: number;
  pro_tier: number;
  total_revenue_estimate: number;
}

export interface UserListItem {
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

export interface UserBillingHistory {
  user: {
    id: number;
    email: string;
    username: string;
    full_name: string | null;
  };
  subscription: {
    tier: string;
    status: string;
    is_active: boolean;
    current_period_start: string | null;
    current_period_end: string | null;
  } | null;
  orders: {
    items: Array<{
      id: number;
      amount: number;
      currency: string;
      status: string;
      created_at: string;
      description: string | null;
      receipt_url: string | null;
    }>;
    total: number;
  };
}

export const adminApi = {
  getStats: async (): Promise<AdminStats> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/stats`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  getUsers: async (page = 1, pageSize = 20, search?: string): Promise<{ users: UserListItem[]; total: number }> => {
    const url = new URL(`${API_BASE_URL}/api/v1/admin/users`);
    url.searchParams.append('page', page.toString());
    url.searchParams.append('page_size', pageSize.toString());
    if (search) url.searchParams.append('search', search);

    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch users');
    return res.json();
  },

  getUserBilling: async (userId: number): Promise<UserBillingHistory> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/users/${userId}/billing`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch user billing history');
    return res.json();
  },

  deleteUser: async (userId: number, permanent = false): Promise<void> => {
    const url = new URL(`${API_BASE_URL}/api/v1/admin/users/${userId}`);
    if (permanent) url.searchParams.append('permanent', 'true');
    
    const res = await fetch(url.toString(), {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete user');
  }
};

export interface ContactSubmission {
  id: number;
  user_id: number | null;
  name: string;
  company_name: string | null;
  email: string;
  phone: string | null;
  message: string;
  is_public: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ContactListResponse {
  contacts: ContactSubmission[];
  total: number;
  page: number;
  page_size: number;
}

export const contactAdminApi = {
  getPublicContacts: async (
    page = 1,
    pageSize = 20,
    status?: string,
    search?: string
  ): Promise<ContactListResponse> => {
    const url = new URL(`${API_BASE_URL}/api/v1/admin/contacts/public`);
    url.searchParams.append('page', page.toString());
    url.searchParams.append('page_size', pageSize.toString());
    if (status) url.searchParams.append('status', status);
    if (search) url.searchParams.append('search', search);

    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch public contacts');
    return res.json();
  },

  getAuthenticatedContacts: async (
    page = 1,
    pageSize = 20,
    status?: string,
    search?: string
  ): Promise<ContactListResponse> => {
    const url = new URL(`${API_BASE_URL}/api/v1/admin/contacts/authenticated`);
    url.searchParams.append('page', page.toString());
    url.searchParams.append('page_size', pageSize.toString());
    if (status) url.searchParams.append('status', status);
    if (search) url.searchParams.append('search', search);

    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch authenticated contacts');
    return res.json();
  },

  getAllContacts: async (
    page = 1,
    pageSize = 20,
    status?: string,
    is_public?: boolean,
    search?: string
  ): Promise<ContactListResponse> => {
    const url = new URL(`${API_BASE_URL}/api/v1/admin/contacts/all`);
    url.searchParams.append('page', page.toString());
    url.searchParams.append('page_size', pageSize.toString());
    if (status) url.searchParams.append('status', status);
    if (is_public !== undefined) url.searchParams.append('is_public', is_public.toString());
    if (search) url.searchParams.append('search', search);

    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch all contacts');
    return res.json();
  },

  getContactDetail: async (contactId: number): Promise<ContactSubmission> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/contacts/${contactId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch contact detail');
    return res.json();
  },

  updateContactStatus: async (contactId: number, status: string): Promise<ContactSubmission> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/contacts/${contactId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update contact status');
    return res.json();
  },
};
