import { useEffect, useRef, useState } from 'react';
import { X, Info } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * InfoPopup - Universelles Popup-Fenster für FRai.TV
 *
 * Verwendung:
 * - Video-Mouseover (Preview-Infos)
 * - Disclaimer/Notices
 * - Kurze Hinweise
 * - Tooltips mit mehr Content
 *
 * Größen: xs, sm, md, lg, xl, full
 * Positionen: center, top, bottom, tooltip (für Mouseover)
 */
export function InfoPopup({
  isOpen,
  onClose,
  title,
  children,
  icon: Icon = Info,
  size = 'sm',
  position = 'center',
  showClose = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  autoClose = false,
  autoCloseDelay = 3000,
  className,
  style,
  anchorElement, // Für Tooltip-Positionierung
}) {
  const popupRef = useRef(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [coords, setCoords] = useState(null);

  // Auto-close timer
  useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose?.();
      }, autoCloseDelay);
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, autoCloseDelay, onClose]);

  // Escape key handler
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose?.();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose, closeOnEscape]);

  // Animation trigger
  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
    }
  }, [isOpen]);

  // Tooltip positioning
  useEffect(() => {
    if (position === 'tooltip' && anchorElement && popupRef.current) {
      const anchorRect = anchorElement.getBoundingClientRect();
      const popupRect = popupRef.current.getBoundingClientRect();

      // Position above or below based on available space
      const spaceBelow = window.innerHeight - anchorRect.bottom;

      let top, left;

      if (spaceBelow > popupRect.height + 10) {
        // Position below
        top = anchorRect.bottom + 10;
      } else {
        // Position above
        top = anchorRect.top - popupRect.height - 10;
      }

      // Center horizontally relative to anchor
      left = anchorRect.left + anchorRect.width / 2 - popupRect.width / 2;

      // Keep within viewport
      left = Math.max(10, Math.min(left, window.innerWidth - popupRect.width - 10));

      setCoords({ top, left });
    }
  }, [position, anchorElement, isOpen]);

  if (!isOpen) return null;

  const sizes = {
    xs: 'max-w-xs',
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-[calc(100vw-2rem)]',
  };

  const positions = {
    center: 'items-center justify-center',
    top: 'items-start justify-center pt-20',
    bottom: 'items-end justify-center pb-20',
    tooltip: '', // Custom positioning via coords
  };

  const handleBackdropClick = (e) => {
    if (closeOnBackdrop && e.target === e.currentTarget) {
      onClose?.();
    }
  };

  const popupStyle =
    position === 'tooltip' && coords
      ? { position: 'fixed', top: `${coords.top}px`, left: `${coords.left}px`, ...style }
      : style;

  return (
    <>
      {/* Backdrop (nur wenn nicht Tooltip) */}
      {position !== 'tooltip' && (
        <div
          className={cn(
            'fixed inset-0 z-[9998] transition-opacity duration-300',
            isAnimating ? 'opacity-100' : 'opacity-0'
          )}
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(4px)',
          }}
          onClick={handleBackdropClick}
        />
      )}

      {/* Popup Container */}
      <div
        className={cn(
          'fixed z-[9999]',
          position === 'tooltip' ? '' : `inset-0 flex p-4 ${positions[position]}`
        )}
        onClick={position !== 'tooltip' ? handleBackdropClick : undefined}
      >
        {/* Popup Box - remAIke.IT Premium Style */}
        <div
          ref={popupRef}
          className={cn(
            'remaike-ui info-popup relative w-full rounded-xl overflow-hidden flex flex-col max-h-[85vh]',
            'transform transition-all duration-300',
            isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0',
            position === 'tooltip' ? '' : sizes[size],
            className
          )}
          style={{
            // fallback inline stying preserved for support
            background: 'linear-gradient(145deg, #070707 0%, #0d0a07 40%, #050505 100%)',
            border: '1.2px solid rgba(201,169,98,0.8)',
            boxShadow:
              '0 20px 60px rgba(0,0,0,0.55), 0 0 0 1px rgba(0,0,0,0.35), 0 0 28px rgba(201,169,98,0.15)',
            ...popupStyle,
          }}
        >
          {/* Gold Accent Bar */}
          <div
            className="absolute top-0 left-0 right-0 h-[2px] z-10"
            style={{
              background: 'linear-gradient(90deg, #c9a962 0%, #e7cf87 50%, #c9a962 100%)',
              boxShadow: '0 0 14px rgba(201, 169, 98, 0.65)',
            }}
          />

          {/* Header */}
          <div className="flex items-center justify-between p-5 border-b border-[#c9a962]/20 bg-[#0a0a0a] shrink-0">
            {Icon && (
              <div className="flex items-center gap-3">
                <Icon size={24} style={{ color: '#c9a962' }} />
                {title && (
                  <h3
                    className="text-xl font-bold tracking-wide"
                    style={{ color: '#c9a962', fontFamily: 'Bebas Neue, sans-serif' }}
                  >
                    {title}
                  </h3>
                )}
              </div>
            )}
            {!Icon && title && (
              <h3
                className="text-xl font-bold tracking-wide"
                style={{ color: '#c9a962', fontFamily: 'Bebas Neue, sans-serif' }}
              >
                {title}
              </h3>
            )}
            {showClose && onClose && (
              <button
                onClick={onClose}
                className="p-2 rounded-full transition-all duration-200 hover:bg-[#c9a962]/10 text-[#999999] hover:text-[#c9a962]"
              >
                <X size={20} />
              </button>
            )}
          </div>

          {/* Content */}
          <div
            className="p-6 overflow-y-auto scrollbar-gold"
            style={{
              color: '#cccccc',
              fontSize: '14px',
              lineHeight: '1.6',
            }}
          >
            {children}
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * QuickNotice - Kleines Hinweis-Popup (Auto-Close)
 */
export function QuickNotice({ isOpen, onClose, message, icon: Icon = Info, variant = 'info' }) {
  const variants = {
    info: { bg: 'rgba(201, 169, 98, 0.15)', color: '#c9a962' },
    success: { bg: 'rgba(34, 197, 94, 0.15)', color: '#22c55e' },
    warning: { bg: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24' },
    error: { bg: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' },
  };

  return (
    <InfoPopup
      isOpen={isOpen}
      onClose={onClose}
      size="xs"
      position="top"
      showClose={false}
      closeOnBackdrop={false}
      autoClose
      autoCloseDelay={2500}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: variants[variant].bg }}
        >
          <Icon size={20} style={{ color: variants[variant].color }} />
        </div>
        <p style={{ color: '#cccccc', margin: 0 }}>{message}</p>
      </div>
    </InfoPopup>
  );
}

/**
 * VideoInfoTooltip - Spezielles Tooltip für Video-Mouseover
 */
export function VideoInfoTooltip({ video, anchorElement, isOpen, onClose }) {
  if (!video) return null;

  return (
    <InfoPopup
      isOpen={isOpen}
      onClose={onClose}
      title={video.title}
      size="md"
      position="tooltip"
      anchorElement={anchorElement}
      showClose={false}
      closeOnBackdrop={true}
      closeOnEscape={true}
    >
      {video.description && (
        <p className="mb-3" style={{ color: '#999999', fontSize: '13px' }}>
          {video.description.slice(0, 150)}...
        </p>
      )}
      <div className="flex items-center gap-4 text-sm" style={{ color: '#666666' }}>
        {video.year && <span>📅 {video.year}</span>}
        {video.duration && <span>⏱️ {video.duration}</span>}
        {video.category && <span>🎬 {video.category}</span>}
      </div>
    </InfoPopup>
  );
}

export default InfoPopup;
