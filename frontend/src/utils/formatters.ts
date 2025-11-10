import { format, parseISO, formatDistanceToNow } from 'date-fns';

// Format currency
export const formatCurrency = (value: string | number | null): string => {
  if (value === null || value === undefined) return 'N/A';

  const num = typeof value === 'string' ? parseFloat(value) : value;

  if (isNaN(num)) return 'N/A';

  if (num >= 10000) {
    return '$' + formatCompactNumber(num);
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

// Format number with commas
export const formatNumber = (value: string | number | null): string => {
  if (value === null || value === undefined) return 'N/A';

  const num = typeof value === 'string' ? parseFloat(value) : value;

  if (isNaN(num)) return 'N/A';

  return new Intl.NumberFormat('en-US').format(num);
};

// Format date
export const formatDate = (dateString: string): string => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy');
  } catch {
    return dateString;
  }
};

// Format datetime
export const formatDateTime = (dateString: string): string => {
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy HH:mm');
  } catch {
    return dateString;
  }
};

// Format relative time (e.g., "2 days ago")
export const formatRelativeTime = (dateString: string): string => {
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
  } catch {
    return dateString;
  }
};

// Format shares (with decimal places)
export const formatShares = (shares: string | number): string => {
  if (shares === null || shares === undefined) return 'N/A';

  const num = typeof shares === 'string' ? parseFloat(shares) : shares;

  if (isNaN(num)) return 'N/A';

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 4,
  }).format(num);
};

// Format percentage
export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};

// Shorten large numbers (e.g., 1.5M, 2.3B, 1.2T)
export const formatCompactNumber = (value: number): string => {
  if (value >= 1_000_000_000_000) {
    return `${(value / 1_000_000_000_000).toFixed(1)}T`;
  } else if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`;
  } else if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  } else if (value >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`;
  }
  return value.toString();
};

// Format currency with short format for large numbers
export const formatCurrencyCompact = (value: string | number | null): string => {
  if (value === null || value === undefined) return 'N/A';

  const num = typeof value === 'string' ? parseFloat(value) : value;

  if (isNaN(num)) return 'N/A';

  // For large numbers (> 1 million), use compact format
  if (num >= 1_000_000) {
    return '$' + formatCompactNumber(num);
  }

  // For smaller numbers, use standard currency format
  return formatCurrency(num);
};

// Format date in CDT timezone (Dallas, TX)
export const formatDateCDT = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago',
      month: 'short',
      day: '2-digit',
      year: 'numeric',
    }).format(date);
  } catch {
    return dateString;
  }
};

// Format datetime in CDT timezone (Dallas, TX)
export const formatDateTimeCDT = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago',
      month: 'short',
      day: '2-digit',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date) + ' CDT';
  } catch {
    return dateString;
  }
};

// Format time only in CDT timezone (Dallas, TX)
export const formatTimeCDT = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Chicago',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date) + ' CDT';
  } catch {
    return dateString;
  }
};
