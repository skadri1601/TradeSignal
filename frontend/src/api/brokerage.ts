/**
 * Brokerage API Client
 *
 * Provides TypeScript methods to interact with the Brokerage API endpoints.
 * Handles OAuth flows, account management, copy trade rules, and trade execution.
 */

import apiClient from './client';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export type BrokerType = 'alpaca' | 'td_ameritrade' | 'interactive_brokers';
export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';
export type TimeInForce = 'day' | 'gtc' | 'ioc' | 'fok';
export type RuleConditionField =
  | 'transaction_type'
  | 'security_type'
  | 'share_volume'
  | 'transaction_value'
  | 'ticker'
  | 'insider_title'
  | 'company_sector';
export type RuleConditionOperator =
  | 'equals'
  | 'not_equals'
  | 'greater_than'
  | 'less_than'
  | 'contains'
  | 'in';

export interface RuleCondition {
  field: RuleConditionField;
  operator: RuleConditionOperator;
  value: any;
}

export interface BrokerageAccount {
  id: number;
  user_id: number;
  broker: string;
  account_number: string;
  account_name?: string;
  is_active: boolean;
  balance?: number;
  buying_power?: number;
  portfolio_value?: number;
  last_synced_at?: string;
  connected_at: string;
  created_at: string;
  updated_at?: string;
}

export interface CopyTradeRule {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  brokerage_account_id: number;
  brokerage_account_name?: string;
  is_active: boolean;
  conditions: RuleCondition[];
  copy_percentage: number;
  max_position_size?: number;
  order_type: string;
  time_in_force: string;
  trades_executed: number;
  total_volume: number;
  last_executed_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ExecutedTrade {
  id: number;
  rule_id: number;
  rule_name: string;
  user_id: number;
  brokerage_account_id: number;
  insider_trade_id: number;
  ticker: string;
  side: string;
  quantity: number;
  order_type: string;
  limit_price?: number;
  stop_price?: number;
  filled_quantity?: number;
  filled_price?: number;
  status: string; // pending, filled, partial, cancelled, failed
  broker_order_id?: string;
  execution_time?: string;
  error_message?: string;
  created_at: string;
}

export interface OAuthAuthorizationResponse {
  authorization_url: string;
  state: string;
}

export interface OAuthCallbackResponse {
  success: boolean;
  account_id: number;
  broker: string;
  account_number: string;
  message: string;
}

export interface BrokerPosition {
  ticker: string;
  quantity: number;
  market_value: number;
  cost_basis: number;
  unrealized_pl: number;
  unrealized_pl_pct: number;
  current_price: number;
}

export interface BrokerOrder {
  broker_order_id: string;
  ticker: string;
  side: string;
  quantity: number;
  order_type: string;
  status: string;
  filled_quantity?: number;
  filled_price?: number;
  created_at: string;
  updated_at?: string;
}

export interface BrokerAccountSummary {
  account: BrokerageAccount;
  positions: BrokerPosition[];
  recent_orders: BrokerOrder[];
  total_positions: number;
  total_market_value: number;
  total_unrealized_pl: number;
  cash_balance: number;
}

export interface CopyTradeRuleCreate {
  name: string;
  description?: string;
  brokerage_account_id: number;
  is_active?: boolean;
  conditions: RuleCondition[];
  copy_percentage: number;
  max_position_size?: number;
  order_type?: OrderType;
  time_in_force?: TimeInForce;
}

export interface CopyTradeRuleUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
  conditions?: RuleCondition[];
  copy_percentage?: number;
  max_position_size?: number;
  order_type?: OrderType;
  time_in_force?: TimeInForce;
}

export interface ManualTradeRequest {
  brokerage_account_id: number;
  ticker: string;
  side: OrderSide;
  quantity: number;
  order_type?: OrderType;
  limit_price?: number;
  stop_price?: number;
  time_in_force?: TimeInForce;
}

// ============================================================================
// API CLIENT
// ============================================================================

/**
 * Brokerage API - Provides methods to interact with brokerage endpoints
 */
export const brokerageApi = {
  // =========================================================================
  // OAUTH ENDPOINTS
  // =========================================================================

  /**
   * Initiate OAuth connection to a broker
   * Returns authorization URL for user to complete OAuth flow
   */
  connectBroker: async (
    broker: BrokerType,
    redirectUri?: string
  ): Promise<OAuthAuthorizationResponse> => {
    const params = redirectUri ? { redirect_uri: redirectUri } : {};
    const response = await apiClient.get<OAuthAuthorizationResponse>(
      `/api/v1/brokerage/connect/${broker}`,
      { params }
    );
    return response.data;
  },

  /**
   * Handle OAuth callback from broker
   * This is typically called by the broker after user authorizes
   */
  handleCallback: async (
    broker: BrokerType,
    code: string,
    state: string,
    redirectUri?: string
  ): Promise<OAuthCallbackResponse> => {
    const params: any = { code, state };
    if (redirectUri) params.redirect_uri = redirectUri;
    const response = await apiClient.get<OAuthCallbackResponse>(
      `/api/v1/brokerage/callback/${broker}`,
      { params }
    );
    return response.data;
  },

  /**
   * Disconnect a brokerage account
   * Revokes OAuth tokens and deactivates the account
   */
  disconnectBroker: async (accountId: number): Promise<void> => {
    await apiClient.post('/api/v1/brokerage/disconnect', { account_id: accountId });
  },

  // =========================================================================
  // ACCOUNT ENDPOINTS
  // =========================================================================

  /**
   * Get all brokerage accounts for the current user
   */
  getAccounts: async (): Promise<BrokerageAccount[]> => {
    const response = await apiClient.get<BrokerageAccount[]>(
      '/api/v1/brokerage/accounts'
    );
    return response.data;
  },

  /**
   * Get detailed account information including positions and recent orders
   */
  getAccountDetails: async (accountId: number): Promise<BrokerAccountSummary> => {
    const response = await apiClient.get<BrokerAccountSummary>(
      `/api/v1/brokerage/accounts/${accountId}`
    );
    return response.data;
  },

  /**
   * Manually sync account data from broker API
   * Updates balance, buying power, and portfolio value
   */
  syncAccount: async (accountId: number): Promise<BrokerageAccount> => {
    const response = await apiClient.post<BrokerageAccount>(
      `/api/v1/brokerage/accounts/${accountId}/sync`
    );
    return response.data;
  },

  // =========================================================================
  // COPY TRADE RULES ENDPOINTS
  // =========================================================================

  /**
   * Get all copy trade rules for the current user
   */
  getRules: async (): Promise<CopyTradeRule[]> => {
    const response = await apiClient.get<CopyTradeRule[]>('/api/v1/brokerage/rules');
    return response.data;
  },

  /**
   * Create a new copy trade rule
   */
  createRule: async (rule: CopyTradeRuleCreate): Promise<CopyTradeRule> => {
    const response = await apiClient.post<CopyTradeRule>(
      '/api/v1/brokerage/rules',
      rule
    );
    return response.data;
  },

  /**
   * Update an existing copy trade rule
   */
  updateRule: async (
    ruleId: number,
    updates: CopyTradeRuleUpdate
  ): Promise<CopyTradeRule> => {
    const response = await apiClient.put<CopyTradeRule>(
      `/api/v1/brokerage/rules/${ruleId}`,
      updates
    );
    return response.data;
  },

  /**
   * Delete a copy trade rule
   */
  deleteRule: async (ruleId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/brokerage/rules/${ruleId}`);
  },

  /**
   * Toggle a copy trade rule active/inactive status
   */
  toggleRule: async (ruleId: number): Promise<{ success: boolean; is_active: boolean; message: string }> => {
    const response = await apiClient.post<{ success: boolean; is_active: boolean; message: string }>(
      `/api/v1/brokerage/rules/${ruleId}/toggle`
    );
    return response.data;
  },

  // =========================================================================
  // EXECUTED TRADES ENDPOINTS
  // =========================================================================

  /**
   * Get executed trades for the current user
   */
  getTrades: async (params?: {
    rule_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<ExecutedTrade[]> => {
    const response = await apiClient.get<ExecutedTrade[]>('/api/v1/brokerage/trades', {
      params,
    });
    return response.data;
  },

  /**
   * Get details of a specific executed trade
   */
  getTradeDetails: async (tradeId: number): Promise<ExecutedTrade> => {
    const response = await apiClient.get<ExecutedTrade>(
      `/api/v1/brokerage/trades/${tradeId}`
    );
    return response.data;
  },

  /**
   * Place a manual trade through connected broker
   * Bypasses copy trade rules for manual execution
   */
  placeManualTrade: async (trade: ManualTradeRequest): Promise<ExecutedTrade> => {
    const response = await apiClient.post<ExecutedTrade>(
      '/api/v1/brokerage/manual-trade',
      trade
    );
    return response.data;
  },
};

