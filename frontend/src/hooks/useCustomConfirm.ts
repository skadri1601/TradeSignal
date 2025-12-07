import { useState, useCallback } from 'react';

interface ConfirmOptions {
  title?: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'danger' | 'info';
}

export function useCustomConfirm() {
  const [confirmState, setConfirmState] = useState<{
    show: boolean;
    message: string;
    title?: string;
    confirmText?: string;
    cancelText?: string;
    type?: 'warning' | 'danger' | 'info';
    onConfirm?: () => void;
  }>({
    show: false,
    message: '',
    type: 'warning'
  });

  const showConfirm = useCallback((
    message: string,
    onConfirm: () => void,
    options?: ConfirmOptions
  ) => {
    setConfirmState({
      show: true,
      message,
      title: options?.title,
      confirmText: options?.confirmText,
      cancelText: options?.cancelText,
      type: options?.type || 'warning',
      onConfirm: () => {
        hideConfirm();
        onConfirm();
      }
    });
  }, []);

  const hideConfirm = useCallback(() => {
    setConfirmState(prev => ({ ...prev, show: false, onConfirm: undefined }));
  }, []);

  return {
    confirmState,
    showConfirm,
    hideConfirm
  };
}

