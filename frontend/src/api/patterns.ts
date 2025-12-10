import apiClient from './client';

export interface PatternAnalysis {
  ticker: string;
  company_name: string;
  days_analyzed: number;
  total_trades: number;
  pattern: string;
  trend: string;
  confidence: number;
  prediction: string;
  recommendation: string;
  risk_level: string;
  buy_ratio: number;
  sell_ratio: number;
  total_buy_value: number;
  total_sell_value: number;
  active_insiders: number;
}

export interface TopPatternCompany {
  ticker: string;
  company_name: string;
  pattern_score: number;
  pattern_details: string;
}

export const patternsApi = {
  // Analyze trading patterns for a specific company
  analyzeCompany: async (ticker: string, daysBack: number = 90): Promise<PatternAnalysis> => {
    const response = await apiClient.get(`/api/v1/patterns/analyze/${ticker}`, {
      params: { days_back: daysBack },
    });
    return response.data;
  },

  // Get top companies with specific trading patterns
  getTopPatterns: async (
    patternType: 'BUYING_MOMENTUM' | 'SELLING_PRESSURE' | 'CLUSTER' | 'REVERSAL',
    limit: number = 10
  ): Promise<{
    pattern_type: string;
    companies: TopPatternCompany[];
    count: number;
  }> => {
    const response = await apiClient.get(`/api/v1/patterns/top/${patternType}`, {
      params: { limit },
    });
    return response.data;
  },
};

