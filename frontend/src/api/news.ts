import apiClient from './client';
import { NewsResponse } from '../types';

export const newsApi = {
  // Get latest news
  getLatestNews: async (limit: number = 50): Promise<NewsResponse> => {
    const response = await apiClient.get('/api/v1/news/latest', {
      params: { limit },
    });
    return response.data;
  },

  // Get general market news
  getGeneralNews: async (limit: number = 50): Promise<NewsResponse> => {
    const response = await apiClient.get('/api/v1/news/general', {
      params: { limit },
    });
    return response.data;
  },

  // Get company-specific news
  getCompanyNews: async (ticker: string, limit: number = 50): Promise<NewsResponse> => {
    const response = await apiClient.get(`/api/v1/news/company/${ticker}`, {
      params: { limit },
    });
    return response.data;
  },

  // Get crypto news
  getCryptoNews: async (limit: number = 50): Promise<NewsResponse> => {
    const response = await apiClient.get('/api/v1/news/crypto', {
      params: { limit },
    });
    return response.data;
  },
};
