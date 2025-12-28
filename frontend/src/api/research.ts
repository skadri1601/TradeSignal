import apiClient from './client';

export interface IVTData {
  ticker: string;
  intrinsic_value: number;
  current_price: number;
  discount_pct: number;
  calculation_date: string;
  confidence_score?: number;
  wacc?: number;
  terminal_growth_rate?: number;
  cached: boolean;
}

export interface TSScoreData {
  ticker: string;
  score: number;
  rating: string;
  price_to_ivt_ratio?: number;
  risk_adjusted: boolean;
  calculation_date?: string;
  cached: boolean;
}

export interface RiskLevelData {
  ticker: string;
  level: string;
  category: string;
  volatility_score?: number;
  assessment_date?: string;
  components: {
    earnings_volatility?: number;
    financial_leverage?: number;
    operating_leverage?: number;
    concentration_risk?: number;
    industry_stability?: number;
  };
  cached: boolean;
}

export interface CompetitiveStrengthData {
  ticker: string;
  rating: string;
  trajectory: string;
  composite_score?: number;
  moat_sources: {
    network_effects?: number;
    intangible_assets?: number;
    cost_advantages?: number;
    switching_costs?: number;
    efficient_scale?: number;
  };
  rating_date?: string;
  cached: boolean;
}

export interface ManagementScoreData {
  ticker: string;
  grade: string;
  composite_score?: number;
  components: {
    ma_track_record?: number;
    capital_discipline?: number;
    shareholder_returns?: number;
    financial_leverage?: number;
    governance?: number;
  };
  scoring_date?: string;
  cached: boolean;
}

export interface FullResearchReport {
  ticker: string;
  report_date?: string;
  ivt?: IVTData;
  ts_score?: TSScoreData;
  risk_level?: RiskLevelData;
  competitive_strength?: CompetitiveStrengthData;
  management_score?: ManagementScoreData;
}

export const researchApi = {
  /**
   * Get Intrinsic Value Target (IVT) for a stock
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getIVT: async (ticker: string): Promise<IVTData | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/ivt`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get TradeSignal Score (TS Score) for a stock
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getTSScore: async (ticker: string): Promise<TSScoreData | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/ts-score`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get Risk Level Assessment for a stock
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getRiskLevel: async (ticker: string): Promise<RiskLevelData | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/risk-level`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get Competitive Strength Rating for a stock
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getCompetitiveStrength: async (ticker: string): Promise<CompetitiveStrengthData | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/competitive-strength`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get Management Excellence Score for a stock
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getManagementScore: async (ticker: string): Promise<ManagementScoreData | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/management-score`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get full research report with all scores
   * Returns null if data is not available (404) - this is expected for companies without coverage
   */
  getFullReport: async (ticker: string): Promise<FullResearchReport | null> => {
    try {
      const response = await apiClient.get(`/api/research/${ticker}/full-report`);
      return response.data;
    } catch (error: any) {
      // Silently return null for 404s (expected when data not available)
      if (error.response?.status === 404) {
        return null;
      }
      // Re-throw other errors
      throw error;
    }
  },

  /**
   * Get list of tickers with research coverage
   */
  getCoverage: async (): Promise<{
    total_coverage: number;
    tickers: string[];
    coverage_types: {
      ivt: number;
      ts_score: number;
    };
  }> => {
    const response = await apiClient.get('/api/research/coverage');
    return response.data;
  },
};

export default researchApi;
