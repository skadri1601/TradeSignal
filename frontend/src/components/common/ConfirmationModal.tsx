import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, AlertCircle, Info, X, Loader2 } from 'lucide-react';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'warning',
  isLoading = false,
}: ConfirmationModalProps) {
  // Icon based on variant
  const Icon = variant === 'danger' ? AlertTriangle : variant === 'warning' ? AlertCircle : Info;

  // Colors based on variant
  const iconColors = {
    danger: 'text-red-400 bg-red-500/20 border-red-500/30',
    warning: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
    info: 'text-purple-400 bg-purple-500/20 border-purple-500/30',
  };

  const confirmButtonColors = {
    danger: 'bg-red-600 hover:bg-red-700 shadow-lg shadow-red-500/20',
    warning: 'bg-purple-600 hover:bg-purple-700 shadow-lg shadow-purple-500/20',
    info: 'bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/20',
  };

  const handleConfirm = () => {
    if (!isLoading) {
      onConfirm();
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="bg-[#0f0f1a] border border-white/10 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
            >
              {/* Header */}
              <div className="relative bg-white/5 border-b border-white/10 px-6 py-4">
                <button
                  onClick={handleClose}
                  disabled={isLoading}
                  className="absolute top-4 right-4 p-1 hover:bg-white/10 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Close"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
                <h2 className="text-xl font-bold text-white pr-8">{title}</h2>
              </div>

              {/* Content */}
              <div className="px-6 py-6">
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center border ${iconColors[variant]}`}>
                    <Icon className="w-6 h-6" />
                  </div>

                  {/* Message */}
                  <div className="flex-1 pt-1">
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {message}
                    </p>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="px-6 py-4 bg-black/20 border-t border-white/10 flex items-center justify-end gap-3">
                <button
                  onClick={handleClose}
                  disabled={isLoading}
                  className="px-4 py-2 rounded-lg font-medium text-gray-300 border border-white/20 hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {cancelText}
                </button>
                <button
                  onClick={handleConfirm}
                  disabled={isLoading}
                  className={`px-4 py-2 rounded-lg font-medium text-white transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${confirmButtonColors[variant]}`}
                >
                  {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  {confirmText}
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
