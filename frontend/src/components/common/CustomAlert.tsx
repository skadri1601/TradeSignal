import { useEffect } from 'react';
import { X } from 'lucide-react';

interface CustomAlertProps {
  title?: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  onClose: () => void;
  show: boolean;
}

export default function CustomAlert({
  title,
  message,
  type = 'info',
  onClose,
  show
}: CustomAlertProps) {
  useEffect(() => {
    if (show) {
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = 'unset';
      };
    }
  }, [show]);

  if (!show) return null;

  const typeStyles = {
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      buttonBg: 'bg-blue-600 hover:bg-blue-700',
      titleColor: 'text-blue-900'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      buttonBg: 'bg-green-600 hover:bg-green-700',
      titleColor: 'text-green-900'
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
      buttonBg: 'bg-yellow-600 hover:bg-yellow-700',
      titleColor: 'text-yellow-900'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      iconBg: 'bg-red-100',
      iconColor: 'text-red-600',
      buttonBg: 'bg-red-600 hover:bg-red-700',
      titleColor: 'text-red-900'
    }
  };

  const styles = typeStyles[type];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
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
              <div className={`w-6 h-6 ${styles.iconColor} font-bold text-center leading-6`}>
                TS
              </div>
            </div>
            <h3 className={`text-lg font-bold ${styles.titleColor}`}>
              {title || 'TradeSignal'}
            </h3>
          </div>
          <button
            onClick={onClose}
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
        <div className="px-6 pb-4">
          <button
            onClick={onClose}
            className={`w-full ${styles.buttonBg} text-white font-semibold py-2.5 px-4 rounded-lg transition-colors`}
          >
            OK
          </button>
        </div>
      </div>
    </div>
  );
}

