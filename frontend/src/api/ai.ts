/**
 * AI Insights API Client
 *
 * Provides AI-powered analysis of insider trading data using Gemini/OpenAI.
 */

import apiClient from './client';

const AI_BASE = '/api/v1/ai';

export interface AIStatus {
  enabled: boolean;
  available: boolean;
  providers: {
    primary: string;
    gemini: {
      configured: boolean;
      model: string | null;
    };
    openai: {
      configured: boolean;
      model: string | null;
    };
  };
  active_provider: string | null;
}

export interface CompanyAnalysis {
  ticker: string;
  company_name: string;
  days_analyzed: number;
  total_trades: number;
  analysis: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  insights: string[];
}

export interface TopTrade {
  ticker: string;
  company: string;
  insider: string;
  role: string;
  type: string;
  shares: number;
  value: number;
  date: string;
}

export interface CompanySummary {
  ticker: string;
  company_name: string;
  summary: string;
  total_value: number;
  trade_count: number;
  buy_count: number;
  sell_count: number;
  insider_count: number;
  latest_date: string;
}

export interface DailySummary {
  company_summaries: CompanySummary[];
  total_trades: number;
  generated_at: string;
  period: string;
  ai_overview?: string;
  diagnostics?: {
    total_trades_in_db?: number;
    trades_in_last_7_days?: number;
    trades_in_last_30_days?: number;
    days_back_configured?: number;
  };
}

export interface ChatResponse {
  question: string;
  answer: string;
  timestamp: string;
  response_metadata?: {
    provider?: string;
    response_length?: number;
    tokens_used?: number;
    max_tokens?: number;
    truncated?: boolean;
    safety_blocked?: boolean;
    finish_reason?: string;
    block_reason?: string;
    error?: boolean;
    errors?: string[];
  };
}

export interface TradingSignal {
  ticker: string;
  company_name: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  strength: 'STRONG' | 'MODERATE' | 'WEAK';
  trade_count: number;
  total_trades?: number;
  buy_volume: number;
  sell_volume: number;
  buy_ratio: number;
  total_value: number;
  reasoning?: string;
  timestamp?: string;
}

export interface TradingSignalsResponse {
  signals: TradingSignal[];
  generated_at: string;
  period: string;
  days_analyzed?: number;
  timestamp?: string;
  message?: string;
  diagnostics?: {
    total_trades_in_db?: number;
    trades_in_last_7_days?: number;
    trades_in_last_30_days?: number;
    companies_with_trades?: number;
    companies_meeting_criteria?: number;
    companies_below_threshold?: number;
    days_back_configured?: number;
  };
}

export interface PricePrediction {
  timeframe: string;
  target_price: number;
  upside_pct: number;
  probability: number;
}

export interface PricePredictionResponse {
  ticker: string;
  company_name: string;
  analysis: string;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  price_predictions: PricePrediction[];
  recommendation: 'BUY' | 'HOLD' | 'SELL' | 'STRONG_BUY' | 'STRONG_SELL';
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
  insights: string[];
  catalysts?: string[];
  risks?: string[];
  disclaimer: string;
}

export const aiApi = {
  /**
   * Check AI service status and availability
   */
  async getStatus(): Promise<AIStatus> {
    const response = await apiClient.get<AIStatus>(`${AI_BASE}/status`);
    return response.data;
  },

  /**
   * Get AI analysis for a specific company
   */
  async analyzeCompany(ticker: string, daysBack: number = 30): Promise<CompanyAnalysis> {
    const response = await apiClient.get<CompanyAnalysis>(
      `${AI_BASE}/analyze/${ticker}`,
      { params: { days_back: daysBack } }
    );
    return response.data;
  },

  /**
   * Get daily summary of top insider trades
   */
  async getDailySummary(): Promise<DailySummary> {
    const response = await apiClient.get<DailySummary>(`${AI_BASE}/summary/daily`);
    return response.data;
  },

  /**
   * Ask a question about insider trading data
   */
  async askQuestion(question: string): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      `${AI_BASE}/ask`,
      { question }
    );
    return response.data;
  },

  /**
   * Get AI-generated trading signals
   */
  async getTradingSignals(): Promise<TradingSignalsResponse> {
    const response = await apiClient.get<TradingSignalsResponse>(`${AI_BASE}/signals`);
    return response.data;
  },

  /**
   * Get AI price predictions for a stock
   *
   * Combines insider trading patterns, technical indicators, fundamental metrics,
   * news sentiment, and analyst ratings for comprehensive stock prediction
   */
  async getPricePrediction(ticker: string): Promise<PricePredictionResponse> {
    const response = await apiClient.get<PricePredictionResponse>(
      `${AI_BASE}/predict/${ticker}`
    );
    return response.data;
  },
};
