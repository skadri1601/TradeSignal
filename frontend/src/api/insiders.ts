import apiClient from './client';
import { Insider, PaginatedResponse, Trade } from '../types';

export const insidersApi = {
  // Get all insiders
  getInsiders: async (page: number = 1, limit: number = 20): Promise<PaginatedResponse<Insider>> => {
    const response = await apiClient.get('/api/v1/insiders/', { params: { page, limit } });
    return response.data;
  },

  // Get single insider by ID
  getInsider: async (id: number): Promise<Insider> => {
    const response = await apiClient.get(`/api/v1/insiders/${id}`);
    return response.data;
  },

  // Get insider trades
  getInsiderTrades: async (id: number, limit: number = 20): Promise<Trade[]> => {
    const response = await apiClient.get(`/api/v1/insiders/${id}/trades`, { params: { limit } });
    return response.data?.items ?? [];
  },

  // Get insider activity summary
  getInsiderActivity: async (id: number) => {
    const response = await apiClient.get(`/api/v1/insiders/${id}/activity`);
    return response.data;
  },
};
