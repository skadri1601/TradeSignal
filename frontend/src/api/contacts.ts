import apiClient from './client';

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

export interface ContactSubmissionDetail extends ContactSubmission {
  user_email: string | null;
  user_username: string | null;
  ip_address: string | null;
}

export interface ContactListResponse {
  total: number;
  page: number;
  page_size: number;
  contacts: ContactSubmission[];
}

export const contactsApi = {
  getPublicContacts: async (
    page: number = 1,
    pageSize: number = 20,
    search?: string,
    statusFilter?: string
  ): Promise<ContactListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (search) params.append('search', search);
    if (statusFilter) params.append('status_filter', statusFilter);

    const response = await apiClient.get<ContactListResponse>(
      `/api/v1/admin/contacts/public?${params.toString()}`
    );
    return response.data;
  },

  getAuthenticatedContacts: async (
    page: number = 1,
    pageSize: number = 20,
    search?: string,
    statusFilter?: string
  ): Promise<ContactListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (search) params.append('search', search);
    if (statusFilter) params.append('status_filter', statusFilter);

    const response = await apiClient.get<ContactListResponse>(
      `/api/v1/admin/contacts/authenticated?${params.toString()}`
    );
    return response.data;
  },

  getAllContacts: async (
    page: number = 1,
    pageSize: number = 20,
    search?: string,
    statusFilter?: string,
    isPublicFilter?: boolean
  ): Promise<ContactListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (search) params.append('search', search);
    if (statusFilter) params.append('status_filter', statusFilter);
    if (isPublicFilter !== undefined) params.append('is_public_filter', isPublicFilter.toString());

    const response = await apiClient.get<ContactListResponse>(
      `/api/v1/admin/contacts/all?${params.toString()}`
    );
    return response.data;
  },

  getContactDetail: async (contactId: number): Promise<ContactSubmissionDetail> => {
    const response = await apiClient.get<ContactSubmissionDetail>(
      `/api/v1/admin/contacts/${contactId}`
    );
    return response.data;
  },

  updateContactStatus: async (
    contactId: number,
    status: 'new' | 'read' | 'replied'
  ): Promise<{ message: string; contact: ContactSubmission }> => {
    const response = await apiClient.patch<{ message: string; contact: ContactSubmission }>(
      `/api/v1/admin/contacts/${contactId}/status?status=${status}`
    );
    return response.data;
  },
};
