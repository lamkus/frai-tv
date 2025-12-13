import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * Modal component with portal rendering
 *
 * Features:
 * - Backdrop blur and click-to-close
 * - Keyboard escape to close
 * - Focus trap
 * - Animations
 * - Multiple sizes
 */
export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  showClose = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  className,
}) {
  const modalRef = useRef(null);
  const [isAnimating, setIsAnimating] = useState(false);

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose, closeOnEscape]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      setIsAnimating(true);
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Focus trap
  useEffect(() => {
    if (!isOpen || !modalRef.current) return;

    const focusableElements = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    firstFocusable?.focus();

    const handleTab = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable?.focus();
      } else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable?.focus();
      }
    };

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [isOpen]);

  if (!isOpen) return null;

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-[calc(100vw-2rem)] max-h-[calc(100vh-2rem)]',
  };

  const handleBackdropClick = (e) => {
    if (closeOnBackdrop && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4',
        isAnimating && 'animate-fade-in'
      )}
      style={{
        background: 'linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(10,10,20,0.95) 100%)',
        backdropFilter: 'blur(8px)',
      }}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-describedby={description ? 'modal-description' : undefined}
    >
      <div
        ref={modalRef}
        className={cn(
          'relative w-full',
          'rounded-xl shadow-2xl overflow-hidden',
          isAnimating && 'animate-scale-in',
          sizes[size],
          className
        )}
        style={{
          background: 'linear-gradient(180deg, rgba(26,26,36,0.98) 0%, rgba(18,18,26,0.99) 100%)',
          border: '1px solid rgba(212, 175, 55, 0.2)',
          boxShadow:
            '0 0 0 1px rgba(255,255,255,0.05), 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 80px -20px rgba(212, 175, 55, 0.15)',
        }}
      >
        {/* Gold accent line */}
        <div
          className="absolute top-0 left-0 right-0 h-[3px]"
          style={{
            background: 'linear-gradient(90deg, #e50914 0%, #d4af37 50%, #e50914 100%)',
            opacity: 0.8,
          }}
        />

        {/* Header */}
        {(title || showClose) && (
          <div className="flex items-start justify-between p-4 sm:p-6 border-b border-accent-gold/10">
            <div>
              {title && (
                <h2 id="modal-title" className="text-fluid-xl font-semibold text-white">
                  {title}
                </h2>
              )}
              {description && (
                <p id="modal-description" className="text-fluid-sm text-retro-muted mt-1">
                  {description}
                </p>
              )}
            </div>
            {showClose && (
              <button
                onClick={onClose}
                className="p-2 text-retro-muted hover:text-accent-gold hover:bg-accent-gold/10 rounded-lg transition-all -mr-1 -mt-1"
                aria-label="Schließen"
              >
                <X size={20} />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className={cn('p-4 sm:p-6', !title && !showClose && 'pt-4 sm:pt-6')}>{children}</div>
      </div>
    </div>
  );
}

/**
 * Confirm dialog modal - FRai.TV Style
 */
export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = 'Bestätigen',
  message,
  confirmText = 'Bestätigen',
  cancelText = 'Abbrechen',
  variant = 'danger',
}) {
  const variants = {
    danger:
      'bg-gradient-to-r from-accent-red to-red-600 hover:from-red-600 hover:to-accent-red text-white',
    warning:
      'bg-gradient-to-r from-accent-amber to-accent-gold hover:from-accent-gold hover:to-accent-amber text-retro-black',
    info: 'bg-gradient-to-r from-accent-cyan to-blue-500 hover:from-blue-500 hover:to-accent-cyan text-retro-black',
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-retro-muted mb-6">{message}</p>
      <div className="flex gap-3">
        <button
          onClick={onClose}
          className="btn flex-1 bg-retro-gray/50 hover:bg-retro-gray border border-retro-light/20 hover:border-accent-gold/30 transition-all"
        >
          {cancelText}
        </button>
        <button
          onClick={() => {
            onConfirm();
            onClose();
          }}
          className={cn('btn flex-1 font-semibold shadow-lg transition-all', variants[variant])}
        >
          {confirmText}
        </button>
      </div>
    </Modal>
  );
}

export default Modal;
