import { useState, useEffect, useCallback } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * Toast notification component
 * 
 * Variants:
 * - success: Green with checkmark
 * - error: Red with X
 * - warning: Amber with alert
 * - info: Blue with info icon
 */
export function Toast({
  message,
  variant = 'info',
  duration = 5000,
  onClose,
  position = 'bottom-right',
}) {
  const [isVisible, setIsVisible] = useState(true);
  const [isLeaving, setIsLeaving] = useState(false);

  const handleClose = useCallback(() => {
    setIsLeaving(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, 200);
  }, [onClose]);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, handleClose]);

  // handleClose is defined above with useCallback

  if (!isVisible) return null;

  const variants = {
    success: {
      icon: CheckCircle,
      bg: 'bg-green-500/10 border-green-500/30',
      iconColor: 'text-green-500',
    },
    error: {
      icon: XCircle,
      bg: 'bg-accent-red/10 border-accent-red/30',
      iconColor: 'text-accent-red',
    },
    warning: {
      icon: AlertCircle,
      bg: 'bg-accent-amber/10 border-accent-amber/30',
      iconColor: 'text-accent-amber',
    },
    info: {
      icon: Info,
      bg: 'bg-accent-cyan/10 border-accent-cyan/30',
      iconColor: 'text-accent-cyan',
    },
  };

  const positions = {
    'top-left': 'top-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    'bottom-right': 'bottom-4 right-4',
  };

  const { icon: Icon, bg, iconColor } = variants[variant];

  return (
    <div
      className={cn(
        'fixed z-50 flex items-center gap-3',
        'px-4 py-3 rounded-lg border backdrop-blur-sm',
        'shadow-lg min-w-[280px] max-w-md',
        bg,
        positions[position],
        isLeaving ? 'animate-fade-out' : 'animate-slide-up'
      )}
      role="alert"
    >
      <Icon className={cn('shrink-0', iconColor)} size={20} />
      <p className="flex-1 text-fluid-sm">{message}</p>
      <button
        onClick={handleClose}
        className="shrink-0 text-retro-muted hover:text-white transition-colors"
        aria-label="Schließen"
      >
        <X size={16} />
      </button>
    </div>
  );
}

/**
 * Toast container for managing multiple toasts
 */
export function ToastContainer({ toasts, removeToast }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={() => removeToast(toast.id)}
          position="bottom-right"
        />
      ))}
    </div>
  );
}

/**
 * Simple hook for toast management
 */
export function useToast() {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, variant = 'info', duration = 5000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, variant, duration }]);
    return id;
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const success = (message) => addToast(message, 'success');
  const error = (message) => addToast(message, 'error');
  const warning = (message) => addToast(message, 'warning');
  const info = (message) => addToast(message, 'info');

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
    ToastContainer: () => <ToastContainer toasts={toasts} removeToast={removeToast} />,
  };
}

export default Toast;
