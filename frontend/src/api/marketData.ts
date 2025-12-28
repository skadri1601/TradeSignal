/**
 * Market Data API Client
 *
 * Provides access to market data from yfinance and Finnhub:
 * - Dividends, earnings, recommendations, financials (yfinance)
 * - Price targets, earnings surprises, IPO calendar, economic calendar (Finnhub)
 */

import apiClient from './client';

const MARKET_DATA_BASE = '/api/v1/market-data';

export interface Dividend {
  ex_date: string;
  amount: number;
}

export interface EarningsCalendar {
  earnings_date?: string;
  eps_estimate?: number;
  revenue_estimate?: number;
}

export interface RecommendationPeriod {
  period: string;
  strong_buy: number;
  buy: number;
  hold: number;
  sell: number;
  strong_sell: number;
}

export interface RecommendationsResponse {
  ticker: string;
  summary: {
    total_analysts: number;
    buy_percent: number;
    hold_percent: number;
    sell_percent: number;
  };
  history: RecommendationPeriod[];
}

export interface FinancialStatement {
  period_end: string;
  data: Record<string, number | string>;
}

export interface PriceTarget {
  target_high?: number;
  target_low?: number;
  target_mean?: number;
  target_median?: number;
  last_updated?: string;
}

export interface EarningsSurprise {
  period: string;
  actual: number;
  estimate: number;
  surprise: number;
  surprise_percent: number;
}

export interface IPOCalendarItem {
  symbol?: string;
  company_name: string;
  exchange?: string;
  ipo_date?: string;
  price_range?: string;
  shares?: number;
  status?: string;
}

export interface EconomicCalendarEvent {
  event: string;
  country: string;
  date?: string;
  time?: string;
  impact?: string;
  actual?: string;
  estimate?: string;
  previous?: string;
  unit?: string;
}

export interface StockOverview {
  ticker: string;
  earnings: EarningsCalendar;
  recommendations: {
    consensus?: string;
    total_analysts?: number;
  };
  price_target?: PriceTarget;
}

export const marketDataApi = {
  /**
   * Get dividend history for a stock (yfinance - no rate limit)
   */
  getDividends: async (ticker: string, refresh: boolean = false): Promise<{ ticker: string; dividends: Dividend[] }> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/dividends/${ticker}`, {
      params: { refresh },
    });
    return response.data;
  },

  /**
   * Get earnings calendar (next earnings date, estimates) (yfinance - no rate limit)
   */
  getEarningsCalendar: async (ticker: string, refresh: boolean = false): Promise<{ ticker: string } & EarningsCalendar> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/earnings-calendar/${ticker}`, {
      params: { refresh },
    });
    return response.data;
  },

  /**
   * Get analyst recommendations (buy/hold/sell) (yfinance - no rate limit)
   */
  getRecommendations: async (ticker: string, refresh: boolean = false): Promise<RecommendationsResponse> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/recommendations/${ticker}`, {
      params: { refresh },
    });
    return response.data;
  },

  /**
   * Get financial statements (income, balance, cashflow) (yfinance - no rate limit)
   */
  getFinancials: async (
    ticker: string,
    statement: 'income' | 'balance' | 'cashflow' = 'income',
    period: 'quarterly' | 'annual' = 'quarterly',
    refresh: boolean = false
  ): Promise<{ ticker: string; statement_type: string; period: string; statements: FinancialStatement[] }> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/financials/${ticker}`, {
      params: { statement, period, refresh },
    });
    return response.data;
  },

  /**
   * Get analyst price targets (Finnhub - rate limited, cached)
   */
  getPriceTarget: async (ticker: string, refresh: boolean = false): Promise<{ ticker: string } & PriceTarget> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/price-target/${ticker}`, {
      params: { refresh },
    });
    return response.data;
  },

  /**
   * Get earnings surprises (actual vs estimate) (Finnhub - rate limited, cached)
   */
  getEarningsSurprises: async (
    ticker: string,
    limit: number = 4,
    refresh: boolean = false
  ): Promise<{ ticker: string; earnings: EarningsSurprise[] }> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/earnings-surprises/${ticker}`, {
      params: { limit, refresh },
    });
    return response.data;
  },

  /**
   * Get IPO calendar (Finnhub - rate limited, cached)
   */
  getIpoCalendar: async (
    fromDate?: string,
    toDate?: string,
    refresh: boolean = false
  ): Promise<{ ipos: IPOCalendarItem[] }> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/ipo-calendar`, {
      params: { from_date: fromDate, to_date: toDate, refresh },
    });
    return response.data;
  },

  /**
   * Get economic calendar (Fed meetings, CPI, jobs, etc.) (Finnhub - rate limited, cached)
   */
  getEconomicCalendar: async (
    fromDate?: string,
    toDate?: string,
    refresh: boolean = false
  ): Promise<{ events: EconomicCalendarEvent[] }> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/economic-calendar`, {
      params: { from_date: fromDate, to_date: toDate, refresh },
    });
    return response.data;
  },

  /**
   * Get all market data for a stock in one call (combined endpoint)
   */
  getStockOverview: async (ticker: string): Promise<StockOverview> => {
    const response = await apiClient.get(`${MARKET_DATA_BASE}/stock-overview/${ticker}`);
    return response.data;
  },
};

