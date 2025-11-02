import apiClient from "./client";
import {
  Alert,
  AlertHistory,
  AlertStats,
  PaginatedResponse,
  AlertFilters,
} from "../types";

export const alertsApi = {
  // Get all alerts with filters
  getAlerts: async (
    filters?: AlertFilters
  ): Promise<PaginatedResponse<Alert>> => {
    const response = await apiClient.get("/api/v1/alerts/", {
      params: filters,
    });
    return response.data;
  },

  // Get single alert by ID
  getAlert: async (id: number): Promise<Alert> => {
    const response = await apiClient.get(`/api/v1/alerts/${id}`);
    return response.data;
  },

  // Create a new alert
  createAlert: async (alertData: Partial<Alert>): Promise<Alert> => {
    const response = await apiClient.post("/api/v1/alerts/", alertData);
    return response.data;
  },

  // Update an existing alert
  updateAlert: async (
    id: number,
    alertData: Partial<Alert>
  ): Promise<Alert> => {
    const response = await apiClient.patch(`/api/v1/alerts/${id}`, alertData);
    return response.data;
  },

  // Delete an alert
  deleteAlert: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/v1/alerts/${id}`);
  },

  // Toggle an alert's active status
  toggleAlert: async (id: number, is_active: boolean): Promise<Alert> => {
    const response = await apiClient.post(`/api/v1/alerts/${id}/toggle`, {
      is_active,
    });
    return response.data;
  },

  // Send a test notification for an alert
  testAlert: async (id: number): Promise<{ message: string }> => {
    const response = await apiClient.post(`/api/v1/alerts/${id}/test`);
    return response.data;
  },

  // Get alert trigger history
  getAlertHistory: async (
    alertId?: number
  ): Promise<PaginatedResponse<AlertHistory>> => {
    const params = alertId ? { alert_id: alertId } : {};
    const response = await apiClient.get("/api/v1/alerts/history/", {
      params,
    });
    return response.data;
  },

  // Get alert statistics
  getAlertStats: async (): Promise<AlertStats> => {
    const response = await apiClient.get("/api/v1/alerts/stats/");
    return response.data;
  },
};