// API constants
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// Transaction types
export const TRANSACTION_TYPES = {
  BUY: 'BUY',
  SELL: 'SELL',
} as const;

// Transaction codes and their descriptions
export const TRANSACTION_CODES: Record<string, string> = {
  P: 'Purchase',
  S: 'Sale',
  A: 'Award',
  M: 'Exercise',
  F: 'Tax Payment',
  G: 'Gift',
  D: 'Disposition',
  I: 'Discretionary',
  W: 'Inheritance',
  X: 'Exercise Out-of-the-Money',
  C: 'Conversion',
  J: 'Other',
};

// Chart colors
export const COLORS = {
  BUY: '#10B981', // green
  SELL: '#EF4444', // red
  PRIMARY: '#3B82F6', // blue
  SECONDARY: '#6B7280', // gray
};

// Date range presets
export const DATE_RANGES = [
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 30 days', days: 30 },
  { label: 'Last 90 days', days: 90 },
  { label: 'Last 365 days', days: 365 },
  { label: 'All time', days: null },
];

// Significant trade threshold (in USD)
// NOTE: This value matches backend default (SIGNIFICANT_TRADE_THRESHOLD env var)
// Backend can override via environment variable
export const SIGNIFICANT_TRADE_THRESHOLD = 100_000;
