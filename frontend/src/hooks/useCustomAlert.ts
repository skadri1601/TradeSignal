import { useState, useCallback } from 'react';

interface AlertOptions {
  title?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
}

export function useCustomAlert() {
  const [alertState, setAlertState] = useState<{
    show: boolean;
    message: string;
    title?: string;
    type?: 'info' | 'success' | 'warning' | 'error';
  }>({
    show: false,
    message: '',
    type: 'info'
  });

  const showAlert = useCallback((message: string, options?: AlertOptions) => {
    setAlertState({
      show: true,
      message,
      title: options?.title,
      type: options?.type || 'info'
    });
  }, []);

  const hideAlert = useCallback(() => {
    setAlertState(prev => ({ ...prev, show: false }));
  }, []);

  return {
    alertState,
    showAlert,
    hideAlert
  };
}

