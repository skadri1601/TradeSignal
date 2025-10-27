import apiClient from './client';
import { Trade, PaginatedResponse, TradeFilters, TradeStats } from '../types';

export const tradesApi = {
  // Get all trades with filters
  getTrades: async (filters?: TradeFilters): Promise<PaginatedResponse<Trade>> => {
    const response = await apiClient.get('/api/v1/trades/', { params: filters });
    return response.data;
  },

  // Get single trade by ID
  getTrade: async (id: number): Promise<Trade> => {
    const response = await apiClient.get(`/api/v1/trades/${id}`);
    return response.data;
  },

  // Get recent trades
  getRecentTrades: async (days: number = 7): Promise<Trade[]> => {
    const response = await apiClient.get('/api/v1/trades/recent', { params: { days } });
    return response.data;
  },

  // Get trade statistics
  getTradeStats: async (filters?: TradeFilters): Promise<TradeStats> => {
    const response = await apiClient.get('/api/v1/trades/stats', { params: filters });
    return response.data;
  },
};
