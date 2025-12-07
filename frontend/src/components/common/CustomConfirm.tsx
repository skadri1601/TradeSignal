import { useEffect } from 'react';
import { X, AlertTriangle } from 'lucide-react';

interface CustomConfirmProps {
  title?: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  show: boolean;
  confirmText?: string;
  cancelText?: string;
  type?: 'warning' | 'danger' | 'info';
}

export default function CustomConfirm({
  title,
  message,
  onConfirm,
  onCancel,
  show,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning'
}: CustomConfirmProps) {
  useEffect(() => {
    if (show) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
  }, [show]);

  if (!show) return null;

  const typeStyles = {
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
      confirmBg: 'bg-yellow-600 hover:bg-yellow-700',
      titleColor: 'text-yellow-900'
    },
    danger: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      iconBg: 'bg-red-100',
      iconColor: 'text-red-600',
      confirmBg: 'bg-red-600 hover:bg-red-700',
      titleColor: 'text-red-900'
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      confirmBg: 'bg-blue-600 hover:bg-blue-700',
      titleColor: 'text-blue-900'
    }
  };

  const styles = typeStyles[type];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onCancel}
      />

      {/* Modal */}
      <div
        className={`relative w-full max-w-md ${styles.bg} ${styles.border} border-2 rounded-xl shadow-2xl transform transition-all`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className={`${styles.iconBg} rounded-full p-2`}>
              <AlertTriangle className={`w-6 h-6 ${styles.iconColor}`} />
            </div>
            <h3 className={`text-lg font-bold ${styles.titleColor}`}>
              {title || 'TradeSignal'}
            </h3>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          <p className="text-gray-700 text-sm leading-relaxed">{message}</p>
        </div>

        {/* Footer */}
        <div className="px-6 pb-4 flex space-x-3">
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-200 text-gray-800 font-semibold py-2.5 px-4 rounded-lg hover:bg-gray-300 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`flex-1 ${styles.confirmBg} text-white font-semibold py-2.5 px-4 rounded-lg transition-colors`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

