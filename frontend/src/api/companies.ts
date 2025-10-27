import apiClient from './client';
import { Company, PaginatedResponse, CompanyFilters, CompanyStats, Trade } from '../types';

export const companiesApi = {
  // Get all companies
  getCompanies: async (filters?: CompanyFilters): Promise<PaginatedResponse<Company>> => {
    const response = await apiClient.get('/api/v1/companies/', { params: filters });
    return response.data;
  },

  // Get single company by ticker
  getCompany: async (ticker: string): Promise<Company> => {
    const response = await apiClient.get(`/api/v1/companies/${ticker}`);
    return response.data;
  },

  // Get company trades
  getCompanyTrades: async (ticker: string, limit: number = 20): Promise<Trade[]> => {
    const response = await apiClient.get(`/api/v1/companies/${ticker}/trades`, { params: { limit } });
    // API returns a paginated response; unwrap items for convenience on detail page
    return response.data?.items ?? [];
  },

  // Get company statistics
  getCompanyStats: async (): Promise<CompanyStats> => {
    const response = await apiClient.get('/api/v1/companies/stats');
    return response.data;
  },
};
