import apiClient from './client';

export interface PublicContactRequest {
  name: string;
  company_name?: string;
  email: string;
  phone?: string;
  message: string;
}

export interface ContactResponse {
  success: boolean;
  message: string;
}

export const submitPublicContact = async (
  data: PublicContactRequest
): Promise<ContactResponse> => {
  const response = await apiClient.post<ContactResponse>(
    '/api/v1/public/contact/',
    data
  );
  return response.data;
};
