import apiClient from './client';
import { Company, PaginatedResponse, CompanyFilters, CompanyStats, Trade } from '../types';

export const companiesApi = {
  // Get all companies
  getCompanies: async (filters?: CompanyFilters): Promise<PaginatedResponse<Company>> => {
    console.log('[companiesApi] Fetching companies with filters:', filters);
    const response = await apiClient.get('/api/v1/companies/', { params: filters });
    console.log('[companiesApi] Response:', {
      status: response.status,
      itemsCount: response.data?.items?.length || 0,
      total: response.data?.total || 0,
    });
    return response.data;
  },

  // Fetch all companies across pages (limited to API max 100 per page)
  getAllCompanies: async (): Promise<Company[]> => {
    const perPage = 100;
    let page = 1;
    let hasNext = true;
    const results: Company[] = [];

    while (hasNext) {
      const response = await apiClient.get<PaginatedResponse<Company>>('/api/v1/companies/', {
        params: { limit: perPage, page },
      });

      results.push(...(response.data?.items ?? []));
      hasNext = response.data?.has_next ?? false;

      if (!hasNext || (response.data?.items?.length ?? 0) === 0) {
        break;
      }

      page += 1;

      // Safety break to avoid infinite loops if API misbehaves
      if (page > 25) {
        console.warn('[companiesApi] Reached pagination safety limit while fetching companies');
        break;
      }
    }

    console.log('[companiesApi] Loaded companies:', results.length);
    return results;
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
