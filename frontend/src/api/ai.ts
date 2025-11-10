/**
 * AI Insights API Client
 *
 * Provides AI-powered analysis of insider trading data using Gemini/OpenAI.
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const AI_BASE = `${API_URL}/api/v1/ai`;

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
}

export interface ChatResponse {
  question: string;
  answer: string;
  timestamp: string;
}

export interface TradingSignal {
  ticker: string;
  company_name: string;
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  strength: 'STRONG' | 'MODERATE' | 'WEAK';
  trade_count: number;
  buy_volume: number;
  sell_volume: number;
  buy_ratio: number;
  total_value: number;
  reasoning?: string;
}

export interface TradingSignalsResponse {
  signals: TradingSignal[];
  generated_at: string;
  period: string;
  message?: string;
}

export const aiApi = {
  /**
   * Check AI service status and availability
   */
  async getStatus(): Promise<AIStatus> {
    const response = await axios.get<AIStatus>(`${AI_BASE}/status`);
    return response.data;
  },

  /**
   * Get AI analysis for a specific company
   */
  async analyzeCompany(ticker: string, daysBack: number = 30): Promise<CompanyAnalysis> {
    const response = await axios.get<CompanyAnalysis>(
      `${AI_BASE}/analyze/${ticker}`,
      { params: { days_back: daysBack } }
    );
    return response.data;
  },

  /**
   * Get daily summary of top insider trades
   */
  async getDailySummary(): Promise<DailySummary> {
    const response = await axios.get<DailySummary>(`${AI_BASE}/summary/daily`);
    return response.data;
  },

  /**
   * Ask a question about insider trading data
   */
  async askQuestion(question: string): Promise<ChatResponse> {
    const response = await axios.post<ChatResponse>(
      `${AI_BASE}/ask`,
      { question }
    );
    return response.data;
  },

  /**
   * Get AI-generated trading signals
   */
  async getTradingSignals(): Promise<TradingSignalsResponse> {
    const response = await axios.get<TradingSignalsResponse>(`${AI_BASE}/signals`);
    return response.data;
  },
};
