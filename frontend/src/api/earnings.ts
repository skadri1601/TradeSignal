import apiClient from './client';

export interface EarningsData {
  ticker: string;
  company_name: string;
  earnings_history: Array<{
    date: string;
    estimate: number | null;
    actual: number | null;
    surprise: number | null;
  }>;
  upcoming_earnings: Array<{
    date: string;
    type?: string;
    estimate?: any;
    days_until: number;
  }>;
  next_earnings_date: string | null;
  earnings_surprises?: Array<any>;
  last_updated?: string;
}

export interface EarningsCalendar {
  ticker: string;
  company_name: string;
  earnings_date: string;
  eps_estimate?: number;
  revenue_estimate?: number;
}

export const earningsApi = {
  // Get earnings data for a specific company
  getCompanyEarnings: async (ticker: string, quarters: number = 8): Promise<EarningsData> => {
    const response = await apiClient.get(`/api/v1/earnings/company/${ticker}`, {
      params: { quarters },
    });
    return response.data;
  },

  // Get earnings calendar
  getEarningsCalendar: async (
    daysAhead: number = 30,
    limit: number = 100
  ): Promise<{ earnings: EarningsCalendar[]; count: number; days_ahead: number }> => {
    const response = await apiClient.get('/api/v1/earnings/calendar', {
      params: { days_ahead: daysAhead, limit },
    });
    return response.data;
  },
};

