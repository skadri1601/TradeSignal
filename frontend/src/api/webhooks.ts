/**
 * Webhooks API Client
 *
 * Provides TypeScript methods to interact with the Webhooks API endpoints.
 * Handles webhook creation, management, delivery history, and testing.
 */

import apiClient from './client';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface Webhook {
  id: number;
  url: string;
  event_types: string[];
  is_active: boolean;
  created_at: string;
}

export interface WebhookDelivery {
  id: number;
  event_type: string;
  status: string;
  response_code?: number;
  attempts: number;
  delivered_at?: string;
  created_at: string;
}

export interface CreateWebhookRequest {
  url: string;
  event_types?: string[];
  secret?: string;
}

export interface TestWebhookResponse {
  delivery_id: number;
  status: string;
  response_code?: number;
}

// ============================================================================
// API CLIENT
// ============================================================================

/**
 * Webhooks API - Provides methods to interact with webhook endpoints
 */
export const webhooksApi = {
  /**
   * Get all webhooks for the current user
   */
  getWebhooks: async (): Promise<Webhook[]> => {
    const response = await apiClient.get<Webhook[]>('/api/v1/webhooks');
    return response.data;
  },

  /**
   * Create a new webhook endpoint
   * Event types: trade_alert, conversion, subscription_updated, user_signed_up, custom
   */
  createWebhook: async (webhook: CreateWebhookRequest): Promise<Webhook> => {
    const response = await apiClient.post<Webhook>('/api/v1/webhooks', webhook);
    return response.data;
  },

  /**
   * Get delivery history for a webhook
   */
  getDeliveries: async (
    webhookId: number,
    params?: {
      status?: string;
      limit?: number;
    }
  ): Promise<WebhookDelivery[]> => {
    const response = await apiClient.get<WebhookDelivery[]>(
      `/api/v1/webhooks/${webhookId}/deliveries`,
      { params }
    );
    return response.data;
  },

  /**
   * Send a test webhook event
   */
  testWebhook: async (webhookId: number): Promise<TestWebhookResponse> => {
    const response = await apiClient.post<TestWebhookResponse>(
      `/api/v1/webhooks/${webhookId}/test`
    );
    return response.data;
  },
};

