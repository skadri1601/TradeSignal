import apiClient from './client';

export interface FedEvent {
  date: string;
  type: string;
  description: string;
  importance: string;
  expected_outcome?: string;
  days_until: number;
}

export interface FedCalendarResponse {
  events: FedEvent[];
  count: number;
  months_ahead: number;
}

export interface InterestRate {
  rate: number;
  date: string;
  unit: string;
  description: string;
}

export interface RateHistoryPoint {
  date: string;
  rate: number;
  unit: string;
}

export interface RateHistoryResponse {
  history: RateHistoryPoint[];
  count: number;
  days_back: number;
}

export interface EconomicIndicator {
  value: number | null;
  date: string;
  series_id: string;
}

export interface EconomicIndicatorsResponse {
  indicators: {
    inflation?: EconomicIndicator;
    unemployment?: EconomicIndicator;
    gdp?: EconomicIndicator;
    retail_sales?: EconomicIndicator;
  };
  last_updated: string;
}

export const fedApi = {
  /**
   * Get FED calendar with upcoming meetings and data releases
   */
  getCalendar: async (monthsAhead: number = 6): Promise<FedCalendarResponse> => {
    const response = await apiClient.get<FedCalendarResponse>('/api/v1/fed/calendar', {
      params: { months_ahead: monthsAhead },
    });
    return response.data;
  },

  /**
   * Get current Federal Reserve interest rate
   */
  getInterestRate: async (): Promise<InterestRate> => {
    const response = await apiClient.get<InterestRate>('/api/v1/fed/interest-rate');
    return response.data;
  },

  /**
   * Get interest rate history
   */
  getRateHistory: async (daysBack: number = 365): Promise<RateHistoryResponse> => {
    const response = await apiClient.get<RateHistoryResponse>('/api/v1/fed/rate-history', {
      params: { days_back: daysBack },
    });
    return response.data;
  },

  /**
   * Get economic indicators (inflation, unemployment, GDP, retail sales)
   */
  getEconomicIndicators: async (): Promise<EconomicIndicatorsResponse> => {
    const response = await apiClient.get<EconomicIndicatorsResponse>('/api/v1/fed/economic-indicators');
    return response.data;
  },
};

