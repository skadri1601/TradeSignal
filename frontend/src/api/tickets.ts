import { getAccessToken } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.yourdomain.com';

function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

export interface TicketMessage {
  id: number;
  ticket_id: number;
  user_id: number;
  message: string;
  is_staff_reply: boolean;
  created_at: string;
}

export interface Ticket {
  id: number;
  user_id: number;
  subject: string;
  status: 'open' | 'answered' | 'closed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
  messages: TicketMessage[];
}

export interface CreateTicketData {
  subject: string;
  message: string;
  priority?: 'low' | 'medium' | 'high';
}

export const ticketsApi = {
  // User methods
  getMyTickets: async (): Promise<Ticket[]> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/tickets/`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch tickets');
    return res.json();
  },

  getTicket: async (id: number): Promise<Ticket> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/tickets/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch ticket');
    return res.json();
  },

  createTicket: async (data: CreateTicketData): Promise<Ticket> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/tickets/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create ticket');
    return res.json();
  },

  replyToTicket: async (id: number, message: string): Promise<TicketMessage> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/tickets/${id}/reply`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error('Failed to reply to ticket');
    return res.json();
  },

  // Admin methods
  getAllTickets: async (status?: string): Promise<Ticket[]> => {
    const url = new URL(`${API_BASE_URL}/api/v1/tickets/admin/all`);
    if (status) url.searchParams.append('status', status);
    
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch all tickets');
    return res.json();
  },

  updateStatus: async (id: number, status: string): Promise<void> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/tickets/${id}/status?status=${status}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to update ticket status');
  }
};
