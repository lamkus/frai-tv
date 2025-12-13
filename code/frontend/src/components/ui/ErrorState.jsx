import { AlertTriangle, WifiOff, ServerCrash, RefreshCw, Home, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/utils';

/**
 * ErrorState - Reusable error display component
 *
 * Variants:
 * - network: Connection/network errors
 * - server: Server/API errors
 * - notFound: Resource not found
 * - generic: General errors
 */
export function ErrorState({
  variant = 'generic',
  title,
  message,
  onRetry,
  showHomeLink = true,
  className,
}) {
  const variants = {
    network: {
      icon: WifiOff,
      defaultTitle: 'Keine Verbindung',
      defaultMessage: 'Bitte überprüfe deine Internetverbindung und versuche es erneut.',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
    },
    server: {
      icon: ServerCrash,
      defaultTitle: 'Server-Fehler',
      defaultMessage: 'Der Server ist momentan nicht erreichbar. Bitte versuche es später erneut.',
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
    notFound: {
      icon: Search,
      defaultTitle: 'Nicht gefunden',
      defaultMessage: 'Das gesuchte Element konnte nicht gefunden werden.',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
    },
    generic: {
      icon: AlertTriangle,
      defaultTitle: 'Ein Fehler ist aufgetreten',
      defaultMessage: 'Etwas ist schiefgelaufen. Bitte versuche es erneut.',
      color: 'text-accent-gold',
      bgColor: 'bg-accent-gold/10',
    },
  };

  const config = variants[variant] || variants.generic;
  const Icon = config.icon;

  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4', className)}>
      {/* Icon */}
      <div
        className={cn(
          'w-20 h-20 rounded-full flex items-center justify-center mb-6',
          config.bgColor
        )}
      >
        <Icon size={40} className={config.color} />
      </div>

      {/* Title */}
      <h2 className="text-xl md:text-2xl font-display font-bold text-white mb-3 text-center">
        {title || config.defaultTitle}
      </h2>

      {/* Message */}
      <p className="text-retro-muted text-center max-w-md mb-8">
        {message || config.defaultMessage}
      </p>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-6 py-3 bg-accent-gold text-black font-bold rounded-lg hover:bg-accent-amber transition-all"
          >
            <RefreshCw size={18} />
            Erneut versuchen
          </button>
        )}

        {showHomeLink && (
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white font-semibold rounded-lg hover:bg-white/20 transition-all border border-white/20"
          >
            <Home size={18} />
            Zur Startseite
          </Link>
        )}
      </div>
    </div>
  );
}

/**
 * FullPageError - Full screen error state
 */
export function FullPageError({ variant, title, message, onRetry }) {
  return (
    <div className="min-h-screen bg-retro-black flex items-center justify-center">
      <ErrorState variant={variant} title={title} message={message} onRetry={onRetry} />
    </div>
  );
}

/**
 * InlineError - Compact inline error message
 */
export function InlineError({ message, onRetry, className }) {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-lg',
        className
      )}
    >
      <AlertTriangle size={20} className="text-red-500 flex-shrink-0" />
      <p className="text-white/80 text-sm flex-1">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-accent-gold hover:text-accent-amber text-sm font-semibold flex items-center gap-1"
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
}

export default ErrorState;
