/**
 * Stock Prices API Client
 *
 * Provides access to live stock prices via Yahoo Finance integration.
 */

import apiClient from './client';

const STOCKS_BASE = '/api/v1/stocks';

export interface StockQuote {
  ticker: string;
  company_name?: string;
  current_price: number;
  previous_close: number;
  price_change: number;
  price_change_percent: number;
  market_cap?: number;
  volume?: number;
  avg_volume?: number;
  day_high?: number;
  day_low?: number;
  fifty_two_week_high?: number;
  fifty_two_week_low?: number;
  market_state: string;
  updated_at: string;
}

export interface PriceHistoryPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export const stocksApi = {
  /**
   * Get current stock quote for a single ticker
   */
  getQuote: async (ticker: string): Promise<StockQuote> => {
    const response = await apiClient.get<StockQuote>(`${STOCKS_BASE}/quote/${ticker}`);
    return response.data;
  },

  /**
   * Get quotes for multiple tickers
   */
  getMultipleQuotes: async (tickers: string[]): Promise<StockQuote[]> => {
    const tickersParam = tickers.join(',');
    const response = await apiClient.get<StockQuote[]>(`${STOCKS_BASE}/quotes`, {
      params: { tickers: tickersParam },
    });
    return response.data;
  },

  /**
   * Get market overview - live prices for companies with recent insider trading activity
   * @param limit - Optional limit on number of companies (default: all)
   */
  getMarketOverview: async (limit?: number): Promise<StockQuote[]> => {
    const response = await apiClient.get<StockQuote[]>(`${STOCKS_BASE}/market-overview`, {
      params: limit ? { limit } : {},
    });
    return response.data;
  },

  /**
   * Get historical price data for a ticker
   */
  getPriceHistory: async (ticker: string, days: number = 30): Promise<PriceHistoryPoint[]> => {
    const response = await apiClient.get<PriceHistoryPoint[]>(`${STOCKS_BASE}/history/${ticker}`, {
      params: { days },
    });
    return response.data;
  },
};
