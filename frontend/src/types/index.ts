// Base types for the application

// Congressional Trading Types (Phase 7)
export interface Congressperson {
  id: number;
  name: string;
  first_name: string | null;
  last_name: string;
  chamber: 'HOUSE' | 'SENATE';
  state: string;
  district: string | null;
  party: 'DEMOCRAT' | 'REPUBLICAN' | 'INDEPENDENT' | 'OTHER';
  display_name: string;
  party_abbrev: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CongressionalTrade {
  id: number;
  congressperson_id: number;
  company_id: number | null;
  transaction_date: string;
  disclosure_date: string;
  transaction_type: 'BUY' | 'SELL';
  ticker: string | null;
  asset_description: string;
  amount_min: number | null;
  amount_max: number | null;
  amount_estimated: number | null;
  is_range_estimate: boolean;
  owner_type: string;
  asset_type: string | null;
  disclosure_url: string | null;
  source: string;
  is_buy: boolean;
  is_sell: boolean;
  is_significant: boolean;
  filing_delay_days: number | null;
  estimated_value: number | null;
  amount_range_display: string;
  created_at: string;
  updated_at: string;
  // Optional nested details
  congressperson?: Congressperson;
  company?: Company;
}

export interface CongressionalTradeFilters {
  congressperson_id?: number;
  company_id?: number;
  ticker?: string;
  chamber?: 'HOUSE' | 'SENATE';
  state?: string;
  party?: string;
  transaction_type?: 'BUY' | 'SELL';
  owner_type?: string;
  transaction_date_from?: string;
  transaction_date_to?: string;
  min_value?: number;
  max_value?: number;
  significant_only?: boolean;
  page?: number;
  limit?: number;
}

export interface CongressionalTradeStats {
  total_trades: number;
  total_buys: number;
  total_sells: number;
  total_value: number;
  total_buy_value: number;
  total_sell_value: number;
  average_trade_size: number;
  largest_trade: number | null;
  most_active_congressperson: string | null;
  most_active_company: string | null;
  house_trade_count: number;
  senate_trade_count: number;
  democrat_buy_count: number;
  democrat_sell_count: number;
  republican_buy_count: number;
  republican_sell_count: number;
}

export interface Company {
  id: number;
  ticker: string;
  name: string;
  cik: string;
  sector: string | null;
  industry: string | null;
  market_cap: number | null;
  website: string | null;
  created_at: string;
  updated_at: string;
}

export interface Insider {
  id: number;
  name: string;
  title: string | null;
  company_id: number;
  is_director: boolean;
  is_officer: boolean;
  is_ten_percent_owner: boolean;
  is_other: boolean;
  primary_role: string;
  roles: string[];
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: number;
  insider_id: number;
  company_id: number;
  transaction_date: string;
  filing_date: string;
  transaction_type: 'BUY' | 'SELL';
  transaction_code: string;
  shares: string;
  price_per_share: string | null;
  total_value: string | null;
  shares_owned_after: string;
  ownership_type: 'Direct' | 'Indirect';
  derivative_transaction: boolean;
  sec_filing_url: string;
  form_type: string;
  notes: string | null;
  is_buy: boolean;
  is_sell: boolean;
  is_significant: boolean;
  filing_delay_days: number;
  created_at: string;
  updated_at: string;
  // Optional nested details returned by API
  company?: Company;
  insider?: Insider;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TradeStats {
  total_trades: number;
  total_buys: number;
  total_sells: number;
  total_shares_traded: number;
  total_value: number;
  total_buy_value: number;
  total_sell_value: number;
  average_trade_size: number;
  largest_trade: number | null;
  most_active_company: string | null;
  most_active_insider: string | null;
}

export interface CompanyStats {
  total_companies: number;
  companies_by_sector: Record<string, number>;
  avg_market_cap: number;
}

// Filter types
export interface TradeFilters {
  ticker?: string;
  insider_id?: number;
  transaction_type?: 'BUY' | 'SELL';
  min_value?: number;
  max_value?: number;
  transaction_date_from?: string;
  transaction_date_to?: string;
  page?: number;
  limit?: number;
}

export interface CompanyFilters {
  sector?: string;
  industry?: string;
  min_market_cap?: number;
  max_market_cap?: number;
  page?: number;
  limit?: number;
}

// API Error type
export interface APIError {
  error: string;
  status_code: number;
  timestamp: string;
  path: string;
}

export type AlertType = "large_trade" | "company_watch" | "insider_role" | "volume_spike";
export type NotificationChannel = "webhook" | "email" | "push" | "discord" | "slack" | "sms";

export interface Alert {
  id: number;
  name: string;
  alert_type: AlertType;
  ticker: string | null;
  min_value: number | null;
  max_value: number | null;
  transaction_type: "BUY" | "SELL" | null;
  insider_roles: string[];
  notification_channels: NotificationChannel[];
  webhook_url: string | null;
  email: string | null;
  discord_webhook_url: string | null;
  slack_webhook_url: string | null;
  sms_phone_number: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertHistory {
  id: number;
  alert_id: number;
  trade_id: number;
  notification_channel: NotificationChannel;
  notification_status: "sent" | "failed" | "retrying";
  error_message: string | null;
  created_at: string;
}

export interface AlertStats {
  total_alerts: number;
  active_alerts: number;
  inactive_alerts: number;
  total_notifications_sent: number;
  notifications_last_24h: number;
  failed_notifications_last_24h: number;
}

export interface AlertFilters {
  is_active?: boolean;
  page?: number;
  limit?: number;
}

// News Types
export interface NewsArticle {
  id: number;
  headline: string;
  summary: string;
  source: string;
  datetime: number; // Unix timestamp
  url: string;
  image: string | null;
  category: string;
  related: string | null; // Comma-separated tickers
}

export interface NewsResponse {
  articles: NewsArticle[];
  total: number;
  limit: number;
}