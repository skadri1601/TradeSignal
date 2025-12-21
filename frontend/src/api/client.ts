import axios from 'axios';
import { getAccessToken } from '../contexts/AuthContext';

const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT ?? '60000'); // Reduced from 120s to 60s

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://api.tradesignal.capital',
  timeout: Number.isFinite(API_TIMEOUT) && API_TIMEOUT >= 0 ? API_TIMEOUT : 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to validate JWT token format
const isValidJWT = (token: string | null | undefined): boolean => {
  if (!token || typeof token !== 'string') {
    return false;
  }
  
  // JWT tokens have 3 parts separated by dots: header.payload.signature
  const parts = token.split('.');
  if (parts.length !== 3) {
    return false;
  }
  
  // Check that all parts are non-empty
  return parts.every(part => part.trim().length > 0);
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token to all requests only if token is valid
    const token = getAccessToken();
    if (token && isValidJWT(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // If token exists but is invalid, don't add it (let backend handle missing token)
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic for transient server errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Retry on 5xx server errors (transient failures)
    if (error.response?.status >= 500 && config) {
      // Initialize retry count
      config._retryCount = config._retryCount || 0;

      // Retry up to 2 times with exponential backoff
      if (config._retryCount < 2) {
        config._retryCount++;
        const delay = 1000 * config._retryCount; // 1s, then 2s
        console.warn(
          `Server error ${error.response.status}, retry ${config._retryCount}/2 in ${delay}ms...`
        );
        await new Promise((r) => setTimeout(r, delay));
        return apiClient(config);
      }
    }

    // Log errors after exhausting retries
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message, {
        baseURL: error.config?.baseURL,
        url: error.config?.url,
        timeout: error.config?.timeout,
      });
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
