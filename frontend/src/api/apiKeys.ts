/**
 * API Keys API Client
 *
 * Provides TypeScript methods to interact with the API Keys endpoints.
 * Handles API key creation, management, and usage tracking.
 */

import apiClient from './client';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface APIKey {
  id: number;
  name: string;
  description?: string;
  key_prefix: string;
  rate_limit_per_hour: number;
  can_read: boolean;
  can_write: boolean;
  can_delete: boolean;
  created_at: string;
  expires_at?: string;
  last_used_at?: string;
  is_active: boolean;
}

export interface APIKeyCreated {
  api_key: APIKey;
  key: string; // Plaintext key - shown only once!
}

export interface APIKeyUsageStats {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_response_time_ms: number;
  days: number;
}

export interface CreateAPIKeyRequest {
  name: string;
  description?: string;
  rate_limit_per_hour?: number;
  permissions?: {
    read?: boolean;
    write?: boolean;
    delete?: boolean;
  };
  expires_in_days?: number;
}

// ============================================================================
// API CLIENT
// ============================================================================

/**
 * API Keys API - Provides methods to interact with API key endpoints
 */
export const apiKeysApi = {
  /**
   * Get all API keys for the current user
   */
  getKeys: async (): Promise<APIKey[]> => {
    const response = await apiClient.get<APIKey[]>('/api/v1/enterprise/api-keys');
    return response.data;
  },

  /**
   * Create a new API key
   * Returns the plaintext key - save it securely, it's only shown once!
   */
  createKey: async (keyData: CreateAPIKeyRequest): Promise<APIKeyCreated> => {
    const response = await apiClient.post<APIKeyCreated>('/api/v1/enterprise/api-keys', keyData);
    return response.data;
  },

  /**
   * Revoke (deactivate) an API key
   */
  revokeKey: async (keyId: number): Promise<void> => {
    await apiClient.delete(`/api/v1/enterprise/api-keys/${keyId}`);
  },

  /**
   * Get usage statistics for an API key
   */
  getUsage: async (keyId: number, days: number = 30): Promise<APIKeyUsageStats> => {
    const response = await apiClient.get<APIKeyUsageStats>(
      `/api/v1/enterprise/api-keys/${keyId}/usage`,
      { params: { days } }
    );
    return response.data;
  },
};

