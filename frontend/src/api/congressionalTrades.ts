import apiClient from './client';
import {
  PaginatedResponse,
  CongressionalTrade,
  CongressionalTradeFilters,
  CongressionalTradeStats,
} from '../types';

export const congressionalTradesApi = {
  getTrades: async (filters?: CongressionalTradeFilters): Promise<PaginatedResponse<CongressionalTrade>> => {
    const response = await apiClient.get('/api/v1/congressional-trades/', { params: filters });
    return response.data;
  },

  getTrade: async (id: number): Promise<CongressionalTrade> => {
    const response = await apiClient.get(`/api/v1/congressional-trades/${id}`);
    return response.data;
  },

  getRecentTrades: async (days: number = 7): Promise<CongressionalTrade[]> => {
    const response = await apiClient.get('/api/v1/congressional-trades/recent', { params: { days } });
    return response.data;
  },

  getTradeStats: async (filters?: CongressionalTradeFilters): Promise<CongressionalTradeStats> => {
    const response = await apiClient.get('/api/v1/congressional-trades/stats', { params: filters });
    return response.data;
  },

  triggerScrape: async (ticker?: string, chamber?: string, daysBack?: number) => {
    const response = await apiClient.post('/api/v1/congressional-trades/scrape', null, {
      params: { ticker, chamber, days_back: daysBack }
    });
    return response.data;
  },
};
